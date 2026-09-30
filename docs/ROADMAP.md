# Proof repository completion roadmap

The target is completion of this proof repository within **50 execution turns**:
40 planned turns and 10 reserve turns. An execution turn is one user-requested
proof-work iteration, including its implementation, validation and repair. The
budget starts with R01 after this planning refactor. It is a target that must be
checked after scope sealing, rather than a guarantee about unknown proof gaps.

The authoritative closure checklist is [proof-roadmap.json](../proof-roadmap.json).
[Coverage](COVERAGE.md) reports closed packets, turn use and the current proof
corpus. Existing theorems receive credit through the obligation audit in R02;
the slice number is not a completion metric.

## Definition of proof repository completion

Completion requires all ten packets below to close with audited evidence:

- Every pinned normative source clause has a reconciled disposition: a model
  obligation, a sourced external implementation/deployment obligation, or a
  justified context/superseded entry. Every in-scope clause has a fixed atomic
  obligation and theorem witnesses at the required scope.
- The pinned mechanism-lang checker accepts all required model proofs, discloses
  no axioms and rejects the required semantic mutations. Assumptions and
  conditional liveness premises remain explicit.
- A reproducible proof-package gate checks semantic and model coverage, source
  provenance, proof evidence and the completed closure checklist.
- The external-obligation ledger retains the source references, required
  evidence and acceptance criteria for Rust refinement, deployment measurements
  and operator decisions. Proof-package completion leaves those obligations open.

The broader [full qualification roadmap](FULL-QUALIFICATION-ROADMAP.md) preserves
the existing model-progress record and deployment backlog. `make qualify` still
requires full implementation and deployment qualification. Its blocked status is
independent of this proof-only plan.

## Fixed closure packets

| Packet | Planned turns | Turn window | Result required before closure |
|---|---:|---|---|
| R01 | 5 | 1-5 | Reconciled semantic ledger, fixed model scope and checked source dispositions. |
| R02 | 3 | 6-8 | Existing proof census, theorem-to-obligation audit and exact remaining gaps. |
| R03 | 5 | 9-13 | Admission, callback ownership, source attribution, shared limits and rate/cost accounting. |
| R04 | 5 | 14-18 | Policy receipts, churn/expiry, resource transitions, recovery and all required tiers. |
| R05 | 5 | 19-23 | Queue/capacity/schedule composition and general state, cost and service witnesses. |
| R06 | 4 | 24-27 | Poll/cancellation continuations, cleanup, priority and conditional cumulative service. |
| R07 | 4 | 28-31 | Authentication boundaries and modeled optimization equivalence with explicit crypto premises. |
| R08 | 4 | 32-35 | Remaining W0-W9 abstractions, external dispositions and an empty model-gap list. |
| R09 | 3 | 36-38 | Assumption/completeness audit, full mutation run and qualification-guard regression. |
| R10 | 2 | 39-40 | Reproducible proof-package gate, final documentation and evidence handoff. |
| Reserve | 10 | 41-50 | Named proof or validation repairs inside the sealed scope. |

Detailed exit criteria and dependencies are in `proof-roadmap.json`. A packet's
`planned_turns` is its allocation; `turns_spent` records actual execution turns,
including failed attempts and repair. The sum of actual turns includes reserve
use. Keep packet identifiers and the ten-packet denominator fixed. Within-packet
subtasks can change without creating a new milestone or dropping an obligation.

## Execution rules

1. Finish R01 before adding new model domains. Classify the complete pinned
   source set, reconcile original/modified requirements and freeze the atomic
   obligation list. External dispositions must follow the proof-only boundary;
   difficulty is not a reason to reclassify a model obligation.
2. Reuse the existing proof corpus in R02. Close all obligations covered by each
   general theorem. Add a helper, finite example or compatibility lemma only
   when it is required by a frozen obligation or a weakening counterexample.
3. Work against one packet's exit criteria each turn. Batch related proof gaps
   and validate the resulting model composition. End with the closed obligation
   IDs, remaining gaps, exact validation evidence and actual turn count.
4. Set `status` to `closed` only after every exit criterion has been audited.
   Each evidence entry records the zero-based `criterion`, a repository-relative
   `path` and its `sha256`. The coverage generator checks these references and
   prerequisite closure. Hashes establish freshness; reviewers still assess
   whether the evidence satisfies the criterion.
5. Keep semantic completeness false until an exhaustive disposition checker
   establishes it. Current catalog/check hard-coded incomplete flags are a
   specific R01 task, not permission to flip a status field. R10 adds the
   proof-only terminal gate; the full qualification guard keeps its meaning.
6. Inspect the remaining gap list at turns 5, 8, 23, 35 and 40. Charge overruns
   against the ten-turn reserve and revise later allocations within 50 turns.
   A change to the sealed scope requires an explicit new baseline. If the
   remaining obligations exceed the reserve, report the named blocker and missed
   target instead of declaring completion or silently weakening the scope.

Regenerate coverage with `python3 -I tools/catalog.py` after updating the closure
checklist. The reported percentage is closed packets divided by ten. It measures
this fixed proof-package checklist, not total effort or deployed Telcoin safety.
