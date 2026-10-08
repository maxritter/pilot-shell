import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

const page = (route) => {
  const paths = [`../build/docs/${route}index.html`, route ? `../build/docs/${route.replace(/\/$/, "")}.html` : "../build/docs.html"];
  const url = paths.map((path) => new URL(path, import.meta.url)).find(existsSync);
  assert.ok(url, `No built page for ${route}; run npm run build first`);
  return readFileSync(url, "utf8");
};

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
  const discuss = page("steps/discuss/");
  assert.match(discuss, /Your turn/);
  assert.match(discuss, /Answer in any order/);
  assert.match(discuss, /one question at a time/);
  assert.match(discuss, /Skip for now/);
  assert.match(discuss, /Your own answer/);
  assert.match(discuss, /Send/);
  assert.match(discuss, /immediately/);
  assert.doesNotMatch(discuss, /question N|Undo.{0,40}five seconds/);
  const plan = page("steps/plan/");
  assert.match(plan, /Technical review findings return to the planning agent/);
  assert.match(plan, /complete Plan appears in the main pane/);
  assert.match(plan, /Approve Plan/);
  assert.match(plan, /Give feedback/);
  assert.doesNotMatch(plan, /Agree to each.{0,40}Done means/);
  assert.match(page("steps/verify/"), /Proof for each Done means point/);
  assert.match(page("team/plans/"), /open page updates as the task changes/);
  assert.doesNotMatch(page("team/plans/"), /Reload the page/);
});

test("the built App guides use Files and Comments and explain the current reading and privacy boundaries", () => {
  const app = page("app/");
  assert.match(app, /Files/);
  assert.match(app, /Comments/);
  assert.match(app, /compact designs/);
  assert.match(app, /document header/);
  assert.match(app, /Agent status/);
  assert.match(app, /dollar amount/);
  assert.match(app, /tokens unpriced/);
  assert.doesNotMatch(app, /Designs.{0,20}tab|Comments.{0,30}Files.{0,30}and.{0,30}Designs/);
  assert.match(page("steps/implement/"), /Implement opens on/);
  assert.match(page("steps/implement/"), /Build/);
  assert.match(page("designs/"), /compact entry in/);
  assert.match(page("reference/files/"), /sends no usage events/);
  assert.match(page("reference/files/"), /raster still/);
  assert.match(page("reference/files/"), /interactive design pages/);
});
