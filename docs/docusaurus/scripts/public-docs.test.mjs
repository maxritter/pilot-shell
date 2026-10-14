import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

const page = (route) => {
  const paths = [`../build/docs/${route}index.html`, route ? `../build/docs/${route.replace(/\/$/, "")}.html` : "../build/docs.html"];
  const url = paths.map((path) => new URL(path, import.meta.url)).find(existsSync);
  assert.ok(url, `No built page for ${route}; run npm run build first`);
  return readFileSync(url, "utf8");
};

const text = (route) => page(route)
  .replace(/<(script|style)\b[^>]*>[\s\S]*?<\/\1>/gi, "")
  .replace(/<[^>]+>/g, " ")
  .replace(/\s+/g, " ");

test("App illustrations open at full size from each guide, with an accessible name and the right theme", () => {
  for (const route of ["", "app/", "steps/discuss/", "steps/plan/", "steps/implement/", "steps/verify/", "steps/review/", "designs/"]) {
    const html = page(route);
    const links = [...html.matchAll(/<a\b[^>]*class="ql-diagram"[^>]*>[\s\S]*?<\/a>/g)].map((m) => m[0]);
    assert.ok(links.length >= 2, `${route}: no full-size illustrations; run npm run build first`);
    for (const link of links) {
      const href = link.match(/href="([^"]+)"/)?.[1];
      const src = link.match(/<img[^>]*src="([^"]+)"/)?.[1];
      assert.equal(href, src, `${route}: full size must open the illustration shown`);
      assert.match(link, /aria-label="Open illustration full size:/);
      assert.match(link, /target="_blank"/);
      assert.match(link, /rel="noopener noreferrer"/);
      assert.match(link, /data-illustration-theme="(?:light|dark)"/);
      assert.match(link, /Open full size/);
    }
  }
});

test("the built guides explain current answers, complete Plan approval and live sharing", () => {
  const discuss = text("steps/discuss/");
  assert.match(discuss, /Your turn/);
  assert.match(discuss, /Answer in any order/);
  assert.match(discuss, /one question at a time/);
  assert.match(discuss, /Skip for now/);
  assert.match(discuss, /your own answer/i);
  assert.match(discuss, /Send/);
  assert.match(discuss, /immediately/);
  assert.doesNotMatch(discuss, /question N|Undo.{0,40}five seconds/);
  const plan = text("steps/plan/");
  assert.match(plan, /Findings from the technical review return to the planning agent/);
  assert.match(plan, /Read the complete Plan/);
  assert.match(plan, /Approve Plan/);
  assert.match(plan, /Give feedback/);
  assert.doesNotMatch(plan, /Agree to each.{0,40}Done means/);
  assert.match(page("steps/verify/"), /Proof for each point/);
  assert.match(page("steps/verify/"), /Done means/);
  assert.match(text("steps/verify/"), /point shows its evidence as it comes in/);
  assert.match(page("team/plans/"), /open page updates as the task changes/);
  assert.doesNotMatch(page("team/plans/"), /Reload the page/);
});

test("the built App guides use Files and Comments and explain the current reading and privacy boundaries", () => {
  const app = text("app/");
  assert.match(app, /Files/);
  assert.match(app, /Comments/);
  assert.match(app, /Working designs are compact entries in/);
  assert.match(app, /Open design canvas/);
  assert.match(app, /document header/);
  assert.match(app, /Agent status/);
  assert.match(app, /Dollar amounts stay hidden until you open it/);
  assert.match(app, /tokens unpriced/);
  assert.doesNotMatch(app, /Designs.{0,20}tab|Comments.{0,30}Files.{0,30}and.{0,30}Designs/);
  assert.match(page("steps/implement/"), /Here in the App/);
  assert.match(page("steps/implement/"), /In my terminal/);
  assert.match(page("steps/implement/"), /Start the build/);
  assert.match(text("steps/implement/"), /Claude Code, Codex or another agent/);
  assert.doesNotMatch(page("steps/implement/"), /Start with (?:Codex|Claude Code)/);
  assert.match(page("steps/implement/"), /Build/);
  assert.match(page("designs/"), /compact entry in/);
  assert.match(text("reference/files/"), /No usage events/);
  assert.match(text("reference/files/"), /Include designs/);
  assert.match(text("reference/files/"), /Shared design previews run no scripts/);
  assert.match(text("reference/files/"), /terminal output/);
});
