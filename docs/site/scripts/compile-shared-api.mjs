import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import ts from "typescript";

const site = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const profiles = {
  current: ["team-files", "team-purge", "screenshots", "sha256", "trial-hash"],
  legacy9: ["team-files", "screenshots"],
};

// These helpers are also loaded directly by Node operator scripts, which need their .ts imports.
// Vercel's Edge compiler retains those suffixes after emitting .js, so give its resolver explicit JS.
export async function compileSharedApi(out = resolve(site, "api/_lib"), { profile = "current", sourceRoot = site } = {}) {
  const names = Object.hasOwn(profiles, profile) ? profiles[profile] : null;
  if (!names) throw new Error("Unknown shared API build profile");
  const config = ts.readConfigFile(resolve(sourceRoot, "tsconfig.json"), ts.sys.readFile);
  if (config.error) throw new Error("Cannot read the shared API compiler configuration");
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, sourceRoot);
  if (!parsed.options.rewriteRelativeImportExtensions) throw new Error("Shared API emission must rewrite relative TypeScript imports");
  const emitted = await Promise.all(names.map(async name => {
    const source = resolve(sourceRoot, "api/_lib", `${name}.ts`);
    const text = await readFile(source, "utf8");
    if (profile === "legacy9" && ts.preProcessFile(text).importedFiles.some(({ fileName }) => fileName.startsWith(".") && /\.tsx?$/.test(fileName))) throw new Error(`Schema-9 helper ${name} needs explicit JavaScript dependency paths`);
    const result = ts.transpileModule(text, {
      fileName: source,
      compilerOptions: { ...parsed.options, module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022, sourceMap: false, inlineSourceMap: false },
    });
    if (ts.preProcessFile(result.outputText).importedFiles.some(({ fileName }) => fileName.startsWith(".") && /\.tsx?$/.test(fileName))) throw new Error(`Unresolved TypeScript import in ${name}`);
    return { name, text: result.outputText };
  }));
  // The deployed schema-9 helpers already use .js imports; emitting launch-only helpers would change that service's module graph.
  if (profile === "legacy9") return [];
  await mkdir(out, { recursive: true });
  for (const { name, text } of emitted) await writeFile(resolve(out, `${name}.js`), text);
  return names.map((name) => `${name}.js`);
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  const args = process.argv.slice(2);
  if (args.length && (args.length !== 2 || args[0] !== "--profile")) throw new Error("Usage: compile-shared-api.mjs [--profile current|legacy9]");
  console.log(`Compiled shared Edge modules: ${(await compileSharedApi(undefined, { profile: args[1] ?? "current" })).join(", ")}`);
}
