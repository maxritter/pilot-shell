# Artifact backend cutover

Status: written, not applied. Nothing here has run against any database, and nothing in
`docs/site/api/_lib/schema.sql` is a migration for it. The renamed client (branch `rename-artifacts`)
works with the live backend as it is, because the team API keeps the word `design` on the wire.

## What stays "design" on the wire today

One constant holds it on the client side, and the API and database hold it on the other:

| Where | What | Value now |
|---|---|---|
| `qualitylayer/src/core/team/wire.ts` | `TEAM_WIRE_KIND` | `"design"` |
| Client requests | `status.kind` and `status.stage` of an artifact publication | `"design"` |
| Client requests | the `?kind=` query of `GET /api/team/tasks` and `GET /api/team/tasks/<id>` | `design` |
| Client requests | the `gate` of an artifact's opinion ask | `"design"` |
| `docs/site/api/team/tasks.ts`, `tasks/[task].ts`, `tasks/[task]/claim.ts`, `tasks/[task]/handed.ts` | accepted `kind` and `stage` values | `"design"` |
| `docs/site/api/_lib/team-store.ts` | the `kind` type | `"design"` |
| `team_tasks.kind` (migration 10) | `check (kind = 'design')` | `'design'` |
| `team_tasks.stage` of those rows | free text | `design` |
| `team_asks.gate` of an artifact ask | free text | `design` |

Not on the list, because it is already renamed: the sealed publication manifest inside the
encrypted envelope (`kind: "artifact"`), the route `/api/team/artifacts/...` of the local server, and
every name above the team-API boundary.

Two tests pin the current word, so the cutover shows up as red tests that have to be flipped on purpose:

- `qualitylayer/tests/core/artifact-publication.test.ts`: "the team API still hears the wire word design".
- `docs/site/api/team/tasks.test.ts`: "still accepts the wire kind design and rejects artifact".

## Steps, in this order

### 1. Widen the database (additive, safe at any time)

Add this block to `docs/site/api/_lib/schema.sql` as the next numbered migration (a change is a new
block, never an edit), and apply it with `scripts/db-migrate.ts` before the API deploy:

```sql
-- migration 11
alter table team_tasks drop constraint if exists team_tasks_kind_check;
alter table team_tasks add constraint team_tasks_kind_check check (kind in ('design', 'artifact'));
```

If production is still at schema 9 (before the table rebuild of migration 10), `team_tasks` keeps
its fields in the `row` jsonb and has no `kind` column or constraint: skip this step and use the
`row->>'kind'` form of step 4.

### 2. Make the API accept both words

In `docs/site/api`, accept `design` and `artifact` for `kind` and `stage` (and the `?kind=` query),
answering with the word the row holds. Touch only these places: `team/tasks.ts` (list filter),
`team/tasks/[task].ts` (create, read and the kind-change check), `team/tasks/[task]/claim.ts` and
`handed.ts` (the "not a hand-over" refusals), `_lib/team-store.ts` (the `kind` type). Add a test that
both words work, then deploy the site. Old clients keep working; new clients can send `artifact`.

### 3. Switch the client (one line)

`qualitylayer/src/core/team/wire.ts`:

```ts
export const TEAM_WIRE_KIND = "artifact"
```

Then flip the two pinning tests above, release the client. A client that sends `artifact` needs
step 2 deployed first. Members on an older client keep sending `design` until they update, so step 4
waits until they have.

### 4. Convert the rows (after the clients have moved)

```sql
update team_tasks set kind = 'artifact', stage = 'artifact' where kind = 'design';
update team_asks set gate = 'artifact' where gate = 'design';
```

On schema 9, where the fields live in `row`:

```sql
update team_tasks
set row = jsonb_set(jsonb_set(row, '{kind}', '"artifact"'), '{stage}', '"artifact"')
where row->>'kind' = 'design';
```

The sealed titles and plans are ciphertext and need nothing: the client already writes
`kind: "artifact"` inside the envelope and reads either word.

### 5. Narrow (only when step 4 left no `design` row)

```sql
-- migration 12
alter table team_tasks drop constraint team_tasks_kind_check;
alter table team_tasks add constraint team_tasks_kind_check check (kind = 'artifact');
```

Then remove `design` from the API (`team/tasks.ts`, `tasks/[task].ts`, `claim.ts`, `handed.ts`,
`_lib/team-store.ts`) and deploy the site.

## Deploy order

1. Migration 11 (widen) on the database.
2. Site deploy with the API accepting both words.
3. Client release with `TEAM_WIRE_KIND = "artifact"`.
4. Wait for the members' clients to update (a team can check which build each member runs).
5. Row conversion (step 4).
6. Migration 12 (narrow) and the site deploy that drops `design`.

Rollback: before step 5 nothing is lost either way, because both words stay accepted. After step 5,
reverse the two `update` statements and widen the constraint again.

## Check after each step

- `GET /api/team/tasks?kind=artifact` and `?kind=design` list the same publications once step 5 is done.
- A new share from the renamed client stores `kind = 'artifact'` after step 3.
- `tests/core/artifact-publication.test.ts` and `docs/site/api/team/tasks.test.ts` pass with the flipped words.
