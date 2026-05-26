# figma-tokens-to-wp

A deterministic, stdlib-only Claude Code plugin that turns a Figma variables
export into a WordPress block-theme `theme.json` + matching CSS.

## Install

```bash
claude plugin marketplace add simonstrumse/vibelabs-plugins
claude plugin install figma-tokens-to-wp@vibelabs-plugins
```

Then in any project Claude Code knows about Figma tokens, it'll reach for this
skill automatically.

## What you get

- **A skill** that activates when you talk about Figma variables, design tokens,
  `theme.json`, fluid spacing/type, or "tokens → code."
- **A pure Python converter** (`convert.py`) — no dependencies, no build step,
  no API calls. Reads zips / folders of `.tokens.json` files, writes the WP
  artefacts to disk.

## Usage

Directly from the shell (or have the agent call it for you):

```bash
python3 $(claude plugin path figma-tokens-to-wp)/skills/figma-tokens-to-wp/convert.py \
  ./design-tokens/figma-export -o ./forge-out
```

Where `./design-tokens/figma-export` is the folder Figma's "Export variables"
produces (or a single zip from it).

It emits:

```
forge-out/
├── theme.json         ← assembled WordPress block-theme settings
├── palette.json       ← settings.color.palette entries
├── colorTokens.css    ← semantic CSS variables aliasing the palette
├── spacing.json       ← settings.spacing.spacingSizes (fluid clamp)
├── typography.json    ← settings.typography.fontSizes (WP fluid format)
└── cornerRadius.json  ← settings.custom.borderRadius
```

## The "deterministic floor" of design-to-code

Modern Figma + WordPress workflows have two layers:

1. **Tokens →  WordPress settings** — deterministic, repeatable, free. This
   plugin handles this layer (the same job Dekode Forge does on the web).
2. **Components / patterns / templates** — the agentic layer. Pair this plugin
   with Claude Code reading from the Figma MCP, and the model handles the
   bigger creative job above tokens.

Keep this skill in your stack as the cheap, predictable conversion step.
Reach for the model for everything above it.

## Calibration

Reverse-engineered from **Dekode Forge** by POSTing real exports to
`theme-spacing.dekodes.no/api/process-zip` and diffing the response. For the
DPE design system that ships in Forge's documentation, **4 of the 5 outputs
are byte-identical**:

| Artefact            | Matches Forge byte-for-byte? |
|---------------------|------------------------------|
| `palette.json`      | ✅ yes                       |
| `spacing.json`      | ✅ yes                       |
| `typography.json`   | ✅ yes                       |
| `cornerRadius.json` | ✅ yes                       |
| `colorTokens.css`   | ❌ — *more correct* than Forge — see below |

### The colorTokens divergence

Forge's `colorTokens.css` for DPE silently drops the `system-on-error`,
`system-on-warning`, and `system-on-success` tokens, and emits the
wrong palette alias for the corresponding error/warning/success entries.
This plugin instead preserves all seven system tokens, aliases to the palette
when the hex matches, and falls back to raw hex when it doesn't.

## Encoded conventions

- **Viewports for fluid sizing:** `376 px → 1920 px`, rem base `16`, 4-decimal rounding.
- **Spacing slugs:** numeric `10`–`90` ascending; names use the pretty form
  (`XXX-small` → `3X-Small`).
- **Typography slugs:** `heading-{level}` for the Headline branch, plain
  `{level}` for the Text branch; ordered descending by size; source casing kept
  (`Heading XXX-large`).
- **Typography output:** WP 6.5+ fluid object `{size, fluid:{min,max}}` — not
  inline `clamp()` (spacing/radius still emit `clamp()`).
- **Corner radius slugs:** `xs / sm / md / lg / xl` ascending.
- **Semantic colour slug rule:** lowercase → drop the word `and` →
  non-alphanumerics → `-` → split into words → **dedup consecutive duplicate
  words**. So `Action/Primary/Primary Hover` → `action-primary-hover`.

## Pairs with the Figma Dev Mode MCP

The Figma remote Dev Mode MCP (`https://mcp.figma.com/mcp`) reads variables
directly from a Figma URL — no manual export step. The full pipeline is then:

```
Figma URL ──MCP──► tokens.json ──this skill──► theme.json ──Claude Code──► WordPress
```

This skill is the deterministic middle step; the MCP eliminates the manual
export at the front; Claude Code carries the result through to actual
components, patterns, and templates at the back.

## License

MIT
