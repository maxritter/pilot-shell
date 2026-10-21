const fs = require("node:fs");
const path = require("node:path");
const publications = require("./release-publications.json");
const { publicationDate } = require("./publication-date.cjs");
const versionOf = (heading) => heading.match(/^## \[?v?(\d+\.\d+\.\d+(?:-[\w.-]+)?)(?:\](?:\([^)]*\))?)?\s*$/)?.[1];

function publicationTime(version) {
  const published = publications[version];
  const label = publicationDate(published);
  return `<time data-release-version="${version}"${label ? ` datetime="${published}"` : ""}>${label ?? "Publication date unavailable"}</time>`;
}

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
    const releases = current.trim().split(/^(?=## )/m);
    const intro = releases[0]?.startsWith("## ") ? "" : releases.shift() ?? "";
    // "Latest" belongs to the newest published version; an "Unreleased" section above it is not one.
    const latest = releases.findIndex((release) => versionOf(release.split("\n")[0]));
    const sections = releases.map((release, i) => {
      const [heading, ...body] = release.trim().split("\n");
      const version = versionOf(heading);
      const metadata = version
        ? publicationTime(version)
        : /^## \[?Unreleased\]?\s*$/i.test(heading) ? "Not published" : "";
      const before = heading.match(/^## 12\.0\.0 betas before beta\.(\d+)$/)?.[1];
      const grouped = before ? Object.keys(publications)
        .filter((v) => /^12\.0\.0-beta\.\d+$/.test(v) && Number(v.split(".").at(-1)) < Number(before))
        .sort((a, b) => Number(b.split(".").at(-1)) - Number(a.split(".").at(-1))) : [];
      const dates = grouped.length ? `<details class="cl-history-dates"><summary>Publication dates for betas 1–${Number(before) - 1}</summary><ul>${grouped.map((v) => `<li><span class="cl-history-version">${v}</span>${publicationTime(v)}</li>`).join("")}</ul></details>` : "";
      return `<section class="cl-rel${i === latest ? " cl-latest" : ""}">\n\n<header class="cl-version">\n\n${heading}\n\n${metadata ? `<p class="cl-published">${metadata}</p>` : ""}\n\n</header>\n\n${body.join("\n").trim()}\n\n${dates}\n\n</section>`;
    }).join("\n\n");
    const content = [
      "---", "title: Changelog", "slug: /changelog",
      "description: Current QualityLayer development changes and preserved Pilot Shell release history.",
      "toc_max_heading_level: 2", "---", "",
      intro.trim(), "", sections, "",
      history ? "## Earlier releases\n\n<details>\n<summary>Pilot Shell release history</summary>\n\n" + history.trim() + "\n\n</details>" : "",
      "", "[Published release downloads](https://github.com/maxritter/qualitylayer/releases)", "",
    ].join("\n");
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    if (!fs.existsSync(destination) || fs.readFileSync(destination, "utf8") !== content) fs.writeFileSync(destination, content);
  }

  // Run before the docs plugin reads its files, then keep root edits in sync.
  generate();
  return {
    name: "qualitylayer-changelog",
    getClientModules: () => [path.join(context.siteDir, "src/changelog-dates.mjs")],
    getPathsToWatch: () => [source],
    loadContent: generate,
  };
};
