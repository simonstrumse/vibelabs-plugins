# cmux plugin

Control the [cmux](https://cmux.com) terminal app from a Claude Code session over its
CLI/Unix-socket API. Spawn or reuse workspaces, open terminal tabs rooted in a folder,
launch Claude Code / Codex / a shell in them, send keystrokes, and read terminal output
back — fully headless, no AppleScript or remoting.

## Install

```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
claude plugin install cmux@vibelabs-plugins
```

Works out of the box on any machine with **cmux** and **Claude Code** installed. No config,
no API keys. `jq`/`python3` are used for smart workspace-matching if present, but the plugin
works without them (the agent parses cmux's JSON itself).

## What you get

- **A skill** the agent loads automatically when you talk about cmux, opening workspaces/tabs,
  spawning or driving sessions, reading a terminal, or freeing RAM from idle sessions.
- **`ccx` helper** — `ccx <folder>` launches a ready Claude Code session for a folder, reusing
  the folder's workspace as a new tab if it exists, else creating the workspace.
- **`cmux-sessions` memory manager** — audit and suspend idle agent sessions to reclaim RAM.

## Free RAM from idle sessions

Idle Claude sessions sit at ~0% CPU but each holds ~130–600 MB. `cmux-sessions` **audits** them and
gracefully suspends the ones **you choose** (exit the agent, leaving the resume command ready) —
lossless, since conversations are saved on exit.

```bash
cmux-sessions                 # AUDIT: per-workspace agent, RAM, CPU, idle/busy
cmux-sessions scan            # accurate-ish loop/busy/idle (focuses each ws, restores)
cmux-sessions suggest         # list idle candidates to review (suspends nothing)
cmux-sessions suspend ws:N    # suspend the one(s) YOU pick; resume = open its tab + press Enter
```

**Suspension is manual by design** — there is no blanket auto-suspend. Loop detection isn't 100%
reliable (a pure `/loop` is invisible while it sleeps between ticks), so nothing is ever killed
unattended: you review, you pick. `suspend` re-checks the target as a backstop (focuses it, skips
if busy/looping unless `--force`, confirms the process exits, leaves `claude --resume`/`--continue`
ready, renames the tab `💤 …`, restores your focus).

**Keep-list:** put any `/loop`/watcher session (looks idle, isn't) in `~/.config/cmux/keep-alive`
(one workspace name or ref per line) — `suggest` marks it `keep` and never proposes it. It's the
deterministic guard for loops the screen-based detection can't see.

## Quick start

Ask Claude things like:

- "Open a Claude session in cmux for `~/code/my-project`."
- "Spawn a background workspace running the dev server in `./web`."
- "Add a tab to the Foo workspace and run the tests, then read the output."

Or use the helper directly (optionally symlink it onto PATH):

```bash
ln -sf "$(claude plugin path cmux 2>/dev/null || echo .)/scripts/ccx" ~/.local/bin/ccx
ccx ~/code/my-project          # smart: new workspace, or a tab if one exists for the folder
CCX_CMD=codex ccx ~/code/foo   # launch Codex instead of Claude
```

## Which agent it launches

Defaults to **Claude Code** (`claude --dangerously-skip-permissions`). Override with `CCX_CMD`
(or `--command` on `new-workspace`). Methods tested working on macOS:

| Agent / mode | `ccx` form |
|---|---|
| Claude Code *(default)* | `ccx <dir>` |
| Claude Code + agent teams | `CCX_CMD="cmux claude-teams --dangerously-skip-permissions" ccx <dir>` |
| Codex | `CCX_CMD=codex ccx <dir>` |
| Codex + subagent panes | `CCX_CMD="cmux codex-teams" ccx <dir>` |
| OpenCode | `CCX_CMD=opencode ccx <dir>` |

Also supported by cmux (needs the underlying tool installed): `cmux omo` (oh-my-openagent),
`cmux omx` (`npm i -g oh-my-codex`), `cmux omc` (`npm i -g oh-my-claude-sisyphus`), plus
`cmux hooks setup` to wire notifications / approval Feed / session restore into codex, gemini,
opencode, cursor, copilot and more. The cmux *team* wrappers turn each agent's subagents into
native cmux splits.

## How it works

cmux exposes a CLI at `/Applications/cmux.app/Contents/Resources/bin/cmux` (macOS; on PATH on
Linux) that drives the running app over a Unix socket. The skill documents the full surface:
`new-workspace`, `new-surface`, `send` / `send-key`, `read-screen` / `capture-pane`,
`list-workspaces --json`, `tree`, splits, `notify` / `set-status` / `set-progress`, and the
built-in browser commands. See `skills/cmux/SKILL.md`.

## License

MIT
