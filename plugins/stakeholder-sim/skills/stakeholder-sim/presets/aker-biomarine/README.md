# Preset — aker-biomarine

A verified persona library for simulating stakeholder reactions to Aker BioMarine (and post-split Aker QRILL Company) press releases. 20 named personas grounded in verbatim public-record quotes, covering the Antarctic krill / NGO / scientist / Norwegian press / investor landscape.

**Last verified:** 2026-04-16. Re-verify persona `last_verified` dates before using for a release dated more than six months after this date.

---

## When to use this preset

The orchestrator auto-loads this preset when:

- The sender identified by `stimulus-analyzer` is Aker BioMarine, Aker QRILL Company, or a related entity (Kori, Lysoveta launch comms, ARK communications)
- The user explicitly requests it: `/stakeholder-sim <file> --preset aker-biomarine`
- The user types natural-language equivalents: "use the Aker preset", "simulate for Aker BioMarine"

When this preset is loaded, Phase 0 (research) is **skipped** — the cast and ground truth come from this directory.

## What's in the preset

```
presets/aker-biomarine/
├── README.md                 # this file
├── ground-truth.md           # corporate structure, CCAMLR-43, products, controversies
├── routing-table.md          # release-type → default cast mapping (Aker-specific)
└── personas/
    ├── _index.md             # human-readable cast overview
    ├── _template.md          # for adding personas to this preset
    ├── christian-asoc.md     # Claire Christian, ASOC
    ├── bengtsson-greenpeace.md
    ├── hammarstedt-seashepherd.md
    ├── allan-bobbrown.md
    ├── werner-pew.md
    ├── savoca-stanford.md
    ├── kawaguchi-aad.md
    ├── brooks-cu.md
    ├── ccamlr-secretariat.md
    ├── fiskeridirektoratet.md
    ├── alberts-mongabay.md
    ├── blindheim-dn.md
    ├── boe-nrk-brennpunkt.md
    ├── seaman-undercurrent.md
    ├── skretting-ceo.md
    ├── schiff-megared.md
    ├── consumer-anna.md
    ├── nbim-esg.md
    ├── sell-side-analyst.md
    └── skogrand-aker.md       # internal counterpart
```

## Cluster distribution

| Cluster | Count | Personas |
|---|---|---|
| Activists | 5 | Christian, Bengtsson, Hammarstedt, Allan, Werner |
| Scientists | 3 | Savoca, Kawaguchi, Brooks |
| Regulators | 2 | CCAMLR Secretariat, Fiskeridirektoratet |
| Press | 4 | Alberts (Mongabay), Blindheim (DN), Bøe (NRK Brennpunkt), Seaman (Undercurrent) |
| Customers | 3 | Skretting CEO, Schiff/MegaRed BM, consumer Anna |
| Investors | 2 | NBIM ESG, sell-side analyst |
| Internal | 1 | Skogrand (Sustainability) |

See `personas/_index.md` for full detail.

## Release-type routing

See `routing-table.md` for the Aker-specific mapping. Covers: `product-launch`, `ccamlr-policy`, `financial`, `bycatch-incident`, `sustainability-report`, `m-and-a`, `general`. When this preset is active, the orchestrator uses this routing table instead of the skill-level generic `routing-heuristics.md`.

## Swapping personas in/out

The orchestrator proposes a cast from the routing table during Phase 1 (plan). You can edit the cast before approving: "drop Seaman, add NBIM", "skip the scientists, add two more journalists". The plan step is where that happens — no need to edit the preset files.

## Source material

The personas are derived from public-record quotes and statements. Signature quotes are verbatim where URLs are cited. Full source list and methodology in the build-out documentation in the source repository (not shipped with the plugin). Each persona file has its own `provenance` block with URLs.

## Extending

To add a persona: copy `personas/_template.md` to `personas/<new-id>.md`, fill every section, verify ≥2 signature quotes against public sources, update `_index.md`, update `routing-table.md` if the persona should be in any default cast.

To build a new preset for a different company: copy this entire directory to `../<new-preset>/`, replace the persona files and ground-truth, update the routing table, and the orchestrator will detect the new preset. No code changes required.

## What this is not

This is not a legal record and it is not fact-checked. The ground-truth file represents "what is publicly known" as of 2026-04-16. Personas treat it as background, not as adjudicated truth. Use the simulation as a pressure test, not as a prediction or as evidence.
