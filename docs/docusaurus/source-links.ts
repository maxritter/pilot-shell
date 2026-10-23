/** Public documentation follows stable main. */
export function docsSourceUrl(docPath: string): string {
  const path = `docs/docusaurus/docs/${docPath}`;
  return `https://github.com/maxritter/qualitylayer/blob/main/${path}`;
}
