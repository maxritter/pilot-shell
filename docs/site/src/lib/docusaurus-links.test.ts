import { describe, expect, it } from "vitest";
import { docsSourceUrl } from "../../../docusaurus/source-links";

describe("documentation source links", () => {
  it("links beta pages to their source and the generated changelog to its original file", () => {
    expect(docsSourceUrl("install.md")).toBe("https://github.com/maxritter/pilot-shell/blob/dev/docs/docusaurus/docs/install.md");
    expect(docsSourceUrl("team/plans.md")).toBe("https://github.com/maxritter/pilot-shell/blob/dev/docs/docusaurus/docs/team/plans.md");
    expect(docsSourceUrl("reference/changelog.md")).toBe("https://github.com/maxritter/pilot-shell/blob/dev/CHANGELOG.md");
  });
});
