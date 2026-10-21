import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// A live docs server uses .docusaurus; production must not overwrite its routes.
const cli = fileURLToPath(new URL("../node_modules/@docusaurus/core/bin/docusaurus.mjs", import.meta.url));
const result = spawnSync(process.execPath, [cli, "build", ...process.argv.slice(2)], {
  stdio: "inherit",
  env: { ...process.env, DOCUSAURUS_GENERATED_FILES_DIR_NAME: ".docusaurus-build" },
});
if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}
process.exit(result.status ?? 1);
