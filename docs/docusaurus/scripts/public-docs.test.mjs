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

test("the built guides explain current answers, changed agreements and live sharing", () => {
  const discuss = page("steps/discuss/");
  assert.match(discuss, /Your turn/);
  assert.match(discuss, /Answer in any order/);
  assert.match(discuss, /immediately/);
  assert.doesNotMatch(discuss, /one question at a time|question N/);
  assert.match(page("steps/plan/"), /Was and Now/);
  assert.match(page("steps/verify/"), /Proof for each Done means point/);
  assert.match(page("team/plans/"), /open page updates as the task changes/);
  assert.doesNotMatch(page("team/plans/"), /Reload the page/);
});
