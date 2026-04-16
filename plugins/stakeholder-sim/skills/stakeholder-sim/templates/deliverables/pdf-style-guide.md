# PDF deliverable style guide

The crisis-PR-agency deliverable aesthetic the `pdf-renderer` agent must produce. Use `pdf-reference.html` as the concrete working example — every convention below is implemented there, and the agent should copy that file's CSS verbatim as the starting point, then adapt content.

## Positioning

This is an **executive-grade advisory deliverable**. The reader is a CEO, Chair, EVP Comms, or board member. The document must inspire trust in thirty seconds — before anyone reads a paragraph. If it looks like a marketing blog post or a consultant's throwaway deck, leadership will not treat the findings seriously.

Reference points (recognisable visual languages):

- **McKinsey / BCG report:** restrained palette, serif body, action titles, pyramid-principle exec summary, lots of whitespace, minimal chrome.
- **Brunswick / Teneo / Edelman memo:** classified footer, "Prepared for [executive names]" on cover, pull-quote-driven, grounded in named stakeholder voices.
- **Deloitte / Oliver Wyman findings pack:** priority-ranked recommendations with timeline, explicit limitations section, appendix with raw material.

## Document structure (non-negotiable)

Every generated PDF must include, in this order:

1. **Cover** — reference number, title, subtitle, client, prepared-for list (named executives), prepared-by, date, assessment type, confidentiality line
2. **Table of contents** — one page
3. **Section 1: Executive summary** — one page, pyramid principle: answer first (what leadership needs to know), then three secondary findings, then action count metrics
4. **Section 2: Methodology** — how the assessment was run, agent pipeline diagram, what this is / is not, disclaimers
5. **Section 3: The stimulus under review** — full text reproduced, plus a classification table
6. **Section 4: Stakeholder cohort briefing** — cluster distribution table + individual persona selections with why-selected
7. **Section 5: Findings** — Consensus signals (5.1), Disagreement axes (5.2), Surprise signals (5.3), Red-line crossings (5.4), each with direct pull-quoted evidence
8. **Section 6: Recommended actions** — priority-ranked (Critical / High / Medium), each with timeline and the specific personas grounding it
9. **Section 7: Coverage limitations** — honest about omissions
10. **Appendix A: Full stakeholder reactions** — every persona's reaction in full
11. **Appendix B: Methodology notes** — agent pipeline responsibilities, persona sourcing, run economics, research grounding

## Typography

- **Body:** `Charter, 'Iowan Old Style', Georgia, serif` at 10.5pt, line-height 1.5
- **Headings (all):** `'Helvetica Neue', Arial, sans-serif`
- **Heading sizes:** h1 22pt, h2 16pt, h3 12pt, h4 10.5pt uppercase with 0.08em letter-spacing
- **Monospace (rare):** `Menlo, Consolas, monospace` 9pt for pipeline diagrams

## Color palette

| Token | Hex | Usage |
|---|---|---|
| navy | `#0f2544` | Primary accent — headings, section borders, pull-quote left-border |
| navy-soft | `#1a3358` | h3 headings, less emphatic navy |
| red | `#7a1a1a` | Classification line, critical callouts, section numbers, "Critical" recommendation badges |
| gold | `#8a6d2b` | Warning callouts, "High" priority badges, standout-line accents |
| grey-1 | `#f4f4f2` | Page backgrounds for callouts and personas |
| grey-2 | `#e6e4df` | Table borders, dividers |
| grey-4 | `#555` | Secondary text |
| grey-5 | `#2b2b2b` | Body text |

No other colors. No gradients. No drop shadows.

## Page layout

- **Size:** A4 with 22mm top/bottom, 20mm left/right margins
- **Cover:** 30mm 25mm 25mm 25mm, `page-break-after: always`, grey-1 background
- **Header (every page except cover):** top-left "Confidential — Client Leadership Only" in red 8pt uppercase 0.08em tracking; top-right short document title in 8pt grey
- **Footer (every page except cover):** bottom-left "Vibe Labs Stakeholder Simulation Practice" in 8pt grey; bottom-right "Page N of M" in 8pt grey

## Section headers

Each main section starts on a new page with:

1. Section number in small caps, red, 0.2em tracking (e.g. `SECTION 01`)
2. Section title in Helvetica Neue Light 20pt navy
3. Section lead in italic Charter 11pt grey — one-sentence summary that answers "what does this section tell me"
4. Horizontal rule, then body

## Pull quotes

```html
<div class="pullquote">
  "quote text here"
  <span class="pullquote-attr">Name · Institution</span>
</div>
```

Navy 2pt left-border, italic Charter 10pt body, attribution in Helvetica 9pt grey on a new line. Pull quotes are the primary evidence device — they let the reader see the stakeholder's actual voice.

## Callouts

Three styles:

- **Default (navy border)** — for context or framing insights
- **Critical (red border, soft red background)** — for must-act-now findings
- **Warn (gold border, soft cream background)** — for watchouts

Each callout has a small uppercase label in the border color.

## Recommendation blocks

Each recommendation in Section 6 is a bordered card with:

1. **Priority badge** — colored pill (red = Critical, gold = High, grey = Medium), uppercase small text
2. **Title** — full-sentence action title in navy
3. **Timeline** — one line below title
4. **Body** — 2-3 paragraphs explaining the recommendation
5. **Grounded in** — footer row listing the personas whose reactions motivate this rec

## Tables

- No outer borders
- Header row: 1pt navy bottom-border, uppercase 8.5pt Helvetica with 0.08em tracking, navy text
- Body rows: alternating grey-1 fill on even rows, 0.3pt grey-2 bottom-border
- Cells: 5pt 6pt padding, vertical-align top, 9.5pt Helvetica

## What NOT to include

- Stock photography or iconography — skip all illustration
- Corporate branding logos — the Vibe Labs mark in the cover footer and page footer is sufficient
- Charts or infographics in the body — if a finding needs a chart, it goes in an appendix
- Watermarks
- Any color outside the palette
- Bold text in body copy (use italic Charter for emphasis; let headings carry weight)
- All-caps in body paragraphs
- Emoji (anywhere)

## Rendering

Produce HTML with embedded `<style>` block, then render to PDF via WeasyPrint:

```bash
weasyprint <input.html> <output.pdf>
```

WeasyPrint supports `@page` rules, page counters, page-break directives, and modern CSS — everything the reference template needs. Chrome headless also works as a fallback.

## The content is the agent's job, the design is this guide's job

The `pdf-renderer` agent reads the run's artifacts (`stimulus.md`, `plan.md`, `findings/persona-*-final.md`, `report.md`, `verification.md`) and writes an HTML file that conforms to this style guide with content adapted to the specific assessment. It must not invent content — every quote, every finding, every recommendation comes from the run's artifacts. The design is fixed; the content is situation-specific.
