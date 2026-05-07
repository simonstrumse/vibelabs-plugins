# Mode index

Canonical enum of published modes. The scoping-designer may only pick a `mode.name` from this list. Unknown modes are rejected by the orchestrator.

| Mode | Status | Benchmark workflow | Typical cast size |
|---|---|---|---|
| `crisis-pre-flight` | ✅ shipped | Pre-flight messaging review; Edelman 2-hour crisis sim short-form; FGS quarterly red-teaming | 12 |
| `crisis-tabletop` | ✅ shipped | Full tabletop exercise; H+K FlightSchool+ full; Polpeo 3-hour live; Hoover Wargaming & Crisis Simulation Initiative | 16 |
| `launch-pre-mortem` | ✅ shipped | Launch pre-mortem; launch messaging review | 10 |
| `regulatory-response` | ✅ shipped | Regulatory response playbook; APCO public-affairs practice | 12 |
| `deal-comms` | ✅ shipped | Transaction communications; Brunswick Capital Markets; FGS transaction/financial comms | 12 |
| `earnings-rehearsal` | ✅ shipped | Earnings rehearsal; mock analyst Q&A; NIRI playbook | 8 |
| `positioning-pressure-test` | ✅ shipped | Rebrand diagnostic; Interbrand/Lippincott/Siegel+Gale pre-rebrand workshop; RepTrak scorecard lens | 10 |
| `counterfactual-compare` | ✅ shipped | A/B message test; counterfactual draft review | 12 |
| `red-team-read` | ✅ shipped | Red team read; US DoD origin; Wag The Dog corporate adaptation | 8 |
| `activist-proxy` | ✅ shipped | Shareholder activism / proxy-fight response; Brunswick/FGS distinct practice | 10 |
| `exec-transition` | ✅ shipped | CEO succession / exec-transition | 10 |
| `internal-first` | ✅ shipped | Layoffs / RTO / restructuring; IABC Handbook cascade | 12 |

## Severity parameter (crisis modes only)

Optional overlay on `crisis-pre-flight` and `crisis-tabletop`. Maps to UK civil-contingencies Gold/Silver/Bronze if the buyer asks, but is not a mode itself.

- `low` / Bronze — operational, one channel at risk
- `medium` / Silver — tactical, multi-channel
- `high` / Gold — strategic, enterprise-level
- `critical` — ongoing acute crisis

Severity affects: cast size (higher = larger), phase composition (high/critical never skip critic, debate, or social-dynamics even if mode default drops them), and factbase freshness window (critical = 7 days, high = 14, medium/low = 30).

## Ship status legend

- ✅ shipped — mode is runnable end-to-end with all phases, artifacts, and the mode-keyed report skeleton.

All 12 modes are now shipped (v1.0.0). The scoping-designer can compose any of them.
