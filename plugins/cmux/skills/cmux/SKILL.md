---
name: cmux
description: >
  Control the cmux terminal app from a Claude session over its CLI. Spawn or reuse
  a workspace, open a terminal tab rooted in a folder, launch Claude Code / Codex / a
  shell in it, send keystrokes, and read terminal output back. Trigger: cmux, "open a
  workspace", "new tab", "launch a claude session in cmux", "spawn a session", "drive
  a terminal", "read the terminal", ccx.
---

# cmux orchestration

cmux ships a CLI that controls the **already-running** app over a Unix socket — no
AppleScript, no remoting, no GUI scripting. From inside one Claude session you can spawn
new sessions, drive them, and read their output.

## 0. Find the cmux binary (do this first)

```bash
CM="$(command -v cmux || echo /Applications/cmux.app/Contents/Resources/bin/cmux)"
"$CM" version    # sanity check
```

On macOS the app bundles the CLI at `/Applications/cmux.app/Contents/Resources/bin/cmux`.
If `cmux` is on PATH (Linux installs, or a symlink), prefer that. Every command below uses `$CM`.

Handles use refs: `window:N`, `workspace:N`, `pane:N`, `surface:N` (a surface = a tab).
UUIDs and indexes also work. Add `--id-format uuids|both` to print UUIDs.

## 1. Fast path — the `ccx` helper (bundled)

`ccx <folder> [name]` launches a ready Claude Code session for a folder, **smartly**:
reuse the folder's workspace as a new tab if it exists, else create the workspace.

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/ccx" ~/code/my-project
"${CLAUDE_PLUGIN_ROOT}/scripts/ccx" .                 # current dir
CCX_CMD=codex "${CLAUDE_PLUGIN_ROOT}/scripts/ccx" ~/code/foo   # launch Codex instead
```

It auto-detects the cmux binary and runs `claude --dangerously-skip-permissions` by default
(override with `CCX_CMD`). For humans who want a short command, symlink it onto PATH:
`ln -sf "${CLAUDE_PLUGIN_ROOT}/scripts/ccx" ~/.local/bin/ccx`.

If you'd rather not use the script (e.g. to customize), every step it does is below — and as
the agent you can parse `list-workspaces --json` yourself, so nothing here needs `jq`.

## 1b. Which agent to launch — default Claude Code, others supported

`ccx` / `new-workspace --command` launch **`claude --dangerously-skip-permissions` by default.**
To launch a different agent set `CCX_CMD` (for `ccx`) or pass `--command` (for `new-workspace`).
cmux also ships native *team* wrappers that turn an agent's subagents into real cmux splits via
a private tmux shim — and because that shim needs to run inside a cmux terminal, it composes
perfectly with `ccx`/`new-workspace` (e.g. `CCX_CMD="cmux claude-teams" ccx .`).

**Tested working (macOS, 2026-05-24):**

| Agent / mode | Raw command | `ccx` form |
|---|---|---|
| Claude Code *(default)* | `claude --dangerously-skip-permissions` | `ccx <dir>` |
| Claude Code + agent teams | `cmux claude-teams [claude args]` | `CCX_CMD="cmux claude-teams --dangerously-skip-permissions" ccx <dir>` |
| Codex | `codex` | `CCX_CMD=codex ccx <dir>` |
| Codex + subagent panes | `cmux codex-teams [codex args]` | `CCX_CMD="cmux codex-teams" ccx <dir>` |
| OpenCode | `opencode` | `CCX_CMD=opencode ccx <dir>` |

**Supported by cmux, needs the underlying tool/setup (not verified on the test machine):**

| Agent / mode | Command | Note |
|---|---|---|
| OpenCode + oh-my-openagent | `cmux omo` | needs `oh-my-openagent`; plain `opencode` works without it |
| Oh My Codex | `cmux omx` | `npm i -g oh-my-codex` |
| Oh My Claude Code | `cmux omc` | `npm i -g oh-my-claude-sisyphus` |
| Gemini CLI | `gemini` | launches but needs its own auth |
| Grok | `grok` | cmux's bundled shim needs a real `grok` binary on PATH |

The team wrappers (`claude-teams`, `codex-teams`, `omo`, `omx`, `omc`) forward all extra args
to the underlying CLI, so `cmux claude-teams --continue --model sonnet` etc. work.

### Agent hooks — notifications, Feed approvals, session restore

`cmux hooks setup` installs cmux integration for every supported agent found on PATH; or
`cmux hooks <agent> install` for one. Supported: `codex, grok, opencode, pi, amp, cursor,
gemini, antigravity, rovodev, hermes-agent, copilot, codebuddy, factory, qoder`. Claude Code
hooks are injected automatically by the cmux claude wrapper, so Claude needs no setup. This
adds desktop notifications, an approval Feed, and session restore for that agent.

## 2. Spawn a new workspace (native cwd + startup command)

```bash
"$CM" new-workspace --name "My Session" --cwd "/abs/path" \
  --command "claude --dangerously-skip-permissions" --focus true
# -> OK workspace:N
```

This is the cleanest spawn: one workspace, one terminal tab, rooted at the folder, running
the command immediately. `--focus false` to spawn in the background.

## 3. Add a tab to an existing workspace

`new-surface` creates a tab but has **no** `--cwd`/`--command`, so cd + launch is *sent in*:

```bash
WS=workspace:10
SU="$("$CM" new-surface --type terminal --workspace "$WS" --focus true | awk '{print $2}')"  # ref = field 2
sleep 2   # IMPORTANT: let the pty come up, or send fails with "Surface is not a terminal"
"$CM" send     --workspace "$WS" --surface "$SU" "cd /abs/path && claude --dangerously-skip-permissions"
"$CM" send-key --workspace "$WS" --surface "$SU" enter
```

## 4. Smart spawn (reuse workspace by folder, else create)

Each workspace exposes its terminal's `current_directory` in JSON — that's the match key:

```bash
DIR="/abs/path"
WS="$("$CM" list-workspaces --json | jq -r --arg d "$DIR" \
       '.workspaces[]|select(.current_directory==$d)|.ref' | head -n1)"
if [ -n "$WS" ]; then
  # …open a tab in $WS (section 3)…
else
  # …new-workspace (section 2)…
fi
```

As the agent you can also just read `list-workspaces --json` and reason about the match
directly, without `jq`. (Match is exact on the *current* dir, so a workspace cd'd away from
its project root won't match — it'll spawn a fresh one.)

## 5. Drive & observe a session

```bash
"$CM" send     --workspace "$WS" --surface "$SU" "npm test"   # type text
"$CM" send-key --workspace "$WS" --surface "$SU" enter         # press a key (enter, c-c, up, …)
"$CM" read-screen  --workspace "$WS" --surface "$SU" --lines 40   # read visible output
"$CM" capture-pane --workspace "$WS" --surface "$SU" --scrollback # tmux-style capture incl. scrollback
```

Read-then-act loops let you spawn a session, wait, read its screen, and respond — fully
headless. `--scrollback` and `--lines <n>` control how much you get.

## 6. Inspect

```bash
"$CM" tree --all                       # window → workspace → pane → surface tree
"$CM" list-workspaces [--json]         # workspaces (+ current_directory, ports, etc. in JSON)
"$CM" list-panes      --workspace "$WS"
"$CM" list-pane-surfaces --workspace "$WS"   # tabs within the focused pane
"$CM" current-workspace
"$CM" identify --json                  # who/where am I (when run inside cmux)
```

## 7. Organize, split, signal

```bash
"$CM" rename-workspace  --workspace "$WS" "New Name"
"$CM" workspace-action  --action set-color --workspace "$WS" --color "#22cc88"
"$CM" select-workspace  --workspace "$WS"            # bring it to front
"$CM" new-split right   --workspace "$WS" --surface "$SU"   # split: left|right|up|down
"$CM" close-surface     --workspace "$WS" --surface "$SU"
"$CM" close-workspace   --workspace "$WS"
"$CM" notify     --title "Done" --body "build passed" --workspace "$WS"
"$CM" set-status build "passing" --workspace "$WS" --color "#22cc88"
"$CM" set-progress 0.42 --label "halfway" --workspace "$WS"
```

## 8. Browser surfaces (cmux has a built-in browser)

```bash
"$CM" new-pane --type browser --workspace "$WS" --url "https://example.com"
"$CM" browser navigate "https://example.com"
"$CM" browser snapshot --interactive        # accessibility snapshot for automation
"$CM" browser click "<selector>"; "$CM" browser screenshot --out /tmp/shot.png
```

## Gotchas (learned by testing)

- **pty warmup:** after `new-surface`, wait ~2 s before `send`/`send-key`, or you get
  `Surface is not a terminal`. (`new-workspace --command` has no such issue — it's native.)
- **surface ref vs id:** plain `new-surface` prints `OK surface:N pane:N workspace:N` → ref is
  **field 2**. With `--json` the key is `surface_ref`; with `--json --id-format uuids` it's
  `surface_id`. Pick one and stay consistent.
- **ambient defaults:** a shell *inside* cmux has `CMUX_WORKSPACE_ID`/`CMUX_SURFACE_ID` auto-set
  and used as defaults. Always pass `--workspace`/`--surface` explicitly when targeting *another*
  session, or commands resolve against the caller's own tab.
- **`list-pane-surfaces` is per-pane** (the focused pane), not the whole workspace; use `tree`
  or `list-panes` for the full picture.
- **`new-surface` can't set cwd/command** — only `new-workspace` can. For tabs, `send` the
  `cd … && <cmd>`.

## Reference

```bash
"$CM" --help            # full command list
"$CM" docs api          # API overview + links
# CLI contract: https://raw.githubusercontent.com/manaflow-ai/cmux/main/docs/cli-contract.md
```
