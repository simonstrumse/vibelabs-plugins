# Routing heuristics — industry-agnostic

When building a cast from scratch (no preset applies), the orchestrator classifies the release into one of the categories below and uses the cluster weighting to guide the stakeholder-mapper. These are heuristics — the mapper adapts to the specific sender and stimulus.

---

## Release types

### product-launch
New offering, rebrand, category entry.

- **Strong** — customer, press (trade + consumer), investor
- **Medium** — peer/competitor, internal
- **Light** — regulator, community
- **Include an adversary?** Only if the category has an active adversary environment (e.g. supplement brands facing retail-pressure activists). Otherwise skip.

### financial
Earnings, dividend, capital raise, guidance, buyback.

- **Strong** — investor (sell-side + buy-side), press (financial + trade)
- **Medium** — internal, customer (if material dependency)
- **Light** — everything else
- **Include an adversary?** One activist or NGO to catch ESG-narrative overclaim when the release includes sustainability framing.

### corporate-m-and-a
Acquisition, divestiture, joint venture, restructure.

- **Strong** — press (trade + financial), investor, customer, peer/competitor
- **Medium** — internal, regulator (competition)
- **Light** — activist, community
- **Include an adversary?** Activist if the deal involves contested assets; otherwise a skeptical press.

### sustainability
ESG report, biodiversity disclosure, climate plan, certification.

- **Strong** — activist (likely constructive critic), scientist, investor (ESG), press (environment)
- **Medium** — regulator, customer, internal
- **Light** — financial press, consumer
- **Include an adversary?** Yes. Sustainability releases with no hostile persona are missing the most predictable critic.

### crisis-response
Response to incident, NGO report, investigation, viral moment.

- **Strong** — full press-room: activist (all flavors), scientist, regulator, press (trade + national + international), customer, investor
- **This is the largest cast.** Default N=16-20.
- **Include an adversary?** Multiple. The point of a crisis simulation is to preview the worst-case coverage.

### policy-position
Lobbying position, regulator-facing comment, treaty input.

- **Strong** — regulator, scientist, activist, policy press
- **Medium** — peer/competitor, investor (if material)
- **Light** — customer, consumer
- **Include an adversary?** Yes. Policy positions have predictable policy opponents.

### partnership
JV announcement, supplier deal, strategic partnership.

- **Strong** — press (trade), customer (downstream of the partnership), peer/competitor
- **Medium** — investor, internal
- **Light** — regulator, activist (unless partnership touches contested territory)

### personnel
Leadership change, board change.

- **Strong** — press (trade + financial), investor, internal
- **Medium** — peer/competitor
- **Light** — activist, regulator
- **Include an adversary?** Only if the outgoing/incoming exec has a controversial public record.

### general (fallback)
Unclassified or cross-cutting.

- Balanced cast: ~2 from each of activist, scientist, press, investor, customer, 1 internal. N=12.

---

## Cast-size heuristics

- **5** — gut-check pass on a short statement, Q&A answer, or pre-release line
- **8-12** — default for most releases
- **14-16** — high-stakes releases (crisis, sustainability, major M&A)
- **18-20** — full pressroom simulation for a material announcement or crisis
- **>20** — diminishing returns. Add variety of viewpoint before adding headcount.

## Always include heuristics

Unless the release is purely internal (HR/employee announcement):

1. **At least one adversary** — the cast should contain at least one persona whose default posture is skeptical or hostile to this sender. Sycophantic casts produce sycophantic reports.
2. **One internal persona** — the sender-side head of sustainability, head of comms, or senior counsel. Cheap coherence check — catches internal-voice inconsistencies.
3. **One journalist from a general-audience outlet** — even trade-focused releases travel when they travel, and this persona catches the "how would this land beyond the industry" angle.

## Red-flag detection

If the stimulus-analyzer flagged any of these, the cast weighting changes:

- **Sustainability claims** → add at least one scientific/NGO voice
- **Financial figures with ESG framing** → add ESG investor
- **References to a regulator** → add that regulator
- **Apology / correction / defensive language** → this is a crisis-response, regardless of what the sender called it. Use the crisis-response cast.
- **Material non-public information flag** → warn the user before spawning any agents

## When to use a preset instead

Presets skip the cast-building phase and load a verified, quote-grounded persona library. Use presets when:

- The sender matches a preset (e.g. Aker BioMarine → `presets/aker-biomarine`)
- The user explicitly requests a preset
- A preset sample is being used for testing or demo purposes

The preset's own `routing-table.md` overrides these heuristics.
