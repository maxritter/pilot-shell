# Spec Branch & Worktree Setup

> Shared runbook for the `--new-branch` and `--worktree=yes` paths of `spec-plan`
> (Step 2) and `spec-bugfix-plan` (Step 1). Both skills build into separate
> SKILL.md files, so neither can see the other's steps — this file is the one
> place the sequence lives.
>
> Read it only when the parsed flag is `--new-branch` or `--worktree=yes`.
> The default (`--worktree=no`, and the whole flow when Branch Isolation is off)
> needs nothing from here: work continues on the current branch.

Callers supply `<plan_slug>` (the plan filename's slug) and the branch prefix:
`feat/` for features, `fix/` for bugfixes.

## `--new-branch`

⛔ **One Bash call.** Shell state (`$STASHED`, `$?`) does not survive across Bash
invocations, so splitting stash/detect/checkout/restore risks stranding the
user's work in a stash nobody pops.

```bash
STASH_MSG="pilot-spec-$(date +%s)"
git stash push -m "$STASH_MSG" --include-untracked 2>/dev/null
# `git stash push` exits 0 even with nothing to stash — detect a real one by message:
STASHED=no; git stash list | grep -q "$STASH_MSG" && STASHED=yes

# Detect the default branch. `git fetch` is a network call; fall back locally if offline.
git fetch origin 2>/dev/null
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
if [ -z "$DEFAULT_BRANCH" ]; then
  for b in main master; do git rev-parse --verify "origin/$b" >/dev/null 2>&1 && { DEFAULT_BRANCH="$b"; break; }; done
fi
DEFAULT_BRANCH=${DEFAULT_BRANCH:-main}

BRANCH_NAME="<prefix>/<plan_slug>"
git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1 && BRANCH_NAME="<prefix>/<plan_slug>-$(date +%m%d-%H%M)"

if git checkout -b "$BRANCH_NAME" "origin/$DEFAULT_BRANCH"; then
  # New branch = latest origin base + the user's own uncommitted work on top.
  if [ "$STASHED" = yes ]; then
    git stash pop 2>/dev/null \
      && echo "on $BRANCH_NAME — restored your working changes" \
      || echo "on $BRANCH_NAME — stash '$STASH_MSG' did NOT auto-apply (conflict with origin/$DEFAULT_BRANCH); recover with: git stash pop"
  else
    echo "on $BRANCH_NAME"
  fi
else
  # checkout failed (e.g. no origin remote) — restore onto the current branch so no work is lost
  [ "$STASHED" = yes ] && git stash pop 2>/dev/null
  echo "checkout failed — restored stash, staying on current branch"
fi
```

A pop conflict preserves the stash for manual recovery; a checkout failure restores it onto the current branch. Either way no work is lost.

After a successful branch creation, continue with `Worktree: No` semantics — the work happens directly on the new branch.

## `--worktree=yes`

```bash
~/.pilot/bin/pilot worktree detect --json <plan_slug>
# If not found:
~/.pilot/bin/pilot worktree create --json <plan_slug>
# → {"path": "...", "branch": "spec/<slug>", "base_branch": "main"}
```

All file writes — including the plan file — use the returned `path` as their base directory. If creation fails (git too old), continue without a worktree and record `Worktree: No` in the header.
