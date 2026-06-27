# Information Architecture — Project Knowledge Base

The engine creates and maintains a knowledge base **inside the user's project directory**, not inside the plugin. This document specifies what that knowledge base looks like: the tiers, the rules, and the exact skeleton templates to use when initializing each file.

---

## The tiers

| Tier | Purpose | Update rule | When to read |
|------|---------|-------------|--------------|
| **Canonical** | Fresh truth — build on this | Updated in place as truth changes | Always |
| **Reference** | How-to docs + raw inventories | Updated as connectors and processes evolve | When you need a specific how-to or raw data |
| **Archive** | Methodology, superseded findings, assumption tests, seeds | Superseded log is append-only; others updated as needed | When tracing decisions or verifying nothing was re-litigated |
| **Map** | README: the entry point to everything | Updated whenever tier contents change | First thing any new session reads |
| **Changelog** | Append-only history, current-state on top | Append on every substantive change | Before modifying any area not recently touched |

---

## The one rule that governs all of them

Shared static facts — price, product IDs, business details, channel commission rates, supplier contacts — live in **one place** and are **pointed to**, never duplicated into per-topic docs. When a fact changes, it changes in one file. Per-topic docs reference the canonical location.

If the project already has a shared-facts file (e.g. `../_SHARED/`, `docs/master-referanse.md`, or a similar conventions file), point to it from `STRATEGY.md` and do not copy its contents into the marketing knowledge base.

---

## Canonical tier

### `marketing/STRATEGY.md` — the master entry point

The engine updates this file in place. It is the answer to "where are we and what are we doing?" at any point in time. Every per-topic doc is linked from here.

```markdown
# [Business Name] — Growth Strategy

> **Status as of [YYYY-MM-DD]:** [One sentence. E.g. "Measurement verified end-to-end; Phase 3 competitive map in progress."]

## Quick links

| Topic | Doc | Status |
|-------|-----|--------|
| Demographics & ICP | [marketing/canon/demographics.md](canon/demographics.md) | [draft / verified / stale] |
| Competitor ad map | [marketing/canon/competitor-map.md](canon/competitor-map.md) | [draft / verified / stale] |
| Keyword & channel gap | [marketing/canon/keyword-gap.md](canon/keyword-gap.md) | [draft / verified / stale] |
| CPA framework & timing | [marketing/canon/cpa-timing.md](canon/cpa-timing.md) | [draft / verified / stale] |
| Positioning | [marketing/canon/positioning.md](canon/positioning.md) | [draft / verified / stale] |
| Campaign build | [marketing/canon/campaign-build.md](canon/campaign-build.md) | [draft / verified / stale] |

## Shared static facts

> [Pointer to wherever the business's canonical facts live — e.g. `../../_SHARED/business.md` or inline if no such file exists.]
> Do not duplicate these here. Link only.

## Measurement status

- Tracking live & verified: [yes / no / partial]
- Verified end-to-end test: [date + event ID, or "not yet"]
- Coverage gaps: [list any channels not yet tracked]

## Open operator action list

Things only the operator can do (engine cannot proceed without these):

- [ ] [Example: add payment method to ad account before first campaign goes live]
- [ ] [Example: complete Meta Business Verification]

## Decision loop — last pass

| Question | Verdict | Date | Source |
|----------|---------|------|--------|
| [E.g. "Do we rank organically on our main commercial terms?"] | [held / weakened / reversed] | [date] | [source] |

---

_Per-topic docs linked above are the source of truth for each area. This file is the index, not the repository._
```

---

### `marketing/canon/demographics.md`

```markdown
# Customer Demographics & ICP

> Last updated: [YYYY-MM-DD] | Status: [draft / verified]

## Primary segments

| Segment | Share of volume | Share of revenue | Source | Confidence |
|---------|----------------|-----------------|--------|------------|
| [e.g. Leisure couples, international] | ~% | ~% | [CRM pull / email sample / operator estimate] | [low / medium / high] |

## Jobs to be done (top motivations)

1. [Motivation ranked #1 — with source]
2. [Motivation ranked #2]
3. ...

## Recurring objections (copy fuel)

These are the questions answered in nearly every customer exchange. Each is a potential headline or FAQ.

- [Objection 1]
- [Objection 2]
- ...

## Watch-outs — proxy vs. truth traps

> If any demographic proxy measure (e.g. phone country code, booking-agent nationality) does not equal
> the actual guest attribute (e.g. true guest nationality), document it here. Say what each number is
> actually a proxy for.

- [Proxy measure] → actually measures [X], not [Y]; true [Y] estimated as [Z] because [reason]

## What the data cannot yet tell us (tests needed)

- [E.g. "LTV by segment — not enough repeat-purchase observations"]
```

---

### `marketing/canon/competitor-map.md`

```markdown
# Competitor Ad Map

> Last updated: [YYYY-MM-DD] | Status: [draft / verified]
> Sources: [ad libraries queried, dates, any browser automation used]

## Summary table

| Competitor | Platforms active | Est. creative volume | Main angle | Open ground |
|------------|-----------------|---------------------|------------|-------------|
| [Name] | [Meta / Search / both] | [low / medium / high] | [one phrase] | [yes / no / partial] |

## Findings

### [Competitor name]

- Platforms: [list]
- Volume: [rough count of active creatives]
- Primary angle: [e.g. "price + convenience", "expert guides", "family-safe"]
- Notable tactics: [proof elements, formats, offers]
- What they cannot credibly claim: [structural gap you could own]

### Empty categories (zero competing ads)

- [Search term / category] — zero competitors found on [date]; [interpretation]

## Strategic implications

- Where competition is thin → likely cheap CPCs; candidate for first campaign
- Where competition is dense → differentiate or avoid
```

---

### `marketing/canon/keyword-gap.md`

```markdown
# Keyword & Channel Gap

> Last updated: [YYYY-MM-DD] | Status: [draft / verified]
> Data source: Search Console pull [date range]

## Organic wins — don't pay here (or verify first)

> Terms where we rank #1–4 organically. Paid ads here risk cannibalizing free clicks on
> navigational/branded queries. Note: for high-intent commercial/local queries, the organic-#1
> assumption may not hold — verify before writing off.

| Term | Avg position | Monthly impressions | Paid needed? | Evidence |
|------|-------------|-------------------|--------------|---------|
| [term] | [pos] | [imp] | [no / verify] | [source] |

## Organic gaps — paid adds incremental value here

| Term | Avg position | Monthly volume (est.) | Priority | Evidence |
|------|-------------|----------------------|----------|---------|
| [term] | [pos] | [vol] | [high / med / low] | [source] |

## Channel gaps (non-search)

| Channel | Current presence | Gap | Priority |
|---------|-----------------|-----|----------|
| [e.g. Meta retargeting] | [none / partial / live] | [what's missing] | [high / med / low] |

## Decision rule

> Paid spend is directed at the gap list above — terms we don't already own organically.
> Update this table whenever a new Search Console pull runs.
```

---

### `marketing/canon/cpa-timing.md`

```markdown
# CPA Framework & Timing

> Last updated: [YYYY-MM-DD] | Status: [draft / verified]

## Unit economics

| Variable | Value | Source | Date verified |
|----------|-------|--------|---------------|
| Average transaction value (excl. tax) | [amount + currency] | [source] | [date] |
| Variable cost per unit | [amount] | [source] | [date] |
| Contribution margin | [amount] | [derived] | [date] |
| OTA/marketplace commission | [%] | [contract / public rate] | [date] |

> **Static business facts (price, tax rate, product IDs):** see [pointer to shared facts file].
> Do not duplicate them here.

## The three CPA numbers (not one)

| Tier | Definition | Current value | Notes |
|------|-----------|---------------|-------|
| Break-even CPA | Contribution margin — the hard solvency ceiling; never exceed on a first sale | [amount] | |
| Benchmark CPA | OTA/marketplace commission (where to push — beat the channel) | [amount] | |
| Target CPA | Contribution margin × acquisition share — tiered by capacity utilization | See table below | |

### Capacity-tiered target CPA

| Capacity state | Target CPA | Rationale |
|---------------|-----------|-----------|
| Empty / perishable inventory | [generous — up to X%] | Incremental revenue from otherwise zero |
| Normal utilization | [standard — Y%] | Standard acquisition economics |
| Near-full / hot slots | [tight or zero] | No incremental benefit from paid acquisition |

## Timing — demand patterns from data

> Source: transaction DB analysis [date range]. Use last *complete* period; ignore mid-fill current period for lead-time conclusions.

| Metric | Finding | Implication |
|--------|---------|-------------|
| Typical lead time (days ahead of event) | [X days median] | Campaign should run [Y days] before event date |
| Lead-time split by channel (direct vs. OTA) | [e.g. "OTAs carry the long-planning tail"] | Don't extrapolate OTA lead time to direct campaigns |
| Peak demand periods | [months / seasons] | Budget pacing |
| Capacity utilization by period | [high / low / variable] | When to run aggressive CPA vs. throttle |

## Decision rule for live campaigns

> Scale: CPA < target → increase budget.
> Hold: CPA at target ± 20% → maintain.
> Cut: CPA > break-even → pause, diagnose.
> All measured on **incremental** conversions (branded/retargeting credited minimally).
```

---

### `marketing/canon/positioning.md`

```markdown
# Positioning — Challenger Strategy

> Last updated: [YYYY-MM-DD] | Status: [draft / verified]

## The ownable position

[One sentence. What can we credibly own that the main incumbent structurally cannot?]

## Evidence base

| Claim | Status | Source |
|-------|--------|--------|
| [E.g. "Small operators win on personalization vs. mass-market players"] | [held / weakened / reversed] | [published study / own data] |

## What to steal from the incumbent (tactics, not position)

- [Proof element type — e.g. review volume, before/after guarantees]
- [Risk-reducer type — e.g. free cancellation framing]
- [Format — e.g. short video testimonials]

## What to differentiate against (never copy their position)

- [Their position claim] → our counter: [our honest differentiation]

## Known / hypothesis separation

| Statement | Type | Test needed |
|-----------|------|------------|
| [E.g. "Our guests care more about X than price"] | hypothesis | [how to validate] |
| [E.g. "Competitor does not offer Y"] | known (ad library confirmed) | none |
```

---

### `marketing/canon/campaign-build.md`

```markdown
# Campaign Build

> Last updated: [YYYY-MM-DD] | Status: [paused / live / draft]
> **Everything built here starts paused. Nothing spends until operator gives explicit go-ahead.**

## Operator action list (blocking)

Before any campaign can go live, the operator must:

- [ ] [E.g. Add payment method to Google Ads account]
- [ ] [E.g. Complete Meta Business Verification]
- [ ] [E.g. Verify conversion tracking end-to-end with a real test event]

## Campaign 1 — [Name / objective]

**Platform:** [Google Search / Meta / etc.]
**Objective:** [Conversions / Traffic / etc.]
**Budget:** [amount/day] — sized for signal (minimum ~50 conversions/month to optimize), not for statistical A/B significance
**Flight dates:** [start – end, or "continuous"]
**Status:** PAUSED

### Ad groups / ad sets

| Group | Keyword set / audience | Match type | Negatives | Priority |
|-------|----------------------|-----------|-----------|----------|
| [name] | [list] | [broad/phrase/exact] | [list] | [high/med/low] |

### Copy

> Written per segment from positioning + objection list. Not templated.

**Ad 1**
- Headline 1: [text — max chars per platform]
- Headline 2: [text]
- Description: [text]
- URL path: [/path]

**Ad 2**
...

### Decision rules

| Signal | Action |
|--------|--------|
| CPA < target → | Increase daily budget by 20%, check weekly |
| CPA at target ± 20% → | Hold |
| CPA > break-even → | Pause, diagnose landing page + audience |

## Landing page punch-list

- [ ] Page speed < 3s on mobile (measure with PageSpeed Insights)
- [ ] Primary CTA above the fold on mobile
- [ ] Conversion event fires on form submit / purchase (verify in tag debug)
- [ ] Social proof visible (review count, trust signal)
- [ ] Objections addressed: [list from demographics.md]
```

---

## Reference tier

### `marketing/reference/` — how-to docs and raw inventories

The engine creates reference docs here as needed. They are not templated in advance — their content depends on which connectors and processes were built. Common examples:

- `reference/how-to-ad-library-search.md` — how to query the ad libraries for this project
- `reference/raw-competitor-creatives/` — downloaded creative inventory
- `reference/connector-setup.md` — how each data connector was wired up
- `reference/search-console-export-instructions.md` — how to pull fresh Search Console data

**Rule:** when a process requires non-obvious steps, write a reference doc so any future session can reproduce it without re-deriving the method.

---

## Archive tier

### `marketing/archive/METHODOLOGY.md` — how we know what we know

```markdown
# Methodology — How This Knowledge Was Built

> This document explains the approach, the decision loop, and the evidence standards.
> It makes the work reproducible and defends findings against "where did that come from?"

## The approach

[2–3 sentences: agentic, data-first, adversarial. Reference the plugin's playbook for full detail.]

## The decision loop

Each material claim went through this cycle:

1. Form a hypothesis (operator's or data-driven)
2. Invite a challenge from the operator
3. Separate fact (known/measured) from hypothesis (must be tested)
4. Verify adversarially — against own data or published research
5. Rate: **held / weakened / reversed**
6. Correct openly — reversals go to the superseded log; strategy updates in place
7. Repeat on the next angle

## Source-quality tiers (applied throughout)

| Tier | Examples | Weight |
|------|---------|--------|
| 1 — Peer-reviewed research | Academic studies, platform-published methodology papers | Highest |
| 2 — Own hard data | CRM/analytics/ad-account data for this business | High (but watch sampling bias) |
| 3 — Industry benchmark | Published industry survey data, category benchmarks | Medium |
| 4 — Vendor/agency number | Platform case studies, ad-platform reps | Low — discount (they sell the spend they measure) |
| 5 — Single case study | One-off blog posts, anecdotes | Very low |
| 6 — Folklore | "Everyone knows..." | Treat as hypothesis, verify |

## How the knowledge base was built — chronology

| Phase | What was done | Date | Key finding |
|-------|--------------|------|-------------|
| Phase 0 | Measurement setup | [date] | [e.g. "Tracking verified end-to-end; conversion event OSE-XXXXX confirmed received"] |
| Phase 1 | Connected inputs | [date] | [e.g. "Search Console, Meta Ads Library, CRM connected"] |
| Phase 2 | Demographics & ICP | [date] | [e.g. "Proxy-vs-truth trap found in phone country codes"] |
| ... | ... | ... | ... |
```

---

### `marketing/archive/SUPERSEDED.md` — append-only reversals log

```markdown
# Superseded Findings

Append-only. Every disproven or materially outdated finding lives here. Never delete rows.
The strategy docs reflect current truth; this log shows how truth changed.

| Date | Old claim | Status now | Why / source |
|------|-----------|------------|--------------|
| [YYYY-MM-DD] | [E.g. "Lead time is long early in the season, compresses in peak month"] | Reversed | [E.g. "Transaction DB shows lead time is short all season; long-planning tail carried entirely by OTAs, not direct. See cpa-timing.md."] |
| [YYYY-MM-DD] | [E.g. "Never bid on terms where we rank #1 organically"] | Weakened/reframed | [E.g. "This holds for navigational/branded queries but not commercial/local — platform study shows ~50% of ad clicks incremental even at organic #1 for high-intent terms. See keyword-gap.md."] |
```

**Rule:** when a finding is reversed in a strategy doc, the old version goes here in the same commit. No reversal is silent.

---

### `marketing/archive/ASSUMPTIONS.md` — adversarial validation log

```markdown
# Assumption Validation

Run at Phase 9 (before building campaigns), and again whenever a material assumption is challenged.

## Validated set — [date]

### Held (survived the challenge)

| Assumption | Evidence | Source | Rating |
|-----------|---------|--------|--------|
| [Claim] | [Evidence used to test] | [Source tier + citation] | held |

### Weakened or reframed

| Assumption | Original form | Reframed as | Source |
|-----------|--------------|-------------|--------|
| [Claim] | [What we thought] | [What the evidence says instead] | [source] |

### Reversed

| Assumption | Old claim | True now | Source | Superseded log entry |
|-----------|-----------|---------|--------|---------------------|
| [Claim] | [Old] | [New] | [source] | [link to SUPERSEDED.md row] |

## Assumptions still needing tests (cannot know without data)

| Assumption | Why untestable now | Planned test |
|-----------|-------------------|-------------|
| [E.g. "What is our true conversion rate from landing page?"] | [Insufficient traffic volume] | [A/B test with minimum N visits] |
```

---

### `marketing/archive/seed/` — starting snapshot

Store the operator's original strategy document, any pre-engagement briefs, and the engine's first rough synthesis here. These files are kept for historical value only.

Add this header to any file placed here:

```markdown
> **SEED — historical only. Do not build on this directly.**
> Captured on [YYYY-MM-DD] before the research phases ran.
> Current truth is in `marketing/STRATEGY.md` and the canon/ docs.
```

---

## Map — `marketing/README.md`

The README is the entry point. It is the tier table itself. Any new session reads this first.

```markdown
# Marketing Knowledge Base

> **Entry point:** read this first. All knowledge lives in subdirectories linked below.
> Last updated: [YYYY-MM-DD]

## Status

[One sentence — e.g. "Phases 0–6 complete; campaign build underway in canon/campaign-build.md."]

## Tier map

| Tier | What's here | Read when |
|------|------------|-----------|
| **Canonical** | Fresh truth — strategy + per-topic docs | Always |
| **Reference** | How-to docs + raw inventories | Need a specific process or raw data |
| **Archive** | Methodology, superseded findings, assumption tests, seeds | Tracing decisions; before re-litigating a question |

## Canonical files

| File | Contents | Status |
|------|----------|--------|
| [STRATEGY.md](STRATEGY.md) | Master entry + per-topic links + open action list | [current / stale] |
| [canon/demographics.md](canon/demographics.md) | ICP, segments, motivations, objections | [current / stale] |
| [canon/competitor-map.md](canon/competitor-map.md) | Who runs ads, on what platforms, with what angle | [current / stale] |
| [canon/keyword-gap.md](canon/keyword-gap.md) | Where we rank organically vs. where paid helps | [current / stale] |
| [canon/cpa-timing.md](canon/cpa-timing.md) | CPA framework, unit economics, demand patterns | [current / stale] |
| [canon/positioning.md](canon/positioning.md) | Ownable position + challenger strategy | [current / stale] |
| [canon/campaign-build.md](canon/campaign-build.md) | Campaigns, copy, decision rules — **PAUSED** | [current / stale] |

## Shared static facts

> [Point to the one place where business-level facts live.]
> Example: `../../_SHARED/business.md`, or inline below if no such file exists.
> These facts are never duplicated into per-topic docs — only linked.

## Archive

| File | Contents |
|------|----------|
| [archive/METHODOLOGY.md](archive/METHODOLOGY.md) | How we know what we know; decision loop; source tiers; chronology |
| [archive/SUPERSEDED.md](archive/SUPERSEDED.md) | Append-only log of disproven findings |
| [archive/ASSUMPTIONS.md](archive/ASSUMPTIONS.md) | Adversarial validation of the full assumption set |
| [archive/seed/](archive/seed/) | Original starting strategy — historical only, do not build on |

## Reference

| File | Contents |
|------|----------|
| [reference/](reference/) | How-to docs and raw inventories — see subdirectory listing |

---

_Per-topic canonical docs are updated in place as truth changes.
The superseded log is append-only — reversals are never deleted.
The changelog (CHANGELOG.md in this directory) records what was done and why._
```

---

## Changelog — `marketing/CHANGELOG.md`

Append-only. Current state at the top. Read before modifying any area not recently touched.

```markdown
# Marketing Changelog

<!-- CURRENT STATE — update in place when the headline changes -->
**Current state:** [One sentence. E.g. "Phase 3 competitive map complete; Phase 4 (disintermediation) in progress."]

---

## [YYYY-MM-DD] — [short summary]

**Changes:**
- [What was done, which files changed, what decision was made and why]
- [E.g. "canon/cpa-timing.md: lead-time finding reversed — OTAs carry the long-planning tail, direct is short all season. Old claim moved to archive/SUPERSEDED.md."]

**Insights:**
- [Any non-obvious finding worth preserving in the log]

**Pending:**
- [What's still open from this session]

---

## [YYYY-MM-DD] — [short summary]

...
```

---

## How the engine uses this spec

When the engine initializes a new project's knowledge base (Phase 1 output):

1. It creates the `marketing/` directory structure.
2. It writes `marketing/README.md` with the tier map, populating the status field with "initializing."
3. It creates stub files for each canonical doc — frontmatter filled in, body skeleton present, content marked `[TBD — populated in PhaseN]`.
4. It creates `marketing/CHANGELOG.md` with the initialization entry.
5. It creates `marketing/archive/METHODOLOGY.md` with the approach description and an empty chronology table.
6. It creates `marketing/archive/SUPERSEDED.md` with headers and zero rows.
7. It does **not** create `archive/ASSUMPTIONS.md` or `archive/seed/` until Phase 9 and the seed-snapshot step respectively — no skeleton files that will sit empty for a long time.
8. It points `STRATEGY.md`'s "shared static facts" section to wherever the business's canonical facts already live, rather than copying those facts in.

Per-topic canon docs are populated incrementally — each phase produces the relevant file. No phase is marked complete until its output doc is written to the canonical tier and the changelog is updated.
