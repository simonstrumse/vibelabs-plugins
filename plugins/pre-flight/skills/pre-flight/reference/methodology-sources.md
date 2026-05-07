# Methodology sources

Every mode, phase, artifact, and schema decision in this skill is grounded in a named real-world workflow or published methodology. This file is the evidence trail. It is cited by the scoping-designer when disambiguating modes, and by anyone asking "did you make this up?"

Organized by mode, phase, and cross-cutting concerns (persona fidelity, stakeholder mapping, quality gates).

---

## Modes

### `crisis-pre-flight`

**Real-world workflow.** Pre-flight messaging review; statement stress test; red team read. A 30-120 minute pass before a statement is pushed.

**Named methodologies:**
- **Edelman Social-Issue Crisis Simulation** — 2-hour virtual format, 16 C-suite/senior execs, staged conflict across stakeholder groups. See [Edelman expertise page](https://www.edelman.com/expertise/crisis-reputation-risk/our-work/social-issue-driven-crisis-simulation).
- **H+K Strategies FlightSchool+** — immersive, real-time, dashboard-driven simulation of news / social / email / phone inbound. Quick pre-flight mode supported. See [FlightSchool+ page](https://www.hkstrategies.com/en/products/flightschool/) and [PR Week launch coverage](https://www.prweek.com/article/1277693/h+k-rolls-flight-school-crisis-simulation-platform).
- **FGS Global red-teaming** — quarterly minimum cadence recommended. See [FGS Global Crisis Management 2025 guide](https://fgsglobal.com/insights/crisis-management-2025-law-and-practice).
- **Polpeo** — modular crisis simulation, off-the-shelf short exercises through full-scale bespoke sims for up to 200 people. See [Polpeo Crisis Simulation](https://polpeo.com/crisis-simulation/).

**Issues-management framing.** Institute for Public Relations defines issues management as "an anticipatory, strategic management process" — distinct from reactive crisis management. See [Institute for PR Crisis Management and Communications](https://instituteforpr.org/crisis-management-and-communications/).

### `crisis-tabletop`

**Real-world workflow.** Full tabletop exercise; crisis simulation; war game.

**Named methodologies:**
- **H+K FlightSchool+ full** — Weibo/Twitter/Facebook/news channel feeds in real time.
- **Polpeo live** — 3-hour live social-media crisis with role-players, scorable against pre-agreed criteria.
- **Weber Shandwick FireBell** — offline replicas of client social pages and anti-fan pages, 2010-era, Adweek Project Isaac award. See [PRNewswire launch coverage](https://www.prnewswire.com/news-releases/weber-shandwick-launches-social-crisis-simulator-firebell-108940364.html).
- **Hoover Wargaming & Crisis Simulation Initiative** — academic/military war-gaming framework with corporate adoption. See [Hoover Institution page](https://www.hoover.org/research-teams/wargaming-and-crisis-simulation-initiative).
- **UK Gold/Silver/Bronze** — civil-contingencies severity tier, used as overlay on corporate BCP. See [Red Goat Gold/Silver/Bronze](https://red-goat.com/gold-silver-bronze/). Supported in this skill as an optional `severity` parameter, not as a mode.

**Tabletop inject structure.** MSEL (Master Scenario Events List) with 12-20 timed injects is the standard format. Documented in crisis-comms literature and encoded in this skill's `social-dynamics` and `memory-update` phases.

### `launch-pre-mortem`

**Real-world workflow.** Launch pre-mortem; launch messaging review; product marketing's pre-launch pattern.

**Named methodologies:**
- **Message house** — universal in branded comms (roof + 3 pillars + proof points). Encoded as artifact in `templates/artifacts/message-house.md`.
- **Tiered media list + embargo strategy + runsheet** — standard product-launch comms pack.
- **Atlassian launch pre-mortem template** is a widely-cited open-source template.

### `regulatory-response`

**Real-world workflow.** Regulatory response playbook; public-affairs rapid response.

**Named agencies:** APCO Worldwide, FGS Global (public-affairs practice), FTI Consulting, Teneo.

**Standard artifacts:** comment letter, stakeholder letter, coalition letter, press statement, op-ed draft. Encoded in the `regulatory-response` mode's artifact set.

See [APCO Crisis and Issues Management guide](https://apcoworldwide.com/blog/crisis-and-issues-management-how-leaders-can-proactively-prepare/).

### `deal-comms`

**Real-world workflow.** Transaction communications; deal comms; Day 1 playbook.

**Named agencies (dominant in deal-comms):**
- **Brunswick Group** — Capital Markets practice; $735B M&A comms in a single year. See [Brunswick Capital Markets](https://www.brunswickgroup.com/what-we-do/practice-groups/investor-engagement/).
- **FGS Global (legacy Sard Verbinnen)** — transaction and financial communications. See [FGS Equity Advisory and IR](https://fgsglobal.com/what-we-do/transaction-and-financial-communications/equity-advisory-and-investor-relations).
- **Joele Frank** — shareholder activism defense, deal comms.
- **Kekst CNC** — international deal comms.

**Canonical artifact: Day 1 / Day 30 / Day 100 plan.** Universal across Brunswick/FGS/Joele Frank/Sard Verbinnen/Kekst CNC. Pre-announcement pack: press release, investor presentation, CEO talking points, employee script, customer letter, regulator filing, analyst call script. Rehearsed analyst call + wargame is standard.

### `earnings-rehearsal`

**Real-world workflow.** Earnings rehearsal; mock analyst Q&A; investor day dry run.

**Named source:** NIRI (National Investor Relations Institute) playbook. Earnings script + Q&A prep doc (20-80 anticipated questions) + analyst-day perception study + ~1-week rehearsal cadence. 30-day pre-event cadence. See [ProInnovation Earnings Call Playbook 2026](https://www.proinnovationproductions.com/strategic-insights/2026/2/16/earnings-call-best-practices-in-2026-a-playbook-for-investor-relations-leaders).

Mock Q&A played by named sell-side analysts is a known practice — strong synthetic-persona fit.

### `positioning-pressure-test`

**Real-world workflow.** Positioning review; rebrand diagnostic; pre-rebrand stress test.

**Named methodologies:**
- **RepTrak Reputation Dimensions** — 7-driver scorecard; used as an output lens for this mode's artifact. See [RepTrak](https://www.reptrak.com).
- **Interbrand Best Global Brands** — Role of Brand Index (RBI). 1% RBI lift → 2.3% share-price lift.
- **Kantar BrandZ** — MDS framework (Meaningful / Different / Salient), MASB-certified, 14k brands.
- **Y&R BAV (Brand Asset Valuator)** — 4 pillars (Differentiation / Relevance / Esteem / Knowledge).
- **Lippincott, Siegel+Gale** — pre-rebrand workshop practitioners.

Note: this mode does NOT replicate the quant survey side of brand audits (RepTrak's 100K+ respondent instruments). It provides the qualitative stakeholder-perception stress-test against a concrete positioning artifact.

### `counterfactual-compare`

**Real-world workflow.** A/B message test; counterfactual draft review. Emerging — no dominant term in corporate PR; borrowed from political consulting.

**Named methodologies (political consulting):**
- **GQR (Greenberg Quinlan Rosner)**, **Lake Research Partners**, **Public Opinion Strategies**, **GBAO** — dial tests, split samples, triplet tests.
- **Cision 2025 PR Trends** explicitly flags this as an emerging gap in corporate PR. See [Cision PR Trends 2025](https://www.cision.com/resources/articles/pr-trends/).

### `red-team-read`

**Real-world workflow.** Red team read; adversarial pass.

**Origin:** US DoD / RAND Corporation red-teaming, 1960s Cold War Soviet-force simulation. Formalized post-9/11 by 2003 Defense Science Board. US Army Directed Studies Office stood up 2004. See [Red team Wikipedia](https://en.wikipedia.org/wiki/Red_team).

**Corporate adaptation:** Wag The Dog framing; FGS explicit quarterly cadence; Red Team Thinking and Bryghtpath as specialist boutiques. See [Wag The Dog — Red Teaming for Crisis Comms](https://www.wagthedog.io/p/red-teaming-forwardlooking-approach-crisis-communication-preparedness-7415).

### `activist-proxy`

**Real-world workflow.** Shareholder activism / proxy-fight response.

**Named agencies:** Brunswick and FGS both list as distinct practice. **Key stakeholders in cast:** institutional investors, proxy advisors (ISS, Glass Lewis), activist fund.

### `exec-transition`

**Real-world workflow.** CEO succession / exec-transition comms. Distinct playbook category per trade-press coverage. High-stakes, named-role cast.

### `internal-first`

**Real-world workflow.** Layoffs, RTO mandates, restructuring. Primary audience = employees; leak risk = high.

**Named methodology:** IABC (International Association of Business Communicators) Handbook cascade methodology — Exec → managers (with toolkit) → town hall → teams → written follow-up. Encoded in this mode's `cascade-pack` artifact.

---

## Phases

### `factbase` phase

**Purpose.** Shared ground truth to prevent persona hallucination.

**Anchor.** No single named methodology — this is adapted journalistic fact-checking discipline + Wikipedia-style sourcing + primary-source triangulation. Inspired by the "oppo file" tradition in political research.

### `cast-design` phase

**Anchor.**
- **Mitchell-Agle-Wood 1997** stakeholder salience (Power × Legitimacy × Urgency). [PDF](https://www.ronaldmitchell.org/publications/mitchell%20and%20agle%201997.pdf). Dominant academic framework. [Umbrex summary](https://umbrex.com/resources/frameworks/organization-frameworks/stakeholder-salience-model-mitchell-agle-wood/).
- **Freeman 1984** stakeholder typology (primary vs secondary stakeholders). Academic background.
- **Power/Interest Grid** (Mendelow) — practical day-to-day tool. See [Improvement Service Scotland Power-Interest Grid](https://www.improvementservice.org.uk/business-analysis-framework/consider-perspectives/powerinterest-grid).

### `deep-research` phase (persona-researcher)

**Anchor.**
- **Park et al. 2024** — [Generative Agent Simulations of 1,000 People](https://arxiv.org/abs/2411.10109). Interview-grounded persona bundles achieve 85% of human test-retest reliability; demographic-only stubs achieve ~40%. Multi-lens expert-reflection module adopted as schema field.
- **Reporter dossier practice** — media-training consultancies (5W PR, CAPIO, PRNewsPress) teach executives to anticipate specific journalists' angles with recent-coverage digests and likely-angle anticipation. Direct analog to named-press persona construction.

### `initial-reactions` + `critic` loop

**Anchor.**
- **Constitutional AI** ([Bai et al. 2022](https://arxiv.org/abs/2212.08073)) — critic-then-revise loop.
- **Li et al. 2024** — [arXiv 2402.10962](https://arxiv.org/abs/2402.10962). Persona drift is measurable (LLaMA2-70B: 0.85 → 0.65 stability over 8 turns). Mitigations: signature_opener (prompt-prefill), forbidden_phrases (hard blocks), rhetorical_constraints (style rules).
- **Roleplay-doh** (2024) — critic persona distinct from worker persona. Adopted in this skill's critic design.

### `social-dynamics` + `debate` phases

**Anchor.**
- **Polpeo live role-player feeds** — explicit pairings of real people reacting to each other's statements.
- **Delphi convergence** (Linstone & Turoff) — iterative expert panel methodology that preserves dissent. Encoded in our synthesizer's disagreement-axes section.

### `memory-update` phase

**Anchor.** Institutional memory practice at Brunswick / FGS Global — proprietary CRMs tracking how named journalists, analysts, regulators have reacted to past announcements. Not a named methodology; informal practice. Confirmed by agent-2 research as a genuine market gap no vendor has productized.

### `counterfactual` phase (counterfactual-compare mode)

**Anchor.** Political consulting dial tests, split samples, triplet tests (GQR, Lake Research, Public Opinion Strategies). Cross-industry borrow — emerging practice in corporate PR per Cision 2025.

### `synthesis` phase

**Anchor.**
- **Orchestrator-worker pattern** — [Anthropic's Multi-Agent Research System](https://www.anthropic.com/engineering/built-multi-agent-research-system). Opus lead + Sonnet workers + Opus synth = 90% uplift over single-agent.
- **After-Action Review (AAR)** format — standard post-tabletop deliverable (Edelman / APCO format).

---

## Cross-cutting concerns

### Holding statement artifact

**Anchor.** Industry-standard fill-in-the-blank comms artifact. Deployable in 15 minutes. See [Workshop — 11 Holding Statement examples](https://useworkshop.com/blog/11-examples-of-holding-statements/) and [Mailchimp Holding Statement guide](https://mailchimp.com/resources/holding-statement/).

### Q&A doc artifact

**Anchor.** NIRI earnings-prep standard: 20-80 anticipated questions with model answers, grouped by audience. Universal across corporate IR and crisis comms.

### Message house artifact

**Anchor.** Universal branded-comms framework. Roof + 3 pillars + proof points. Taught in most PR curricula. Used by Edelman, Ketchum, Weber Shandwick, in-house comms teams.

### Stakeholder heat map artifact

**Anchor.** Mitchell-Agle-Wood 1997 salience scoring + Power/Interest Grid visual conventions. Cluster labels (activist, scientist, regulator, press, customer, investor, internal, peer-company) pulled from Freeman 1984 stakeholder typology.

### Red_lines concept

**Anchor.** Fisher/Ury BATNA (Best Alternative To Negotiated Agreement) + crisis-comms "Rehearsing Questions" framework. A persona's red_line is the specific trigger that moves them from dialogue to confrontation. Each red_line is a concrete stimulus action, not a vague value violation.

### Quote verification

**Anchor.** Journalistic fact-checking discipline; oppo-research quote-hygiene; defamation-risk management. No verbatim quote may be attributed to a real person that they did not verbatim say. Enforced by `scripts/verify_quotes.py`.

### Use-constraint field (legal boundary)

**Anchor.** Personality rights, defamation law, deepfake statutes (California AB 730, EU Digital Services Act). Named-person simulations produced for internal rehearsal carry different legal exposure than outputs distributed publicly. Default for named personas: "internal rehearsal only, not for public-facing output."

### Severity parameter (Gold/Silver/Bronze overlay)

**Anchor.** UK civil-contingencies hierarchy. Gold = strategic, Silver = tactical, Bronze = operational. Used by corporate BCP/crisis-management teams with UK exposure. See [Databarracks BC command structures](https://www.databarracks.com/blog/bc-command-structures-gold-silver-and-bronze/).

---

## Industry survey anchors (macro-validation)

- **USC Annenberg 2025 Global Communication Report "Mind the Gap"** — 1,000+ professionals. AI persona-based stakeholder testing is called out as emerging, not mature. See [USC Annenberg press release](https://annenberg.usc.edu/news/research-and-impact/center-public-relations-global-communication-report-uncovers-key-industry).
- **ICCO World PR Report 2024-2025** — Crisis preparedness and resilience-building named as biggest admitted growth area for agencies. See [ICCO 2024-2025 PDF](https://iccopr.com/wp-content/uploads/2025/03/2024-2025-ICCO-World-PR-Report.pdf).
- **Edelman Trust Barometer 2025** — 33,000 respondents, 28 countries. Trust metrics inform the report's sentiment-and-trust_delta fields.

Competitive landscape (agent-2 findings):
- **Artificial Societies** — 500k AI personas, F100 PR clients.
- **Ask Rally** — $100/mo GenPop™.
- **Hotwire Spark** — agency-proprietary.
- **SightsAI** — digital-twin polling dashboard.
- **Synthetic Users, Evidenza** — UX / B2B GTM-coded, not corporate comms.

Pre-Flight's positioning: named-stakeholder archetype simulation with longitudinal memory + strict quote verification + mode-routed artifact output. Virgin position in PR trade press per agent-2 scan.

---

## Versioning

This document is versioned with the skill. When a mode or phase is added, extend this file with the new mapping before the mode's file is published to `modes/`. No new mode ships without an evidence trail here.

**Current version:** v2.0.0 (M1).
