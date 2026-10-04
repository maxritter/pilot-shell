#!/usr/bin/env bash
# The release notes of one version: its section of CHANGELOG.md, from the line under the version's
# `## <version>` heading down to the next `## ` heading, without either heading. The section is
# grouped as `### New`, `### Fixed` and `### Good to know`, and goes unchanged into the GitHub
# release, the updater's manifest, the App and the terminal.
#
#   scripts/changelog-section.sh <version> [CHANGELOG.md]
#
# A heading is `## 12.0.0-beta.14`, `## v12.0.0-beta.14` or `## [12.0.0-beta.14] - 2026-10-05`: the
# version is the first word, whole, so beta.1 never finds beta.14. A version with no section, or a
# section with nothing in it, fails with what to write, so a release never goes out without notes;
# two headings for one version fail too (exit 4), so nobody has to guess which one is meant.
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ] || [ -z "$1" ]; then
  echo "Usage: scripts/changelog-section.sh <version> [CHANGELOG.md]" >&2
  exit 2
fi

version="${1#v}"
file="${2:-CHANGELOG.md}"

if [ ! -f "$file" ]; then
  echo "error: ${file} not found: the release notes come from it." >&2
  exit 1
fi

# awk ends with 3 when no heading names the version, and 4 when two do.
found=0
notes="$(
  awk -v want="$version" '
    /^## / {
      inside = 0
      split(substr($0, 4), words, /[ \t]+/)
      token = words[1]
      sub(/^\[/, "", token)
      sub(/\].*$/, "", token)
      sub(/^v/, "", token)
      if (token == want) {
        hits++
        inside = (hits == 1)
      }
      next
    }
    inside { print }
    END { exit hits == 0 ? 3 : (hits > 1 ? 4 : 0) }
  ' "$file"
)" || found=$?

# Blank lines around the section are not part of it.
notes="$(printf '%s\n' "$notes" | sed -e '/./,$!d')"
notes="${notes%"${notes##*[![:space:]]}"}"

if [ "$found" -eq 4 ]; then
  {
    echo "error: ${file} has two sections for ${version}: it is not clear which one is the release's notes."
    echo "Keep one \"## ${version}\" heading, with the release's \"### New\", \"### Fixed\" and \"### Good to know\"."
  } >&2
  exit 4
fi

if [ "$found" -eq 3 ]; then
  {
    echo "error: ${file} has no section for ${version}."
    echo "Add \"## ${version}\" with the release's \"### New\", \"### Fixed\" and \"### Good to know\" before it is released."
  } >&2
  exit 1
fi

if [ -z "$notes" ]; then
  {
    echo "error: the section for ${version} in ${file} is empty: there is nothing to tell people about this release."
    echo "Write what is \"### New\", \"### Fixed\" and \"### Good to know\" under \"## ${version}\"."
  } >&2
  exit 1
fi

printf '%s\n' "$notes"
