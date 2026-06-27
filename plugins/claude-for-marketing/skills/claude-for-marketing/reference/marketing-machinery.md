# Marketing machinery — optional engines catalog

A menu of additional engines the orchestrator can stand up. Each is independent: pick the ones
relevant to the project, in any order. None replaces the core phases in `reference/playbook.md` —
they extend the system once the measurement foundation (Phase 0) is in place.

Each entry: what it does, the process, when to use it, and the human/quality gate.

---

## 1. Post-purchase review solicitation

**What it does.** After a completed transaction, asks the customer for a review on the right
platform — the one they're most likely to have (or be found through), and that the operator
benefits most from. Routes marketplace customers to the platform they came through; direct
customers to the operator's primary organic review profile; customers booked via an agency or
internal B2B contract to no marketplace link at all (they're not anonymous consumers).

**Process.**

1. **Pull completed transactions** from the system-of-record. Filter to fulfillment-confirmed
   events in a configurable lookback window.

2. **Classify acquisition channel per customer.** Dispatch a subagent over the transaction record
   and available booking metadata. The agent reasons about the signals available (source channel
   field, promo code origin, referring domain logged at lead-capture, booking-portal route) and
   assigns one of three routing buckets:
   - *Marketplace-sourced* — came through a third-party listing platform; route to that platform's
     review flow.
   - *Direct* — found you via organic, search, ad, or direct referral; route to your primary review
     profile (typically your most visible organic listing — local search profile, primary industry
     directory, or both).
   - *Agency / B2B / internal* — contracted, trade-account, or internally-coordinated booking;
     exclude from automated review flow entirely (a review ask to a corporate travel coordinator
     is noise at best, a compliance problem at worst).
   
   Where signals are ambiguous, the agent flags the row for human review rather than guessing.

3. **Check the dedup log.** Before drafting anything, query the review-solicitation log (a
   flat-file or DB table: `customer_id | transaction_id | asked_at | channel | status`). Skip any
   customer already asked within the policy window (typically 90 days). Also skip any customer
   who left a review in the last pass of the review-scraping engine (Engine 2 below).

4. **Draft per-customer messages.** A subagent writes each message from scratch — the customer's
   language (detected from correspondence or booking locale), the specific experience or product
   they bought, and no template copy. The message includes the exact review link for their routing
   bucket. No bulk-merge; each one is a fresh composition.

5. **Human approval gate.** Present the full batch: routing breakdown, dedup summary, and the
   draft messages (or a representative sample if large). No message sends until explicit operator
   approval. After approval, log each send to the dedup log immediately.

6. **Commit the dedup log.** After each run, the updated log is committed so the next run has a
   clean state regardless of whether a session persists.

**When to use it.** After any period of fulfilled transactions — weekly or monthly depending on
volume. Especially valuable when organic review velocity has slowed or when a marketplace
channel's rating has been outpacing direct-search presence.

**Human/quality gate.** Full message batch shown before any send. Routing logic shown explicitly
so the operator can catch misclassified channel signals. No automation of the actual send until
approval.

---

## 2. Review scraping and refresh

**What it does.** Maintains a single source of truth for all reviews across listings: ratings,
counts, and full review text per platform. Keeps it current on a schedule and opens a pull
request (or equivalent review) when new content arrives, so the operator stays aware of their
review landscape without logging into each platform manually.

**Process.**

1. **Map the listings.** Enumerate the platforms where the business appears — local search
   profiles, industry directories, marketplace listings, and any other rated surfaces. These are
   explicitly listed in the project's connector map (see `reference/connectors.md`, connector
   catalog).

2. **Scrape per platform.** For each listing, a subagent fetches the current review data. Where
   a platform exposes a clean API, use it (scoped under the business's own credentials; scouted
   and verified per the MCP-scout protocol). Where no API exists, use browser automation driving
   the authenticated or public listing page — this is a first-class connector, not a workaround.
   JavaScript-rendered pages require a real browser session; static scrapes will miss them.

3. **Dedup against the source-of-truth store.** Compare incoming reviews against the existing
   store by a stable ID (platform + reviewer handle + review date). New or updated reviews are
   flagged; unchanged reviews are skipped. The store is a flat file or lightweight DB in the
   operator's project directory.

4. **Open a PR / change set.** New reviews are committed to the store and surfaced as a diff for
   the operator. The diff includes aggregate rating changes per platform and any notably negative
   reviews (flagged by a subagent reading the sentiment, not a regex threshold — the agent reads
   the text).

5. **Flag operational signals.** The subagent reading each new batch notes: recurring complaints
   (copy fuel for FAQs and landing pages), praise language worth incorporating into ad copy, and
   any review that names a competitor or a specific objection the operator hasn't addressed.

**When to use it.** On a schedule (weekly or biweekly suits most businesses). Also run
immediately before the review-solicitation engine to ensure the dedup log reflects current state.

**Human/quality gate.** The PR/diff is shown to the operator before merging — they confirm the
store update and decide whether any flagged signals warrant immediate action. The engine does not
auto-respond to reviews; it only reads.

---

## 3. AI-visibility monitoring

**What it does.** Tracks whether the business surfaces in generative-search answers (the AI
overviews and chat responses that increasingly intercept queries before a click happens), which
competitors are named ahead, what sources those answers cite, and recommends one concrete fix per
run. Produces a JSON time-series so drift is visible over time.

**Background.** Generative search surfaces citations from a small set of trusted sources — often
third-party directories, review aggregators, editorial content, and the business's own structured
pages. Appearing in those answers matters independently of traditional rank because many queries
now resolve without a click to organic results. Knowing which sources power the answers to your
category queries tells you where to invest in presence.

**Process.**

1. **Define the query set.** Start with 10–20 representative buyer queries across intent stages
   (awareness, consideration, decision) for the domain's industry. Store these in a flat file in
   the project. Add or prune after each run based on what's generating meaningful signal.

2. **Run each query through generative-search surfaces.** A subagent opens each query in the live
   surfaces (native Claude Code subagents on the Max plan — never API keys; no third-party
   monitoring SaaS). Where a surface requires browser automation (any JS-rendered answer panel),
   use the browser connector, scouted and verified per the MCP-scout protocol.

3. **Extract per-query structured output.** For each query:
   - Is the business named? (yes / no / partial)
   - Competitors named, and in what order?
   - Sources cited by the generative answer (domain names)
   - The answer text (stored for longitudinal comparison)

4. **Write to the time-series store.** Append the run's output to a JSON file:
   `{date, query, brand_mentioned, competitors_named: [], sources_cited: [], answer_text}`. One
   record per query per run. The orchestrator can plot this over time to see drift.

5. **Subagent recommends one fix.** After ingesting the full run, a subagent reads the pattern —
   which sources are consistently cited and the business doesn't appear in, which competitors are
   named in its category, which queries are open. It recommends a single, specific, actionable
   fix: "your business is absent from [source type] which is cited in 7 of 10 queries — add a
   listing there" or "competitor X is named on [query type] because it has an editorial piece
   covering [topic] — you don't; create one." One fix, not a list. The rest stay in the store.

**When to use it.** Monthly cadence for most businesses; weekly if there's active content
publishing or a competitor making aggressive moves. The time-series value compounds — a single
run is a snapshot; four runs are a trend.

**Human/quality gate.** The operator reviews the monthly summary and the single recommended fix.
The fix is proposed, not executed — content creation, listing submissions, and structured-data
changes go through the operator's normal approval flow.

---

## 4. Structured data, local SEO, and AIO readiness

**What it does.** Makes the business machine-readable to both traditional search crawlers and
AI training/retrieval pipelines. Generates schema markup from the reviews source-of-truth and the
business's canonical facts; sets a considered robots policy; creates an `llms.txt`; and anchors
the business's entity in any available knowledge graphs. Together these lift both classic SEO and
AI-answer inclusion probability.

**The four sub-tasks are independent; apply as many as relevant.**

### 4a. Schema markup

Generate the schema types relevant to the business and embed them in the site. Derive values
from the reviews source-of-truth (Engine 2) and the project's canonical facts file — never
hardcode what can be read from a live source.

Relevant types (pick those that apply):

- **LocalBusiness** (or a more specific subtype) — name, address, geo, phone, hours, price range,
  aggregate rating from the reviews store. The aggregate rating feeds directly from Engine 2.
- **Product / Service / Offer** — what is for sale, price range, availability, currency.
- **Review / AggregateRating** — sourced from the reviews store; regenerated on each Engine 2 run.
- **Breadcrumb** — site structure for any content deeper than the homepage.
- **FAQPage** — generated from the recurring objections list compiled in Phase 2.
- **Event** — for any time-bounded experience the business offers.

A subagent generates the JSON-LD blocks. A human checks them (especially price ranges and
aggregate rating counts) before they're deployed to the site. Use a validation tool
(schema.org validator or equivalent) as part of the process — the agent runs it, the operator
reviews any warnings.

### 4b. Robots policy

Set `robots.txt` and `meta robots` to explicitly allow the crawlers and training bots you want
to reach. The default "allow all" is fine for most businesses trying to build AI-answer presence.
Where the operator wants to restrict training-data inclusion (a legitimate choice), set
`X-Robots-Tag: noai` or the relevant per-bot directive — but do so consciously, not by accident
from an overly broad `Disallow`. The subagent reads the current `robots.txt`, flags any unintended
broad disallows, and proposes a revised version. Human reviews and approves before deploy.

### 4c. llms.txt

An `llms.txt` file (placed at the site root, mirroring the convention of `robots.txt`) is a
plain-language description of the business intended for language-model consumption — it tells an
AI reading the site what the business is, what it offers, who it serves, and what the canonical
sources of truth are. It is not a ranking signal for traditional crawlers; it is a legibility layer
for AI-native retrieval.

Generate from the canonical facts file and the strategy doc. Keep it under 500 words — dense with
facts, no marketing copy. A subagent drafts it; the operator reviews for accuracy before publish.

### 4d. Off-site entity anchor

The business should appear as a structured entity in at least one authoritative off-site graph
(Wikidata being the most widely used by AI pipelines). A Wikidata entry linking the business's
name, location, industry category, and official URL gives generative-search systems an
unambiguous entity to reference independent of the website.

Check whether an entry exists. If not, create one with the minimal required fields — a subagent
drafts the entity data; the operator reviews before submission. This requires a Wikidata account
(the business's or the operator's) and is a one-time action with periodic upkeep.

**When to use this engine.** Once after initial site setup, then incrementally whenever the
reviews store is refreshed (regenerate the AggregateRating markup), a new product/service is
launched (new Product schema), or new FAQ content is published.

**Human/quality gate.** Schema blocks, robots policy, and `llms.txt` are reviewed before deploy.
The Wikidata entry is reviewed before submission. No automated deploy of any of these.

---

## 5. Distribution mapping

**What it does.** Builds a channel/partner matrix that maps every pipe that can carry the
business's offering to customers — owned, earned, paid, and partnered — sorted by two strategic
axes: (1) does this channel feed AI-answer citation chains (the "AIO weight"), and (2) is it a
one-toggle connect or does it require engineering work?

**Why it matters.** The classic channel audit lists CPCs and commissions. This one adds the AIO
dimension because the pipes that feed AI answers have become a distinct asset class: a presence
in a widely-cited industry directory is worth more than a presence in one that AI systems ignore,
even if both charge similar listing fees. The matrix makes that visible.

**Process.**

1. **Enumerate all current and candidate channels.** Pull existing channels from the transaction
   record (which sources appear in actual bookings). Supplement with a subagent research pass:
   which channels do competitors appear on (from Phase 3 and Phase 4), which platforms in the
   industry are widely cited in generative-search answers (carry over signal from Engine 3)?

2. **Score each channel on four dimensions** (subagent reasoning, not a formula):
   - **AI citation weight** — how often does this platform appear as a source in generative-search
     answers for the domain's category queries? (Use the Engine 3 time-series if available;
     otherwise a fresh subagent research pass.)
   - **Volume potential** — rough customer volume this channel is capable of delivering at the
     business's scale.
   - **Integration cost** — one-toggle/API connect vs. custom engineering vs. ongoing manual work.
   - **Commission/cost** — total margin impact (not just the headline rate; see Phase 4 on
     commission reframing).

3. **Cluster into tiers.** High-AIO-weight + low-integration-cost channels go in Tier 1 (do these
   first regardless of volume). High-volume but high-engineering-cost go in Tier 2 (plan them).
   Low-AIO-weight and low-volume go in Tier 3 (deprioritize).

4. **Flag disintermediation candidates.** Where a Tier 1 channel is also a high-commission
   intermediary, it surfaces as a disintermediation candidate (cross-reference Phase 4). The
   matrix doesn't make that call — it flags it for the operator.

**Output.** A markdown table in the project's canonical strategy directory: rows = channels,
columns = AIO weight / volume potential / integration cost / commission / tier / action.

**When to use it.** Phase 1 or Phase 4, and whenever the Engine 3 time-series shifts significantly
(a new platform starts dominating citations → re-sort the matrix).

**Human/quality gate.** The operator reviews tier assignments and the disintermediation flags before
any partner relationship is acted on.

---

## 6. Programmatic-SEO data pages

**What it does.** Builds interactive, live-data pages that rank for informational queries in the
domain's category — the kind of queries that generate traffic but don't convert directly —
and uses them to funnel internal links to conversion pages, while embedding Dataset/ItemList
schema that feeds both traditional indexing and AI-answer extraction.

**The mechanic.** Informational queries ("best time of year to X", "how much does X cost in
[city type]", "X vs. Y comparison") attract high search volume and are poorly served by static
pages because the data changes. A live-data widget — pulling from the business's own transaction
record or public data the business has access to — is indexable, linkable, and credible in a way
a static blog post isn't. The schema tells crawlers and AI systems exactly what structured data
the page contains.

**Process.**

1. **Identify target queries.** Subagent research pass over the organic-vs-paid gap document
   (Phase 5): informational queries with real volume where the business ranks poorly and no
   competitor has a live-data answer. These are the candidates.

2. **Map each query to a data source.** Each candidate needs a specific data backing: aggregate
   booking windows, pricing distributions, demand seasonality, capacity utilization patterns, or
   external public data the business can credibly curate. No fabricated data; each widget pulls
   from a real, updatable source.

3. **Build the widget.** A lightweight, server-rendered or static-with-live-fetch component —
   no heavy framework dependency, no external CDN. The page loads fast (page speed is a ranking
   factor and a conversion factor; it is measured in Phase 10's landing-page audit). Data is
   fetched from the system-of-record via an API endpoint the orchestrator builds.

4. **Embed Dataset / ItemList schema.** For any page presenting structured list or tabular data,
   add the corresponding schema type so crawlers can extract the structured payload. The schema
   is generated from the live data, not hardcoded.

5. **Internal link architecture.** Each data page links explicitly to the relevant conversion
   page(s). Anchor text is descriptive, not generic ("book a [type] experience" not "click here").
   The link structure is planned before pages are published, not added as an afterthought.

**When to use it.** After the Phase 5 organic-vs-paid gap analysis surfaces a cluster of
informational queries the business could credibly own with live data. Not a Phase 0 or Phase 1
task — requires the measurement foundation and the keyword gap analysis to be complete first.

**Human/quality gate.** The operator approves the query target list and the data sources before
any page is built. Each page is reviewed before publication for accuracy and internal link
targets.

---

## 7. Lead magnets

**What it does.** Captures the email address (and, where available, UTM/click-ID attribution)
of visitors who don't convert to a transaction — turning browsing intent into a workable lead
before the session ends. Wires the capture event to fire the platform Lead event (see
`reference/measurement-implementation.md`) so the conversion is attributed and the ad platform
can optimize toward it.

**Two capture patterns — pick one or both.**

### 7a. Exit-intent capture

Triggered when the session is about to leave without converting (cursor leaving the viewport on
desktop; scroll-depth + time signals on mobile). Shows a minimal overlay: one clear value offer
(a pricing guide, a planning checklist, first-time discount — whatever is relevant to the
domain) and a single email field. The offer must be immediately useful, not a newsletter signup
dressed up.

### 7b. Persistent FAB (floating action button)

A fixed-position element visible throughout the browsing session — low friction, no overlay, the
user initiates it. Works well for businesses where the purchase consideration is long and the
visitor may want to return. Clicking opens a minimal capture form or scrolls to one.

**Process.**

1. **Define the offer.** A subagent reads the objections list from Phase 2 and the positioning
   from Phase 6 to propose the offer that addresses the highest-ranked unconverted objection —
   not a generic "subscribe." The operator approves the offer before anything is built.

2. **Build the capture mechanism.** Lightweight, no third-party embed (no external CDN — inline
   JS, inline CSS). On submit: write the email to the CRM/list; fire the Lead event to all
   active ad platforms via the measurement layer established in Phase 0 (include click IDs and
   UTM parameters captured at session start so the lead is attributable); redirect to or render
   the promised offer immediately.

3. **Wire the Lead event correctly.** The click ID (e.g. `fbclid`, `gclid`, `ttclid`) must be
   captured at page load (from the URL parameter) and passed with the Lead event, not just the
   email. This is the bridge that lets the ad platform credit the right campaign when the visitor
   eventually converts — the same lead-event firing pattern described in
   `reference/measurement-implementation.md`.

4. **Dedup against existing contacts.** Before writing to the CRM, check whether this email is
   already a known contact. A new lead from an existing customer is still a conversion signal;
   it should update the record, not create a duplicate.

5. **Connect to the review-solicitation and email sequences.** New leads enter whatever follow-up
   sequence the operator runs. The review-solicitation engine (Engine 1) checks the CRM, so leads
   who convert to transactions are picked up automatically.

**When to use it.** Any site that has measurable non-converting traffic — visitors reaching the
pricing or detail pages and leaving. Especially valuable when the transaction requires a longer
decision window (high price, group coordination, gift purchase planning) and the visitor has
clear intent but isn't ready to book.

**Human/quality gate.** The offer is approved before build. The event-firing logic (specifically:
which click IDs are captured and which platforms receive the Lead event) is reviewed with the
operator before go-live. No email sends automatically from the capture — those go through the
operator's existing sequence or are approved separately.

---

## Cross-engine dependencies

These engines share infrastructure. Build these once and point all engines at them:

| Shared resource | Used by |
|---|---|
| Reviews source-of-truth store | Engines 2, 3, 4a |
| Review-solicitation dedup log | Engine 1, Engine 2 |
| Canonical facts file (price, category, entity IDs) | Engines 4a, 4c, 5 |
| Measurement layer / Lead event firing | Engine 7, Phase 0 |
| Organic-vs-paid gap document (Phase 5) | Engines 3, 5, 6 |
| System-of-record connection (Phase 1) | Engines 1, 6 |

Set these up once in the project's `marketing/` directory. Point each engine at the canonical
file; never let two engines maintain their own copy of the same facts.

---

## Guardrails that apply to all engines

- **Dedup every outreach.** Any engine that touches a customer (Engine 1 review asks, Engine 7
  lead capture) must check a dedup log before acting and write to it immediately after. No
  customer contacted twice.

- **Human approval before any send.** Nothing sends — email, schema deploy, Wikidata submission,
  page publish — without an explicit operator green light. Show the full draft and the routing
  logic.

- **Source-quality tiering throughout.** AI-visibility monitoring (Engine 3) pulls answer text
  from live surfaces, which changes daily — tag every observation with its date. Review sentiment
  (Engine 2) is own-data tier; generative-search competitor presence is observational (not
  peer-reviewed). State the tier.

- **No deterministic routing in Engine 1.** Channel classification is a subagent judgment call
  over the available signals — not a lookup table or a hardcoded if/else on a field value. Where
  signals are ambiguous, the agent flags for human review.

- **Commit the stores and logs cleanly.** The dedup log, the reviews store, the AI-visibility
  time-series, and the distribution matrix are versioned in the project repo. Commit them after
  each engine run with relevant files only, not a bulk catchall.
