# R02 existing proof audit, first pass

R02 is active at one execution turn of its planned three. The sealed source
requirements are unchanged. This pass reviews existing W1 admission and
accounting statements for M004, M005, M009 and M013. It adds no mechanism-lang
declaration and closes no frozen model obligation.

[proof-audit.json](../proof-audit.json) retains all 83 model obligation IDs and
their sealed R03-R08 assignments. Four have a first witness review; 79 remain
unreviewed. Every acceptance criterion has an explicit disposition. Outstanding
audit work is distinct from an established proof gap: a criterion marked
`unreviewed` may already have a suitable theorem elsewhere in the corpus.

## Reviewed statements and remaining audit work

| Obligation | Existing evidence reviewed | Remaining audit |
|---|---|---|
| M004 | General held-slot denial, arbitrary finite pool occupancy bound and conservation. | Total-pool saturation implies refusal in every indexed admission branch, including modules 37 and 39. |
| M005 | General local unowned no-op, duplicate terminal idempotence, arbitrarily old generations and all five terminal reasons. | Indexed receipt ownership, unrelated-slot preservation and whole-pool baseline restoration for every terminal branch. |
| M009 | General source-system trace slot bound and protected-cell eviction. | Re-registration, multiple-prefix attribution, restart/epoch lifetimes and shared T4b/T8 debt/ban retention. |
| M013 | General aggregate burst-plus-trusted-ticks envelope and a closed two-swarm reuse example. | Distinct source/prefix time envelopes, IPv4/IPv6 attribution, fresh identities, trusted traffic and unvalidated victim-address rejection. |

The census contains 991 explicit proof declarations across 57 modules, using the
existing catalog classifier. Counts describe the pinned corpus, not the number
of discharged requirements. Exact statements are copied from their declarations
by a local transformation and checked against the current source. Whole-module
hashes also pin definitions and proof bodies. Each reviewed witness records its
scope kind, established property, premises and limits. The aggregate rate theorem
requires initial credits at most the burst and counts authoritative trusted
ticks. The two-swarm reuse theorem fixes its trace, initial state and numerical
parameters; it receives no general coverage credit.

## Checks and boundary

`make audit` checks the scope/ledger pins, complete corpus census, every model
obligation and acceptance-criterion index, exact proof statements, scope labels,
premise records and pinned semantic-control definitions. `make audit-regression`
rejects stale pins, missing criteria, helper references, finite-only credit,
closed statements labeled general, altered controls and unsupported R02 closure.
It also rejects unknown scope or status labels, missing witness or criterion
text and duplicate criterion witnesses.
The model checker includes these inputs and the audit summary in its receipt.
CI runs the audit regressions alongside the existing source and scope controls.

These checks establish provenance and bookkeeping. Reviewers must still assess
semantic entailment, whether each scope label is correct and whether recorded
premises suffice. Arbitrary trace results, general transitions, conditional
liveness and finite examples have separate scope labels. A witnessed criterion
does not close an obligation until the complete sealed scope is reviewed and
witnessed with weakening controls. The first-pass records leave that scope open.

`python3 -I tools/audit.py --require-complete` exits 2 while full model witness
coverage is incomplete. The existing full-qualification command retains its
implementation and deployment requirements. All 43 external obligations remain
open, and R02 remains active. The next pass must review the indexed admission
bridges and continue through the remaining W0-W9 obligations before R02 closure.
