#!/usr/bin/env bash
# Plaintext guard for the encrypted trees.
#
# The trees are qualitylayer/ and docs/site/api/, plus the site's backend
# operation scripts and deploy check, the feedback-store worker and scripts/cutover.sh (see
# is_guarded). Every tracked path under them must be reported as encrypted by
# `git-crypt status`, except the four manifest files under qualitylayer/ that
# supply-chain scanners need in plaintext. A file that slipped into history
# unencrypted (git-crypt flags it with a NOT ENCRYPTED warning) also fails.
#
# With --range, it instead scans a commit range: every blob a commit of the
# range adds or changes under those paths must begin with git-crypt's header.
# That needs no key and no git-crypt, and it prints paths, never contents.
#
# Run locally as a pre-push check and in CI (works on a locked checkout).
#
# Usage: scripts/check_qualitylayer_encrypted.sh [--range <rev-range>] [repo-dir]

set -euo pipefail

RANGE=""
REPO_DIR="."
while [ $# -gt 0 ]; do
  case "$1" in
  --range)
    RANGE="${2:?--range needs a revision range, for example origin/main..HEAD}"
    shift 2
    ;;
  --range=*)
    RANGE="${1#--range=}"
    shift
    ;;
  *)
    REPO_DIR="$1"
    shift
    ;;
  esac
done
cd "$REPO_DIR"

ALLOWLIST=(
  "qualitylayer/package.json"
  "qualitylayer/bun.lock"
  "qualitylayer/tsconfig.json"
  "qualitylayer/biome.json"
)

is_allowed() {
  local path="$1"
  for allowed in "${ALLOWLIST[@]}"; do
    if [ "$path" = "$allowed" ]; then
      return 0
    fi
  done
  return 1
}

# The guarded paths outside the two trees: the backend operation scripts, the
# deploy check that probes the routes, their tests and the backup recipient, every file of the feedback-store worker, and
# the cut-over script. The website's own build scripts stay plaintext.
is_guarded() {
  case "$1" in
  qualitylayer/* | docs/site/api/*) return 0 ;;
  docs/site/scripts/backup.ts | docs/site/scripts/restore.ts | docs/site/scripts/db-migrate.ts) return 0 ;;
  docs/site/scripts/upload-workflow.ts | docs/site/scripts/load-check.ts) return 0 ;;
  docs/site/scripts/check-deploy.sh) return 0 ;;
  docs/site/scripts/backup-recipient.txt | docs/site/scripts/*.test.ts) return 0 ;;
  docs/site/workers/feedback-store/*) return 0 ;;
  scripts/cutover.sh) return 0 ;;
  esac
  return 1
}

# Names the guarded paths that sit outside the two trees, so a run shows them.
list_extra() {
  local path
  while IFS= read -r path; do
    case "$path" in
    qualitylayer/* | docs/site/api/*) ;;
    *) echo "  encrypted: $path" ;;
    esac
  done
}

# git-crypt starts every encrypted file with NUL, "GITCRYPT", NUL.
GITCRYPT_HEADER="004749544352595054"

LISTING=""

scan_range() {
  local failures=0 checked=0 meta blob path head
  LISTING="$(mktemp)"
  trap 'rm -f "${LISTING:?}"' EXIT

  # One "<blob> <path>" line per added or changed path in the range, once each.
  git log --format= --raw --no-renames --diff-filter=AM --root "$RANGE" |
    while IFS=$'\t' read -r meta path; do
      is_guarded "$path" || continue
      if is_allowed "$path"; then
        continue
      fi
      read -r _ _ _ blob _ <<<"$meta"
      printf '%s %s\n' "$blob" "$path"
    done | sort -u >"$LISTING"

  while IFS=' ' read -r blob path; do
    checked=$((checked + 1))
    head="$(git cat-file blob "$blob" | head -c 9 | od -An -tx1 | tr -d ' \n' || true)"
    if [ "$head" != "$GITCRYPT_HEADER" ]; then
      echo "PLAINTEXT IN RANGE: $path (blob ${blob:0:10}) is not encrypted" >&2
      failures=$((failures + 1))
    fi
  done <"$LISTING"

  if [ "$failures" -gt 0 ]; then
    echo "check_qualitylayer_encrypted: $failures plaintext blob(s) in $RANGE" >&2
    exit 1
  fi
  cut -d' ' -f2- "$LISTING" | list_extra
  echo "check_qualitylayer_encrypted: OK ($checked blob(s) in $RANGE are encrypted)"
}

if [ -n "$RANGE" ]; then
  scan_range
  exit 0
fi

if ! command -v git-crypt >/dev/null 2>&1; then
  echo "error: git-crypt is not installed" >&2
  exit 2
fi

failures=0
checked=0
extra_paths=""

# `git-crypt status` prints one line per tracked file:
#   "    encrypted: path" or "not encrypted: path", optionally followed by
#   " *** WARNING: staged/committed version is NOT ENCRYPTED! ***".
while IFS= read -r line; do
  status="${line%%: *}"
  rest="${line#*: }"
  # Strip a trailing git-crypt warning from the path column.
  path="${rest%% \*\*\**}"

  is_guarded "$path" || continue
  if is_allowed "$path"; then
    continue
  fi

  checked=$((checked + 1))

  case "$status" in
  *"not encrypted"*)
    echo "PLAINTEXT: $path is tracked unencrypted" >&2
    failures=$((failures + 1))
    ;;
  *encrypted*)
    if [[ "$line" == *"NOT ENCRYPTED"* ]]; then
      echo "PLAINTEXT IN HISTORY: $path has an unencrypted staged/committed version" >&2
      failures=$((failures + 1))
    else
      extra_paths+="$path"$'\n'
    fi
    ;;
  *)
    echo "UNRECOGNISED git-crypt status line: $line" >&2
    failures=$((failures + 1))
    ;;
  esac
done < <(git-crypt status)

if [ "$failures" -gt 0 ]; then
  echo "check_qualitylayer_encrypted: $failures plaintext path(s) among the guarded paths" >&2
  exit 1
fi

printf '%s' "$extra_paths" | list_extra
echo "check_qualitylayer_encrypted: OK ($checked encrypted path(s), ${#ALLOWLIST[@]} allowlisted)"
