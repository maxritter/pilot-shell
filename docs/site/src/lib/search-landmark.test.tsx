import { renderToReadableStream } from "react-dom/server.browser";
import { dirname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import ts from "typescript";
import { expect, it } from "vitest";
import SearchMain from "../../../docusaurus/src/components/SearchMain";

it("typechecks the shared docs landmark using the site's own React dependencies", () => {
  const site = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
  const configPath = resolve(site, "tsconfig.app.json");
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  expect(config.error).toBeUndefined();
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, site, undefined, configPath);
  const source = resolve(site, "../docusaurus/src/components/SearchMain.tsx");
  const host = ts.createCompilerHost(parsed.options);
  const exists = host.fileExists;
  const docsPackages = resolve(site, "../docusaurus/node_modules") + sep;
  // A site-only checkout must not need the docs application's installed packages.
  host.fileExists = (path) => !path.startsWith(docsPackages) && exists(path);
  const program = ts.createProgram([source], parsed.options, host);
  const errors = ts.getPreEmitDiagnostics(program).map((error) => ts.flattenDiagnosticMessageText(error.messageText, "\n"));
  expect(errors).toEqual([]);
});

it("gives search results a main landmark that a keyboard user can focus", async () => {
  const stream = await renderToReadableStream(<SearchMain><h1>Search the documentation</h1><p>No results found.</p></SearchMain>);
  await stream.allReady;
  const html = await new Response(stream).text();
  expect(html).toContain('<main id="main-content" tabindex="-1">');
  expect(html).toContain("No results found.");
  expect(html).not.toContain("<nav");
  expect(html).not.toContain("<footer");
});
