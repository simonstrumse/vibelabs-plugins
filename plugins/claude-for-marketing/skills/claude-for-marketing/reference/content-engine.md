# Content engine — original, SEO-grade articles from human source material

How this engine produces written content that ranks: original articles built from real
human-written source material, authored fresh to a distilled voice, fact-checked claim by
claim, quality-gated by review passes, and published behind a date gate. It is the organic
counterpart to the paid build in `reference/playbook.md` Phase 5 (organic-vs-paid gap) and
Phase 10 (build), and it leans on the connectors in `reference/connectors.md` (search
console, the customer inbox, browser automation) and the frameworks in
`reference/marketing-foundations.md` (JTBD for topic angle, TOFU/MOFU/BOFU for intent
mapping, North Star for what the content is supposed to move).

**This is human-in-the-loop and quality-gated. Say it plainly up front.** The engine drafts,
researches, fact-checks, and assembles — but the human voice review and the fact review are
not optional, and an editor gates publication. A recurring cadence can sit on top (a queue of
topics worked one at a time, a date gate that reveals finished pieces over weeks). The cadence
schedules *already-written, already-reviewed* pieces. It does not author them unattended. Do
not turn this into a generator that writes on a timer and publishes without a human reading the
words. The whole point is the opposite of AI-on-AI slop: the source material is human, the
voice is learned from humans, and a human signs off before anything goes live.

The mechanics of *how content ranks* — schema, internal linking, the rewrite passes, the audit
scoring — are not reinvented here. Point those at **your SEO/AEO/GEO skill set** (e.g. an
`seo-aeo-geo` marketplace plugin exposing `/seo-audit`, `/seo-aeo-rewrite`, `/seo-geo-rewrite`).
This doc owns the *content production pipeline*: where the words come from, how the voice is
learned, how facts are verified, and how the editor gates a batch. Where a step is pure SEO
mechanics, it hands off to that skill set by name rather than duplicating it.

---

## The seven steps

Sequential, but they loop — a fact-check that fails sends a piece back to authoring; a voice
drift caught in QC sends it back to the voice guide. Each step says its goal, what it produces,
and where the human gate sits.

### Step 1 — Voice research first

Before a single article is drafted, learn the voice. You cannot write original, on-register
content by prompting a model to "write like an expert" — that produces the generic register
every other AI-written page has. Instead, harvest real human writing and distill it.

- **Goal:** a short, concrete voice guide and an antipattern blacklist, both grounded in real
  human-written examples from the domain.
- **Harvest:** dispatch a research subagent (see the dispatch note at the end) to collect
  **10–20 real human-written pieces** from the best authors, trade publications, and
  competitors in the domain's industry. Store **annotated excerpts with attribution** — author
  or publication, URL, date — so every voice decision traces back to a real source, and so a
  future reader can see what the voice was learned from. Never store the full copied article;
  store the excerpt and the link.
- **Distill into a voice guide:** register (formal/conversational, first/third person), the
  **vocabulary bank** (the domain's real terms of art, the words practitioners actually use),
  **sentence-shape patterns** (typical length, rhythm, how they open and close), and the
  **cultural constraints** (claims the field treats as table stakes, claims it treats as
  vendor puffery, regulatory or etiquette lines you don't cross).
- **Distill an antipattern blacklist:** the banned words, the superlatives the field rolls its
  eyes at, the cliché noun-stacks, the AI tells. This is the negative space of the voice — what
  a credible human in this domain would never write. It runs alongside the house writing
  standard (direct, concrete, dry; no negation-reframe; earn every sentence).
- **Output:** `content/voice-guide.md` and `content/antipattern-blacklist.md` in the user's
  project, each citing its source excerpts.
- **Human gate:** the operator reads and corrects the voice guide before any piece is authored.
  They know their field's register better than any harvest does; a five-minute correction here
  saves rewriting every article later.

### Step 2 — Topic selection from a SERP/keyword gap audit

Pick topics by reasoning backward from where competitors are weak, not from a brainstorm.

- **Goal:** a ranked topic list, each topic justified by a real gap and approved by the operator.
- **Audit:** run a **SERP and keyword gap analysis** against competitors — the queries they own
  (where they rank and you don't), and the holes they leave (real-volume queries nobody answers
  well). This is SEO mechanics; **run it through your SEO/AEO/GEO skill set** (`/seo-audit`)
  rather than hand-rolling keyword research here. Pull your own current organic position per
  query from search console (the Phase 5 connector) so the topic list targets the gap, not terms
  you already rank for.
- **Reason backward:** from each gap to a concrete article topic and the job it serves — map it
  to a funnel stage (TOFU awareness / MOFU consideration / BOFU decision, per
  `reference/marketing-foundations.md`) and to a JTBD the audience is hiring content to do.
- **Output:** `content/topic-queue.md` — topic, target query/intent, gap evidence, funnel stage,
  priority.
- **Human gate (veto):** the operator vetoes and reorders. They know which topics are off-brand,
  legally fraught, or already covered elsewhere on the site. The queue is theirs to approve before
  authoring starts.

### Step 3 — Author each piece fresh

Write to the voice guide and the blacklist, in-session, one piece at a time.

- **Goal:** a complete draft that reads as if a credible human in the domain wrote it, with every
  factual claim sourced.
- **Author against the artifacts from Step 1**, not against a generic "write a blog post" prompt.
  The voice guide and blacklist are loaded into the authoring context every time. No templates, no
  fill-in-the-blank structure across pieces — each article is shaped to its topic.
- **Cite as you write.** Every factual claim carries a source inline (URL or reference) so Step 4
  can verify it. A sentence you can't source is a sentence you flag, not one you assert. This is
  the same fact-vs-hypothesis discipline the playbook applies to strategy claims.
- **Native-language versions are hand-written, never machine-translated.** If the domain's
  audience reads in another language, author a fresh version in that language to its own voice
  guide. A machine translation of an English draft reads as a machine translation — wrong
  idiom, wrong register, dead on arrival in the local SERP. Harvest local-language sources in
  Step 1 if you'll publish in that language.
- **Output:** a draft per topic in `content/drafts/`, each with its inline citations and a
  claim list for the fact-checker.

### Step 4 — Quality-control passes

Several passes, run as subagents or by humans. Workers don't publish; they return findings.

- **Voice cleanup:** read the draft against the voice guide and blacklist. Flag every banned
  word, every superlative the field wouldn't use, every sentence that drifted into generic AI
  register. Return edits, not a rewrite from scratch.
- **Fact verification:** take the claim list and verify each claim against a source — every claim
  maps to a URL or reference, rated by the same evidence tier the rest of the engine uses
  (peer-reviewed > own hard data > industry benchmark > vendor number > single case study >
  folklore). A claim that resolves only to folklore or a vendor's own marketing is downgraded or
  cut. An unsourceable claim does not ship.
- **Consistency:** check internal consistency (no claim contradicting another), consistency with
  the canonical strategy and shared facts (price, product details — pointed to, never re-stated
  wrong), and consistency of terminology against the vocabulary bank.
- **Adversarial read:** one pass whose only job is to attack the piece — where would a domain
  expert call this thin, wrong, or AI-written? What's the weakest claim? What did it dodge? This
  is the decision loop applied to a single article: assume the draft is flawed and find how.
- **Output:** each pass returns a structured finding list (issue, location, suggested fix,
  source where relevant) against the draft. The pieces are not yet published.
- **The editor gate:** a single editor (human, or the orchestrator acting as editor with the
  operator's sign-off) reviews the findings, applies or rejects fixes, and **commits the
  approved batch in one pass**. Workers never publish directly. This is the
  build-paused/confirm-before-irreversible guardrail from the playbook, applied to content:
  nothing goes live until the editor gates it.

### Step 5 — Enrich for answer engines

Once the prose is approved, layer on the machine-readable enrichment — and again, this is SEO
mechanics, so hand it to the SEO/AEO/GEO skill set rather than reinventing it.

- **AEO direct-answer blocks:** the concise, lead-with-the-answer passages that answer engines
  lift into featured snippets and AI overviews. Add them where the topic has a clear question →
  answer shape. Generated/checked via `/seo-aeo-rewrite`.
- **GEO citation patterns:** structure the piece so generative engines can cite it — clear
  claims, attributable statements, the source scaffolding LLM-driven search rewards. Via
  `/seo-geo-rewrite`.
- **Schema:** the structured-data markup (Article, FAQ, HowTo, Breadcrumb as the piece warrants).
  Generated by the SEO skill set, not hand-authored here.
- **Output:** the enriched, schema-bearing version of each approved piece, ready to index.

### Step 6 — Publish behind a date gate

Pieces are written up front. The date gate reveals them on a schedule.

- **A publish gate is not a generator.** Be precise about this: all the articles in a batch are
  authored and reviewed in Step 3–4. The publish layer is a typed content index (or CMS entries)
  with a `publishDate` per piece; on each date the corresponding finished piece becomes visible.
  The date reveals work that already exists — it does not trigger a model to write something new
  at publish time. A cadence that authors-and-publishes unattended is exactly the slop pipeline
  this engine refuses to be.
- **Build:** a typed index / CMS collection where each entry carries title, slug, `publishDate`,
  `dateModified`, the approved body, and the schema from Step 5. A scheduled reveal flips
  visibility on `publishDate`.
- **On publish:** regenerate the sitemap and **ping IndexNow** (and submit the sitemap to search
  console) so the new URL is discovered fast. These are mechanical and safe to automate — the
  human gate already happened at the editor step.
- **Output:** live URLs, an updated sitemap, IndexNow confirmation, and a publish-log entry per
  piece (what went live, when, which topic/gap it served).

### Step 7 — Measure and refresh

Content is a position you hold, not a thing you ship once.

- **Measure:** pull organic rank, impressions, and clicks per published URL/query as a time
  series from search console. The instrumentation lives in
  `reference/measurement-implementation.md`; read it for the connection and the metric
  definitions. Tie movement back to the topic's target query so you can see which gap-bets paid
  off — and feed that back into Step 2's priority ordering (a topic that ranked is evidence for
  the next adjacent topic).
- **Refresh:** run **quarterly freshness passes** — revisit each live piece, update stale facts,
  re-verify citations, bump `dateModified` only when the content genuinely changed (a touched
  date with no real edit is a tell, not a ranking trick). A piece that has slipped in rank is a
  candidate for a re-author against the current voice guide and a fresh gap read.
- **Output:** a rank/traffic time series per URL, and a refresh log feeding the next cadence cycle.

---

## How the orchestrator dispatches the content engine

The orchestrator runs this per topic. The bundled agent definition lives in
`agents/content-engine.md`; the orchestrator dispatches it the same way it dispatches the
research agents in `reference/research-archetypes.md` — a sharp mandate in, a structured summary
out, the main thread converging the results and gating publication.

Concretely, per cycle:

1. **Voice guide once, refreshed rarely.** Step 1 runs at engagement start (and on a freshness
   pass). The voice guide and blacklist are inputs to every subsequent dispatch — load them into
   each authoring agent's context. Don't re-harvest per article.
2. **One topic, one dispatch.** For each approved topic in `content/topic-queue.md`, the
   orchestrator dispatches the `content-engine` agent with: the topic + target query, the funnel
   stage and JTBD, the voice guide, the blacklist, the relevant shared facts (pointed to, not
   pasted), and the language. The agent authors the draft and returns it **with its claim list and
   inline citations** — it does not publish.
3. **Fan out the QC.** The orchestrator dispatches the Step-4 passes (voice cleanup, fact-verify,
   consistency, adversarial read) as separate subagents against the draft — parallel where they
   don't depend on each other — each returning a structured finding list with sources and evidence
   tiers. The main thread converges the findings.
4. **The editor gate is the orchestrator's call, with the operator's sign-off.** The orchestrator,
   acting as editor, applies or rejects the findings, runs the Step-5 enrichment through the
   SEO/AEO/GEO skill set, and commits the approved batch. Nothing reaches the publish index without
   passing this gate.
5. **Schedule, don't generate.** Approved, enriched pieces go into the date-gated index with their
   `publishDate`. The cadence reveals them. Step 7's measurement feeds the next round of topic
   priorities.

Model choice follows the house rule (`reference/connectors.md`): a stronger model for authoring
and the adversarial read where voice and reasoning carry the piece, a bulk model for the
mechanical verification sweeps. All of it native Claude Code subagents on the operator's Max
plan — never API keys, never per-token billing outside the plan. Code does the plumbing (harvest
fetches, the publish index, the IndexNow ping, the search-console pull); every judgment about what
to write, whether a claim holds, and whether a piece is good enough to ship is reasoned in context
by an agent, with a human at the voice gate, the topic veto, and the editor gate.
