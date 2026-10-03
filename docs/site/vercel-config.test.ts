import { readdirSync, readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * One deployment answers both hosts: pilot-shell.com pages move to qualitylayer.dev,
 * while pilot-shell.com's API and share links keep answering. This evaluates vercel.json's redirect and rewrite rules the way
 * Vercel does, in order, first match wins: `:name` is one segment, `:name*` the rest,
 * a parenthesised group is a raw regular expression, `$1` and `:name` fill a destination.
 * An API file with a fixed path is served before any rewrite; a dynamic one (`[task].ts`)
 * only after the rewrites, so a catch-all rewrite would hide it. It is an approximation
 * of Vercel's matcher, enough for the rules this file holds; the deployed check
 * (scripts/check-deploy.sh) is the real one.
 */

type Rule = {
  source: string;
  destination: string;
  permanent?: boolean;
  has?: { type: string; value: string }[];
};
const config = JSON.parse(readFileSync(new URL("./vercel.json", import.meta.url), "utf8")) as {
  redirects: Rule[];
  rewrites: Rule[];
  headers: { source: string; headers: { key: string; value: string }[] }[];
};

/** The deployed API routes, one per file in api/: a `[name]` segment matches any one segment. */
const apiRoutes = readdirSync(new URL("./api", import.meta.url), { recursive: true, encoding: "utf8" })
  .filter((file) => file.endsWith(".ts") && !file.endsWith(".test.ts") && !file.startsWith("_lib"))
  .map((file) => {
    const route = `/api/${file.replace(/\.ts$/, "")}`;
    return { dynamic: route.includes("["), regex: new RegExp(`^${route.replace(/\[[^\]]+\]/g, "[^/]+")}$`) };
  });
const apiRoute = (path: string, dynamic: boolean) =>
  apiRoutes.some((route) => route.dynamic === dynamic && route.regex.test(path.split("?")[0] as string));

function compile(source: string): { regex: RegExp; names: string[] } {
  const names: string[] = [];
  let out = "";
  for (let i = 0; i < source.length; ) {
    const char = source[i] as string;
    if (char === "(") {
      // A raw group, copied to its matching close parenthesis.
      let depth = 0;
      let j = i;
      for (; j < source.length; j++) {
        if (source[j] === "\\") j++;
        else if (source[j] === "(") depth++;
        else if (source[j] === ")" && --depth === 0) break;
      }
      names.push(String(names.length + 1));
      out += source.slice(i, j + 1);
      i = j + 1;
    } else if (char === ":") {
      const name = /^:([A-Za-z_]+)(\*?)/.exec(source.slice(i));
      if (name === null) throw new Error(`bad source ${source}`);
      names.push(name[1] as string);
      out += name[2] === "*" ? "(.*)" : "([^/]+)";
      i += name[0].length;
    } else {
      out += char.replace(/[.+?^${}|[\]\\]/g, "\\$&");
      i++;
    }
  }
  return { regex: new RegExp(`^${out}$`), names };
}

function fill(destination: string, names: string[], groups: string[]): string {
  let out = destination;
  names.forEach((name, index) => {
    out = out.replaceAll(`:${name}*`, groups[index] ?? "").replaceAll(`:${name}`, groups[index] ?? "");
  });
  return out.replace(/\$(\d)/g, (_, digit: string) => groups[Number(digit) - 1] ?? "");
}

const hostMatches = (rule: Rule, host: string) =>
  (rule.has ?? []).every(
    (condition) => condition.type !== "host" || new RegExp(`^(?:${condition.value})$`).test(host),
  );

type Answer =
  | { kind: "redirect"; status: number; location: string }
  | { kind: "function" }
  | { kind: "rewrite"; to: string }
  | { kind: "none" };

function answer(host: string, path: string): Answer {
  for (const rule of config.redirects) {
    const { regex, names } = compile(rule.source);
    const hit = regex.exec(path);
    if (hit === null || !hostMatches(rule, host)) continue;
    return {
      kind: "redirect",
      status: rule.permanent === true ? 308 : 307,
      location: fill(rule.destination, names, hit.slice(1)),
    };
  }
  if (apiRoute(path, false)) return { kind: "function" };
  for (const rule of config.rewrites) {
    const { regex, names } = compile(rule.source);
    const hit = regex.exec(path);
    if (hit !== null && hostMatches(rule, host)) {
      return { kind: "rewrite", to: fill(rule.destination, names, hit.slice(1)) };
    }
  }
  if (apiRoute(path, true)) return { kind: "function" };
  return { kind: "none" };
}

const OLD = "pilot-shell.com";
const NEW = "qualitylayer.dev";
const V2_LINK = "/s/Xk3Jd92xA7pQ4mZr1bTnWe";

describe("pilot-shell.com pages move to qualitylayer.dev", () => {
  it("sends the pricing page there for good, keeping the path", () => {
    expect(answer(OLD, "/pricing")).toEqual({
      kind: "redirect",
      status: 308,
      location: "https://qualitylayer.dev/pricing",
    });
  });

  it("sends the home page, the docs and the blog there, and the www host too", () => {
    expect(answer(OLD, "/")).toEqual({ kind: "redirect", status: 308, location: "https://qualitylayer.dev/" });
    expect(answer(OLD, "/docs/features/hooks")).toMatchObject({
      status: 308,
      location: "https://qualitylayer.dev/docs/features/hooks",
    });
    expect(answer(OLD, "/blog/some-post")).toMatchObject({ location: "https://qualitylayer.dev/blog/some-post" });
    expect(answer(`www.${OLD}`, "/pricing")).toMatchObject({ location: "https://qualitylayer.dev/pricing" });
  });

  it("serves the beta's install script from the dev branch, on either host", () => {
    for (const host of [OLD, NEW]) {
      expect(answer(host, "/install.sh"), host).toEqual({
        kind: "redirect",
        status: 307,
        location: "https://raw.githubusercontent.com/maxritter/pilot-shell/dev/install.sh",
      });
    }
  });
});

describe("doc pages that moved or were removed", () => {
  it("send the Pilot Shell 11 pages to the docs home", () => {
    for (const path of ["/docs/features/hooks", "/docs/workflows/spec"]) {
      expect(answer(NEW, path), path).toEqual({ kind: "redirect", status: 308, location: "/docs" });
    }
  });

  it("send each merged page to the section that took it over", () => {
    expect(answer(NEW, "/docs/phases/verify")).toEqual({ kind: "redirect", status: 308, location: "/docs/steps/verify" });
    expect(answer(NEW, "/docs/workflow/check/verify")).toEqual({ kind: "redirect", status: 308, location: "/docs/steps/verify" });
    expect(answer(NEW, "/docs/guides/cockpit")).toEqual({ kind: "redirect", status: 308, location: "/docs/app" });
    expect(answer(NEW, "/docs/cockpit")).toEqual({ kind: "redirect", status: 308, location: "/docs/app" });
    expect(answer(NEW, "/docs/reference/peers")).toMatchObject({ location: "/docs/reference/commands#session-messaging" });
  });
});

describe("what pilot-shell.com still answers itself", () => {
  it("serves its API routes itself", () => {
    for (const path of ["/api/share", "/api/share/Xk3Jd92xA7pQ4mZr1bTnWe", "/api/share/feedback/batch", "/api/team/pass", "/api/trial/start"]) {
      expect(answer(OLD, path), path).toEqual({ kind: "function" });
    }
  });

  it("serves the files the share page loads, or a link opened there would be an empty page", () => {
    // The page's script, stylesheet and fonts are 'self' under the share page's policy,
    // so they must come from pilot-shell.com itself, not from a redirect to another origin.
    for (const path of ["/assets/website-DZk-iDwE.js", "/assets/website-rIc8s26h.css", "/fonts/geist-latin.woff2", "/brand/favicon.svg", "/favicon.ico"]) {
      expect(answer(OLD, path).kind, path).not.toBe("redirect");
    }
  });

  it("shows the share page for a link, without redirecting", () => {
    expect(answer(OLD, V2_LINK)).toEqual({ kind: "rewrite", to: "/" });
  });
});

describe("qualitylayer.dev is not redirected", () => {
  it("serves pages, the API and share links itself", () => {
    expect(answer(NEW, "/pricing")).toEqual({ kind: "rewrite", to: "/" });
    expect(answer(NEW, "/docs/app")).toEqual({ kind: "rewrite", to: "/docs/app" });
    expect(answer(NEW, "/api/team/pass")).toEqual({ kind: "function" });
    expect(answer(NEW, V2_LINK)).toEqual({ kind: "rewrite", to: "/" });
  });

  it("serves every team route, the dynamic ones too, and not the page in their place", () => {
    // A shared task is PUT to /api/team/tasks/<id>: the page in its place answered 405 to the client.
    for (const path of ["/api/team/tasks", "/api/team/tasks/t-1", "/api/team/tasks/t-1/comments?after=0", "/api/team/members"]) {
      expect(answer(NEW, path), path).toEqual({ kind: "function" });
    }
  });
});

describe("the App's pages and its update endpoint", () => {
  it("shows the page in the browser for the landing page a Slack DM opens and for the download page", () => {
    for (const path of ["/open/ask/t_9c2/7f3a", "/open/team/t_9c2", "/download"]) {
      expect(answer(NEW, path), path).toEqual({ kind: "rewrite", to: "/" });
    }
  });

  it("answers the updater's and the download page's addresses from their API routes, which exist", () => {
    for (const [path, route] of [
      ["/app/latest.json", "/api/app/latest"],
      ["/app/downloads.json", "/api/app/downloads"],
    ] as const) {
      expect(answer(NEW, path), path).toEqual({ kind: "rewrite", to: route });
      expect(apiRoute(route, false), route).toBe(true);
    }
  });
});

describe("the demo of the App", () => {
  it("moved from /cockpit-demo to /app-demo, and the old address redirects there", () => {
    for (const [from, to] of [
      ["/cockpit-demo", "/app-demo/"],
      ["/cockpit-demo/", "/app-demo/"],
      ["/cockpit-demo/index.html", "/app-demo/index.html"],
    ] as const) {
      expect(answer(NEW, from), from).toEqual({ kind: "redirect", status: 308, location: to });
    }
    expect(answer(NEW, "/app-demo/index.html")).toEqual({ kind: "rewrite", to: "/app-demo/index.html" });
  });
});

describe("the landing page's own headers", () => {
  const policy = () => {
    const rule = config.headers.find((h) => h.source === "/open/(.*)");
    return rule?.headers.find((h) => h.key === "Content-Security-Policy")?.value ?? "";
  };

  it("lets the page make no request and open nothing but the App's own link in a frame", () => {
    expect(policy()).toContain("connect-src 'none'");
    expect(policy()).toContain("frame-src qualitylayer:");
    expect(policy()).toContain("default-src 'self'");
  });
});

describe("the share page's own headers", () => {
  it("keep the strict content security policy on /s/*", () => {
    const rule = config.headers.find((h) => h.source === "/s/(.*)");
    expect(rule?.headers.find((h) => h.key === "Content-Security-Policy")?.value).toContain("default-src 'self'");
  });
});
