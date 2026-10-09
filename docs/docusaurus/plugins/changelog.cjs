const fs = require("node:fs");
const path = require("node:path");

// Render the repository's changelog without maintaining another copy by hand.
module.exports = function changelogPlugin(context) {
  const source = path.resolve(context.siteDir, "../../CHANGELOG.md");
  const destination = path.join(context.siteDir, "docs/reference/changelog.md");

  function generate() {
    const markdown = fs.readFileSync(source, "utf8").replace(/^# Changelog\s*\n/, "");
    const legacy = [...markdown.matchAll(/^## (?:Earlier Pilot Shell.*|\[(\d+)[^\]]*\].*)$/gm)]
      .find((match) => match[1] === undefined || Number(match[1]) < 12);
    const legacyStart = legacy?.index ?? -1;
    const current = legacyStart === -1 ? markdown : markdown.slice(0, legacyStart);
    let history = legacyStart === -1 ? "" : markdown.slice(legacyStart);
    // Keep old releases readable inside one disclosure, out of the main TOC.
    let fence = null;
    history = history.split("\n").map((line) => {
      const marker = line.match(/^\s*(`{3,}|~{3,})/);
      if (marker) {
        if (fence === null) fence = marker[1][0];
        else if (fence === marker[1][0]) fence = null;
        return line;
      }
      if (fence === null) return line.replace(/^(#{2,6}) /, (_, hashes) => "#".repeat(Math.min(6, hashes.length + 2)) + " ");
      return line;
    }).join("\n");
    // Each current release becomes one section, so the page can set the version beside its notes.
    const [intro, ...releases] = current.trim().split(/^(?=## )/m);
    // "Latest" belongs to the newest published version; an "Unreleased" section above it is not one.
    const latest = releases.findIndex((release) => /^## \[?v?\d/.test(release));
    const sections = releases.map((release, i) =>
      `<section class="cl-rel${i === latest ? " cl-latest" : ""}">\n\n${release.trim()}\n\n</section>`).join("\n\n");
    const content = [
      "---", "title: Changelog", "slug: /changelog",
      "description: Current QualityLayer development changes and preserved Pilot Shell release history.",
      "toc_max_heading_level: 2", "---", "",
      intro.trim(), "", sections, "",
      history ? "## Earlier releases\n\n<details>\n<summary>Pilot Shell release history</summary>\n\n" + history.trim() + "\n\n</details>" : "",
      "", "[Published release downloads](https://github.com/maxritter/pilot-shell/releases)", "",
    ].join("\n");
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    if (!fs.existsSync(destination) || fs.readFileSync(destination, "utf8") !== content) fs.writeFileSync(destination, content);
  }

  // Run before the docs plugin reads its files, then keep root edits in sync.
  generate();
  return {
    name: "qualitylayer-changelog",
    getPathsToWatch: () => [source],
    loadContent: generate,
  };
};
