import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

const site = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const names = ["team-files", "team-purge", "screenshots", "sha256", "trial-hash"];

// These helpers are also loaded directly by Node operator scripts, which need their .ts imports.
// Vercel's Edge compiler retains those suffixes after emitting .js, so give its resolver explicit JS.
export async function compileSharedApi(out = resolve(site, "api/_lib")) {
  const config = ts.readConfigFile(resolve(site, "tsconfig.json"), ts.sys.readFile);
  if (config.error) throw new Error("Cannot read the shared API compiler configuration");
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, site);
  if (!parsed.options.rewriteRelativeImportExtensions) throw new Error("Shared API emission must rewrite relative TypeScript imports");
  await mkdir(out, { recursive: true });
  for (const name of names) {
    const source = resolve(site, "api/_lib", `${name}.ts`);
    const result = ts.transpileModule(await readFile(source, "utf8"), {
      fileName: source,
      compilerOptions: { ...parsed.options, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, sourceMap: false, inlineSourceMap: false },
    });
    if (ts.preProcessFile(result.outputText).importedFiles.some(({ fileName }) => fileName.startsWith(".") && /\.tsx?$/.test(fileName))) throw new Error(`Unresolved TypeScript import in ${name}`);
    await writeFile(resolve(out, `${name}.js`), result.outputText);
  }
  return names.map((name) => `${name}.js`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  console.log(`Compiled shared Edge modules: ${(await compileSharedApi()).join(", ")}`);
}
