// Migration A: dry-run first, then --apply, then --verify with the beta's existing injected env.
// No R2 objects or Redis records are changed. Run against the deployment's exact database/Redis pair.
import { pathToFileURL } from "node:url";
import { type Db, db } from "../api/_lib/db.ts";
import { type Redis, redis } from "../api/_lib/hot.ts";
import { importLegacyFiles, type LegacyPart, legacyParts } from "../api/_lib/team-file-store.ts";

type Reader = Pick<Redis, "scan" | "hscan">;
type Mode = "dry-run" | "apply" | "verify";
type Options = { mode: Mode; maxScans: number; maxTeams: number; maxParts: number; cursor: string; team?: string };
class Refusal extends Error {}

function options(args: string[]): Options {
  const result: Options = { mode: "dry-run", maxScans: 100, maxTeams: 100, maxParts: 10_000, cursor: "0" };
  let modes = 0;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--apply" || arg === "--verify" || arg === "--dry-run") { result.mode = arg.slice(2) as Mode; modes++; continue; }
    if (arg === "--team") {
      const team = args[++i];
      if (!team || team.length > 512 || /[\s*?[\]]/.test(team)) throw new Refusal("--team needs one exact team id");
      result.team = team;
      continue;
    }
    if (arg === "--cursor") {
      const cursor = args[++i] ?? "";
      if (!/^\d+$/.test(cursor)) throw new Refusal("--cursor must be a Redis cursor");
      result.cursor = cursor;
      continue;
    }
    const key = ({ "--max-scans": "maxScans", "--max-teams": "maxTeams", "--max-parts": "maxParts" } as Record<string, "maxScans" | "maxTeams" | "maxParts">)[arg ?? ""];
    if (!key) throw new Refusal("Unknown option; use --dry-run, --apply, --verify, --team, --cursor or --max-scans/teams/parts");
    const value = Number(args[++i]);
    const cap = key === "maxParts" ? 100_000 : 10_000;
    if (!Number.isSafeInteger(value) || value < 1 || value > cap) throw new Refusal(`${arg} must be between 1 and ${cap}`);
    result[key] = value;
  }
  if (modes > 1) throw new Refusal("Choose one of --dry-run, --apply and --verify");
  return result;
}

export async function verifyLegacyFiles(sql: Db, team: string, rows: LegacyPart[]): Promise<{ matchedParts: number; matchedBytes: number; durableParts: number; durableBytes: number }> {
  const [found] = await sql.query<{ matched_parts: number; matched_bytes: string; durable_parts: number; durable_bytes: string }>(
    `select (select count(*)::int from jsonb_to_recordset($2::jsonb) as x(file text, part int, bytes int, by text)
       join team_files f on f.team_id = $1 and f.file_id = x.file and f.owner_key = x.by and f.deleting_at is null
       join team_file_parts p on p.team_id = $1 and p.file_id = x.file and p.part = x.part and p.bytes = x.bytes and p.stored_at is not null) as matched_parts,
      (select coalesce(sum(x.bytes), 0) from jsonb_to_recordset($2::jsonb) as x(file text, part int, bytes int, by text)
       join team_files f on f.team_id = $1 and f.file_id = x.file and f.owner_key = x.by and f.deleting_at is null
       join team_file_parts p on p.team_id = $1 and p.file_id = x.file and p.part = x.part and p.bytes = x.bytes and p.stored_at is not null) as matched_bytes,
      (select count(*)::int from team_file_parts where team_id = $1 and stored_at is not null) as durable_parts,
      (select coalesce(sum(bytes), 0) from team_file_parts where team_id = $1 and stored_at is not null) as durable_bytes`,
    [team, JSON.stringify(rows)]);
  return { matchedParts: Number(found?.matched_parts ?? 0), matchedBytes: Number(found?.matched_bytes ?? 0), durableParts: Number(found?.durable_parts ?? 0), durableBytes: Number(found?.durable_bytes ?? 0) };
}

export async function backfillTeamFiles(args: string[], deps: { sql: Db; redis: Reader; now?: number }): Promise<Record<string, string | number | boolean>> {
  const opts = options(args);
  let scans = 0;
  let teams = 0;
  let parts = 0;
  let bytes = 0;
  let matchedParts = 0;
  let matchedBytes = 0;
  let durableParts = 0;
  let durableBytes = 0;
  let conflicts = 0;
  let complete = false;
  let cursor = opts.cursor;
  const seen = new Set<string>();
  const read = async (team: string) => {
    let partCursor = "0";
    const values: Record<string, unknown> = {};
    let unique = 0;
    do {
      if (scans >= opts.maxScans) throw new Refusal("Scan budget exhausted before a complete team ledger; increase --max-scans or use --team");
      scans++;
      const [next, flat] = await deps.redis.hscan(`teamfiles:${team}`, partCursor, { count: 100 });
      partCursor = String(next);
      for (let i = 0; i < flat.length; i += 2) {
        const raw = flat[i + 1];
        let value: unknown = raw;
        if (typeof raw === "string") { try { value = JSON.parse(raw); } catch { /* validation below refuses malformed rows */ } }
        const name = String(flat[i]);
        if (!Object.hasOwn(values, name)) unique++;
        values[name] = value;
        if (unique > opts.maxParts) throw new Refusal("Team ledger exceeds --max-parts; no partial team import was made");
      }
    } while (partCursor !== "0");
    const rows = legacyParts(values, opts.maxParts);
    if (opts.mode === "apply") await importLegacyFiles(deps.sql, team, rows, deps.now ?? Date.now());
    const verified = await verifyLegacyFiles(deps.sql, team, rows);
    teams++;
    parts += rows.length;
    bytes += rows.reduce((sum, row) => sum + row.bytes, 0);
    matchedParts += verified.matchedParts;
    matchedBytes += verified.matchedBytes;
    durableParts += verified.durableParts;
    durableBytes += verified.durableBytes;
    conflicts += rows.length - verified.matchedParts;
  };
  if (opts.team !== undefined) { await read(opts.team); complete = true; }
  else do {
    if (scans >= opts.maxScans || teams >= opts.maxTeams) break;
    const before = cursor;
    scans++;
    const [next, keys] = await deps.redis.scan(cursor, { match: "teamfiles:*", count: Math.min(100, opts.maxTeams - teams) });
    cursor = String(next);
    for (const key of keys) {
      if (seen.has(key)) continue;
      if (teams >= opts.maxTeams || scans >= opts.maxScans) { cursor = before; return { mode: opts.mode, complete: false, cursor, scans, teams, parts, bytes, matchedParts, matchedBytes, durableParts, durableBytes, conflicts }; }
      seen.add(key);
      if (key.startsWith("teamfiles:")) await read(key.slice("teamfiles:".length));
    }
    complete = cursor === "0";
  } while (!complete);
  return { mode: opts.mode, complete, cursor, scans, teams, parts, bytes, matchedParts, matchedBytes, durableParts, durableBytes, conflicts };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const sql = db();
    const client = redis();
    if (!sql || !client) throw new Refusal("DATABASE_URL and the existing Upstash REST credentials must be injected");
    const result = await backfillTeamFiles(process.argv.slice(2), { sql, redis: client });
    console.log(JSON.stringify(result));
    if (!result.complete || (result.mode !== "dry-run" && result.conflicts !== 0)) process.exitCode = 1;
  } catch (error) {
    console.error(error instanceof Refusal ? error.message : "File backfill failed; check connectivity, migration 8 and the legacy ledger without printing credentials");
    process.exitCode = 1;
  }
}
