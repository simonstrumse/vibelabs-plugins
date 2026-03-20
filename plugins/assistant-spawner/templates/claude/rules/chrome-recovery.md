# Chrome Recovery — Auto-Reset on Failure

When Chrome MCP tools (`mcp__claude-in-chrome__*`) fail with connection errors, timeouts, or "tab doesn't exist" errors:

1. **Run `/chrome-reset`** — kills stale native hosts, orphaned processes, and stale MCP servers, then reconnects
2. **Retry the failed operation** after reset completes
3. If it still fails after reset, **tell the user** — don't keep retrying

Common failure signals:
- "Multiple Chrome extensions connected"
- Tool call returns error or times out
- Tab ID not found / invalid tab
- No response from browser extension
- "Native host has exited" or similar connection errors

**Before handing off Chrome to another agent:** Run `/chrome-reset` to ensure a clean connection.
