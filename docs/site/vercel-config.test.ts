import { readdirSync, readFileSync } from "node:fs";
import { matchesGlob } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * This evaluates vercel.json's redirect and rewrite rules the way Vercel does, in order, first
 * match wins: `:name` is one segment, `:name*` the rest, a parenthesised group is a raw regular
 * expression, `$1` and `:name` fill a destination. An API file with a fixed path is served before
 * any rewrite; a dynamic one (`[task].ts`) only after the rewrites, so a catch-all rewrite would
 * hide it. It is an approximation of Vercel's matcher, enough for the rules this file holds; the
 * deployed check (scripts/check-deploy.sh) is the real one.
 */

type Rule = {
  source: string;
  destination: string;
  permanent?: boolean;
};
const config = JSON.parse(readFileSync(new URL("./vercel.json", import.meta.url), "utf8")) as {
  regions: string[];
  redirects: Rule[];
  rewrites: Rule[];
  headers: { source: string; headers: { key: string; value: string }[] }[];
};

/** A file in api/ that Vercel deploys as a function: not a test, and not under a folder or named with a leading underscore (`_lib`, `__fixture__`). */
const isHandler = (file: string) =>
  file.endsWith(".ts") && !file.endsWith(".test.ts") && !file.split("/").some((part) => part.startsWith("_"));

/** The deployed API routes, one per file in api/: a `[name]` segment matches any one segment. */
const apiRoutes = readdirSync(new URL("./api", import.meta.url), { recursive: true, encoding: "utf8" })
  .filter(isHandler)
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

type Answer =
  | { kind: "redirect"; status: number; location: string }
  | { kind: "function" }
  | { kind: "rewrite"; to: string }
  | { kind: "none" };

function answer(path: string): Answer {
  for (const rule of config.redirects) {
    const { regex, names } = compile(rule.source);
    const hit = regex.exec(path);
    if (hit === null) continue;
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
    if (hit !== null) {
      return { kind: "rewrite", to: fill(rule.destination, names, hit.slice(1)) };
    }
  }
  if (apiRoute(path, true)) return { kind: "function" };
  return { kind: "none" };
}

const V2_LINK = "/s/Xk3Jd92xA7pQ4mZr1bTnWe";

describe("no Pilot Shell host is left", () => {
  it("names neither pilot-shell.com nor claude-pilot in any redirect, rewrite or header rule", () => {
    expect(JSON.stringify(config)).not.toMatch(/pilot-shell\.com|claude-pilot/);
  });

  it("serves the install scripts from the release repository's dev branch", () => {
    for (const script of ["install.sh", "install.ps1"]) {
      expect(answer(`/${script}`), script).toEqual({
        kind: "redirect",
        status: 307,
        location: `https://raw.githubusercontent.com/maxritter/pilot-shell/dev/${script}`,
      });
    }
  });
});

describe("doc pages that moved or were removed", () => {
  it("lands every section redirect on a heading that exists in the current docs", () => {
    for (const rule of config.redirects) {
      if (!rule.destination.startsWith("/docs") || !rule.destination.includes("#")) continue;
      const [route, anchor] = rule.destination.split("#");
      const file = route === "/docs" ? "intro" : route.slice("/docs/".length);
      const markdown = readFileSync(new URL(`../docusaurus/docs/${file}.md`, import.meta.url), "utf8");
      const headings = [...markdown.matchAll(/^#{1,6}\s+(.+)$/gm)].map((match) => {
        const explicit = match[1].match(/\{#([^}]+)\}/);
        return explicit?.[1] ?? match[1].toLowerCase().replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-");
      });
      expect(headings, `${rule.source} → ${rule.destination}`).toContain(anchor);
    }
  });

  it("send the Pilot Shell 11 pages to the docs home", () => {
    for (const path of ["/docs/features/hooks", "/docs/workflows/spec"]) {
      expect(answer(path), path).toEqual({ kind: "redirect", status: 308, location: "/docs" });
    }
  });

  it("send each merged page to the section that took it over", () => {
    expect(answer("/docs/phases/verify")).toEqual({ kind: "redirect", status: 308, location: "/docs/steps/verify" });
    expect(answer("/docs/workflow/check/verify")).toEqual({ kind: "redirect", status: 308, location: "/docs/steps/verify" });
    expect(answer("/docs/guides/cockpit")).toEqual({ kind: "redirect", status: 308, location: "/docs/app" });
    expect(answer("/docs/cockpit")).toEqual({ kind: "redirect", status: 308, location: "/docs/app" });
    expect(answer("/docs/reference/peers")).toMatchObject({ location: "/docs/reference/commands#session-messaging" });
  });
});

describe("qualitylayer.dev is not redirected", () => {
  it("serves pages, the API and share links itself", () => {
    expect(answer("/pricing")).toEqual({ kind: "rewrite", to: "/" });
    expect(answer("/docs/app")).toEqual({ kind: "rewrite", to: "/docs/app" });
    expect(answer("/api/team/pass")).toEqual({ kind: "function" });
    expect(answer(V2_LINK)).toEqual({ kind: "rewrite", to: "/" });
  });

  it("serves every team route, the dynamic ones too, and not the page in their place", () => {
    // A shared task is PUT to /api/team/tasks/<id>: the page in its place answered 405 to the client.
    for (const path of ["/api/team/tasks", "/api/team/tasks/t-1", "/api/team/tasks/t-1/comments?after=0", "/api/team/members"]) {
      expect(answer(path), path).toEqual({ kind: "function" });
    }
  });
});

describe("the App's pages and its update endpoint", () => {
  it("shows the page in the browser for the landing page a Slack DM opens and for the download page", () => {
    for (const path of ["/open/ask/t_9c2/7f3a", "/open/team/t_9c2", "/download"]) {
      expect(answer(path), path).toEqual({ kind: "rewrite", to: "/" });
    }
  });

  it("answers the updater's and the download page's addresses from their API routes, which exist", () => {
    for (const [path, route] of [
      ["/app/latest.json", "/api/app/latest"],
      ["/app/downloads.json", "/api/app/downloads"],
    ] as const) {
      expect(answer(path), path).toEqual({ kind: "rewrite", to: route });
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
      expect(answer(from), from).toEqual({ kind: "redirect", status: 308, location: to });
    }
    expect(answer("/app-demo/index.html")).toEqual({ kind: "rewrite", to: "/app-demo/index.html" });
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
  const policyOf = (source: string) =>
    config.headers.find((h) => h.source === source)?.headers.find((h) => h.key === "Content-Security-Policy")?.value ?? "";

  it("keep the strict content security policy on /s/*, with a frame only for the site's own mockup page", () => {
    const policy = policyOf("/s/(.*)");
    expect(policy).toContain("default-src 'self'");
    expect(policy).toContain("script-src 'self'");
    expect(policy).toContain("frame-src 'self'");
    expect(policy).not.toContain("frame-src 'none'");
  });

  it("serve the mockup frame under its own policy: inline scripts and styles, data images, no network, framed by the site only", () => {
    const policy = policyOf("/s-frame.html");
    for (const part of ["default-src 'none'", "script-src 'unsafe-inline'", "style-src 'unsafe-inline'", "img-src data: blob:", "font-src data:", "frame-ancestors 'self'"])
      expect(policy, part).toContain(part);
    // Nothing that lets a mockup reach out: no fetch, no frames of its own, no remote images.
    expect(policy).not.toContain("connect-src");
    expect(policy).not.toContain("frame-src");
    expect(policy).not.toContain("https:");
  });

  it("keeps the mockup frame where the share page can load it", () => {
    expect(answer("/s-frame.html").kind).not.toBe("redirect");
  });
});

describe("where the functions run", () => {
  it("keeps tests and fixtures out of the deployment while including every handler", () => {
    const patterns = readFileSync(new URL("../../.vercelignore", import.meta.url), "utf8")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line !== "" && !line.startsWith("#"));
    const ignoredPath = (path: string) => patterns.some((pattern) => matchesGlob(path, pattern.endsWith("/") ? `${pattern}**` : pattern));
    const ignored = (file: string) => ignoredPath(`docs/site/api/${file}`);
    const files = readdirSync(new URL("./api", import.meta.url), { recursive: true, encoding: "utf8" });
    const tests = files.filter((file) => file.endsWith(".test.ts"));
    expect(tests.length).toBeGreaterThan(0);
    expect(tests.filter((file) => !ignored(file))).toEqual([]);
    expect(ignored("__fixture__/orphan.ts")).toBe(true);
    expect(files.filter(isHandler).filter((file) => ignored(file))).toEqual([]);
    for (const privateFile of ["docs/site/.env.local", "qualitylayer/dist/dev-trial-key.json", "docs/plans/a-task/01-discuss.md", "docs/designs/a-design.html", ".verify-backend/live-routes.json", "VERIFY-REPORT.md"]) {
      expect(ignoredPath(privateFile), privateFile).toBe(true);
    }
  });

  it("defaults any newly discovered function to Frankfurt too", () => {
    expect(config.regions).toEqual(["fra1"]);
  });

  it("pins every handler to fra1, next to the database and Redis", () => {
    const handlers = readdirSync(new URL("./api", import.meta.url), { recursive: true, encoding: "utf8" }).filter(isHandler);
    expect(handlers.length).toBeGreaterThan(0);
    const regions = Object.fromEntries(
      handlers.map((file) => {
        const source = readFileSync(new URL(`./api/${file}`, import.meta.url), "utf8");
        return [file, /export const config = \{[^}]*regions: (\[[^\]]*\])/.exec(source)?.[1]];
      }),
    );
    expect(regions).toEqual(Object.fromEntries(handlers.map((file) => [file, '["fra1"]'])));
  });
});

describe("who may call the API from a browser", () => {
  it("sets no CORS header for the whole API: each route answers for itself, and only the share page's two do", () => {
    // A blanket `/api/(.*)` rule once sent `Access-Control-Allow-Origin: *` on every route, over the methods each one serves.
    const cors = config.headers.filter((rule) => rule.headers.some((header) => header.key.toLowerCase().startsWith("access-control-")));
    expect(cors).toEqual([]);
  });
});
