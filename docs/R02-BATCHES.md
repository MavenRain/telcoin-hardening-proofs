# R02 completion in five total execution turns

The user set a cap of five total R02 execution turns on 2026-10-01. Turns 1 and
2 already established the census and reviewed indexed admission witnesses. The
remaining obligations are grouped by their frozen R03-R08 closure assignments.
Each batch is one execution turn, including validation and repair. Subtasks and
tool calls do not count as separate execution turns.
The cap is an upper bound: combine the remaining batches and close earlier if
every R02 exit criterion is satisfied.

| R02 turn | Frozen packets reviewed | Obligations | Exit |
|---|---|---:|---|
| 1-2 | Initial census and indexed admission | 4 initially reviewed | Historical receipts retain their original scope. |
| 3 | R03 admission/ownership/rate and R04 policy/churn/recovery | 36, including the original 4 | Complete: 32 new reviews; M009/M013's remaining criteria classified; no unreviewed R03/R04 criterion. |
| 4 | R05 composition, R06 service/cleanup and R07 authentication/optimization | 25 | Complete: 51 criteria classified; bounded outcome-independent poll work witnessed; exact composition, service and authentication gaps retained. |
| 5 | R08 remaining abstractions and R02 closure | 22 | Complete: 44 criteria classified; all 83 obligations reviewed; per-criterion evidence audited and R02 closed. |

The three remaining-turn groups are disjoint and cover all 83 frozen model
obligations. Turn 5 completes the final 22 R08 reviews and classifies all 44
remaining criteria. All 83 obligations are reviewed, with zero unaudited
criteria. The original R02 planned allocation stays three turns in
`proof-roadmap.json`; turns 4 and 5 use two of the ten reserve turns.
The overall 50-turn target and the ten closure-packet denominator stay
fixed. Actual `turns_spent` is incremented once per execution turn.

For each batch, inspect the exact statement and the relevant model definitions.
Record quantifiers, initial-state invariants, validation/clock authority and
cost/scheduling premises. Distinguish finite examples, general transitions,
arbitrary traces and conditional liveness. A partial general statement receives
only its actual scope. Missing model transitions, attribution bridges or
composition statements remain explicit model gaps; they are not reclassified
as external obligations. Add no new proof domain while doing the witness audit.

Turn 4 includes poll/cancellation cleanup and conditional service, not merely
queue safety. It must inspect authentication and optimization equivalence
premises as well as the existing composition corpus. Turn 5 covers the remaining
W0-W9 abstractions and checks that every gap is routed to R03-R08 without changing
the sealed source clauses or obligation assignments.

R02 closes only when `witness_audit_complete` is true, all 83 obligations are
reviewed, zero criteria remain `unreviewed`, and the evidence satisfies each
R02 exit criterion. Exact gaps may remain for R03-R08. `model_coverage_complete`
and full implementation/deployment qualification remain separate gates. The
existing `audit.py --require-complete` command requires complete model coverage,
so its blocked exit does not by itself mean the R02 witness census is unfinished.

Each turn runs the audit validator and its weakening regressions, reconciles
the generated inventory/coverage, and records commands, outcomes and input
hashes in a new batch receipt. Reuse compiler/mutation evidence only when every
relevant input matches the earlier receipt, and label that evidence as reused.
The final turn checks prerequisite closure and records fresh per-criterion R02
evidence hashes. Budget use alone never closes the packet.
