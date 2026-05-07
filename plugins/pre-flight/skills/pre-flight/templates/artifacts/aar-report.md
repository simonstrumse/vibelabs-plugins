# Artifact: After-Action Review (AAR)

The central `crisis-tabletop` deliverable. Edelman/APCO tabletop-convention format. 3-8 pages typical. Findings + recommendations + playbook updates.

## Structure

```markdown
# After-Action Review — <stimulus title>

**Run:** <run-id> · **Tabletop date:** <ISO> · **Severity:** <high / critical> · **Rounds:** <2 or 3> · **Personas consulted:** <n>

## 1. Executive summary

(3-5 bullets)
- **Net outcome of the tabletop:** <one sentence — narrative hardened / softened / held>
- **Largest single risk surfaced:** <one sentence>
- **Largest opportunity surfaced:** <one sentence>
- **Top 3 playbook updates required:** <list>
- **Readiness assessment:** the team is <ready / mostly ready with specific gaps / not ready> to manage this scenario in reality.

## 2. Scenario and scope

(1-2 paragraphs)
- The stimulus tested, the cast consulted, the rounds run, the injects used (if any).
- Boundary of what was tested and what was deliberately out of scope.

## 3. Findings

Organized around the AAR convention: narrative arc, decision points, stakeholder response, playbook gaps.

### 3.1 Narrative arc
- **Where the story began** (Round 1 net posture): <one paragraph>
- **Where the story went** (Round 2 → 3 movement): <one paragraph>
- **Where the story landed** (final state): <one paragraph>
- **Key inflection points:** <2-3 moments when the narrative shifted, each named with cause>

### 3.2 Decision points — what we did, what we should have done
For each material decision the company proxy (or the comms lead in the room) faced during the tabletop:
- **Decision point <n>:** <description>
- **Company took:** <action>
- **Stakeholder read of that action:** <aggregate reception + key persona quote>
- **Better call (if applicable):** <alternative action + why, grounded in personas who would have responded better>

### 3.3 Stakeholder response — cluster by cluster
- **Activists:** <aggregate posture trajectory + key quote + coalition signal>
- **Scientists:** <...>
- **Regulators:** <...>
- **Press:** <...>
- **Customers:** <...>
- **Investors:** <...>
- **Internal:** <...>
- **Peer companies:** <...>

### 3.4 Coalition dynamics
- **Who aligned:** <grounded in social-dynamics phase>
- **Who opposed:** <grounded in debate phase>
- **Persuadable / undecided:** <who's in play and what would move them>

## 4. Playbook updates — what to change

Specific, actionable updates to existing crisis playbooks:

1. **<playbook section>:** <current state> → <proposed update> — motivated by <which finding from §3>.
2. **<playbook section>:** ...
3. ...

(Cap at 8. More than 8 = playbook needs a rewrite, not updates.)

## 5. Readiness assessment

Per the AAR convention, a direct answer to: is the team ready to manage this in reality?

- **Ready:** <yes / no / partial>
- **Specific capability gaps surfaced:**
    1. <gap + how to close it>
    2. <gap + how to close it>
- **Next rehearsal recommendation:** <when to run again, with which variations>

## 6. Quote appendix — stakeholder voices

For each cluster, the 2-3 quotes that most defined the cluster's posture across rounds. Each attributed (persona name, institution, round number, verbatim from reaction file).

## Length target

2500-4000 words depending on rounds and cast size.
```

## Grounding rules

- Every "finding" grounded in a specific persona reaction or social-dynamics/debate transcript.
- Decision-point analysis cites specific personas whose reactions support the "better call" recommendation.
- Playbook updates must be concrete (name the section, name the change), not abstract.
- Readiness assessment is direct. "Partial" is OK; hedging ("it depends...") is not useful.
- Quote appendix quotes are verbatim from findings files — `verify_quotes.py` will check.
