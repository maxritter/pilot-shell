import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { beta9Statements, FEATURE_ID } from "./db-beta9.ts";

type Row = Record<string, unknown>;
export type Query = (text: string, params?: unknown[]) => PromiseLike<Row[]>;
export type Feature = { id: typeof FEATURE_ID; applied_at: string };
export type PreparedSource = {
  schema: string;
  featureSql: string;
  provenance: { frontendCommit: string; backendBase: string; apiDigest: string; overlayDigest: string; schemaSha256: string; featureSha256: string };
};
export type PreparedState = { tables: string[]; features: Feature[] };

const hash = (bytes: string | Uint8Array) => createHash("sha256").update(bytes).digest("hex");
const SCHEMA_HASH = "a338affdec3a7d9e062288f52ce4f6f5a5366471d954f801d0691367f81ee27a";
const FEATURE_HASH = "5184e71904f0ecd7578693f2e8d8d8852d873b62df75a1beefbab849e750b985";
export const LEGACY_TABLES = ["team_tasks", "team_comments", "team_asks", "team_access", "team_devices", "team_epochs", "team_wrapped_keys", "team_groups", "team_slack", "shares", "share_comments", "trials", "workflow_texts", "team_follows", "team_slack_queue", "team_slack_open", "team_slack_digests", "team_handovers", "team_instructions", "team_file_ledgers", "team_files", "team_file_parts", "team_visits"];
const ARTIFACT_TABLES = ["beta9_artifact_versions", "beta9_artifact_editors"];
// Fingerprints include ordered columns, types, nullability/defaults and constraints, never data.
const CATALOG_HASHES = { base: "ff187258ee57013d882bf52425da49a4666cbbbb0c5723687588574267ebff37", artifacts: "43075a1656eb55feae8b959f375a23edbec4f73a9737493df9f964d2fddfcece" };

export function preparedArguments(args: string[]): { directory: string; source: string } | undefined {
  if (!args.includes("--prepared") && !args.includes("--source")) return undefined;
  const value = (name: string) => {
    const at = args.indexOf(name), result = args[at + 1];
    if (at < 0 || args.lastIndexOf(name) !== at || !result || result.startsWith("--"))
      throw new Error("--prepared <directory> and --source <commit> are required together, once each.");
    return result;
  };
  return { directory: value("--prepared"), source: value("--source") };
}

export async function preparedSource(directory: string, frontend: string): Promise<PreparedSource> {
  // Keep the existing JavaScript preparer's runtime validation as the single receipt boundary.
  const preparer = await import(new URL("./prepare-beta-backend.mjs", import.meta.url).href) as {
    verifyPrepared: (directory: string, frontend: string) => { frontendCommit: string; backendBase: string; apiDigest: string; overlayDigest: string };
  };
  const receipt = preparer.verifyPrepared(directory, frontend);
  const schema = readFileSync(join(directory, "api/_lib/schema.sql"), "utf8");
  const featureSql = readFileSync(join(directory, "api/_lib/beta9-schema.sql"), "utf8");
  if (hash(schema) !== SCHEMA_HASH || hash(featureSql) !== FEATURE_HASH)
    throw new Error("Prepared backup requires the reviewed schema9 and additive artifact SQL bytes.");
  beta9Statements(featureSql);
  const { frontendCommit, backendBase, apiDigest, overlayDigest } = receipt;
  return { schema, featureSql, provenance: { frontendCommit, backendBase, apiDigest, overlayDigest, schemaSha256: SCHEMA_HASH, featureSha256: FEATURE_HASH } };
}

export const CATALOG_QUERIES = [
  "select c.relname as name from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relkind in ('r','p','f','m','v') order by c.relname",
  "select c.relname as table_name,a.attname as column_name,format_type(a.atttypid,a.atttypmod) as type,a.attnotnull as required,pg_get_expr(d.adbin,d.adrelid) as default_value from pg_class c join pg_namespace n on n.oid=c.relnamespace join pg_attribute a on a.attrelid=c.oid left join pg_attrdef d on d.adrelid=c.oid and d.adnum=a.attnum where n.nspname='public' and c.relkind in ('r','p') and a.attnum>0 and not a.attisdropped order by c.relname,a.attnum",
  "select t.relname as table_name,c.contype as type,pg_get_constraintdef(c.oid,false) as definition from pg_constraint c join pg_class t on t.oid=c.conrelid join pg_namespace n on n.oid=t.relnamespace where n.nspname='public' order by t.relname,c.contype,pg_get_constraintdef(c.oid,false)",
  "select t.relname as table_name from pg_trigger g join pg_class t on t.oid=g.tgrelid join pg_namespace n on n.oid=t.relnamespace where n.nspname='public' and not g.tgisinternal order by t.relname",
] as const;

export const LEDGER_QUERY = "select n from schema_migrations order by n";
export const FEATURE_QUERY = "select id,applied_at::text as applied_at from beta9_overlay_migrations order by id";

/** Inspection is read-only; callers may collect these statements in their snapshot transaction. */
export function stateFromCatalog(catalog: Row[][], ledger: Row[], feature: Row[]): PreparedState {
  if (JSON.stringify(ledger) !== JSON.stringify(Array.from({ length: 9 }, (_, i) => ({ n: i + 1 }))))
    throw new Error("Backup requires the genuine main migration ledger exactly1–9.");
  const names = (catalog[0] ?? []).map((row) => row.name);
  const hasFeature = names.includes("beta9_overlay_migrations");
  const expected = [...LEGACY_TABLES, "schema_migrations", ...(hasFeature ? ["beta9_overlay_migrations", ...ARTIFACT_TABLES] : [])].sort();
  if (JSON.stringify(names) !== JSON.stringify(expected))
    throw new Error("Backup public tables differ from the complete known schema9 table set.");
  if (hasFeature && (feature.length !== 1 || feature[0]?.id !== FEATURE_ID || !validTime(feature[0]?.applied_at)))
    throw new Error("Backup artifact feature ledger is unknown or incomplete.");
  if (hash(JSON.stringify(catalog.slice(1))) !== CATALOG_HASHES[hasFeature ? "artifacts" : "base"])
    throw new Error("Backup schema9 column, constraint or trigger shape differs from the reviewed contract.");
  return { tables: [...LEGACY_TABLES, ...(hasFeature ? ARTIFACT_TABLES : [])], features: hasFeature ? [{ id: FEATURE_ID, applied_at: feature[0]!.applied_at as string }] : [] };
}

export async function inspectPrepared(query: Query): Promise<PreparedState> {
  const catalog = [];
  for (const text of CATALOG_QUERIES) catalog.push(await query(text));
  const ledger = await query(LEDGER_QUERY);
  const feature = catalog[0]?.some((row) => row.name === "beta9_overlay_migrations") ? await query(FEATURE_QUERY) : [];
  return stateFromCatalog(catalog, ledger, feature);
}

/** Only allow the two known feature states, with original ledger time preserved as decimal text. */
export function copyFeatures(value: unknown): Feature[] {
  if (!Array.isArray(value) || value.length > 1 || value.some((row) => !row || typeof row !== "object" || Object.keys(row).sort().join() !== "applied_at,id" || row.id !== FEATURE_ID || !validTime(row.applied_at)))
    throw new Error("Backup contains unknown or malformed artifact feature metadata.");
  return value as Feature[];
}

function validTime(value: unknown): value is string {
  return typeof value === "string" && /^\d{1,19}$/.test(value) && BigInt(value) <= 9223372036854775807n;
}

export function preparedTables(features: Feature[]): string[] {
  return [...LEGACY_TABLES, ...(features.length ? ARTIFACT_TABLES : [])];
}
