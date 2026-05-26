#!/usr/bin/env python3
"""
Figma design tokens → WordPress theme.json (Dekode Forge–equivalent).

Deterministic. Reverse-engineered from Dekode Forge (theme-spacing.dekodes.no/api/process-zip)
by inspecting its actual output for the DPE_Variables_Exported export, then encoding the rules:

  - palette ramps          → theme.json `settings.color.palette` entries
  - semantic color tokens  → CSS variables aliasing the palette presets
  - dimension values       → theme.json `spacingSizes` (fluid clamp 375→1920)
                             `fontSizes` (WP fluid format), and `custom.borderRadius`
  - slug normalisation     → lowercase, "and" dropped, consecutive duplicate words deduped
                             (Action/Primary/Primary → action-primary)

Usage:
  python convert.py <input> [-o OUTDIR]
  <input> may be a folder of .tokens.json files, a folder of zips, a single zip,
  or a folder containing both (e.g. an unwrapped Figma export).
"""
from __future__ import annotations
import argparse, json, os, re, sys, zipfile, io
from pathlib import Path

# ---- viewport breakpoints (matched against Forge's actual output) -----------
VW_MIN = 376     # mobile (matches Forge's actual calc — derived empirically)
VW_MAX = 1920    # desktop
REM_BASE = 16

def rem(px):  return round(px / REM_BASE, 4)

def fmt_rem(px):
    v = rem(px)
    s = f"{v:g}rem"
    return s

def clamp_expr(min_px, max_px):
    """Forge's fluid clamp using 375→1920 viewports, rem-based."""
    if min_px == max_px:
        return fmt_rem(min_px)
    slope_px_per_vp = (max_px - min_px) / (VW_MAX - VW_MIN)
    intercept_px    = min_px - slope_px_per_vp * VW_MIN
    intercept_rem   = round(intercept_px / REM_BASE, 4)
    slope_vw        = round(slope_px_per_vp * 100, 4)   # because 1vw = viewport/100
    lo, hi = (min_px, max_px) if min_px < max_px else (max_px, min_px)
    return f"clamp({fmt_rem(lo)}, {intercept_rem:g}rem + {slope_vw:g}vw, {fmt_rem(hi)})"

# ---- slug normalisation ----------------------------------------------------
def slugify_path(path_segments: list[str]) -> str:
    """Forge's rule: join path, lowercase, drop the word 'and', replace
    non-alphanumeric (incl '/' and spaces) with '-', then split into words and
    dedup *consecutive* identical words. Crucially, hyphens *inside* a segment
    are preserved (so 'X-large' → 'x-large', not 'xlarge'). E.g.:
      Action/Primary/Primary       → action-primary
      Action/Primary/Primary Hover → action-primary-hover
      Text and icon/Default        → text-icon-default
      Headline/X-large             → heading-x-large (when 'heading-' prefix added)
    """
    s = "/".join(path_segments).lower()
    s = re.sub(r"\band\b", "", s)                      # drop the word 'and'
    s = re.sub(r"[^a-z0-9-]+", "-", s)                 # non-alnum (keep '-') → '-'
    s = re.sub(r"-+", "-", s).strip("-")               # collapse + trim
    parts = s.split("-")
    out: list[str] = []
    for w in parts:
        if not w: continue
        if out and out[-1] == w: continue              # dedup consecutive duplicate words
        out.append(w)
    return "-".join(out)

def display_name(path_segments: list[str]) -> str:
    return " ".join(re.sub(r"[/]", " ", " ".join(path_segments)).split())

# ---- token-tree walk -------------------------------------------------------
def walk_tokens(obj, path=()):
    """Yield (path, token_dict) for every leaf token. A leaf has $value/$type
    (W3C design-tokens format Figma exports natively)."""
    if not isinstance(obj, dict): return
    for k, v in obj.items():
        if k.startswith("$"): continue
        if isinstance(v, dict):
            if "$value" in v or "value" in v:
                yield path + (k,), v
            else:
                yield from walk_tokens(v, path + (k,))

def leaf_value(tok):
    return tok.get("$value", tok.get("value"))

def leaf_type(tok):
    return tok.get("$type", tok.get("type"))

# ---- collection classification ---------------------------------------------
def classify(tokens_files: list[dict]) -> str:
    """Decide what this collection is, from one or more mode files:
    'palette'        — flat colour ramps (Name/Number, hex), single mode
    'color-tokens'   — semantic colours, named modes (Light Mode, Dark Mode …)
    'design-values'  — numeric tokens with Mobile/Desktop modes
    """
    has_colors = has_numbers = False
    ramp_like = semantic = 0
    for f in tokens_files:
        for path, tok in walk_tokens(f):
            v = leaf_value(tok)
            if isinstance(v, dict) and "hex" in v:
                has_colors = True
                # Ramp-like: last segment is a number ("100", "300", "500"...)
                if path and re.fullmatch(r"\d+", path[-1]): ramp_like += 1
                else: semantic += 1
            elif isinstance(v, (int, float)) or (isinstance(v, str) and re.fullmatch(r"-?\d+(\.\d+)?", str(v))):
                has_numbers = True
    if has_numbers and not has_colors: return "design-values"
    if has_colors and ramp_like >= semantic:      return "palette"
    if has_colors:                                 return "color-tokens"
    return "unknown"

# ---- converters per type ---------------------------------------------------
def convert_palette(tokens_files: list[dict]) -> list[dict]:
    out = []
    for f in tokens_files:
        for path, tok in walk_tokens(f):
            v = leaf_value(tok)
            if isinstance(v, dict) and "hex" in v:
                hexv = v["hex"].upper()
                out.append({
                    "name":  display_name(list(path)),
                    "slug":  slugify_path(list(path)),
                    "color": hexv,
                })
    return out

def convert_color_tokens(tokens_files: list[dict], palette: list[dict]) -> str:
    """Each file is a mode (e.g. Light Mode). Output CSS aliasing palette presets
    via --wp--preset--color--{palette-slug}, falling back to raw hex if no match."""
    hex2slug = {p["color"].upper(): p["slug"] for p in palette}
    blocks = []
    for f in tokens_files:
        mode_name = (f.get("$extensions", {}).get("com.figma.modeName")
                     or f.get("$mode") or "default")
        mode_slug = slugify_path([mode_name])
        lines = [f"/* {mode_name} */", f".color-scheme-{mode_slug} {{"]
        for path, tok in walk_tokens(f):
            v = leaf_value(tok)
            if not (isinstance(v, dict) and "hex" in v): continue
            hexv = v["hex"].upper()
            sl   = slugify_path(list(path))
            preset = hex2slug.get(hexv)
            if preset:
                lines.append(f"  --color--{sl}: var(--wp--preset--color--{preset});")
            else:
                lines.append(f"  --color--{sl}: {hexv};")
        lines.append("}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"

# ---- dimension grouping ----------------------------------------------------
SIZE_NAME_MAP = {
    "xxx-small": "3X-Small", "xx-small": "2X-Small", "x-small": "X-Small",
    "small": "Small", "medium": "Medium", "large": "Large",
    "x-large": "X-Large", "xx-large": "2X-Large", "xxx-large": "3X-Large",
    "display": "Display",
}
def pretty_size_name(seg: str) -> str:
    key = seg.strip().lower()
    return SIZE_NAME_MAP.get(key, seg.strip())

def convert_design_values(tokens_files: list[dict]) -> dict:
    """Pair Mobile + Desktop modes (the two files) for each path. Mobile = min,
    Desktop = max. Group by category: Spacing / Typography Size / Corner Radius."""
    # Map: mode_name -> { path_tuple -> px_value }
    modes: dict[str, dict[tuple, float]] = {}
    for f in tokens_files:
        mode = (f.get("$extensions", {}).get("com.figma.modeName") or "default")
        m = modes.setdefault(mode, {})
        for path, tok in walk_tokens(f):
            v = leaf_value(tok)
            if isinstance(v, (int, float)): m[path] = float(v)
            elif isinstance(v, str) and re.fullmatch(r"-?\d+(\.\d+)?", v): m[path] = float(v)

    # Determine min (Mobile) and max (Desktop) modes
    mob_key = next((k for k in modes if "mobile" in k.lower()), None)
    dsk_key = next((k for k in modes if "desktop" in k.lower()), None)
    if mob_key is None and dsk_key is None:
        # single mode → use it for both
        only = next(iter(modes))
        mob_key = dsk_key = only
    elif mob_key is None: mob_key = dsk_key
    elif dsk_key is None: dsk_key = mob_key
    mob, dsk = modes[mob_key], modes[dsk_key]
    all_paths = sorted(set(mob) | set(dsk), key=lambda p: dsk.get(p, mob.get(p, 0)))

    spacing = []
    typo_headline, typo_text = [], []
    radii = {}

    # Build spacing list (slugs 10..N0 by ascending size, names "3X-Small"..."3X-Large")
    spacing_paths = sorted(
        [p for p in all_paths if p and p[0] == "Spacing"],
        key=lambda p: dsk.get(p, mob.get(p, 0))
    )
    for i, p in enumerate(spacing_paths, start=1):
        leaf = p[-1]
        mn, mx = mob.get(p, dsk.get(p)), dsk.get(p, mob.get(p))
        spacing.append({
            "name": pretty_size_name(leaf),
            "slug": str(i * 10),
            "size": clamp_expr(mn, mx),
        })

    # Typography: split Headline / Text branches, sorted DESCENDING by size
    # (Forge convention: biggest first within each branch, headings before text).
    # Names keep source casing (e.g. "Heading XXX-large"); only spacing gets the
    # pretty-name conversion ("3X-Large" etc.).
    typo_paths = [p for p in all_paths if p and p[0] in ("Typography Size", "Typography")]
    seen = set()
    typo_paths_unique = [p for p in typo_paths if not (p in seen or seen.add(p))]
    typo_paths_sorted = sorted(typo_paths_unique,
                               key=lambda p: -dsk.get(p, mob.get(p, 0)))
    for p in typo_paths_sorted:
        if len(p) < 3: continue
        branch = p[1]
        leaf   = p[-1]
        mn, mx = mob.get(p, dsk.get(p)), dsk.get(p, mob.get(p))
        is_heading = branch.lower().startswith("head")
        slug = ("heading-" + slugify_path([leaf])) if is_heading else slugify_path([leaf])
        name = (("Heading " + leaf) if is_heading else leaf).strip()
        entry = {"name": name, "slug": slug, "size": fmt_rem(mx)}
        entry["fluid"] = {"min": fmt_rem(mn), "max": fmt_rem(mx)} if mn != mx else False
        (typo_headline if is_heading else typo_text).append(entry)
    typography = typo_headline + typo_text

    # Corner Radius: T-shirt slugs xs..xl by ascending size
    rad_paths = sorted(
        [p for p in all_paths if p and p[0] == "Corner Radius"],
        key=lambda p: dsk.get(p, mob.get(p, 0))
    )
    tshirts = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl"]
    radii_map = {}
    for i, p in enumerate(rad_paths):
        if i >= len(tshirts): break
        mn, mx = mob.get(p, dsk.get(p)), dsk.get(p, mob.get(p))
        radii_map[tshirts[i]] = clamp_expr(mn, mx)
    # Forge uses descending size ordering (xl largest); reorder to match
    if rad_paths:
        # reverse so xl = largest
        ordered = {}
        keys = list(radii_map.keys())
        vals = list(radii_map.values())
        for k, v in zip(reversed(keys), reversed(vals)): ordered[k] = v
        radii_map = ordered
    if radii_map:
        radii = {"custom": {"borderRadius": radii_map}}

    return {"spacing": spacing, "typography": typography, "cornerRadius": radii}

# ---- assembled theme.json --------------------------------------------------
def assemble_theme_json(palette, color_css, spacing, typography, corner_radius, font_families=None):
    settings = {
        "appearanceTools": True,
        "layout": {"contentSize": "760px", "wideSize": "1200px"},
        "color":      {"palette": palette} if palette else {},
        "spacing":    {"spacingSizes": spacing, "units": ["px","rem","em","vw","%"], "blockGap": True} if spacing else {},
        "typography": {"fontSizes": typography} if typography else {},
        "custom":     corner_radius.get("custom", {}) if corner_radius else {},
    }
    if font_families:
        settings.setdefault("typography", {})["fontFamilies"] = font_families
    return {"$schema": "https://schemas.wp.org/trunk/theme.json", "version": 3, "settings": settings}

# ---- input loading ---------------------------------------------------------
def load_input_collections(input_path: Path) -> list[tuple[str, list[dict]]]:
    """Returns [(collection_name, [tokens_dicts])] — one entry per zip/folder."""
    collections = []
    def load_zip(zpath: Path, label: str):
        files = []
        with zipfile.ZipFile(zpath, "r") as z:
            for n in z.namelist():
                if not n.endswith(".tokens.json") and not n.endswith(".json"): continue
                files.append(json.loads(z.read(n)))
        collections.append((label or zpath.stem, files))

    if input_path.is_file():
        if input_path.suffix.lower() == ".zip":
            load_zip(input_path, input_path.stem)
        elif input_path.suffix.lower() == ".json":
            collections.append((input_path.stem, [json.loads(input_path.read_text())]))
    else:
        # Directory: each .zip is a collection; OR each subfolder of .tokens.json files is one
        zips = sorted(input_path.glob("*.zip"))
        if zips:
            for z in zips: load_zip(z, z.stem)
        else:
            for sub in sorted([p for p in input_path.iterdir() if p.is_dir()]):
                jsons = sorted(sub.glob("*.json"))
                if jsons:
                    collections.append((sub.name, [json.loads(j.read_text()) for j in jsons]))
            top_jsons = sorted(input_path.glob("*.tokens.json")) + sorted(input_path.glob("*.json"))
            if top_jsons and not collections:
                collections.append((input_path.name, [json.loads(j.read_text()) for j in top_jsons]))
    return collections

# ---- main ------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Figma tokens → WordPress theme.json (Forge-equivalent)")
    ap.add_argument("input", help="zip / folder of zips / folder of .tokens.json")
    ap.add_argument("-o", "--out", default="forge-out", help="output folder (default: ./forge-out)")
    a = ap.parse_args(argv)

    in_path = Path(a.input).expanduser().resolve()
    out_dir = Path(a.out).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cols = load_input_collections(in_path)
    if not cols:
        print(f"No token files found in {in_path}", file=sys.stderr); sys.exit(2)

    palette, color_css, spacing, typography, corner_radius = [], "", [], [], {}
    for name, files in cols:
        kind = classify(files)
        print(f"  {name}: {kind} ({len(files)} mode file(s))")
        if kind == "palette":      palette = convert_palette(files)
        elif kind == "color-tokens": pass  # need palette first
        elif kind == "design-values":
            r = convert_design_values(files)
            spacing       = r["spacing"]
            typography    = r["typography"]
            corner_radius = r["cornerRadius"]

    # second pass for color-tokens (now palette known)
    for name, files in cols:
        if classify(files) == "color-tokens":
            color_css = convert_color_tokens(files, palette)

    # write artefacts
    if palette:        (out_dir / "palette.json").write_text(json.dumps(palette, indent=2, ensure_ascii=False))
    if color_css:      (out_dir / "colorTokens.css").write_text(color_css)
    if spacing:        (out_dir / "spacing.json").write_text(json.dumps(spacing, indent=2, ensure_ascii=False))
    if typography:     (out_dir / "typography.json").write_text(json.dumps(typography, indent=2, ensure_ascii=False))
    if corner_radius:  (out_dir / "cornerRadius.json").write_text(json.dumps(corner_radius, indent=2, ensure_ascii=False))

    theme = assemble_theme_json(palette, color_css, spacing, typography, corner_radius)
    (out_dir / "theme.json").write_text(json.dumps(theme, indent=2, ensure_ascii=False))

    print(f"\nWrote → {out_dir}")
    for p in sorted(out_dir.iterdir()): print("  ", p.name, f"({p.stat().st_size}B)")

if __name__ == "__main__": main()
