#!/bin/bash
# The workflow texts of one release, on qualitylayer.dev's store. Prints what it did,
# never a secret.
#
#   upload-workflow.sh upload <version> <bundle.json> <sha256>
#       SET workflow:<version> to the bundle through the Upstash REST API (environment:
#       KV_REST_API_URL and KV_REST_API_TOKEN of the store behind the site being
#       released), then read it back and compare its digest. Refuses a bundle whose
#       digest is not the one the build computed, and one above 900 KB.
#   upload-workflow.sh probe <version> <base-url>
#       Start a trial for a fresh random fingerprint (product qualitylayer) and ask
#       <base-url>/api/workflow for <version> with it; it must answer 200 with texts.
#   upload-workflow.sh --help
#
# Needs curl and jq.

set -euo pipefail

MAX_BYTES=$((900 * 1024))
VERSION_PATTERN='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]{1,40})?$'

usage() {
  sed -n '2,/^$/p' "$0" | sed -e 's/^# \{0,1\}//' -e '/^$/d'
}

die() {
  echo "error: $1" >&2
  exit 1
}

sha256_of() {
  if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1; else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

need_tools() {
  command -v curl >/dev/null || die "curl is not installed"
  command -v jq >/dev/null || die "jq is not installed"
}

# One Redis command through the REST API: $1 is the JSON array of the command. The reply goes to stdout.
kv_command() {
  curl -fsS --max-time 30 -X POST \
    -H "Authorization: Bearer $KV_REST_API_TOKEN" -H 'content-type: application/json' \
    --data-binary @"$1" "$KV_REST_API_URL"
}

upload() {
  version="${1:-}"
  bundle="${2:-}"
  expected="${3:-}"
  [ -n "$version" ] && [ -n "$bundle" ] && [ -n "$expected" ] || die "usage: upload <version> <bundle.json> <sha256>"
  [[ "$version" =~ $VERSION_PATTERN ]] || die "'$version' is not a version"
  [ -f "$bundle" ] || die "no bundle at $bundle"
  [ -n "${KV_REST_API_URL:-}" ] && [ -n "${KV_REST_API_TOKEN:-}" ] || die "KV_REST_API_URL and KV_REST_API_TOKEN must be set"

  size="$(wc -c <"$bundle" | tr -d ' ')"
  [ "$size" -le "$MAX_BYTES" ] || die "the bundle is $size bytes, above the $MAX_BYTES cap"
  actual="$(sha256_of "$bundle")"
  [ "$actual" = "$expected" ] || die "the bundle's digest is $actual, the build computed $expected"

  work="$(mktemp -d)"
  trap 'rm -rf "${work:?}"' EXIT
  jq -Rs --arg key "workflow:$version" '["SET", $key, .]' "$bundle" >"$work/set.json"
  answer="$(kv_command "$work/set.json" | jq -r '.result // empty')"
  [ "$answer" = "OK" ] || die "the store answered '$answer' to SET workflow:$version"

  jq -n --arg key "workflow:$version" '["GET", $key]' >"$work/get.json"
  kv_command "$work/get.json" | jq -j '.result // empty' >"$work/readback"
  stored="$(sha256_of "$work/readback")"
  [ "$stored" = "$expected" ] || die "workflow:$version reads back as $stored, expected $expected"
  echo "workflow:$version stored ($size bytes), read back, digest $expected"
}

probe() {
  version="${1:-}"
  base="${2:-}"
  [ -n "$version" ] && [ -n "$base" ] || die "usage: probe <version> <base-url>"
  [[ "$version" =~ $VERSION_PATTERN ]] || die "'$version' is not a version"
  base="${base%/}"

  work="$(mktemp -d)"
  trap 'rm -rf "${work:?}"' EXIT
  fingerprint="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"

  curl -fsS --max-time 30 -X POST -H 'content-type: application/json' \
    -d "$(jq -nc --arg fp "$fingerprint" '{fingerprint: $fp, product: "qualitylayer"}')" \
    "$base/api/trial/start" >"$work/trial.json" || die "trial start at $base failed"
  trial="$(jq -r '.trial_key // empty' "$work/trial.json")"
  [ -n "$trial" ] || die "trial start at $base gave no trial"

  status="$(curl -sS --max-time 30 -o "$work/workflow.json" -w '%{http_code}' -X POST \
    -H 'content-type: application/json' \
    -d "$(jq -nc --arg v "$version" --arg fp "$fingerprint" --arg t "$trial" '{version: $v, fingerprint: $fp, trial: $t}')" \
    "$base/api/workflow")"
  [ "$status" = "200" ] || die "$base/api/workflow answered $status for $version, expected 200"
  count="$(jq '.texts | length' "$work/workflow.json")"
  [ "$count" -gt 0 ] && [ -n "$(jq -r '.grant // empty' "$work/workflow.json")" ] || die "$base/api/workflow answered 200 without a grant and texts"
  echo "$base/api/workflow serves $count texts for $version to a fresh trial"
}

case "${1:-}" in
  upload) need_tools; shift; upload "$@" ;;
  probe) need_tools; shift; probe "$@" ;;
  --help | -h) usage ;;
  *) echo "usage: upload-workflow.sh upload <version> <bundle.json> <sha256> | probe <version> <base-url> | --help" >&2; exit 2 ;;
esac
