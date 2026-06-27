# Research Agent Archetypes — Parameterized Dispatch Templates

A library of reusable prompt templates the orchestrator dispatches as subagents. Each archetype covers: when to use it, and a parameterized template with `<PLACEHOLDERS>` that returns a structured summary with numbers and sources.

These complement the formal agent definitions in `agents/` — the templates here are for ad-hoc dispatch with task-specific parameters, invoked directly from the main orchestration loop wherever the playbook calls for a fan-out research step.

**Dispatch model:** All reasoning runs as native Claude Code subagents on the Max plan. No API keys, no SDK, no token costs outside the plan. Use `model: haiku` for bulk/repetitive passes, `model: sonnet` for nuanced analysis, `model: opus` when quality is critical and the answer is load-bearing.

**Return contract:** every archetype must return a structured summary with: the key finding stated as a claim, the number or rate that supports it, the source and its quality tier (peer-reviewed > own hard data > industry benchmark > vendor number > single case study > folklore), and an explicit `STATUS: held / weakened / reversed` where applicable.

---

## Archetype 1 — Competitor Ad-Library Teardown

**When to use:** Phase 3 (Competitive ad landscape). Dispatch once per serious competitor, or once per platform if you want a category-wide picture. Use before finalizing channel and keyword choices.

**What it answers:** who is spending, on which platforms, with what creative angle, at what apparent volume, and for how long — plus who is brand-bidding on your name.

**Template:**

```
You are a competitive intelligence agent. Your task: tear down the paid-ad presence of <COMPETITOR_NAME> (website: <COMPETITOR_URL>) in the category <CATEGORY_DESCRIPTION>.

Context: The business commissioning this research is <CLIENT_BUSINESS_DESCRIPTION>. Their primary keywords/topics are: <CLIENT_KEYWORDS_LIST>.

Do this in order:

1. META AD LIBRARY — go to https://www.facebook.com/ads/library/ and search for the advertiser domain <COMPETITOR_URL> and brand name <COMPETITOR_NAME>. For each active ad (or the most recent 10 if >10): note the ad ID, format (image/video/carousel), approximate start date, headline/hook, CTA, offer or angle, and the landing page URL.

2. GOOGLE ADS TRANSPARENCY CENTER — go to https://adstransparency.google.com/ and search for <COMPETITOR_NAME> and <COMPETITOR_URL>. Note: platforms advertised on (Search/Display/YouTube), regions, approximate creative count visible, and any ad copy you can read.

3. BRAND-BIDDING CHECK — search Google for [<CLIENT_BRAND_NAME>] and [<CLIENT_BRAND_NAME> <CATEGORY_KEYWORD>]. Note whether <COMPETITOR_NAME> or any other advertiser appears in the paid positions above organic results. Screenshot or quote the ad copy if present.

4. LONGEVITY SIGNAL — ads running for >60 days are almost certainly profitable (advertisers do not sustain losing spend). Flag any ad in the Meta library with an active start date >60 days ago as a "proven angle."

5. EMPTY-CATEGORY CHECK — search Google for [<CATEGORY_KEYWORD_1>], [<CATEGORY_KEYWORD_2>], <CLIENT_KEYWORDS_LIST>. Note whether any paid ads appear at all. An empty search = low competition signal.

Return a structured summary:
- COMPETITOR PROFILE table: Competitor | Platforms active | Approx active creatives | Longest-running ad age | Primary angle/offer
- PROVEN ANGLES list: each angle, evidence of longevity (days running), and the hook verbatim if available
- BRAND BIDDING: yes/no per competitor found, ad copy quoted, recommendation (bid own brand defensively or not)
- OPEN GROUND: any category keyword searched with zero or near-zero paid competition
- SOURCE QUALITY: Meta Ad Library (direct observation), Google Transparency Center (direct observation), Google SERP (direct observation)
- LIMITATIONS: note any access blocks, missing data, or gaps in coverage
```

---

## Archetype 2 — Customer / Demographics Profiler

**When to use:** Phase 2 (Jobs-to-be-done, ICP & demographics). Run once after connecting the transaction DB and the customer inbox. Re-run whenever a new channel or product mix changes the customer base materially.

**What it answers:** who actually buys (hard attributes from the DB), why they buy (qualitative from the inbox), what objections recur, and where proxy data misleads.

**Template:**

```
You are a customer intelligence agent. Your task: build a demographics and jobs-to-be-done profile for <CLIENT_BUSINESS_DESCRIPTION>.

You have access to:
- Transaction/booking database at <DB_CONNECTION_OR_FILE_PATH>: fields available are <FIELD_LIST>
- Customer inbox at <INBOX_SOURCE> covering <DATE_RANGE>
- Operator's stated hypothesis: "<OPERATOR_HYPOTHESIS_ABOUT_CUSTOMERS>"

Do this in order:

1. HARD ATTRIBUTES — query the transaction DB for the last <N_MONTHS> complete months (exclude current partial period). Compute:
   - Geographic distribution of customers (country/city if available). State what the field captures (billing address? IP? phone country code?) — this matters for proxy-vs-truth assessment.
   - Group/party size distribution if available.
   - Channel split (how they booked/bought): percentages by source.
   - Lead time distribution: days between purchase and consumption/delivery date. Compute median, 25th percentile, 75th percentile.
   - Repeat rate: what share of customers appear more than once in the period?
   - Revenue by segment if segmentation exists.

2. QUALITATIVE INBOX MINING — read the most recent <N_EMAILS> customer emails (inbound to the business). Extract:
   - Recurring questions asked before purchase (these are objections or information gaps — copy fuel).
   - Stated occasions or motivations ("birthday", "corporate", "anniversary", "tourist", "gift") — tally frequency.
   - Tone signals: are customers price-sensitive, convenience-driven, quality-seeking, gift-giving?
   - Any recurring complaints or friction points post-purchase.

3. PROXY-VS-TRUTH AUDIT — for each demographic attribute in step 1, assess whether the field actually captures what it appears to measure. Example: phone country codes capture the SIM's country, not the customer's nationality. If agents or hotels book on behalf of end guests, the booker's data is not the guest's data. Flag each mismatch explicitly with: field name | what it actually measures | what it might be mistaken for | recommended caveat.

4. CROSS-CHECK — compare the hard-data portrait to the operator's stated hypothesis. Note: held / weakened / reversed, with the specific number that supports the verdict.

Return a structured summary:
- SEGMENT TABLE: Segment name | Defining characteristics | Share of bookings/revenue | Primary motivation | Top objection
- TOP OBJECTIONS LIST: objection verbatim → copy implication (what the ad/landing page should address)
- PROXY-VS-TRUTH FLAGS: field | what it measures | caveat
- HYPOTHESIS VERDICT: operator's hypothesis | status (held/weakened/reversed) | supporting data point | source quality tier
- DATA GAPS: what questions this analysis cannot answer and what data would close them
```

---

## Archetype 3 — Assumption Validator (Adversarial)

**When to use:** Phase 9 (Adversarial validation of the whole assumption set). Also use mid-engagement whenever a load-bearing assumption needs pressure-testing before it drives a spend decision. Fan out multiple instances in parallel — one per cluster of 3–5 related assumptions.

**What it answers:** for each assumption: held, weakened, or reversed — with the specific published source, number, or case study that produced the verdict.

**Template:**

```
You are an adversarial research agent. Your task: test a batch of assumptions against published research, expert consensus, and real-world case studies. Rate each one.

The business context: <CLIENT_BUSINESS_DESCRIPTION>, operating in <MARKET/CATEGORY>, primary acquisition channels under consideration: <CHANNELS>.

Test each assumption below. For each one:
a) State the assumption as a falsifiable claim.
b) Search for published evidence that bears on it (peer-reviewed studies, well-cited industry reports, documented case studies from named companies). Use WebSearch and WebFetch. Prefer primary sources over summaries.
c) Rate the verdict: HELD (evidence supports it), WEAKENED (evidence partially contradicts or narrows it — state the condition under which it holds), or REVERSED (evidence clearly contradicts it).
d) State the specific number, finding, or mechanism that produced the verdict.
e) Cite the source with quality tier: peer-reviewed > own data > industry benchmark > vendor number > single case study > folklore.

ASSUMPTIONS TO TEST:
<ASSUMPTION_1>
<ASSUMPTION_2>
<ASSUMPTION_3>
[...up to ~5 per instance; fan out multiple instances for larger sets]

Return a structured summary:
- ASSUMPTION VERDICTS table: Assumption | Verdict | Key finding | Source | Quality tier
- REVERSALS section: for each reversed assumption, state what is true instead and why the original was wrong
- REFRAMES section: for each weakened assumption, state the condition under which it holds vs. breaks
- RESEARCH GAPS: assumptions where no published evidence was found — flag as "untested; empirical test required"
- SOURCE LIST: numbered bibliography, each entry with URL/DOI and quality tier

Do not soften reversals. If the evidence contradicts an assumption, say so directly and state what is true instead. Do not hedge a reversal into a "it depends" when the evidence is directional.
```

---

## Archetype 4 — Unit Economist / CPA Framework Builder

**When to use:** Phase 7 (Unit economics & CPA framework). Run once you have price, variable cost, and channel commission data. Re-run when pricing, product mix, or capacity utilization changes materially.

**What it answers:** break-even CPA, competitive benchmark, and capacity-tiered target CPAs — the three numbers that govern every "scale / hold / cut" call. Incremental only.

**Template:**

```
You are a unit economics agent. Your task: derive a CPA framework for paid acquisition for <CLIENT_BUSINESS_DESCRIPTION>.

Inputs:
- Price per unit sold (pre-tax): <PRICE>
- Tax rate applied (if any): <TAX_RATE> — note whether commission is calculated on price incl. or excl. tax, because this reframe changes the effective rate
- Variable cost per unit (direct COGS, not fixed overhead): <VARIABLE_COST>
- Existing channel commissions (OTA/marketplace): <COMMISSION_RATE> on <COMMISSION_BASE (incl/excl tax)>
- Repeat/referral behavior by segment (if known): <REPEAT_RATE_AND_LTV_NOTES>
- Capacity utilization context: <IDLE_CAPACITY_DESCRIPTION> — which slots/times/SKUs are undersold?

Derive the following. Show your arithmetic explicitly at each step.

1. CONTRIBUTION MARGIN = Price (pre-tax) − Variable cost. This is the maximum any acquisition can cost while remaining solvent on the first sale. Call this BREAK-EVEN CPA. State it as: "Never pay more than $X to acquire one customer, or the first sale loses money."

2. COMMISSION BENCHMARK = effective commission in dollar terms (commission rate × applicable base). This is what you pay a middleman per sale. Use it as a signal for where to push: a direct acquisition costing less than this number beats the channel economics. Do NOT treat it as your target — it is a competitive reference point, not a ceiling.

3. CAPACITY-TIERED TARGETS — derive three target CPAs based on how empty the inventory is:
   a. HIGH IDLE (>40% unfilled): Target CPA = Contribution margin × <AGGRESSIVE_SHARE, suggest 0.5–0.7> — you can afford to buy demand aggressively because idle inventory is a perishable loss.
   b. MODERATE IDLE (15–40% unfilled): Target CPA = Contribution margin × <MODERATE_SHARE, suggest 0.3–0.45>
   c. NEAR FULL (<15% unfilled): Target CPA = Contribution margin × <CONSERVATIVE_SHARE, suggest 0.1–0.2> or pause ads entirely — you are paying to fill capacity you don't have.

4. LTV ADJUSTMENT — if repeat rate is meaningful (>15% of customers return within 12 months), calculate LTV-adjusted CPA ceiling: Contribution margin × (1 + repeat_rate × average_repeat_orders). Segment this if one segment (e.g., B2B/partner) repeats at a materially different rate than another (e.g., tourist/one-off).

5. INCREMENTALITY NOTE — all CPAs above are targets for *incremental* conversions only. Branded search and retargeting have high measured ROAS but low incrementality — meaning most of those customers would have converted anyway. Apply a discount factor of <INCREMENTALITY_DISCOUNT, suggest 0.3–0.5 for branded/retargeting> when evaluating those campaign types against these targets.

Return a structured summary:
- BREAK-EVEN CPA: $X — hard ceiling, never exceed
- COMMISSION BENCHMARK: $Y (effective per-sale cost via <CHANNEL>) — beat this with direct
- CAPACITY-TIERED TARGETS table: Utilization state | Target CPA | Rationale
- LTV-ADJUSTED CEILING (if applicable): $Z per segment
- INCREMENTALITY NOTE: which campaign types to discount and by how much
- ARITHMETIC TRAIL: show each calculation so it can be audited
- ASSUMPTIONS FLAGGED: anything that is an estimate rather than a known figure
```

---

## Archetype 5 — MCP Scout

**When to use:** Any time the playbook or an operator identifies a new data source, API, or tool category that would benefit from MCP integration. Always run this before installing any MCP. Never blind-install.

**What it answers:** the newest/best MCP for the stated goal, supply-chain verification (who built it, what the source does, any red flags), and a clear install-or-not recommendation.

**Template:**

```
You are an MCP supply-chain research agent. Your task: find the best available MCP server for the following goal, verify it, and recommend whether to install it.

Goal: <MCP_GOAL_DESCRIPTION — e.g., "read and write to a Shopify store's orders and products", "query Google Analytics 4 data", "send and read Gmail">
Business context: <CLIENT_BUSINESS_DESCRIPTION>
Constraints: <ANY_CONSTRAINTS — e.g., "must support OAuth, not API key", "must be open source", "must support read-only mode">

Do this in order:

1. DISCOVERY — search for MCP servers matching this goal. Sources to check:
   - https://github.com/modelcontextprotocol/servers (official registry)
   - npm registry: search "mcp <keyword>" sorted by recent publish date
   - GitHub search: "mcp server <goal keyword>" filtered to repos updated in last 6 months
   - Any official MCP published by the target platform/vendor itself
   List all candidates found: name, author/org, GitHub URL or npm package, last publish date, star count if available.

2. SELECTION — for the top 1–2 candidates, assess:
   - Is there an official MCP from the platform vendor themselves? (highest trust)
   - Maintenance signal: last commit date, open issues count, whether issues get responses
   - Install method: npm package, Docker, Python package, or clone-and-run
   - Auth method: API key, OAuth, service account — which is required?

3. SUPPLY-CHAIN VERIFICATION — for the top candidate:
   - Fetch the source code (GitHub repo) or the npm package source
   - Check: does it make network calls to any domain other than the stated target API? (red flag if yes)
   - Check: does it request more permissions/scopes than the goal requires? (flag excess)
   - Check: is the package published by the same org as the GitHub repo? (flag mismatch)
   - Check: any `postinstall` scripts that execute arbitrary code? (flag if present)
   - Verdict: CLEAN / FLAG (explain what you flagged)

4. INSTALL COMMAND — if verdict is CLEAN, provide the exact install command or config block for `.mcp.json` or the project's MCP config. If FLAGGED, state why you recommend against installing and what alternative approach exists (direct API integration, different MCP, browser automation).

Return a structured summary:
- CANDIDATES table: Name | Author | Last updated | Stars | Auth method | Source URL
- RECOMMENDED: name, version, install command or config block
- SUPPLY-CHAIN VERDICT: CLEAN or FLAG with specific findings
- SCOPES/PERMISSIONS REQUIRED: list what access it needs and whether that matches the goal
- ALTERNATIVE IF NOT RECOMMENDED: what to do instead
- SOURCE QUALITY: direct source-code inspection (highest), npm metadata, GitHub signals
```

---

## Archetype 6 — Channel / Arbitrage Analyst

**When to use:** Phase 4 (Channel economics, arbitrage & disintermediation). Run after connecting the transaction DB. Re-run if a new intermediary appears in the data or if commission structures change.

**What it answers:** who the intermediaries are, what they cost, what they actually do (are they genuine demand generators or are they reselling your own audience?), and where to coexist vs. disintermediate.

**Template:**

```
You are a channel economics and arbitrage research agent. Your task: identify and tear down the intermediaries in <CLIENT_BUSINESS_DESCRIPTION>'s transaction data, and produce a coexist-vs-disintermediate plan.

You have access to:
- Transaction/booking database at <DB_CONNECTION_OR_FILE_PATH>: relevant fields are <FIELD_LIST including channel/source/promo-code/agent-name fields>
- Date range: last <N_MONTHS> complete months

Do this in order:

1. INTERMEDIARY IDENTIFICATION — query the transaction DB for all distinct channel/source/partner/promo-code values. Group by channel. For each channel that accounts for >5% of bookings or revenue:
   - Name and apparent identity
   - Volume (bookings and revenue %)
   - Effective cost (commission rate × sales, or inferred from promo-code discounts)
   - Average transaction value vs. the direct-channel average — higher or lower?
   - Lead time vs. direct — do they book further out or closer in?

2. ARBITRAGEUR TEST — for each significant third-party channel, determine whether they are a genuine demand generator (they find new customers you would not have reached) or an arbitrageur (they capture intent that was already heading toward you and resell it). Signals of arbitrage:
   - They bid on your brand keywords in paid search (check Google Transparency Center and Google SERP for their domain)
   - Their customers overlap geographically with your organic traffic / direct-booking customers
   - They promote your listing on social with your own product images (check their social accounts)
   - Transaction lead times match direct-booking patterns (customers booked with them may have searched you first)

3. TEARDOWN — for any confirmed or suspected arbitrageur: what is their business model? What marketing channels do they use? What angles/copy do they run? What can you learn from how they sell your product (transferable best practices)?

4. COEXIST-VS-DISINTERMEDIATE PLAN — for each channel:
   - KEEP: channels that demonstrably add new demand (different geographic reach, B2B relationships, gift buyers you don't otherwise reach) where their effective cost is below your break-even CPA
   - DISINTERMEDIATE (gradually): channels where you pay commission on demand that was already yours — transition volume to direct by targeting the same segments with direct paid or SEO
   - MONITOR: channels where evidence is ambiguous — specify what data would resolve it

Return a structured summary:
- INTERMEDIARY TABLE: Channel | Volume % | Revenue % | Effective cost/booking | Avg transaction vs direct | Lead time vs direct
- ARBITRAGE VERDICTS: Channel | Verdict (genuine/arbitrageur/ambiguous) | Evidence
- TEARDOWN (per arbitrageur): their model, channels, angles, transferable practices
- COEXIST-VS-DISINTERMEDIATE PLAN: Channel | Recommendation | Rationale | Transition step if disintermediate
- DATA QUALITY NOTES: any fields that were missing, inconsistent, or ambiguous
```

---

## Archetype 7 — Booking / Demand-Pattern Analyst

**When to use:** Phase 8 (Capacity, timing & demand patterns). Run once after the transaction DB is connected and you have at least 3 complete months of data. Use last complete period as ground truth — do not draw lead-time conclusions from a current month that is still filling.

**What it answers:** when customers book relative to consumption (lead time), what seasonality looks like, where capacity sits idle vs. oversold, channel-by-channel differences in lead time, and what this means for ad timing and budget pacing.

**Template:**

```
You are a booking and demand-pattern analyst. Your task: extract timing, seasonality, and capacity insights from <CLIENT_BUSINESS_DESCRIPTION>'s transaction data to drive ad-flight and budget decisions.

Database: <DB_CONNECTION_OR_FILE_PATH>
Available fields: <FIELD_LIST — including booking/purchase date, consumption/service/event date, channel, product/SKU, quantity/capacity>
Analysis period: last <N_COMPLETE_MONTHS> complete months only. Explicitly exclude <CURRENT_PARTIAL_MONTH> from lead-time analysis — it is still filling and will show artificially short lead times.

Do this in order:

1. LEAD TIME DISTRIBUTION — compute (consumption_date − purchase_date) in days for all transactions in the period. Report:
   - Median lead time
   - 25th percentile (short-lead segment)
   - 75th percentile (long-lead segment)
   - Percentage of bookings made within 7 days of consumption
   - Percentage made 30+ days ahead
   - Channel breakdown: compute median lead time separately for each channel accounting for >10% of volume. Flag any channel that skews materially longer or shorter than the overall median.

2. SEASONALITY — aggregate bookings and revenue by month for the full period (and year-over-year if data spans >12 months). Identify:
   - Peak months (top 3 by volume)
   - Trough months (bottom 3 by volume)
   - Whether the operator's stated seasonality hypothesis matches the data (state: held / weakened / reversed)

3. CAPACITY UTILIZATION — if capacity data exists (max capacity per slot/day/product), compute:
   - Utilization rate per product/time-slot for each month
   - Which products/slots/day-parts are consistently below 70% full (idle inventory — worth advertising)
   - Which are consistently above 85% full (near-sold-out — ads here mostly cannibalize free demand)
   - Day-of-week pattern if applicable (busier on weekends/weekdays?)

4. TIMING IMPLICATIONS — derive concrete ad-timing rules from the above:
   - Given the median lead time of X days, ads should be in-market by at least X days before the target consumption period
   - Given the lead-time distribution, what share of bookings happen within <SHORT_WINDOW> days? Use this to size any "last-minute availability" campaign
   - Which months should have elevated budget (demand is there, capacity is idle)?
   - Which months should budget be reduced or paused (already near capacity, or true off-season with no idle inventory to fill)?

5. HYPOTHESIS CHECK — the operator's stated demand pattern hypothesis is: "<OPERATOR_SEASONALITY_HYPOTHESIS>". State: held / weakened / reversed, with the specific number from the data that produced the verdict.

Return a structured summary:
- LEAD TIME TABLE: Metric | All channels | Channel A | Channel B | [per channel >10% share]
- SEASONALITY TABLE: Month | Bookings | Revenue | Utilization % (if available) | Budget recommendation
- IDLE CAPACITY LIST: product/slot | avg utilization | recommendation (advertise / hold / pause)
- AD-TIMING RULES: plain-language decision rules derived from the data
- HYPOTHESIS VERDICT: operator's hypothesis | status | supporting data point
- DATA LIMITATIONS: missing fields, partial periods used, any caveats
```

---

## Archetype 8 — Landing-Page Conversion Audit

**When to use:** Phase 10 (Build campaigns & verify the conversion path), or any time a campaign is paused and the first hypothesis for low conversion rate is the page itself. Run before finalizing ad destinations.

**What it answers:** page speed (real numbers from PageSpeed Insights), mobile UX issues, form friction, conversion plumbing gaps, and a prioritized punch-list.

**Template:**

```
You are a landing-page conversion auditor. Your task: audit the conversion readiness of the landing page(s) that paid traffic will land on for <CLIENT_BUSINESS_DESCRIPTION>.

Pages to audit: <URL_LIST>
Repo/codebase path (if available): <REPO_PATH_OR_"not available">
Key conversion action: <DESIRED_ACTION — e.g., "submit a booking inquiry form", "click Book Now", "complete checkout">

Do this in order:

1. SPEED — for each URL, fetch the PageSpeed Insights API result:
   GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<URL>&strategy=mobile
   GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<URL>&strategy=desktop
   (No API key required for basic results.)
   Record: LCP (Largest Contentful Paint), CLS (Cumulative Layout Shift), FID/INP, overall Performance score (0–100). Flag anything below: LCP >2.5s (mobile) or >2.0s (desktop); Performance score <70.

2. MOBILE UX — fetch the live page. Assess:
   - Is the primary CTA (Book Now / Contact / Buy) visible above the fold on a 375px wide viewport without scrolling?
   - Are tap targets ≥44px (Apple HIG) / ≥48dp (Material)?
   - Is the phone number a tap-to-call `<a href="tel:...">` link?
   - Does the form (if any) use appropriate input types (`type="email"`, `type="tel"`, `autocomplete` attributes)?
   - Any interstitials or pop-ups that block content on load?

3. FORM FRICTION — if a form exists (inspect the page source or the repo):
   - How many fields? (Each field costs ~5–10% conversion rate — cite Formstack/Baymard benchmark)
   - Is any field likely unnecessary for the stated conversion goal? List candidates to remove.
   - Does the submit button label describe the outcome ("Get a Quote", "Check Availability") or is it generic ("Submit")?
   - Is there a confirmation message or redirect after submission? If not, users may resubmit.
   - Is the form tested for mobile keyboard behavior (does the viewport scroll to the active field)?

4. CONVERSION PLUMBING — check the tracking setup:
   - Does the page fire a conversion event on form submit / checkout complete? (Check for the pixel/tag in the source or via the repo)
   - Is the conversion event firing on the *actual* action (not just on page load)?
   - For paid traffic: does the URL structure preserve UTM parameters through to the conversion page?
   - If using a booking widget in an iframe: does the conversion event fire from inside the iframe or is it lost? (Iframe-conversion tracking is a common gap — flag explicitly if found)

5. COPY / OBJECTION MATCH — given the top objections identified in the Customer Profiler (if run), does the page address them above the fold? List each top objection and whether it is addressed (yes / no / buried below fold).

Return a structured summary:
- SPEED TABLE: URL | Mobile LCP | Mobile Score | Desktop LCP | Desktop Score | Flag
- MOBILE UX ISSUES: bulleted list of specific failures, each with: element | issue | fix
- FORM AUDIT: field count | fields to remove | button label verdict | confirmation status
- CONVERSION PLUMBING GAPS: each gap, severity (blocks attribution / degrades measurement / minor), fix
- OBJECTION COVERAGE TABLE: Top objection | Addressed on page | Location (above fold / below / missing)
- PRIORITIZED PUNCH-LIST: issues ranked by conversion impact (highest impact first), each with: issue | fix | effort (low/medium/high)
- SOURCE QUALITY: PageSpeed Insights (direct API), live page observation (direct), repo inspection (direct), Baymard/Formstack benchmarks for field-count effect (industry benchmark)
```

---

## Usage Notes for the Orchestrator

**Parallelism:** archetypes 1, 2, 4, 5, and 8 can run in parallel once the relevant data connectors are live. Archetype 3 (assumption validator) should run after archetypes 1, 2, 4, and 7 have returned, so their findings populate the assumption list. Archetype 4 (unit economist) depends on having price and commission inputs confirmed by the operator first.

**Evidence tiers:** require every archetype instance to tag its findings by evidence quality. A finding supported only by a vendor number or folklore is flagged as low-confidence and should be routed through the adversarial validator (archetype 3) before driving a spend decision.

**Superseded log:** when an archetype returns a verdict that reverses a previous finding, the orchestrator must write the old claim and its replacement to the project's superseded log. The templates surface contradictions — the orchestrator closes the loop by updating the canonical strategy doc.

**Return format contract:** every instance must end with a SOURCE LIST section that names each source, its URL or citation, and its quality tier. Unsourced claims should not be accepted as findings.
