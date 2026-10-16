import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { publicationLoader, refreshPublicationDates } from "../src/changelog-dates.mjs";

const changelogPlugin = createRequire(import.meta.url)("../plugins/changelog.cjs");

// The plugin reads <siteDir>/../../CHANGELOG.md and writes <siteDir>/docs/reference/changelog.md.
function render(changelog) {
  const root = mkdtempSync(join(tmpdir(), "ql-changelog-plugin-"));
  try {
    const siteDir = join(root, "docs", "docusaurus");
    mkdirSync(siteDir, { recursive: true });
    writeFileSync(join(root, "CHANGELOG.md"), changelog);
    changelogPlugin({ siteDir });
    return readFileSync(join(siteDir, "docs", "reference", "changelog.md"), "utf8");
  } finally {
    rmSync(root, { recursive: true, force: true });
  }
}

const CHANGELOG = [
  "# Changelog",
  "",
  "Notable changes.",
  "",
  "## Unreleased",
  "",
  "### New",
  "",
  "- Not shipped yet.",
  "",
  "## 12.0.0-beta.28",
  "",
  "### Fixed",
  "",
  "- Shipped.",
  "",
  "## 12.0.0-beta.27",
  "",
  "### Fixed",
  "",
  "- Older.",
  "",
].join("\n");

test("an Unreleased section is listed but never carries the Latest badge: the newest version does", () => {
  const page = render(CHANGELOG);
  const sections = [...page.matchAll(/<section class="([^"]+)">\s*([\s\S]*?)<\/section>/g)];
  assert.equal(sections.length, 3);
  const [unreleased, newest, older] = sections;
  assert.match(unreleased[2], /## Unreleased/);
  assert.match(unreleased[2], /Not published/);
  assert.equal(unreleased[1], "cl-rel");
  assert.match(newest[2], /## 12\.0\.0-beta\.28/);
  assert.equal(newest[1], "cl-rel cl-latest");
  assert.equal(older[1], "cl-rel");
});

test("without an Unreleased section the first version is still the Latest", () => {
  const page = render(CHANGELOG.replace(/## Unreleased[\s\S]*?(?=## 12\.0\.0-beta\.28)/, ""));
  const latest = [...page.matchAll(/<section class="cl-rel cl-latest">\s*<header class="cl-version">\s*## (\S+)/g)];
  assert.deepEqual(latest.map((match) => match[1]), ["12.0.0-beta.28"]);
});

test("published versions retain their exact heading and get GitHub publication times in UTC", () => {
  const page = render("# Changelog\n\n## 12.0.0-beta.57\n\n### Fixed\n\n- A fix.\n\n## 12.0.0-beta.999\n\n- Not known.\n");
  assert.match(page, /## 12\.0\.0-beta\.57\n/);
  assert.match(page, /datetime="2026-10-16T06:50:36Z">Published 16 Oct 2026, 06:50 UTC/);
  assert.match(page, /data-release-version="12\.0\.0-beta\.999">Publication date unavailable/);
});

test("all 57 published betas have an offline publication fallback", () => {
  const publications = JSON.parse(readFileSync(new URL("../plugins/release-publications.json", import.meta.url)));
  for (let i = 1; i <= 57; i++) assert.match(publications[`12.0.0-beta.${i}`], /^2026-\d\d-\d\dT\d\d:\d\d:\d\dZ$/);
});

test("the grouped early betas each show their actual time without fabricating a final 12.0.0 date or new headings", () => {
  const page = render("# Changelog\n\n## 12.0.0 betas before beta.14\n\n- Earlier notes stay grouped.\n");
  assert.match(page, /## 12\.0\.0 betas before beta\.14/);
  assert.match(page, /Publication dates for betas 1–13/);
  assert.equal([...page.matchAll(/data-release-version=/g)].length, 13);
  assert.doesNotMatch(page, /data-release-version="12\.0\.0"/);
  assert.doesNotMatch(page, /cl-latest/);
  assert.equal([...page.matchAll(/^## /gm)].length, 1);
  assert.match(page, /Published 1 Oct 2026, 20:50 UTC/);
});

test("one cached batch supplies a release published after the build without changing headings", async () => {
  let requests = 0;
  const load = publicationLoader(async (url) => {
    requests++;
    assert.equal(url, "/app/releases.json");
    return { ok: true, json: async () => ({ releases: { "12.0.0-beta.58": "2026-10-17T01:02:03Z" } }) };
  });
  const attributes = { "data-release-version": "12.0.0-beta.58" };
  const node = { textContent: "Publication date unavailable", getAttribute: (key) => attributes[key], setAttribute: (key, value) => { attributes[key] = value; } };
  const root = { querySelectorAll: () => [node] };
  await Promise.all([refreshPublicationDates(root, load), refreshPublicationDates(root, load)]);
  assert.equal(requests, 1);
  assert.equal(node.textContent, "Published 17 Oct 2026, 01:02 UTC");
  assert.equal(attributes.datetime, "2026-10-17T01:02:03Z");
});

test("offline or invalid live metadata leaves the static publication text intact", async () => {
  const node = { textContent: "Published 16 Oct 2026, 06:50 UTC", getAttribute: () => "12.0.0-beta.57", setAttribute: () => assert.fail("invalid dates are not applied") };
  const root = { querySelectorAll: () => [node] };
  await refreshPublicationDates(root, publicationLoader(async () => { throw new Error("offline"); }));
  await refreshPublicationDates(root, async () => ({ "12.0.0-beta.57": "not a date" }));
  assert.equal(node.textContent, "Published 16 Oct 2026, 06:50 UTC");
});
