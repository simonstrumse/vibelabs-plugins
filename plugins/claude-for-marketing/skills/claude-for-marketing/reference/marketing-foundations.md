# Marketing foundations — the canonical frameworks, enriched

The reference the orchestrator consults when it needs a framework applied correctly. Each entry gives a
tight definition, when to reach for it, the common failure mode, and a one-line note on running it
agentically inside this engine (native Claude Code subagents on the Max plan — never API keys). This is a
lookup, not a course. Read the entry you need; skip the rest.

Framework set inspired by Sean Percival's Vibecoding + Marketing session (JTBD wizard, ICE tool),
enriched with the primary sources for each.

How these fit the engine: the decision loop (form a view → invite the challenge → separate fact from
hypothesis → verify against own-data or research → rate held/weakened/reversed → correct openly) runs *on
top of* these frameworks. A framework gives you the question to ask; the loop keeps your answer honest.
Source-quality tiering applies throughout: peer-reviewed > own hard data > industry benchmark > vendor
number > folklore. Tag every number you cite with its tier.

---

## Jobs-To-Be-Done (JTBD)

**Two lineages, one idea.** Customers don't buy products; they "hire" a product to make progress in a
situation, and "fire" it when something does the job better. Christensen's framing (the milkshake study:
people hired a morning milkshake to make a boring commute go faster and stay full till lunch — competitors
were bananas and bagels, not other milkshakes) is the *demand-side* story: study the job and its context,
not the customer's demographics. Tony Ulwick's **Outcome-Driven Innovation (ODI)** operationalizes it: a
job is stable over time, and customers measure success by a set of **desired outcomes** you can write down,
quantify, and prioritize.

**The desired-outcome statement** (Ulwick's structured need): *direction of improvement + metric + object
of control + contextual clarifier.* Example: "minimize the time it takes to get the songs in the desired
order for listening." Each statement gets two 1–10 ratings in interviews — **importance** and current
**satisfaction**. The gap (high importance, low satisfaction) is an underserved opportunity; high
importance + high satisfaction is saturated; low importance is noise. Ulwick's opportunity algorithm:
`opportunity = importance + max(importance − satisfaction, 0)`.

**When to use it.** Early discovery, before targeting or copy. Use JTBD when you need to understand *why*
people buy and what they're really comparing you against (the competitive set is "anything that does the
job," which is usually wider than your named competitors). It is the engine's Phase 2 backbone.

**How to interview for it.** Reconstruct the *story of a real purchase*, not opinions. Walk back to the
first thought ("when did you first realize you needed this?"), the trigger, what they considered, what
nearly stopped them, the moment they bought. Avoid hypotheticals and feature wishlists — you want the
forces (push of the situation, pull of the new solution, anxiety about switching, habit of the old). For
ODI specifically: extract desired-outcome statements, then rate importance × satisfaction.

**Failure mode.** Confusing the job with the product, or with a demographic. "Busy professionals" is not a
job. "Get a satisfying meal during a 20-minute commute alone in a car" is.

**Run it agentically:** dispatch a subagent over the customer inbox / reviews / call notes to mine the
recurring "I was trying to…" stories and the objections answered in nearly every reply — those become
desired-outcome statements and copy fuel. Reconstruct purchase narratives from the transaction record where
correspondence exists; never invent the story.

---

## ICP, segmentation & personas (and how they differ from JTBD)

**Ideal Customer Profile (ICP)** describes the *account/customer type* you should pursue: the firmographic
or demographic + behavioral attributes of customers who buy fast, stay, pay well, and refer. **Segmentation**
splits the whole market into groups that respond differently. **Personas** are semi-fictional archetypes of
individuals within a segment — useful for aligning a team on "who we're writing to," dangerous when treated
as research.

**JTBD vs. ICP/personas — when each.** They answer different questions and you usually need both. JTBD =
*why people buy and what they compare you to* (job + context). ICP/segmentation = *who to spend on and how
to reach them* (attributes + media). Build the JTBD first to understand demand; build the ICP to operate
against it. The trap is letting a persona's demographics stand in for the job — Christensen's whole point is
that two people in the same demographic can hire the product for opposite jobs, and the same person hires it
for different jobs at different times.

**When to use ICP/segmentation.** Targeting, channel selection, budget allocation, and qualifying which
intermediaries to study. Anchor segments in *hard attributes you can pull* (geography, order value, lead
time, channel, repeat behavior) before layering soft motivations on top.

**Failure mode — proxy vs. truth.** A measured attribute can be true about the *data* but false about the
*world*. (Worked example: phone country-codes read ~52% US, but agents and concierges booked US guests on
local numbers, so true guest-nationality was far higher. Both numbers are real — about different things. Say
which.) Always name the sampling bias of each source.

**Run it agentically:** pull hard attributes from whatever system-of-record exists and cross-check the
operator's intuition against them in the decision loop; rate "our customers are mostly X" as held / weakened
/ reversed against the actual distribution. Personas are written *after* the data, never as the starting
guess.

---

## AARRR "Pirate Metrics" — and the RARRA reorder

**AARRR** (Dave McClure, "Startup Metrics for Pirates," 2007) is the canonical customer-lifecycle funnel:
**A**cquisition (they find you), **A**ctivation (first good experience), **R**etention (they come back),
**R**eferral (they bring others), **R**evenue (they pay). One metric per stage, instrumented end to end, so
you can see *where* the lifecycle leaks instead of arguing about it.

**RARRA** (Gabor Papp / Thomas Petit, 2017, originally for app businesses) reorders the same five stages to
put retention first: **R**etention, **A**ctivation, **R**eferral, **R**evenue, **A**cquisition. The argument:
pouring acquisition into a product nobody comes back to is filling a leaky bucket — fix retention before you
scale spend. AARRR is the *measurement map*; RARRA is a *prioritization stance* (don't optimize the top of
the funnel while the middle leaks).

**When to use which.** Use AARRR as the instrumentation checklist for any business — it tells you which
events to track and is directly what Phase 0 wires up. Adopt the RARRA ordering when retention is weak or
unknown: it's the explicit reason this engine refuses to greenlight ad spend before activation/retention and
conversion tracking are verified. For a transactional/one-off business (a tour, a one-time service),
"retention" reads as repeat + referral + reviews, not subscription renewal — translate the stage, don't skip
it.

**Run it agentically:** map each AARRR stage to a real event in the system-of-record during Phase 0, verify
each fires end to end, and surface the worst-leaking stage as the first thing to fix — challenge "our problem
is acquisition" against the actual stage-by-stage drop-off before approving any spend.

---

## Prioritization — ICE and RICE

You will generate more ideas than you can run. Score them so the order is defensible, not political.

**ICE** (Sean Ellis — coined "growth hacking"; used to rank experiments at Dropbox/LogMeIn). Score each idea
1–10 on three factors and average:

> **ICE = (Impact + Confidence + Ease) / 3**

- **Impact** — how much this moves the target metric if it works.
- **Confidence** — how sure you are it'll work (your evidence, not your hope).
- **Ease** — how cheap/fast to ship (inverse of effort).

**RICE** (Sean McBride, Intercom) adds **Reach** to fix ICE's blind spot — it ignores how many people an
idea touches:

> **RICE = (Reach × Impact × Confidence) / Effort**

- **Reach** — number of people/events affected in a set period (use a real count, e.g. monthly sessions on
  the page).
- **Impact** — per-person effect (a fixed scale, e.g. 3 = massive, 1 = medium, 0.25 = minimal).
- **Confidence** — a percentage (100% = strong evidence, 50% = a hunch) that discounts wishful Reach/Impact.
- **Effort** — person-months (or any consistent cost unit); it divides, so cheap ideas rise.

**When to use which.** ICE for a high-velocity early-stage backlog where most ideas hit a similar audience —
it's faster and gives a shared language. RICE when ideas target *very different* audience sizes (a fix on a
high-traffic page vs. a niche one) — Reach stops you from over-ranking a clever idea that barely anyone sees.

**Scoring honestly.** The scores are only as good as the discipline behind Confidence. Make Confidence carry
the evidence tier: a peer-reviewed/own-data-backed idea earns high Confidence; a vendor claim or folklore
earns low. Don't let Impact be aspirational — it's the expected effect, not the best case. Re-score after
results come in; a reversed assumption should drag its ideas down.

**Run it agentically:** Claude scores in real time with the full context (own-data + research priors), states
the evidence behind each Confidence number, and surfaces the *reasoning*, not just the ranked list — never a
hardcoded scoring function. Feed disproven assumptions back as Confidence downgrades.

---

## Growth loops vs. funnels, the North Star Metric, and the marketing funnel

**The marketing funnel (TOFU / MOFU / BOFU)** is the content/awareness staging most teams already think in:
**T**op of funnel = awareness (broad, educational — blog, social, video); **M**iddle = consideration
(comparison guides, case studies, webinars, newsletters); **B**ottom = decision (demos, trials, pricing,
testimonials, the booking/checkout). Useful for matching message to intent stage and for SEO content
mapping. Its weakness: it's one-directional — pour in at the top, harvest at the bottom, with no model for
*reinvesting the output*.

**Growth loops** (Brian Balfour, Casey Winters, Kevin Kwok, Andrew Chen — Reforge) fix that. A loop is a
self-reinforcing system where the *output of one cycle becomes the input of the next*: a user signs up →
creates content/invites/value → which acquires the next user. Loops force you to stop treating acquisition,
product, and monetization as silos and ask how they compound. The funnel describes a *campaign*; the loop
describes a *durable growth engine*. Most small/local/transactional businesses run weaker loops (reviews →
ranking → more customers → more reviews; referrals; repeat purchase), and naming the loop tells you which
output to reinvest.

**North Star Metric** — the single metric that best captures the core value a customer gets from the
product, the one acquisition/activation/retention all feed. It is *not* revenue (that's the result); it's the
leading indicator of delivered value (e.g. nights booked, not gross bookings). Pick one, make every other
metric a contributor to it, and judge experiments by whether they move it.

**When to use which.** Use the marketing funnel to plan content and ad messaging by intent stage. Use the
growth-loop lens when designing the *system* — what compounds, what to reinvest. Use the North Star to keep a
sprawling test program pointed at one outcome instead of vanity metrics.

**Run it agentically:** name the business's actual loop(s) from the transaction + review data rather than
assuming a SaaS viral loop; propose a North Star candidate and challenge it in the decision loop ("does
moving this actually predict revenue in our own data?"); map planned content/ads to funnel stage so spend
isn't all bottom-of-funnel or all awareness.

---

## Positioning — Ries & Trout's category law, Dunford's operating method

**Ries & Trout** (*Positioning: The Battle for Your Mind*, term coined 1969; *The 22 Immutable Laws of
Marketing*) established that positioning happens in the customer's *mind*, not in the product. Two load-bearing
laws: the **Law of the Mind** (it's better to be first in the mind than first in the market) and the **Law
of Category** — *if you can't be first in a category, create a new category you can be first in.* For a
challenger facing an entrenched incumbent, this is the structural move: don't out-spend them in their
category; define a sub-category where you are the obvious leader.

**April Dunford** (*Obviously Awesome*) turns that into a repeatable method. Five components, derived in
order:

1. **Competitive alternatives** — what customers would actually do if you didn't exist (a rival, a manual
   workaround, or nothing). *Start here* — differentiation is meaningless without the baseline.
2. **Unique attributes** — what you have that the alternatives don't (features/capabilities).
3. **Value (and proof)** — the benefit those attributes deliver, with evidence.
4. **Target market** — the customers who care *most* about that value.
5. **Market category** — the context you frame yourself in so your value is obvious to that target. (Plus a
   bonus: relevant **trends** that make you timely without overreaching.)

Dunford's key insight: positioning that starts from your own features sounds good in the office and dies with
customers because it isn't anchored to a real alternative. Start from "what else would they use," then ask
"what do we have that those don't."

**When to use it.** Whenever you need a defensible angle against a bigger competitor (engine Phase 6), or when
copy feels generic. Positioning precedes every piece of ad/landing copy — it's the source the copy draws from.

**Run it agentically:** validate the chosen position against strategy literature and segment-size data via a
research subagent (can a small premium/niche player actually beat an incumbent *on position* rather than
budget, and under what conditions?), and strictly separate "what we know from data" from "assumptions to
test." Identify which incumbent tactics to copy (proof elements, risk-reducers, format) vs. which position to
differentiate against.

---

## Unit economics primer — the numbers that govern spend

These set the ceiling on what you can pay to acquire a customer. The engine treats CPA as a *framework of
three numbers*, not one (see playbook Phase 7) — these are the building blocks.

- **Contribution margin** = price − variable cost per unit sold. The money a sale actually contributes after
  the costs that scale with it. This is the hard floor: **break-even CPA can never exceed contribution margin
  on a first sale.** Always compute downstream economics on margin, not revenue.
- **CAC (Customer Acquisition Cost)** = total sales+marketing spend ÷ customers acquired in the same period.
  Be honest about what's *incremental* — branded/retargeting clicks that would have converted anyway should
  be credited minimally, or CAC flatters itself.
- **LTV (Lifetime Value)** = the *gross-margin* contribution of a customer over their whole relationship
  (margin per purchase × purchases × expected lifetime, discounted if long-horizon). Compute on margin, never
  revenue — revenue-based LTV overstates by the cost ratio.
- **LTV:CAC** — the headline ratio. **3:1 is the widely-cited minimum** at which unit economics are
  defensible (attributed to David Skok); top-quartile runs **4:1–6:1**. Treat 3:1 as the start of a
  conversation, not a pass/fail — and note it's an *industry benchmark* tier, not a law for your vertical.
  Much higher than ~5:1 can mean you're *under*-investing in growth.
- **CAC payback period** — months to recover CAC out of gross-margin contribution. **≤12 months is the
  common healthy bar**; sub-12 is top-quartile, >24 is a cash-risk flag. Two businesses can share a 3:1 ratio
  yet be in completely different positions if one pays back in 6 months and the other in 18 — the ratio hides
  cash timing, so always pair it with payback.

**When to use it.** Before any paid spend (gating Phase 7), to set the three CPA numbers — break-even
(solvency ceiling), competitive benchmark (e.g. the OTA/marketplace commission you'd otherwise pay → *where*
to push), and target (margin × an acquisition share that scales with how empty your capacity is). Adjust
target CPA by LTV per segment: a one-off buyer and a high-repeat partner relationship tolerate very different
spend.

**Failure modes.** Computing LTV/payback on revenue instead of margin; using a benchmark from another vertical
as if it were yours; trusting last-click CAC at low volume (lean on research priors and incrementality logic
instead — a clean lift test often needs ~200 conversions, which many small businesses don't have).

**Run it agentically:** derive the three CPA numbers from the operator's price + variable cost + commission
structure (confirm whether commission is on price incl./excl. tax — it reframes the benchmark), compute LTV on
margin per segment, and treat every "scale / hold / cut" decision against this framework. Confirm before any
spend; build campaigns paused.

---

## Choosing between them — a quick map

- *Why do people buy / what do we compete against?* → JTBD (Christensen story + Ulwick outcomes).
- *Who do we spend on and how do we reach them?* → ICP / segmentation; personas only after the data.
- *Where does the lifecycle leak?* → AARRR to instrument; RARRA ordering if retention is the weak link.
- *Which idea first?* → ICE (similar reach) or RICE (very different reach); Confidence carries the evidence
  tier.
- *What's our durable engine / one true metric / content plan?* → growth loops; North Star; TOFU-MOFU-BOFU.
- *What angle can we own vs. the incumbent?* → Ries & Trout Law of Category; Dunford's five components.
- *How much can we pay to acquire?* → unit economics → the three-number CPA framework.

Every one of these produces a *claim*. Send each load-bearing claim through the decision loop before you
build on it. A framework that no challenge dented wasn't actually challenged.

---

## Sources

- JTBD / ODI — [Strategyn (Ulwick), JTBD framework](https://strategyn.com/jobs-to-be-done-template/);
  [Outcome-Driven Innovation, Wikipedia](https://en.wikipedia.org/wiki/Outcome-Driven_Innovation);
  [anthonyulwick.com](https://anthonyulwick.com/outcome-driven-innovation/)
- AARRR / RARRA — [Mind the Product: AARRR vs RARRA](https://www.mindtheproduct.com/aarrr-vs-rarra-pirate-metrics-explained/);
  [ProductPlan: AARRR](https://www.productplan.com/glossary/aarrr-framework)
- ICE / RICE — [GrowthMethod: ICE](https://growthmethod.com/ice-framework/);
  [GrowthMentor: RICE](https://www.growthmentor.com/glossary/rice-scoring-model/) (Intercom origin)
- Growth loops / North Star — [Reforge: Growth Loops are the New Funnels](https://www.reforge.com/blog/growth-loops)
- Marketing funnel — [Funnel.io: TOFU/MOFU/BOFU](https://funnel.io/blog/tofu-mofu-bofu)
- Positioning — [April Dunford: Quickstart Guide to Positioning](https://www.aprildunford.com/post/a-quickstart-guide-to-positioning);
  [Ries & Trout, 22 Immutable Laws](https://grahammann.net/book-notes/the-22-immutable-laws-of-marketing-al-ries-jack-trout)
- Unit economics — [Fiscallion: SaaS unit economics](https://www.fiscallion.io/blog/saas-unit-economics);
  [LTV:CAC 3:1 benchmark](https://ecomcalctools.com/blog/cac-vs-ltv/)
