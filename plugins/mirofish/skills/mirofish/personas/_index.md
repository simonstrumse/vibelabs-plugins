# Persona index — Aker BioMarine library

20 named personas grounded in public-record quotes and institutional positions. Load individually; do not load the whole directory in a single spawn.

**Last verified:** 2026-04-16. Sources in `research/use-case/stakeholder-personas.md` at repo root.

## Activists (5)

| id | name | institution | posture |
|---|---|---|---|
| christian-asoc | Claire Christian | ASOC | policy-expert, skeptical-hostile |
| bengtsson-greenpeace | Frida Bengtsson | Greenpeace Nordic | moral-authority, skeptical |
| hammarstedt-seashepherd | Peter Hammarstedt | Sea Shepherd Global | direct-action, hostile |
| allan-bobbrown | Alistair Allan | Bob Brown Foundation | retail-pressure, hostile |
| werner-pew | Rodolfo Werner | Pew Bertarelli | science-policy, skeptical-constructive |

## Scientists (3)

| id | name | institution | posture |
|---|---|---|---|
| savoca-stanford | Matthew Savoca | Stanford/Hopkins | skeptical-quantitative |
| kawaguchi-aad | So Kawaguchi | Australian Antarctic Division | neutral-technical |
| brooks-cu | Cassandra Brooks | University of Colorado Boulder | skeptical-analytical |

## Regulators (2)

| id | name | institution | posture |
|---|---|---|---|
| ccamlr-secretariat | CCAMLR Secretariat | CCAMLR (Hobart) | neutral-diplomatic |
| fiskeridirektoratet | Frank Bakke-Jensen | Norwegian Directorate of Fisheries | transactional-bureaucratic |

## Press (4)

| id | name | institution | posture |
|---|---|---|---|
| alberts-mongabay | Elizabeth Claire Alberts | Mongabay | skeptical-investigative |
| blindheim-dn | Anne Marte Blindheim | Dagens Næringsliv | transactional-market |
| boe-nrk-brennpunkt | Eivind Bøe | NRK Brennpunkt | skeptical-investigative |
| seaman-undercurrent | Tom Seaman | Undercurrent News | transactional-positive |

## Customers (3)

| id | name | institution | posture |
|---|---|---|---|
| skretting-ceo | Skretting CEO (pattern) | Skretting / Nutreco | transactional-ESG-cautious |
| schiff-megared | Brand Manager | Schiff / MegaRed (Reckitt) | transactional-nervous |
| consumer-anna | Anna | private Norwegian consumer | neutral-switchable |

## Investors (2)

| id | name | institution | posture |
|---|---|---|---|
| nbim-esg | NBIM ESG analyst | Oljefondet | skeptical-dialogue-seeking |
| sell-side-analyst | Sell-side ESG analyst | DNB/SEB/Pareto (archetype) | transactional-modeling |

## Internal (1)

| id | name | institution | posture |
|---|---|---|---|
| skogrand-aker | Pål Skogrand | Aker BioMarine (Sustainability) | engaged-constructive |

---

## How personas are used

Each persona is one markdown file with YAML frontmatter (`id`, `name`, `role`, `institution`, `archetype`, `cluster`, `posture`) and body sections: **Voice** (rhetorical style), **Primary concerns**, **Signature quotes** (verbatim from public sources), **Talking points**, **Red lines**, **Channel**, **Reaction pattern**, **Provenance** (sources + last_verified date).

The persona-worker reads the whole file and inhabits the voice. The synthesizer never reads persona files directly — it reads only the reaction files.

## Adding a persona

Copy `_template.md`, fill all sections, add a row to this index, verify signature quotes against public sources, set `last_verified`. If you can't find ≥2 signature quotes from public record, the persona is not Mirofish-grade — either find them or don't add it.
