# Artifact: Counterfactual delta

The central `counterfactual-compare` deliverable. Full cross-draft comparison with side-by-side tables, per-dimension winners, cluster narratives, quote comparison, recommended path forward. Output of the `counterfactual-comparator` agent.

## Structure

```markdown
# Counterfactual delta — <stimulus title>

**Run:** <run-id> · **Mode:** counterfactual-compare · **Drafts compared:** <n> · **Cast size:** <n> · **Total reactions:** <drafts × cast>

## 1. Delta table — per cluster

| Cluster | Draft A | Draft B | Draft C | Draft D | Winner | Margin |
|---|---|---|---|---|---|---|
| Activist | <sentiment / trust Δ / would_act %> | ... | ... | ... | <letter> | clear / narrow / tied |
| Scientist | ... | ... | ... | ... | ... | ... |
| Regulator | ... | ... | ... | ... | ... | ... |
| Press | ... | ... | ... | ... | ... | ... |
| Customer | ... | ... | ... | ... | ... | ... |
| Investor | ... | ... | ... | ... | ... | ... |
| Internal | ... | ... | ... | ... | ... | ... |
| Peer-company | ... | ... | ... | ... | ... | ... |

## 2. Per-dimension winners

- **Highest trust-lift across cast:** Draft <letter> — cast-wide trust delta: +<X>
- **Fewest red-line crossings:** Draft <letter> — <n> crossings vs <n+1> in next-best
- **Largest supportive coalition:** Draft <letter> — <n> personas with would_act: yes + sentiment supportive
- **Strongest message-house roof:** Draft <letter> — signature roof phrase: "<extraction>"
- **Clearest differentiation from competitor framing:** Draft <letter> — per <peer-company persona>

## 3. Cluster-by-cluster narratives

### Activist cluster (n=<n>)

**Draft A:** <one-paragraph reading with at least one verbatim quote>.
**Draft B:** <reading with quote>.
**Draft C:** <reading with quote>.
(Per draft count.)

- **Cluster winner:** Draft <letter>. **Why:** <one sentence with quote>.
- **Cluster risk across all drafts:** <red-line crossings common to ≥2 drafts, if any>.

### Scientist cluster
(...same structure...)

### Regulator cluster
### Press cluster
### Customer cluster
### Investor cluster
### Internal cluster
### Peer-company cluster

## 4. Quote-comparison highlights

The signature lines each draft produced across all cluster reactions:

- **Draft A strongest supporting quote:** <persona (institution)>: "<quote>"
- **Draft A worst hostile quote:** <persona>: "<quote>"
- **Draft B strongest:** ...
- **Draft B worst:** ...
- (Per draft.)

## 5. Recommended draft + revisions

**Recommended:** Draft <letter>.

**Why:** <2-3 sentences — which dimensions it wins, where the margin is clearest, why the alternatives fall short>.

**Weaknesses the next revision must address:**
1. <weakness grounded in specific persona reaction to this draft>
2. <weakness>
3. <weakness>

## 6. Elements to borrow from other drafts

For a revised Draft <letter>:

- **From Draft <X>:** <specific phrase or framing to borrow> — because <why it works per personas>.
- **From Draft <Y>:** <specific phrase> — because <why>.

## 7. Proposed synthesized draft (optional)

<Only include if the pattern of wins suggests a clean combination. 2-3 paragraphs sketching the synthesized draft with specific borrowings from each. If no clean combination exists — omit this section. Honesty > forced synthesis.>

## 8. Coverage gaps

Dimensions where all drafts produced similar reactions — these aren't discriminated between drafts. Signal: the question being tested isn't well-addressed by any draft.

- <dimension where all drafts tied>: <reason it's not being discriminated — e.g. "all drafts are silent on X; no persona distinguishes on this axis">
- ...

## Length target

~2000-2500 words for 3 drafts × 12 personas.
```

## Grounding rules

- Every per-cluster reading quotes at least one persona per draft.
- Winners declared, not hedged. Tie = "tied"; no draft wins = "no draft wins" (with elements-to-borrow as the productive output).
- No invented quotes. Every quote traces verbatim to a specific reaction file across the drafts.
- Proposed synthesized draft is OPTIONAL. Forced Frankenstein drafts are worse than honest "pick B and revise."
- Coverage gaps section mandatory. Drafts tying on a dimension is informative — don't hide it.
