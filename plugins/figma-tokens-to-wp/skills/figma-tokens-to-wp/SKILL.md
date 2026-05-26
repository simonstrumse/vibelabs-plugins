---
name: figma-tokens-to-wp
description: Convert a Figma variables export (W3C design tokens) into a WordPress block-theme theme.json + matching semantic CSS. Deterministic. Use when the user mentions Figma variables, design tokens, theme.json, fluid clamp, design-to-code, WordPress block theme, or wants to "convert tokens" / "produce theme.json from Figma".
---

# Figma design tokens → WordPress `theme.json`

A deterministic, stdlib-only converter that turns a Figma variables export into
the five artefacts a modern WordPress block theme wants:

1. **`palette.json`**      — `settings.color.palette` entries (primitive ramps)
2. **`colorTokens.css`**   — semantic CSS variables aliasing the palette presets
3. **`spacing.json`**      — `settings.spacing.spacingSizes`, fluid `clamp()`
4. **`typography.json`**   — `settings.typography.fontSizes` in WP's fluid format
5. **`cornerRadius.json`** — `settings.custom.borderRadius`
6. **`theme.json`**        — assembled from all of the above

Reverse-engineered from **Dekode Forge** (`theme-spacing.dekodes.no`) and
calibrated against its real API output. **4 of the 5 artefacts are byte-identical
to Forge** for the reference design system; the 5th (semantic colour CSS) is
more correct (we preserve `on-error / on-warning / on-success` tokens that
Forge drops).

## When this skill activates

- The user has a Figma variables export and wants a WordPress `theme.json`.
- The user mentions Forge, design tokens, fluid spacing, fluid typography,
  `--wp--preset--*`, or "tokens to code".
- After reading variables from a Figma URL via the Figma MCP, the next step is
  WordPress code.

## How to invoke

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/figma-tokens-to-wp/convert.py <input> -o <outdir>
```

`<input>` can be:
- a zip from Figma's "Export variables" feature,
- a folder containing per-collection zips (the wrapper structure Figma produces
  for multi-collection libraries),
- or a folder of `*.tokens.json` files already extracted.

The script auto-classifies each collection as **palette / color-tokens /
design-values** and runs the matching converter.

## Pairs with the Figma MCP

The Figma Dev Mode MCP can read variables straight from a Figma URL (no manual
export). Together:

```
Figma URL ──(MCP get_variable_defs)──► tokens ──(this skill)──► theme.json
```

When invoked alongside the Figma MCP, prefer reading the source live and writing
a `tokens.json` to disk, then call this skill on it.

## Conventions encoded (Forge-equivalent)

- **Viewports for fluid sizing:** `376 px → 1920 px`. Rem base `16`. Numbers
  rounded to 4 decimals.
- **Spacing slugs:** numeric `10` → `90`, ascending by size; names use the
  pretty conversion (`XXX-small` → `3X-Small`).
- **Typography slugs:** `heading-{level}` for the Headline branch, plain
  `{level}` for the Text branch. Ordered descending by size. Names keep source
  casing (e.g. `Heading XXX-large`) — different convention from spacing.
- **Typography output uses the WP 6.5+ fluid format** (`{size, fluid:{min,max}}`),
  not inline `clamp()`. Spacing/radius do use inline `clamp()`.
- **Corner radius slugs:** T-shirt `xs / sm / md / lg / xl` ascending.
- **Semantic colour slug rule:** lowercase → drop the word `and` → non-alphanumerics
  → `-` → split into words → **dedup consecutive duplicate words**. So
  `Action/Primary/Primary Hover` → `action-primary-hover`.
- **Semantic → palette aliasing:** match by hex; fall back to raw hex when no
  palette entry matches.

## Honest caveats

- Tested against the DPE export. Other Figma libraries may exercise edge cases
  (mode names other than Mobile/Desktop, multi-mode colour schemes, etc.). The
  classifier falls back to "unknown" rather than guessing.
- **This is the deterministic floor.** It does **not** generate WordPress block
  templates, patterns, or any of the layers above tokens — that's the agentic
  layer above. Pair this skill with Claude Code for the rest.
