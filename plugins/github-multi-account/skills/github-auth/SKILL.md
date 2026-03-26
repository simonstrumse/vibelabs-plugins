---
name: github-auth
description: >
  GitHub multi-account guard — auto-check and switch gh auth before git push.
  Prevents 'Repository not found' when repos belong to different GitHub accounts.
  Trigger: git push, gh repo, gh pr, github, "push to github", "push til github".
---

# GitHub Multi-Account Auth Guard

Machines with multiple GitHub accounts (via `gh auth`) will silently fail on
`git push` if the wrong account is active. This skill catches that before it happens.

## Before any git push or gh command

```bash
# 1. Check which account is active
gh auth status 2>&1 | grep "Active account: true" -B2

# 2. Check which account owns this repo's remote
REMOTE_OWNER=$(git remote get-url origin 2>/dev/null | sed 's|.*github.com/||;s|/.*||')
ACTIVE_ACCOUNT=$(gh auth status 2>&1 | grep "Active account: true" -B1 | grep "account" | awk '{print $NF}')

echo "Remote owner: $REMOTE_OWNER"
echo "Active account: $ACTIVE_ACCOUNT"

# 3. If they don't match — switch
if [ "$REMOTE_OWNER" != "$ACTIVE_ACCOUNT" ]; then
  echo "MISMATCH: switching to $REMOTE_OWNER"
  gh auth switch --user "$REMOTE_OWNER"
fi
```

## Why this matters

- `gh auth` supports multiple accounts but only one is "active" at a time
- `git push` over HTTPS uses the active account's token
- Pushing to a repo owned by the non-active account gives: "Repository not found"
- This is silent — no permission prompt, just a confusing 404

## Common scenario

You have `personal-account` and `org-account`. You work on personal projects,
then switch to an org repo. Git push fails because the wrong token is used.

## Error you'll see if wrong account

```
remote: Repository not found.
fatal: repository 'https://github.com/org-account/repo.git/' not found
```

Fix: `gh auth switch --user org-account`
