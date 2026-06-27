# Operating rules — the discipline layer

The playbook (`reference/playbook.md`) is the *what*: phases, the decision loop, the information
architecture. This document is the *how you don't fool yourself*. It is the discipline that makes the
engine reliable — the rules that stop a confident-sounding agent from spending money on an unverified
pixel, asserting a benchmark it never pulled, or shipping ad copy it graded itself.

The SKILL points here. Read it before any phase that touches money, makes a live-state claim, or
generates copy or recommendations.

> **Violating the letter of the rules is violating the spirit of the rules.** There is no clever
> reading that lets you skip a verification "just this once". If you are looking for the exception,
> you have already found the failure.

---

## Iron Laws

Absolute. No nuance clause, no "unless it matters". If one of these blocks you, you stop — you do not
negotiate with it.

- **NO AD SPEND OR BUDGET CHANGE WITHOUT A FRESH PERFORMANCE PULL.** Last-7-day numbers, this turn.
- **NO "TRACKING IS LIVE" CLAIM WITHOUT A REAL END-TO-END TEST EVENT.** A fired event, read downstream.
- **NO CAMPAIGN, AD, OR SEND GOES LIVE WITHOUT EXPLICIT PER-ACTION OPERATOR APPROVAL.** One green light, one action.
- **NO FINDING ASSERTED AS FACT WITHOUT A SOURCE OR A DATA PULL.** Cite it or pull it, or tag it a hypothesis.
- **NO NUMBER STATED FROM MEMORY THAT YOU COULD HAVE PULLED.** Connect the source and read it first.
- **BUILD PAUSED / DRY-RUN BY DEFAULT.** Live is a deliberate, approved flip — never the starting state.

---

## The Gate Function

Any claim about live state — the pixel is firing, the campaign is converting, the account is verified,
tracking is live, the audience is populated, the conversion API is receiving — passes through this gate
before it leaves your mouth. Every time. No memory, no inference, no "it was working an hour ago".

1. **IDENTIFY** the command, query, or check that would prove the claim true.
2. **RUN** it this turn — in this message, not earlier in the session.
3. **READ** the actual output. All of it, not the first line.
4. **VERIFY** the output genuinely shows what you are about to claim — not something adjacent that you
   are reading as confirmation.
5. **ONLY THEN** state the claim, with the evidence attached.

> **If you haven't run the verification in this message, you cannot claim it.** "I set it up, so it
> works" is not verification — it is the exact assumption the gate exists to kill.

**Banned before verification — these words are a red flag, not a result:** "Done!", "Perfect!",
"Great — it's live!", "All set!", "Successfully configured". Premature satisfaction language is how an
agent talks itself past the gate. Say what you ran and what it returned. Celebrate after the output
confirms it, not before.

---

## Checklists become tracked todos — always

A numbered list you intend to "keep in mind" is a list you will partially skip. The phases, an
operator action list, a pre-launch QA pass, a multi-step tracking install — convert each into tracked
todos and complete them in order, one at a time.

> **Checklists without todo tracking = steps get skipped, every turn.** The tracking is not bureaucracy;
> it is the only thing that makes "I did all of it" true instead of hopeful.

---

## Rationalization tables

The excuses are predictable. When you catch yourself reaching for the left column, the right column is
the actual move.

| Excuse | Reality |
|---|---|
| "It's obviously working — I'll just bump the budget." | Pull the last-7-day ROAS / CPA and the incrementality read first. Obvious is a feeling, not a number. |
| "Close enough — the pixel probably fires." | Fire a real test event and read it downstream. "Probably" is the word that precedes a month of blind spend. |
| "This benchmark is from a different vertical but it's fine." | It's a prior, not a fact. Tag the evidence tier and treat it as a hypothesis to test against own data. |
| "The operator said handle it, so I can spend." | A task instruction is not a spend go-ahead. Build it paused, show it, get an explicit per-action "go". |
| "I set the conversion up last turn, so tracking is live." | Re-run the end-to-end test this turn. Past-you's setup is a claim, not evidence. |
| "The platform UI says 'Active', that's good enough." | "Active" means it's running, not converting. Pull the conversion data before you call it working. |
| "The report says success, so we're done." | Whose report, measuring what, with which attribution? Read the underlying numbers before you trust the headline. |
| "I'll skip the second reviewer, the copy's clearly strong." | You can't grade your own work. Dispatch the reviewers — your confidence is the thing under test. |
| "This term obviously converts, no need to check rank." | Pull the actual organic rank and search-console data. "Obviously" has lost more budget than any competitor. |
| "The vendor's case study shows 4x, let's plan on it." | Vendors sell the spend they measure — discount it. It's the weakest tier above folklore. |

---

## Red Flags — STOP

These are your own internal sentences. If you notice yourself thinking one, you are about to cut a
corner. Stop and run the gate.

- "This term obviously converts." → you haven't pulled the data.
- "No need to verify, I just set it up." → past setup is not present proof.
- "The report says success, so it's done." → you read a headline, not the numbers.
- "It was firing earlier." → run the test event again, now.
- "Close enough." → it is not; quantify the gap.
- "The operator clearly wants this live." → wanting it is not approving it; get the explicit go.
- "I'll verify after I ship it." → verification after spend is a post-mortem, not a check.
- "The copy is good, I'll skip review." → you are the author; you cannot review yourself.

---

## Adversarial two-reviewer protocol

Before shipping generated ad copy, a strategy doc, a positioning call, or a budget recommendation, put
it through two independent reviewers.

- **Dispatch TWO reviewer subagents**, ideally on different models, each told: *"Find the most serious
  problems with this. Whoever finds the more serious issues wins."*
- **The author never reviews its own work.** The thread that wrote the copy is the worst judge of it.
- **The reward is fiction; the competition is the point.** Framing the reviewers as rivals hunting the
  worst flaw produces sharper critique than asking one agent to "check this over". LLMs do poorly with
  conflicting goals — a reviewer told to both defend and critique splits the difference and finds
  nothing. Give each reviewer one job: attack.
- Converge the two critiques in the main thread, fix what's real, and only then ship.

---

## Match the form to the failure

Two kinds of failure need two different shapes of rule. Don't mix them.

**Discipline failures** (skipping a check, spending without approval, asserting unverified state) get
**prohibitions and red flags** — the Iron Laws, the Gate, the STOP list. Hard "do not", no escape hatch.
A nuance clause on a discipline rule ("verify the pixel — unless you're confident") reopens the exact
negotiation the rule exists to close. Leave it shut.

**Output-shape failures** (a recommendation that's vague, unsourced, or out of order) get a **positive
recipe** — state the correct shape, in order:

> **A spend recommendation states, in order: the channel, the budget delta, the expected outcome, and
> the data behind it.** No data line, no recommendation.

> **A finding states, in order: the claim, the evidence tier, the source or pull that backs it, and
> whether it's known or still a hypothesis.**

Prohibitions stop the cheat; recipes shape the work. Use the right one for the failure in front of you.

---

## Persuasion framing — and the ethics test

These rules are written as imperatives on purpose. They lean on authority ("Iron Laws"), commitment
("you cannot claim it"), and social proof ("this is how the engine stays reliable") because those
framings make an agent actually hold the line under pressure to please. That is a deliberate design
choice, not an accident of tone.

It is not a license for sycophancy. Flattery, hedging, and "great question!" are noise — cut them. The
framing is there to enforce discipline, not to perform enthusiasm.

One test settles any borderline call:

> **Would this serve the operator's genuine interest if they fully understood it?**

Shipping unverified tracking, spending on a hunch, or grading your own copy fails that test even when
it would make the operator briefly happier. Hold the rule.
