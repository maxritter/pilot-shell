#!/bin/bash
# Checks a QualityLayer website deployment. Prints what it found, never a secret.
#
#   check-deploy.sh --env <production|preview> [--branch <name>]
#                                         the Vercel project's variables for that environment:
#                                         the signing key, the three Polar names, the two
#                                         store names and the three Slack names must all be
#                                         set. Preview is read for
#                                         branch <name> (default dev).
#   check-deploy.sh <base-url> [--keys <file>]
#                                         the routes a QualityLayer client uses: the install
#                                         script redirect, trial start, the team pass, the
#                                         workflow route and the share page and API
#   check-deploy.sh --help                this text
#
# <base-url> is a deployment (https://xyz.vercel.app) or a live domain
# (https://qualitylayer.dev). --keys names a file with `Team: <licence key>` and
# `Solo: <licence key>` lines; the pass route is only asked to validate them (an
# activation would take a seat). With a Team key the check also creates a share link,
# comments on it and revokes it.
#
# The pilot-shell.com redirect is conditioned on the host, so it can only be seen on the
# live pilot-shell.com; on any other host that check is reported as skipped, not passed.

set -u

ORG_ID="team_jAsHrk71vRyWK6bCTYGJyp0q"
PROJECT_ID="prj_TXccrJI83HyNvQUZxqStUFgus9NB"
NAMES="RSA_PRIVATE_KEY POLAR_ACCESS_TOKEN POLAR_ORGANIZATION_ID POLAR_TEAM_BENEFIT_ID KV_REST_API_URL KV_REST_API_TOKEN SLACK_CLIENT_ID SLACK_CLIENT_SECRET SLACK_TOKEN_KEY"

failed=0
pass() { printf 'ok       %s\n' "$1"; }
fail() { printf 'FAIL     %s\n' "$1"; failed=1; }
skip() { printf 'skipped  %s\n' "$1"; }

usage() {
  sed -n '2,/^$/p' "$0" | sed -e 's/^# \{0,1\}//' -e '/^$/d'
}

env_names() {
  # Names only: the value column is never read. $1 is the environment, $2 an optional git branch.
  (
    cd "$(mktemp -d)" || exit 1
    VERCEL_ORG_ID="$ORG_ID" VERCEL_PROJECT_ID="$PROJECT_ID" vercel env ls "$1" ${2:+"$2"} 2>/dev/null \
      | sed -e 's/\x1b\[[0-9;]*m//g' | awk '$1 ~ /^[A-Z][A-Z0-9_]+$/ { print $1 }'
  )
}

check_env() {
  environment="$1"
  branch=""
  if [ "$environment" = "preview" ]; then branch="${2:-dev}"; fi
  command -v vercel >/dev/null || { fail "the vercel CLI is not installed"; return; }
  label="$environment${branch:+ ($branch)}"
  names="$(env_names "$environment" "$branch")"
  if [ -z "$names" ]; then fail "$label: could not list the project's variables (is vercel logged in?)"; return; fi
  for name in $NAMES; do
    if printf '%s\n' "$names" | grep -qx "$name"; then pass "$label: $name is set"; else fail "$label: $name is not set"; fi
  done
}

check_url() {
  base="${1%/}"
  host="${base#*://}"
  host="${host%%/*}"
  keys=""
  if [ "${2:-}" = "--keys" ]; then keys="${3:-}"; fi

  # A deployment behind Vercel's protection answers 401 to a plain request; `vercel curl` signs in.
  case "$host" in
    *.vercel.app) http() { vercel curl "$1" --deployment "$base" -- -s "${@:2}" 2>/dev/null; } ;;
    *) http() { curl -sS "$base$1" "${@:2}"; } ;;
  esac
  code() { http "$1" -o /dev/null -w '%{http_code}' "${@:2}"; }
  json() { http "$1" -X POST -H 'content-type: application/json' "${@:2}"; }

  echo "checking $base"

  # 1. pilot-shell.com pages move; nothing is followed, so the redirect itself is seen.
  case "$host" in
    pilot-shell.com | www.pilot-shell.com)
      got="$(http /pricing -o /dev/null -w '%{http_code} %{redirect_url}')"
      if [ "$got" = "308 https://qualitylayer.dev/pricing" ]; then pass "/pricing answers 308 to qualitylayer.dev/pricing"; else fail "/pricing answered '$got', expected 308 to https://qualitylayer.dev/pricing"; fi
      ;;
    *) skip "the pilot-shell.com redirect is conditioned on the host and shows only on the live domain" ;;
  esac

  # 2. The installer is served from the repository.
  got="$(http /install.sh -o /dev/null -w '%{http_code} %{redirect_url}')"
  case "$got" in
    "307 https://raw.githubusercontent.com/maxritter/pilot-shell/"*"/install.sh") pass "/install.sh redirects to ${got#307 }" ;;
    *) fail "/install.sh answered '$got', expected 307 to raw.githubusercontent.com/maxritter/pilot-shell/<branch>/install.sh" ;;
  esac

  # 3. Trial start: a QualityLayer client gets a trial (a fresh fingerprint, so a probe never meets an ended one);
  #    a request without a product is refused.
  fingerprint="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
  trial="$(json /api/trial/start -d "{\"fingerprint\":\"$fingerprint\",\"product\":\"qualitylayer\"}")"
  if printf '%s' "$trial" | grep -q '"trial_key":"'; then pass "trial start gives a QualityLayer trial"; else fail "trial start answered '$trial'"; fi
  no_product="$(code /api/trial/start -X POST -H 'content-type: application/json' -d "{\"fingerprint\":\"$fingerprint\"}")"
  if [ "$no_product" = "400" ]; then pass "trial start refuses a request without a product (400)"; else fail "trial start answered $no_product without a product, expected 400"; fi

  # 4. The team pass and the workflow route answer an empty request with a refusal, not an error.
  no_key="$(code /api/team/pass -X POST -H 'content-type: application/json' -d '{}')"
  case "$no_key" in 400 | 401) pass "the pass route refuses a request without a key ($no_key)" ;; *) fail "the pass route answered $no_key without a key, expected 400 or 401" ;; esac
  no_body="$(code /api/workflow -X POST)"
  if [ "$no_body" = "400" ]; then pass "the workflow route refuses a request without a body (400)"; else fail "the workflow route answered $no_body without a body, expected 400"; fi

  # 5. Share links: the API answers itself on every host, only a v2 plan is accepted, and the page opens.
  unknown="$(printf 'A%.0s' $(seq 22))"
  missing="$(code "/api/share?id=$unknown")"
  if [ "$missing" = "404" ]; then pass "the share API answers itself (404 for an unknown id, no redirect)"; else fail "the share API answered $missing for an unknown id, expected 404"; fi
  v1="$(code /api/share -X POST -H 'content-type: application/json' -d '{"data":"ZGVwbG95LWNoZWNr"}')"
  if [ "$v1" = "400" ]; then pass "a Pilot Shell 11 share payload is refused (400)"; else fail "a Pilot Shell 11 share payload answered $v1, expected 400"; fi
  case "$host" in
    127.0.0.1:* | localhost:*) skip "/s/<id>: the local backend serves the API, not the site's pages" ;;
    *)
      page="$(code "/s/$unknown")"
      if [ "$page" = "200" ]; then pass "/s/<id> serves the share page (200, no redirect)"; else fail "/s/<id> answered $page, expected 200"; fi
      ;;
  esac

  # 6. The pass route, asked only to validate, and the share link a Team seat makes with it.
  if [ -z "$keys" ]; then skip "the pass route and a share link: no --keys file given"; return; fi
  team="$(sed -n 's/^Team: *//p' "$keys" | head -1)"
  solo="$(sed -n 's/^Solo: *//p' "$keys" | head -1)"
  if [ -z "$team" ] || [ -z "$solo" ]; then fail "the keys file needs a 'Team:' and a 'Solo:' line"; return; fi
  reply="$(json /api/team/pass -d "{\"key\":\"$team\"}" -w '\n%{http_code}')"
  status="${reply##*$'\n'}"
  body="${reply%$'\n'*}"
  name="$(printf '%s' "$body" | sed -n 's/.*"name":"\([^"]*\)".*/\1/p')"
  if [ "$status" = "200" ] && printf '%s' "$body" | grep -q '"pass":"' && [ -n "$name" ]; then
    pass "the Team key gets a pass for the team '$name'"
    token="$(printf '%s' "$body" | sed -n 's/.*"pass":"\([^"]*\)".*/\1/p')"
    # The pass carries no seats itself; it opens the team's seats on the members route.
    seats="$(http /api/team/members -H "x-team-pass: $token" | sed -n 's/.*"seats":{"used":\([0-9]*\),"total":\([0-9]*\)}.*/\1 of \2/p')"
    if [ -n "$seats" ]; then pass "the pass opens the team's seats: $seats used"; else fail "the pass did not open the team's seats"; fi
    check_share "$token"
  else
    fail "the Team key answered $status"
  fi
  solo_status="$(code /api/team/pass -X POST -H 'content-type: application/json' -d "{\"key\":\"$solo\"}")"
  if [ "$solo_status" = "402" ]; then pass "the Solo key is answered 402"; else fail "the Solo key answered $solo_status, expected 402"; fi
}

# A Team seat shares a plan, a guest comments and the comment is polled, then the team revokes the link.
check_share() {
  created="$(json /api/share -H "x-team-pass: $1" -d '{"v":2,"task":"deploy check","docs":{"README.md":"# deploy check"}}')"
  id="$(printf '%s' "$created" | sed -n 's/.*"id":"\([A-Za-z0-9]*\)".*/\1/p')"
  if [ -z "$id" ]; then fail "creating a share answered '$created'"; return; fi
  if http "/api/share?id=$id" | grep -q '"task":"deploy check"'; then pass "a share reads back its plan"; else fail "a share did not read back"; fi
  now="$(($(date +%s) * 1000))"
  posted="$(code /api/share/feedback -X POST -H 'content-type: application/json' \
    -d "{\"id\":\"$id\",\"payload\":{\"author\":\"check-deploy\",\"createdAt\":$now,\"annotations\":[{\"id\":\"a1\",\"blockId\":\"README.md\",\"originalText\":\"x\",\"text\":\"deploy check comment\",\"createdAt\":$now}]}}")"
  case "$posted" in 2??) pass "a comment posted to the share was accepted ($posted)" ;; *) fail "posting a comment answered $posted" ;; esac
  polled="$(json /api/share/feedback/batch -d "{\"items\":[{\"id\":\"$id\",\"cursor\":0}]}")"
  if printf '%s' "$polled" | grep -q 'deploy check comment'; then pass "the batch feedback route returns the comment"; else fail "the batch feedback route did not return the comment: $polled"; fi
  revoked="$(code "/api/share/$id" -X DELETE -H "x-team-pass: $1")"
  if [ "$revoked" = "204" ] && [ "$(code "/api/share?id=$id")" = "404" ]; then pass "the team revokes the link and it is gone"; else fail "revoking the share answered $revoked"; fi
}

case "${1:-}" in
  --help | -h) usage ;;
  --env)
    case "${2:-}" in
      production | preview) check_env "$2" "${4:-}" ;;
      *) echo "usage: check-deploy.sh --env <production|preview> [--branch <name>]" >&2; exit 2 ;;
    esac
    ;;
  http://* | https://*) check_url "$@" ;;
  *) echo "usage: check-deploy.sh --env <production|preview> [--branch <name>] | <base-url> [--keys <file>] | --help" >&2; exit 2 ;;
esac

exit "$failed"
