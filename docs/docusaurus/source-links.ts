/** Beta documentation lives on dev; the generated changelog comes from the repository root. */
export function docsSourceUrl(docPath: string): string {
  const path = docPath === "reference/changelog.md" ? "CHANGELOG.md" : `docs/docusaurus/docs/${docPath}`;
  return `https://github.com/maxritter/pilot-shell/blob/dev/${path}`;
}
