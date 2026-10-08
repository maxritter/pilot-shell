import { readFileSync } from "node:fs";

const requiredNames = [
  "RSA_PRIVATE_KEY", "POLAR_ACCESS_TOKEN", "POLAR_ORGANIZATION_ID", "POLAR_TEAM_BENEFIT_ID",
  "DATABASE_URL", "UPSTASH_KV_REST_API_URL", "UPSTASH_KV_REST_API_TOKEN",
  "SLACK_CLIENT_ID", "SLACK_CLIENT_SECRET", "SLACK_TOKEN_KEY",
  "FEEDBACK_GITHUB_TOKEN", "FEEDBACK_STORE_URL", "FEEDBACK_STORE_SECRET", "FEEDBACK_LINK_SECRET",
  "RESEND_API_KEY",
];

function fail(message) {
  throw new Error(message);
}

function jsonFile(path) {
  try { return JSON.parse(readFileSync(path, "utf8")); }
  catch { fail("could not read deployment JSON"); }
}

function deploymentUrl(value) {
  if (typeof value !== "string" || !value || value.trim() !== value) fail("deployment URL is invalid");
  let parsed;
  try { parsed = new URL(value.includes("://") ? value : `https://${value}`); }
  catch { fail("deployment URL is invalid"); }
  if (parsed.protocol !== "https:" || parsed.username || parsed.password || parsed.port ||
      !/^[a-z0-9-]+\.vercel\.app$/.test(parsed.hostname) ||
      (parsed.pathname !== "/" && parsed.pathname !== "") || parsed.search || parsed.hash)
    fail("deployment URL is invalid");
  return parsed.origin;
}

function receipt(value) {
  if (!value || typeof value.id !== "string" || !/^dpl_[A-Za-z0-9]+$/.test(value.id))
    fail("deployment receipt has no valid id");
  return { id: value.id, url: deploymentUrl(value.url) };
}

try {
  const [command, ...rest] = process.argv.slice(2);
  const options = new Map();
  const allowed = new Set(["--deployment", "--metadata", "--project", "--target", "--git-ref", "--git-sha"]);
  for (let index = 0; index < rest.length; index += 2) {
    const flag = rest[index], value = rest[index + 1];
    if (!allowed.has(flag) || !value || value.startsWith("--") || options.has(flag)) fail("invalid verifier arguments");
    options.set(flag, value);
  }
  if (!options.has("--deployment")) fail("deployment receipt is required");
  const deployed = receipt(jsonFile(options.get("--deployment")));
  if (command === "receipt-id" && options.size === 1) {
    process.stdout.write(`${deployed.id}\n`);
  } else if (command === "verify" && options.size === allowed.size) {
    const target = options.get("--target"), ref = options.get("--git-ref"), sha = options.get("--git-sha");
    if (!((target === "preview" && ref === "dev") || (target === "production" && ref === "main")) ||
        !/^[0-9a-f]{40}$/.test(sha)) fail("expected deployment target or revision is invalid");
    const runtime = jsonFile(options.get("--metadata"));
    if (!runtime || runtime.id !== deployed.id || deploymentUrl(runtime.url) !== deployed.url ||
        runtime.source !== "cli" || runtime.projectId !== options.get("--project") || runtime.readyState !== "READY")
      fail("deployment is not the ready CLI deployment of the expected project");
    if (target === "preview" ? runtime.target !== null && runtime.target !== "preview" : runtime.target !== "production")
      fail("deployment target does not match the expected environment");
    if (runtime.meta?.githubCommitRef !== ref || runtime.meta?.githubCommitSha !== sha)
      fail("deployment does not match the expected Git revision");
    if (!Array.isArray(runtime.env) || !runtime.env.every((name) => typeof name === "string"))
      fail("deployment runtime variable names are unavailable");
    const missing = requiredNames.filter((name) => !runtime.env.includes(name));
    if (missing.length) fail(`deployment runtime variables are missing: ${missing.join(", ")}`);
    process.stdout.write(`${deployed.url}\n`);
  } else fail("invalid verifier arguments");
} catch (error) {
  process.stderr.write(`deployment verification failed: ${error.message}\n`);
  process.exitCode = 1;
}
