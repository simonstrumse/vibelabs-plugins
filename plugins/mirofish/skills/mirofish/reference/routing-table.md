# Persona routing table

Classify the stimulus into one of these release types and load the corresponding default cast. The orchestrator can always add or drop personas based on the user's input.

Persona IDs match files in `personas/`.

---

## product-launch

**Triggers:** Lysoveta, PL+, Superba, Reverva, Kori product releases. New brand launches.

**Default cast (n=10):**
- customer: schiff-megared
- customer: skretting-ceo
- customer: consumer-anna
- press: seaman-undercurrent
- press: blindheim-dn
- investor: nbim-esg
- investor: sell-side-analyst
- scientist: savoca-stanford
- internal: skogrand-aker
- **adversary:** bengtsson-greenpeace _(to catch sustainability framing risks)_

**Skip by default:** Hammarstedt, Allan, Werner, Kawaguchi, Brooks, CCAMLR Secretariat, Fiskeridirektoratet.

---

## ccamlr-policy

**Triggers:** Antarctic Treaty System, CCAMLR positions, MSC recertification responses, sustainability-commitment announcements touching Antarctic operations.

**Default cast (n=14):**
- activist: christian-asoc
- activist: bengtsson-greenpeace
- activist: hammarstedt-seashepherd
- activist: allan-bobbrown
- activist: werner-pew
- scientist: savoca-stanford
- scientist: kawaguchi-aad
- scientist: brooks-cu
- regulator: ccamlr-secretariat
- regulator: fiskeridirektoratet
- press: alberts-mongabay
- press: boe-nrk-brennpunkt
- investor: nbim-esg
- internal: skogrand-aker

**Skip by default:** schiff-megared, consumer-anna, seaman-undercurrent (will pick up from other sources).

---

## financial

**Triggers:** Quarterly earnings, dividend announcements, annual reports, investor-day material.

**Default cast (n=8):**
- press: blindheim-dn
- press: seaman-undercurrent
- investor: nbim-esg
- investor: sell-side-analyst
- customer: skretting-ceo
- internal: skogrand-aker
- scientist: savoca-stanford _(ESG contagion check)_
- **adversary:** christian-asoc _(to catch ESG-narrative overclaim)_

---

## bycatch-incident

**Triggers:** Whale death, documented entanglement, NGO video release, any incident where Aker-associated vessels caused documented harm.

**Default cast (n=16 — full press-room):**
- All activists (5)
- All scientists (3)
- regulator: ccamlr-secretariat
- regulator: fiskeridirektoratet
- All press (4)
- customer: skretting-ceo
- investor: nbim-esg
- internal: skogrand-aker

This is the "crisis cast." Run all personas that would plausibly comment within 72 hours.

---

## sustainability-report

**Triggers:** Annual sustainability report, ESG disclosure, biodiversity disclosure, climate-transition plan.

**Default cast (n=10):**
- activist: christian-asoc
- activist: werner-pew
- scientist: brooks-cu
- scientist: kawaguchi-aad
- press: alberts-mongabay
- press: blindheim-dn
- investor: nbim-esg
- investor: sell-side-analyst
- customer: skretting-ceo
- internal: skogrand-aker

**Skip by default:** Hammarstedt, Allan (they don't engage with sustainability reports — they ignore and release counter-material).

---

## m-and-a

**Triggers:** Acquisition, divestiture, joint venture, restructuring. The AIP sale was the archetype.

**Default cast (n=8):**
- press: seaman-undercurrent
- press: blindheim-dn
- investor: nbim-esg
- investor: sell-side-analyst
- customer: skretting-ceo
- customer: schiff-megared
- internal: skogrand-aker
- activist: christian-asoc _(to catch governance-narrative risks)_

---

## general (fallback)

**Triggers:** Unclassified or cross-cutting release.

**Default cast (n=12):**
- activist: christian-asoc
- activist: bengtsson-greenpeace
- scientist: savoca-stanford
- regulator: fiskeridirektoratet
- press: blindheim-dn
- press: alberts-mongabay
- press: seaman-undercurrent
- customer: schiff-megared
- customer: skretting-ceo
- investor: nbim-esg
- investor: sell-side-analyst
- internal: skogrand-aker

---

## Cast-modification heuristics

**Add an adversary** (hammarstedt-seashepherd or allan-bobbrown) if:
- Stimulus mentions Antarctica, MSC, sustainability, or krill fishery
- Stimulus makes any "sustainable" / "responsible" / "precautionary" claim
- Cast is otherwise all-transactional (no hostile voices)

**Add a scientist** if:
- Stimulus cites specific scientific claims
- Stimulus touches climate, biodiversity, or whale/penguin populations

**Add a regulator** if:
- Stimulus addresses CCAMLR procedure, flag-state compliance, or quota

**Add an internal (Skogrand)** always — internal coherence check is cheap and catches surprises.

**Drop customers** if:
- Stimulus is purely financial with no product angle

**Drop press (Seaman, Blindheim)** if:
- Stimulus is a retail-consumer announcement with no trade/financial angle

## Cast size guidance

- **5** — gut check on a small statement or Q&A answer
- **8-12** — default for most releases
- **14-16** — high-stakes (CCAMLR, crisis, major M&A)
- **20+** — dry run for a critical announcement; diminishing returns past 20
