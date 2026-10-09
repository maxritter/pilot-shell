import assert from "node:assert/strict";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";

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
  assert.match(unreleased[2], /^## Unreleased/);
  assert.equal(unreleased[1], "cl-rel");
  assert.match(newest[2], /^## 12\.0\.0-beta\.28/);
  assert.equal(newest[1], "cl-rel cl-latest");
  assert.equal(older[1], "cl-rel");
});

test("without an Unreleased section the first version is still the Latest", () => {
  const page = render(CHANGELOG.replace(/## Unreleased[\s\S]*?(?=## 12\.0\.0-beta\.28)/, ""));
  const latest = [...page.matchAll(/<section class="cl-rel cl-latest">\s*## (\S+)/g)];
  assert.deepEqual(latest.map((match) => match[1]), ["12.0.0-beta.28"]);
});
