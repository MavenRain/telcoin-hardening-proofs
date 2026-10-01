# Evidence still required
R01 now seals all 1,383 source dispositions and the 83 model/43 external
obligations in [proof-scope.json](../proof-scope.json). See the
[closure audit](../docs/R01-CLOSURE.md) and
[checked receipt](../evidence/r01-closure-check.json). Earlier batch receipts
record their historical snapshots. R02 must still audit exact theorem witnesses;
implementation and deployment evidence remains outstanding.



No runtime or deployment result has been supplied or synthesized. The `.build`
report records local model checking only. The current complete-qualification
command rejects all implementation and deployment certification.

`source-disposition-check.json` records the current pinned source-disposition
links and the exact pending remainder, which is now zero.
`t2-t5-source-audit-model-check.json` records the full proof/mutation run and
blocked-qualification regression after the fourth R01 audit batch. That batch
audited the original T02/T05 drafts and selected revised requirements, and
retained twelve model and twenty-two external obligations. It assigned no
theorem witnesses or new proof credit. Candidate implementation links were not
checked in that run. The fifth turn reviewed the remaining source units and
closed R01. See `r01-closure-check.json`.

`initial-model-check.json` preserves the first model-checking receipt.
`trace-model-check.json` records the expanded transition proofs, atomic ledger,
semantic mutation checks and validation of the pinned implementation file hashes.
`portable-bootstrap-model-check.json` repeats that validation after fixing fresh
GitHub bootstrapping to fetch only the compiler's required Veil submodule.
`policy-model-check.json` records versioned policy and receipt proofs, mixed
resource traces, their negative controls and the pinned implementation source links.
`source-table-model-check.json` records bounded source-table churn, preservation
of existing security state, four additional atomic obligations and 15 additional
semantic mutation checks. It was produced without `--implementation`, so its
`implementation_links` status is `not_checked_this_run`: that run did not compare
the pinned implementation file hashes.
The earlier receipts carry `source_links_checked`, most recently
`policy-model-check.json` (revision 579aa551fe39593e32a48e1dbcfeccbccab64e3e,
6 entries). To restore the check, run `python3 -I tools/check.py --implementation
/path/to/telcoin-network` against a checkout at that revision and copy
`.build/report.json` over the receipt being refreshed.
`source-enforcement-model-check.json` records bounded per-source charging,
simultaneous restrictions, independent trusted expiry, four new atomic
obligations and 27 new semantic mutation checks. It also has
`implementation_links: not_checked_this_run`. That receipt covers 264 proof
declarations, 44 atomic obligations and 90 rejected negative checks. Those two
source receipts do not establish keyed-table/global-resource composition.
`source-system-model-check.json` records keyed lookup and mixed source-table
churn, charging, bans and expiry, with four new atomic obligations and 18 new
semantic mutation checks. It covers 293 equality and order proof declarations,
48 atomic obligations and 108 rejected negative checks. Its
`implementation_links` status is also `not_checked_this_run`. That receipt
covers source-system composition alone.
`source-admission-model-check.json` records atomic admission across source quota,
shared credits and pending ownership, indexed internal receipts, mixed trace
bounds, four new atomic obligations and 32 new semantic mutation checks. It
covers 344 equality and order proof declarations, 52 atomic obligations and
140 rejected negative checks. Its `implementation_links` status remains
`not_checked_this_run`. That receipt covers state bounds and indexed lifecycle
behavior, before adding a coupled cumulative rate bound.
`source-admission-rate-model-check.json` records receipt-counted accepted starts,
shared-credit conservation, a discrete burst-plus-rate envelope and its per-start
cost bound. It includes four new atomic obligations and 25 new semantic mutation
checks, covering 366 equality and order proof declarations, 56 atomic obligations
and 165 rejected negative checks. Its `implementation_links` status remains
`not_checked_this_run`. Real clock correspondence, dominance of the supplied
per-start cost weight over real accepted-start work, rejected-attempt cost, live
per-source pending attribution, established-resource integration,
configuration changes, timer validation, restart persistence and deployment
qualification remain open.
`indexed-source-admission-model-check.json` extends the lifecycle guarantees to
arbitrary pending indices, including exact admission receipts and accepted-start
counting, matching completion, stale and duplicate callbacks, and held or missing
slot refusal. It adds 21 equality proof declarations, four atomic obligations
and 16 semantic mutations (module-39 theorems reject 11 of them, and older
pool-capacity proofs reject five), bringing the totals to 387 proof declarations
across 24 modules, 60 atomic obligations and 181 rejected negative checks. Each new
mutant also type-checks through its changed definition before a theorem rejects
it. The receipt's `implementation_links` status is `not_checked_this_run`.
Stable runtime indices, internal receipt provenance, atomic callback behavior
and machine generation arithmetic still require refinement; this receipt does
not establish deployment qualification.

`policy-source-admission-model-check.json` records receipt-gated policy/source
composition, exact indexed admission and counting, publication without resource
resets, and inherited state, rate and cost bounds over mixed traces. It adds 31
equality and order proof declarations, four atomic obligations and 19 semantic
mutations, bringing the totals to 418 declarations across 25 modules, 64 atomic
obligations and 200 rejected negative checks. Every new mutation type-checks
through its changed definition before a module-41 theorem over variables rejects
it. The receipt is from a run without `--implementation`, so its implementation
links are `not_checked_this_run`. This closes the abstract policy/source
composition gap left by the earlier source receipts. Runtime receipt provenance,
atomic publication and enforcement, authoritative inputs, real clock and cost
correspondence, established resources and deployment qualification remain open.


These are reproducible local receipts within the trust boundary described in
[TRUST.md](../docs/TRUST.md), not deployment measurements or external attestations.

The authoritative run requirements are in
[the acceptance specification](../sources/w1-modified/04-DECISIONS-AND-ACCEPTANCE.md).
Each future run needs exact implementation/dependency/configuration identities,
accepted thresholds, hardware and host settings, topology, offered and accepted
load, traffic generation details, raw metrics, instrumentation overhead, test
duration, failures and uncertainty. Include the firewall state and all swarms.

Gate 1 covers the maintained Retry feature. Gates 2 through 6 additionally cover
resource/timeout settings, resilience, topology/transaction paths, operations
and storage. A feature-level result does not satisfy the remaining gates.

Operational evidence remains an explicit environmental assumption even when a
formal model proves that its recorded values satisfy an acceptance predicate.

`policy-work-model-check.json` records the independent policy-work budget and its
composition with policy/source admission. It adds four atomic obligations,
27 explicit equality/order declarations and 27 negative controls. The resulting
bundle has 445 declarations across 26 modules, 68 atomic obligations and
227 rejected negative checks. The work envelope counts processed attempts and
publications even when denied; the combined cost result uses supplied symbolic
weights and preserves the accepted-start envelope. Implementation links are
`not_checked_this_run`. Guard, receipt-production, maintenance and completion
costs, receipt provenance, runtime refinement, clock correspondence, established
resources and deployment qualification remain open.

`policy-ingress-model-check.json` records budgeted internal policy queries and
their state-dependent composition with policy/source admission. It adds four
atomic obligations, 24 equality/order declarations and 20 negative controls.
The resulting bundle has 469 declarations across 27 modules, 72 atomic
obligations and 247 rejected negative checks. Queries use the current policy
view and attempted identity only when work credit is available; authentication
denials consume work credit without changing resources or producing an admission
receipt. Mixed traces retain the pending-capacity and combined cost bounds.
The policy-operation cost weight now assumes it covers query and receipt
production as well as delegated work. Authentication, identity binding, atomic
runtime enforcement and measured cost bounds remain implementation obligations.
Pre-guard work, exhausted guards, maintenance, completion, established resources
and deployment qualification remain open. Implementation links are
`not_checked_this_run`.

`policy-ingress-poll-model-check.json` records the fueled ingress-poll extension.
The bundle has 492 declarations across 28 modules, 76 atomic obligations and
265 rejected negative checks, including 18 new poll mutations. Every dispatched
event consumes fuel; the exact ordered prefix/remainder split, wake requests,
state projection, continuation execution and pending-capacity bound are checked.
Completion and maintenance execute at zero policy work credit if poll fuel
remains. A conditional event-cost term accounts for dispatch and exhausted
guards alongside the prefix policy/handshake cost envelopes.

The receipt is a model-checking result. Concrete per-event cost bounds, queue
construction, pre-dispatch authentication, executor overhead and cleanup
scheduling remain open. Implementation links are `not_checked_this_run`;
full implementation and deployment qualification remains blocked.

`policy-ingress-queue-model-check.json` records persistent FIFO queue service.
The bundle has 515 declarations across 29 modules, 80 atomic obligations and
285 rejected negative checks, including 20 new queue mutations. The model
preserves ordered arrivals and carried state, services any original prefix in
its own length of delivered turns with one unit of fuel each, and connects
repeated service to the actual dispatched trace. The pending-capacity bound
and a combined cost envelope span all those turns without adding a new initial
burst per turn.

This receipt is a model-checking result. Progress is conditional on delivery of
the modeled service turns. Queue memory, enqueue and empty-turn costs, real
wakeups, concurrent producers, other fuel schedules and wall-clock cleanup
latency remain open. Implementation links are `not_checked_this_run`;
full implementation and deployment qualification remains blocked.

`policy-ingress-schedule-model-check.json` records arbitrary finite varying-fuel
service, including zero-fuel turns. The bundle has 536 explicit equality/order
declarations across 30 modules, 84 atomic obligations and 310 rejected negative
checks, including 25 new schedule mutations. It preserves exact queue and state
semantics, derives prefix service from sufficient cumulative delivered fuel,
and retains pending capacity and a combined cost envelope with each initial
burst counted once. The prefix relation carries an exact suffix witness;
supporting relation-valued proofs are checked but excluded from the explicit
equality/order declaration count.

This extends the earlier unit-fuel receipt at the model level. Runtime fuel
delivery, queue memory, enqueue and empty-turn costs, real wakeups, concurrent
producers and wall-clock cleanup latency remain open. Implementation links
are `not_checked_this_run`; full implementation and deployment qualification
remains blocked.


`policy-ingress-overload-model-check.json` records fixed-capacity admission
before each varying-fuel turn, with exact accepted-prefix/rejected-suffix
accounting. The bundle has 559 explicit equality/order declarations across
31 modules, 88 atomic obligations and 331 rejected negative checks, including
21 new overload mutations. Supporting relation-valued proofs are checked but
excluded from the explicit equality/order declaration count. The cap bounds
retained queue entries when the initial queue fits. Filtering preserves fuel,
conditional original-prefix service, exact dispatched-state semantics, pending
capacity and the combined dispatch envelope.

This is an abstract model extension. Entry counts do not bound payload bytes,
offered-batch construction, admission, rejection or queue-storage costs.
Rejected arrivals have no service guarantee, including newly offered cleanup
or control events; safe runtime delivery or loss/retry semantics remain open.
Real fuel delivery, wall-clock latency, concurrent producers, cancellation,
restart and cap changes also require refinement. Implementation links are
`not_checked_this_run`; full qualification remains blocked.

`policy-ingress-payload-model-check.json` records variable immutable payload
charges composed with the queue-entry cap. The bundle has 589 explicit
equality/order declarations across 32 modules, 92 atomic obligations and 351
rejected negative checks, including 20 new payload mutations. Supporting
relation-valued proofs and computational certificates are also checked.
The new slice proves exact arrival partitioning, fitting-head acceptance,
entry and payload bounds across finite schedules, a closed freed-payload
reuse witness,
conditional prefix service, dispatched-state semantics, pending capacity and
the combined execution envelope.

Payload charges need a runtime storage-dominance argument. Offered and rejected
batches, temporary selections, proof certificates, allocator overhead and
charge/admission work are outside the retained-queue budget. Safe delivery of
mandatory events, actual fuel delivery, real-time progress, cancellation,
restart and cap changes remain open. Implementation links are
`not_checked_this_run`; full implementation and deployment qualification
remains blocked.

`policy-ingress-scan-model-check.json` records a separate bounded admission
scan before payload and entry filtering. The bundle has 612 explicit equality
and order declarations across 33 modules, 96 atomic obligations and 370 rejected
negative checks, including 19 new scan mutations. Relation-valued proofs and
computational helpers are also checked.

The new slice proves the exact accepted/rejected/unexamined partition, queue
bounds across finite schedules, execution correspondence, conditional service
of existing backlog and a symbolic per-turn admission-plus-dispatch envelope.
Examined rejections and zero-payload events still receive a scan charge; zero
service fuel does not erase admission work.

Unexamined suffixes remain caller-owned, with no retained-storage or progress
guarantee. Concrete scan-cost dominance, offered-batch construction, backlog
measurement, external suffix handling, rejected-event disposal, executor work
and mandatory-event delivery remain open. Implementation links are
`not_checked_this_run`; implementation and deployment qualification remain
blocked.

`policy-ingress-resumption-model-check.json` records persistent caller-owned
admission resumption. The bundle has 633 explicit equality and order
declarations across 34 modules, 100 atomic obligations and 394 rejected negative
checks, including 24 new resumption mutations. Relation-valued proofs and
computational helpers are checked as well.

The slice proves exact FIFO conservation across resumed scans, conditional
examination of an original deferred prefix under enough delivered scan fuel,
independent service of an admitted prefix, admitted queue and pending bounds,
and dispatched-state correspondence. Its whole-schedule symbolic cost envelope
includes every examined arrival and counts each initial policy/handshake burst
once. The new controls have well-typed mutated definitions that fail subsequent
proofs.

Deferred storage has no modeled capacity bound. Examination can reject an
event, and real resubmission, wakeups, enough fuel, concrete cost dominance,
omitted allocation/traversal work and mandatory-event delivery remain open.
Implementation links are `not_checked_this_run`; implementation refinement and
deployment qualification remain blocked.

The 600-second qualification wrapper timed out under host contention, both
sequentially and with four isolated batches. Completion reused 388 finished
controls after checking exact candidate bytes, diagnostics and validated
checker progression. The unchanged negative-check function checked the three
remaining mutations and all generic guard controls afresh in four isolated
batches. The validator then completed with the expected qualification-blocked
exit 2. The receipt lists 394 distinct controls; generic guards also ran in
each recovery batch. No repository timeout or rejection rule was weakened.

`policy-ingress-deferred-model-check.json` records the bounded caller-owned
handoff extension. The bundle has 658 explicit equality and order declarations
across 35 modules, 104 atomic obligations and 419 rejected negative checks,
including 25 new controls. Every new mutated executable definition type-checks
before a later proof rejects its changed behavior.

The slice proves an exact examined/retained/overflow FIFO partition, a bounded
returned deferred prefix, explicit overflow returned with the continuation,
conditional single-turn examination, admitted queue and resource bounds, and
symbolic scan and overflow charges. Overflow cost still depends on input length;
deferred payload and total memory have no bound from the deferred entry cap.
Runtime ownership, concrete costs, overflow delivery, repeated bounded handoffs,
cancellation, restart and mandatory-event handling remain open. Implementation
links are `not_checked_this_run`; implementation refinement and deployment
qualification remain blocked.

The qualification wrapper allows 3,600 seconds for the expanded complete
suite. The per-invocation compiler timeout, semantic rejection requirements,
input hashes and expected qualification-blocked exit remain enforced.

`policy-ingress-handoff-schedule-model-check.json` records the finite bounded
handoff schedule extension: 680 explicit equality and order declarations in 36
modules, 108 atomic obligations and 446 rejected negative checks. The 27 new
mutations each have a type-correct executable prefix and fail a later proof.
They cover dropped or replayed retained input, skipped initial deferred input,
terminal deferred resubmission, scan and service fuel, capacity, overflow loss
and reordering, admitted limits, the carried queue, execution and occurrence
counts. An existing final-suffix mutation now includes its module-51 function
context to keep the target unique. It produces exactly the same original
mutated bundle; the checker rejection rules are unchanged.

C69-C72 connect the schedule to the existing single-turn handoff, preserve
deferred entry bounds under initial fit and admitted/resource bounds under
their existing premises, return chronological overflow without internal replay,
and conserve the recursive examined/overflow/final-deferred occurrence count.
Examined occurrences include later admission rejections. Output-history
storage, deferred payload, external delivery, concrete costs, ownership,
cancellation, restart and progress remain outside this result. Implementation
links are `not_checked_this_run`; implementation refinement and deployment
qualification remain blocked.

`policy-ingress-handoff-service-model-check.json` records the conditional
bounded-handoff service extension: 696 explicit equality and order declarations
in 37 modules, 112 atomic obligations and 465 rejected negative checks. The
19 new controls corrupt examined-trace extraction, capacity and scan allowance,
turn counting, retained suffixes, the unit and service suffixes and the overflow
example. Seventeen test general statements; two test the finite example with
variable events. Every control must fail with a proof type mismatch.

C73-C76 cover exact retention of a fitting prefix, progress through arbitrary
finite schedules with one ingress scan per turn, full examination given enough
turns, and occurrence-count bounds for any fixed scan allowance. The checked
examples separate scan work from dispatch fuel and show why capacity fit and
sufficient turns matter. Runtime delivery of turns, admission and dispatch,
overflow handling, storage, concrete costs and wall-clock progress remain open.
The receipt retains incomplete implementation and deployment status. The
qualification-gate regression runs the complete checker with
`--require-complete` and verifies that these open obligations still block it.

`policy-ingress-handoff-pauses-model-check.json` records the paused-handoff
extension: 712 explicit equality and order declarations in 38 modules,
116 atomic obligations and 490 rejected negative checks. The 25 new controls
corrupt pause/scan selection and counting, dispatch fuel, FIFO input order,
retention, overflow, prefix witnesses, the scan bound and the mixed example.
Every control must fail with a proof type mismatch.

C77-C80 cover bounded deferred retention across zero-or-one-scan schedules,
exact partial-prefix examination, full examination given enough delivered
scans, and examined occurrence-count bounds. A four-turn example alternates
pauses and scans, preserving original priority and chronological overflow.
Runtime scan delivery, admission, dispatch, storage, concrete costs and latency
remain open. Queue/resource composition and whole-schedule occurrence
conservation were open at this receipt's revision. The receipt retains
incomplete implementation and deployment status, and the qualification-gate
regression must still reject full qualification.

`policy-ingress-paced-execution-model-check.json` records the paced executor
extension: 725 explicit equality and order declarations in 39 modules,
120 atomic obligations and 508 rejected negative checks. C81-C84 link the
executor, conditional retained-queue and pending bounds, recursive occurrence-count
identity and dispatched-trace cost envelope. All 18 new controls require
semantic mismatches. The prior queue-erasure control gains unique surrounding
context while retaining its original mutation.

The receipt does not establish concrete scan or admission costs, deferred or
overflow storage bounds, runtime refinement, service delivery or latency.
The qualification-gate regression runs the entire checker and requires the
incomplete-qualification exit status 2. Implementation and deployment remain
unproved and unqualified.

`policy-ingress-paced-cost-model-check.json` records the paced administrative
cost extension: 738 explicit equality and order declarations in 40 modules,
124 atomic obligations and 532 rejected negative checks. C85-C88 link weighted
examination, repeated offered-item visits, administrative costs and the composed
execution envelope. The 24 new controls each type-check with module-57 proof
declarations removed and are rejected when those proofs are restored. Controls
cover omitted charges, weakened limits and incorrect handoff threading.

The visit limit accounts for the actual initial deferred suffix and every fresh
batch, then permits a full deferred buffer on each later turn. Pauses, repeated
retention, oversized overflow and zero dispatch fuel do not erase work. A fixed
turn charge also covers empty turns. Runtime interpretation requires dominating
scan/admission, handoff and fixed-turn weights alongside the existing execution
weights, all in a common unit. Concrete cost dominance, external batch costs,
output-history storage and real-time progress remain open. The receipt keeps
`implementation_links` as `not_checked_this_run`; implementation refinement and
deployment qualification remain false.

`policy-ingress-variable-scans-model-check.json` records the natural-allowance
extension: 768 explicit equality and order declarations in 41 modules, 128
atomic obligations and 565 rejected negative checks. Module 58 adds 30 proof
declarations and C89-C92 link variable scan accounting, original-prefix FIFO
service, conditional state bounds and the combined symbolic cost envelope.
All 33 new controls also reject after removing `variableDeferredIngressMixedExamined`,
`variableDeferredIngressMixedRemainder` and `variableDeferredIngressMixedOverflow`;
the general equations and bounds detect the faults without these fixed-schedule
witnesses. Existing mutation rows and gate logic are unchanged.

The full `make gate-regression` run checks the positive bundle, empty axiom
disclosure, source and catalog freshness, all negative controls, and the expected
qualification-blocked exit 2. This receipt is copied from that full report and
its input hashes match the final checked files. Runtime scan delivery, exclusive
ownership, concrete domination of the six cost weights, output-history storage
and latency remain open. Implementation links remain `not_checked_this_run`;
implementation refinement and deployment qualification remain false.

`policy-ingress-accounting-model-check.json` records chronological occurrence
accounting: 783 explicit equality and order declarations in 42 modules, 132 atomic
obligations and 590 rejected negative checks. Module 59 adds 15 proof declarations;
C93-C96 link per-turn reconstruction, actual-output projections, whole-schedule
chronology and its count corollary, and fixed-schedule boundary witnesses.

All 25 new controls also reject after removing `variableDeferredIngressLedgerMixed`,
`variableDeferredIngressLedgerInterleaving`, `variableDeferredIngressChronologicalInterleaving`,
`variableDeferredIngressLedgerDuplicateOccurrences` and `variableDeferredIngressLedgerZeroCapacity`.
The remaining positive bundle still checks, and the general proofs reject each
fault with a type mismatch. Three direct equality, order and termination checks
also reject in that reduced-witness run. Existing mutation rows are unchanged.

The full `make gate-regression` run checks the positive bundle, empty axiom
disclosure, source and catalog freshness, all 590 negative controls, and the
expected qualification-blocked exit 2. This receipt is copied from that full
report and its input hashes match the final checked files. Reconstruction is a
finite mathematical history, with no proved runtime storage or cost bound.
Implementation links remain `not_checked_this_run`; implementation refinement
and deployment qualification remain false.

`policy-ingress-composition-model-check.json` records finite schedule and ledger
composition: 799 explicit equality and order declarations in 43 modules, 136
atomic obligations and 612 rejected negative checks. Module 60 adds 16 proof
declarations; C97-C100 link schedule and ledger laws, exact deferred continuation,
output projections, chronological concatenation and pause/overflow witnesses.

All 22 new controls also reject after removing
`composedVariableDeferredIngressPauseOverflow` and
`composedVariableDeferredIngressRepeatedChronology`. The reduced positive bundle
checks, and all 22 faults produce proof type mismatches in the remaining general
proofs. Three direct equality, order and termination checks also reject.
Existing mutation rows are unchanged.

The full `make gate-regression` run checks the positive bundle, empty axiom
disclosure, source and catalog freshness, all 612 negative controls, and the
expected qualification-blocked exit 2. The receipt copies that report with
input hashes matching the final checked files. The model assumes the same
deferred capacity for both schedule segments. Complete runtime state composition,
ownership transfer, construction and output-history storage remain open.
Implementation links remain `not_checked_this_run`; implementation refinement
and deployment qualification remain false.

`policy-ingress-execution-composition-model-check.json` records complete model
execution across schedule boundaries: 813 equality and order declarations in
44 modules, 140 atomic obligations and 641 rejected negative checks. Module 61
adds 14 equality proofs, four operational definitions, atoms C101-C104 and 29
semantic mutations. Complete handoff equality covers the deferred trace,
admitted queue, policy/resource state and ordered overflow. Dispatch histories
compose using the exact intermediate state, at fixed parameters and without
an initial-fit premise.

All 29 new controls also reject with type mismatches after removing
`variableDeferredIngressExecutionPauseBoundary`; the reduced positive bundle
checks. The fixed witness separately covers paused dispatch, carried backlog,
nonzero service, deferred retention and overflow with arbitrary event values,
resource state and configuration. Existing mutation rows are unchanged.

The full `make gate-regression` run checks the positive bundle, empty axiom
disclosure, source and catalog freshness, all 641 negative controls and the
expected qualification-blocked exit 2. The receipt is copied from that report
and its input hashes match the checked files. Implementation links remain
`not_checked_this_run`; runtime refinement and deployment qualification remain
false. Concrete ownership, parameter changes, storage and cost domination are
outside these finite model equalities.

`policy-ingress-cost-composition-model-check.json` records symbolic cost
composition across schedule boundaries: 834 equality and order declarations in
45 modules, 144 atomic obligations and 675 rejected negative checks. Module 62
adds 21 proofs, five operational definitions, C105-C108 and 34 controls.
Administrative visits and turns, dispatched occurrences, processed-policy
operations and accepted handshakes retain their existing charges across a
split that carries the actual deferred, queued and resource state. The sum of
the segment costs inherits the single whole-schedule envelope under the
original credit bounds, with no fresh resource burst at the boundary.

All 34 new controls reject with type mismatches against universal statements;
module 62 has no closed example proofs. Controls include corrupted boundary
state and limits, changed second-segment weight or configuration, lost
deferred or queued work, erased cost components and incorrect induction or
composition arguments. The latter check proof-term constraints. Existing
mutation rows and rejection criteria remain unchanged.

The full `make gate-regression` run checks the positive bundle, empty axiom
disclosure, catalog and source freshness, all 675 controls and the expected
qualification-blocked exit 2. This receipt is copied from that report, with
matching input hashes. Implementation links remain `not_checked_this_run`;
implementation refinement and deployment qualification remain false. Concrete
cost domination, runtime state transfer, configuration changes, construction,
history storage and real-time delivery remain open.

`policy-ingress-capacity-handoff-model-check.json` records explicit deferred
capacity changes at a handoff: 855 equality and order declarations in 46
modules, 148 atomic obligations and 696 rejected negative checks. Module 63
adds 21 proofs, two operational definitions, C109-C112 and 21 controls.
Resizing preserves the exact partition of retained and rejected occurrences,
carries the admitted queue and policy/resource state, and preserves retained
work without further overflow when the same limit is reapplied. Resumed
execution reports boundary overflow before later overflow
and satisfies the new deferred bound without an initial-fit premise, including
an empty schedule. The admitted entry and payload bounds retain their premises.

The new controls corrupt boundary disposition, retained capacity, admitted
state, overflow chronology or resumption parameters. They must produce proof
type mismatches under the unchanged gate criteria. Finite witnesses cover
shrinking, spare capacity, repeated occurrences, paused turns and a later scan.

The full `make gate-regression` checks the positive bundle, empty axiom
disclosure, catalog and source freshness, all 696 controls and the expected
qualification-blocked exit 2. The receipt is copied from its report with
matching input hashes. Implementation links remain `not_checked_this_run`;
implementation refinement and deployment qualification remain false. Runtime
authority, overflow cleanup, resizing costs and storage, other resource-limit
changes, and ledger/cost composition across the boundary remain open.

`policy-ingress-capacity-accounting-model-check.json` records occurrence
accounting across a deferred-capacity boundary: 873 equality and order
declarations in 47 modules, 152 atomic obligations and 712 rejected negative
checks. Module 64 adds 18 proofs, one operational definition, one witness
schedule, C113-C116 and 16 controls. The boundary ledger reconstructs the
original deferred input followed by every subsequent arrival, preserving order
and multiplicity without initial fit. Its examined projection matches the
resized-prefix execution; deferred and overflow projections equal the actual
resized-execution fields. Empty schedules and zero capacity retain the
boundary disposition, while finite witnesses cover fresh overflow during a
pause, later multi-item examination and repeated equal-valued occurrences.

The 16 altered ledger definitions were checked through their declarations
before the full bundle rejected them with proof type mismatches at statements
over variables. They change boundary examination, retained-length metadata,
overflow or the continuation's input, capacity or schedule. These controls test
the definitions' constraints on proof terms; rejection alone does not establish
that every variant has different extensional behavior.

The full `make gate-regression` checks the positive bundle, empty axiom
disclosure, catalog and source freshness, all 712 controls and the expected
qualification-blocked exit 2. The receipt is copied from its report with
matching input hashes. Implementation links remain `not_checked_this_run`;
implementation refinement and deployment qualification remain false. Runtime
authority, occurrence ownership, cleanup, resize costs and history storage,
composition with a preceding segment and repeated capacity changes remain open.

## Capacity composition model check

`policy-ingress-capacity-composition-model-check.json` records 886 checked proof
declarations in 48 modules, 155 atomic obligations and 724 rejected negative
checks. Module 65 adds 13 proofs, one operational definition, C117-C119 and
12 controls. The ledger joins a preceding variable-scan segment, one explicit
deferred-capacity boundary and a following segment. It reconstructs the exact
initial deferred input and both fresh-arrival histories, including multiplicity,
without initial fit. Examined and overflow projections concatenate in segment
order; final deferred ownership comes from the resized following ledger.

Each altered definition typechecks before its full bundle fails with a proof
type mismatch. The controls remove or corrupt earlier history, change capacity
or schedule selection, replay or drop carried input, or omit the resize.
Finite witnesses distinguish overflow before, at and after the boundary and
cover zero capacity and growth with empty schedules.

The receipt comes from the full `make gate-regression` report, including empty
axiom disclosure, freshness checks, all 724 negatives and the expected blocked
qualification exit 2. Implementation refinement and deployment qualification
remain false. Full execution and cost composition across changed limits,
repeated resizes, runtime ownership, cleanup and bounded history storage remain
open. Earlier receipts above describe their respective historical slices.
## Capacity execution model check

`policy-ingress-capacity-execution-model-check.json` records 902 checked proof
declarations in 49 modules, 159 atomic obligations and 751 rejected negative
checks. Module 66 adds 16 proofs, three operational definitions, C120-C123 and
27 controls. Two execution segments use independently chosen deferred capacities
and the exact first handoff state. Their combined filtered schedule executes
the actual final queue and policy/resource state, dispatch histories concatenate
in order, and ledger deferred/overflow projections match the execution handoff.

The final deferred bound needs no initial fit; admitted entry and payload bounds
retain their respective initial-fit premises. Pending occupancy stays within
the original lease capacity. Empty, zero-capacity, shrink, growth and repeated
event witnesses cover the boundary and carried queue. The dispatch-cost envelope
uses the original credit bounds and excludes scanning, admission, retention,
overflow handling and resizing costs.

Each altered definition typechecks before the universal statements reject it
with a type mismatch, without the concrete witnesses. The full
`make gate-regression` report includes empty axiom disclosure, freshness checks,
all 751 negatives and the expected qualification-blocked exit 2. Implementation
refinement and deployment qualification remain false. Repeated capacity changes,
administrative and resize cost composition, other parameter changes, runtime
ownership, cleanup, real delivery and bounded history storage remain open.
## Capacity cost model check

`policy-ingress-capacity-cost-model-check.json` records 912 checked proof
declarations in 50 modules, 162 atomic obligations and 777 rejected negative
checks. Module 67 adds ten proofs, six cost definitions, C124-C126 and 26 controls.

The logical resize count includes retained and rejected occurrences and equals
the complete boundary input length. Its charge includes one fixed boundary
cost even for empty input. The actual first execution handoff supplies the
resize input; the next administrative segment starts from the retained prefix
at the new capacity. Administrative costs combine with the composed schedule's
dispatch cost under the original work and handshake credit bounds. The limit
retains the actual resize-input charge and needs no initial deferred fit.

All 26 altered definitions typecheck independently, and general proofs reject
all 26 without the three specialized witnesses. The existing 748 mutation rows
are unchanged. `make gate-regression` checks the complete bundle, empty axiom
disclosure, source and catalog freshness, all 777 negative checks and the
expected qualification-blocked exit 2.

Implementation links were not checked in this run. Implementation refinement
and deployment qualification remain false. The new disclosed resize-cost
assumption still requires concrete domination of every partition pass,
materialization, ownership transfer and mandatory cleanup in a common cost
unit. Repeated reconfiguration, external construction, uncharged allocation,
bounded history storage, real service delivery and elapsed time remain open.

## Capacity schedule model check

`policy-ingress-capacity-schedule-model-check.json` records the passing checks
for `68-policy-ingress-capacity-schedule.mech`, atoms C127-C130, and the complete
proof bundle. The slice adds a finite resize/poll schedule, chronological
occurrence reconstruction and count, the terminal bound at the final capacity,
and equality with the earlier fixed-capacity and single-resize ledgers.

The initial-fit premise is required for the general terminal bound, including
the empty schedule. A leading resize establishes the terminal bound without
initial fit. Chronological reconstruction has no such premise. A mixed witness
checks two shrinks, growth and zero-scan arrivals; a separate theorem checks
that growth after a zero-capacity boundary does not revive discarded work.

All 30 new controls require semantic proof rejection. The full receipt retains
empty axiom disclosure and the existing incomplete qualification status.
This receipt covers deferred accounting. Module 69 adds repeated-change
execution and module 70 adds cost composition. Runtime authority, ownership,
cleanup, real service delivery and bounded history storage remain open.

## Capacity schedule execution model check

`policy-ingress-capacity-schedule-execution-model-check.json` records the passing
checks for `69-policy-ingress-capacity-schedule-execution.mech`, atoms C131-C134,
and the complete proof bundle. Seventeen new proof declarations connect finite
resize/poll execution to the examined ledger trace, preserve total dispatch fuel
across arbitrary finite interleavings, preserve the earlier
fixed-capacity filtered schedule and establish deferred, admitted entry,
payload and pending-resource bounds under their stated premises.

The runner constructs deferred and overflow handoff fields from the ledger and
executes the filtered payload-aware admitted schedule. These field equalities
are by construction. Empty and lone-resize handoffs are checked generally;
three concrete schedules check shrink/growth FIFO retention, repeated overflow
and dispatch from a carried queue with zero scan fuel. They quantify over event
values and resource state without claiming general liveness.

All 32 new controls require semantic proof rejection. The full receipt retains
empty axiom disclosure and the existing incomplete qualification status.
Module 70 adds repeated-change cost composition. Runtime simulation, authorized
serialized updates, ownership, cleanup, real service delivery and bounded
history storage remain open.

## Capacity schedule cost model check

`policy-ingress-capacity-schedule-cost-model-check.json` records the passing
full gate for module 70 and atoms C135-C138: 951 proof declarations across 53
modules, 174 atomic obligations, 1,383 source units and 872 rejected negative
checks. The ten new proof declarations establish polling and resize charges,
the inductive administrative bound, the combined dispatch envelope, empty
cost, and two concrete schedules with duplicate occurrences and a pause.

The administrative limit starts from the actual deferred input length and
propagates the active capacity after every resize or poll. Every boundary pays
for its input occurrences and fixed work. Every poll pays for examined work,
all offered visits and fixed work even when scanning or dispatch is paused.
The combined envelope requires only the original work and handshake credit
bounds, with fixed admitted limits, payload weights and resource configuration.

All 33 new controls require semantic proof rejection. The full run checks empty
axiom disclosure, source and catalog freshness, all existing controls, and the
expected qualification-blocked exit 2. The receipt reports implementation links
as not checked in this run. Runtime refinement and deployment qualification
remain incomplete; no cost weight, real service rate, allocation bound or
bounded history storage has been established by these symbolic proofs.

The completed gate uses `python3 -I tools/check_gate.py --jobs 4`. An initial
serial run was stopped as it approached the runner's one-hour limit. The
parallel mode retains the per-check timeout, semantic diagnostic rules, full
case set and deterministic report order. A duplicate case name is rejected
before workers start; the default worker count and CI commands remain unchanged.
`tools/check.py` collects worker results with `ThreadPoolExecutor.map`, so the
report keeps case order and a failed rejection in any worker fails the run.
It rejects duplicate case names and a worker count outside 1-8 before any
worker starts. No repository test compares the results of different worker
counts. Both command-line entry points also reject an invalid worker count
before starting the checker.

## Capacity schedule composition model check

`policy-ingress-capacity-schedule-composition-model-check.json` records the
full gate for module 71 and atoms C139-C141: 961 proof declarations across 54
modules, 177 atomic obligations, 1,383 source units and 890 rejected negative
checks. The ten new proofs cover associative schedule concatenation, its right
identity, active-capacity propagation, ledger and lowered schedule composition,
and final deferred, overflow and admitted queue agreement across arbitrary
finite execution cuts.

The second segment receives the actual terminal deferred suffix and admitted
queue state at the first segment's final capacity. Admitted limits, payload
weights and policy configuration stay fixed. The equalities have no initial-fit
premise and do not establish resource bounds for invalid initial states.

All 18 new controls require semantic proof rejection. They corrupt five
operational definitions and test lost boundaries, continuations, arrivals and
overflow, swapped scan/dispatch fuel, stale capacity, discarded or restarted
deferred work, restarted admitted state and a skipped second segment. The gate
also checks all prior controls, empty axiom disclosure, source hashes, catalog
freshness and the expected qualification-blocked exit 2. The receipt reports
implementation links as not checked in this run. Runtime refinement, deployment
qualification, earlier single-boundary execution equivalence and segmented
cost equivalence remain incomplete.

## Capacity schedule cost composition model check

`policy-ingress-capacity-schedule-cost-composition-model-check.json` records the
full gate for module 72 and atoms C142-C144: 970 proof declarations across 55
modules, 180 atomic obligations, 1,383 source units and 910 rejected negative
checks. The nine new proofs connect additive administrative charges, the
actual deferred and work-state boundary, dispatched-trace and dispatch-cost
composition, total-cost equality, its combined envelope and empty execution.

All 20 new controls require semantic proof rejection. They alter five
operational definitions to skip execution, lose deferred or queued input,
omit charges, use stale capacity, discard a segment or restart boundary state.
The new controls were also checked separately with the three direct negative
checks before the full gate. The gate checks all prior controls, empty axiom
disclosure, source hashes, catalog freshness and the expected
qualification-blocked exit 2.

The bound uses one concatenated-schedule limit under the original work-credit
and handshake-credit premises, with no initial deferred/admitted fit premise.
The receipt reports implementation links as not checked in this run. Runtime
refinement and deployment qualification remain incomplete, as does compatibility
with the earlier fixed-capacity and single-boundary segmented cost models.

## Capacity schedule compatibility model check

`policy-ingress-capacity-schedule-compatibility-model-check.json` records the
full gate for module 73 and atoms C145-C147: 981 proof declarations across 56
modules, 183 atomic obligations, 1,383 source units and 925 rejected negative
checks. Eleven new proofs connect fixed-capacity and single-boundary occurrence
ledgers, lowered schedules and the actual runners' complete final admitted
queue. Empty-prefix and zero-resize statements cover arbitrary waiting input.

All 15 new controls require semantic proof rejection. Eleven corrupt the new
single-boundary embedding, and four corrupt the earlier variable-schedule
embedding. The latter can fail at earlier module-69 statements. The new controls
were also checked separately with the three direct negative checks before the
full gate. The gate checks all prior controls, empty axiom disclosure, source
hashes, catalog freshness and the expected qualification-blocked exit 2.

The equalities require fixed admitted limits, payload weights and configuration,
with no initial-fit or credit-bound premise. They do not establish resource
bounds for invalid initial states or separately equate full handoff records.
The receipt reports implementation links as not checked in this run. Runtime
refinement and deployment qualification remain incomplete. Module 74 later
establishes compatibility with the earlier segmented symbolic cost formulas.

## Capacity schedule cost compatibility

`policy-ingress-capacity-schedule-cost-compatibility-model-check.json` records
module 74 with ten proof declarations and three atomic model obligations,
C148-C150. General equalities relate per-turn administrative charges to the
earlier aggregate formula and relate the single-boundary administrative and
complete execution costs to the earlier segmented model. Fixed-capacity full
execution costs agree as well. Boundary statements cover empty schedules,
paused scans with independent dispatch fuel and empty resize segments.

Twelve new controls mutate operational charge definitions and must produce
type mismatches. They may be rejected by earlier proofs. The full gate checks
all 937 negative cases, empty axiom disclosure, source hashes and catalog
freshness. The separate gate regression checks the expected qualification
block, including the require-complete exit 2. No initial-fit or credit-bound
premise is added to these equalities. Concrete cost domination, runtime
refinement, ownership, storage, cleanup and service delivery remain open.

## Source disposition ledger

`source-disposition-check.json` is a byte copy of
`.build/source-disposition-report.json` from `make dispositions`. It validates
the pinned ledger for all 1,383 source units. All 1,383 units have an audited
disposition: 672 context, 681 obligation and 30 superseded. No unit remains
pending. The ledger assigns 83 model obligations, M001-M083, and 43 external
obligations, E001-E043. The checker verifies source pins, exhaustive unit
coverage, obligation links and reconciliation structure. It gives no proof
credit. Reviewers must still assess each rationale and each closure scope.

`source-ledger-model-check.json`, `t1-t4-source-audit-model-check.json` and
`t6-t7-source-audit-model-check.json` preserve the first three R01 audit receipts
with their historical counts. `t2-t5-source-audit-model-check.json` records the
fourth batch: 57 modules, 991 checked proof declarations, 186 atomic model
obligations, 1,383 source units, no axioms and 937 rejected negative checks.
Its `source_dispositions` block equaled the `dispositions` block of
`source-disposition-check.json` after the fourth batch. `r01-closure-check.json`
records the current counts. Implementation links were not checked in this
run. The full qualification command still returns the expected blocked exit 2.

The fourth batch audits every original T02/T05 unit and selected revised
T2b/T5, resource, decision, crosswalk and regression clauses. E011 retains
release-direction, negotiated-group, effective-deadline and baseline/lane
observations. E020 requires the candidate Retry integration matrix, including
spoofing/token edges, policy changes and progress before the outer event loop.
Historical unconditional acceptance and zero-refusal/zero-capacity-warning
guards are reconciled to intended Retry behavior and declared D02/D04 bounds.

M012 requires established-resource grant/release accounting and whole-process
composition across trusted/exempt peers and all swarms. E021 separately requires
honest resource calibration, accurate concurrent occupancy and resident-memory
measurement limits. E022 requires selected allocations and passing M3b regressions
for hostile ceiling attempts alongside catch-up and critical traffic. Credit is
not resident memory, cumulative connection counts are not concurrent occupancy,
and lowering constants alone does not close the measured whole-process budget.
No theorem witnesses or candidate atoms are credited to the new obligations.
R01 was active after four execution turns. The fifth turn closed claim
decomposition. Implementation proof and deployment qualification remain
incomplete.

## R02 composition and authentication audit, turn 4

`r02-composition-auth-audit-check.json` records all 25 R05/R06/R07 witness
reviews and their 51 criterion dispositions. There are now 61 reviewed model
obligations: M005 remains covered, 60 remain partial, and only the 22 R08
obligations and their 44 criteria await review. The last batch includes the
R02 exit-evidence audit and closure, under the existing five-turn cap.

M008's bounded examination criterion has a general theorem over every finite
Accept/Retry/Refuse/Ignore trace. Wake flags and counted critical-service
rounds retain their stated premises; they do not prove command-age or timer
service bounds. Weighted scalar/pool bounds do not model class reserves or
spawned/waiting tasks. Ingress chronological reconstruction does not establish
task completion or class-stage retry/drop accounting. A sleeping-constructor
equality receives finite-example scope. Certificate/transcript verification,
verifier-result lifetime, cryptographic group negotiation and aggregate-key
proof of possession remain explicit R07 gaps, with crypto premises still to
be modeled. All gaps retain their sealed R05/R06/R07 assignments.

Audit, scope and source-disposition validation and their regressions are fresh.
The 57 modules, 991 proof declarations, compiler identity, axiom result and
semantic-mutation controls are reused from the pinned turn-3 receipt. The new
receipt records the historical receipt hash, relevant input comparisons,
current metadata hashes and commands actually run. Full model and qualification
checks were not rerun for this audit-only batch. The semantic model source hash
retains its historical meaning; current input hashes and the audit summary are
recorded separately. R02 is active after four turns, using one reserve turn;
all 43 external obligations remain open.

## R02 admission and policy audit, turn 3

`r02-admission-policy-audit-check.json` records the batched R03/R04 witness
review. All 36 obligations assigned to those packets are now reviewed: M005
remains covered, 35 are partial, and no R03/R04 criterion remains unreviewed.
This adds 32 obligation reviews and finishes the M009/M013 gap classifications.
The remaining census is 47 obligations and 95 criteria. See the
[five-turn plan](../docs/R02-BATCHES.md): R05/R06/R07 form turn 4 (25 obligations),
and R08 plus R02 closure form turn 5 (22 obligations).

The corpus remains 57 modules and 991 explicit proof declarations. No new
mechanism-lang declaration or semantic mutation is introduced. Exact existing
statements retain their general or finite scopes. Retry-policy credit does not
establish reachability-evidence composition; capped scalar/pending costs do not
establish established-resource vectors; snapshot agreement does not model both
outbound decision points. Missing peer/discovery/recovery and endpoint lifecycle
models remain exact R03/R04 gaps, not external reclassifications. All 43 external
obligations remain open.

The receipt records fresh audit/provenance regressions and the proof/qualification
checks actually run. Historical compiler evidence can be reused only with
matching relevant input hashes and an explicit reuse label. R02 is active at
three total execution turns; the original three-turn allocation and overall
50-turn target stay fixed, with at most two reserve turns allocated to finish
the census. The earlier receipts below retain their historical counts.

## R02 witness audit, first pass

`r02-witness-audit-check.json` records the first R02 witness-audit pass and the
full model/qualification-guard run: 57 modules, 991 checked proof declarations,
186 existing atomic model obligations, 1,383 source units, no axioms and 937
rejected negative checks. Its `proof_witness_audit` block matches the generated
inventory: four partial reviews, zero covered frozen obligations, 79 unreviewed
obligations and 167 acceptance criteria still awaiting audit.

The receipt retains input hashes. Separate regressions passed: 29 witness-audit
checks, 40 source-disposition checks and 15 scope checks. The audit complete
coverage command and the full qualification command both return the expected
blocked exit 2. Implementation links were not checked in this run.

The reviewed requirements are M004 (pending capacity), M005 (owned release),
M009 (source bookkeeping) and M013 (source/prefix and aggregate rates). General
trace/transition statements are distinct from the fixed two-swarm example.
Unreviewed criterion work may already have witnesses elsewhere; it is not
automatically an absent proof. R02 remains active after one of its planned three
execution turns. The source scope is unchanged and all external obligations
remain open. The second pass below supersedes this section. See [the current
audit](../docs/R02-AUDIT.md).

## R02 indexed witness audit, second pass

`r02-indexed-witness-audit-check.json` records the second R02 pass and the full
model/qualification-guard run. The corpus remains 57 modules, 991 checked proof
declarations, 186 atomic model obligations and 1,383 source units, with no axioms
and 938 rejected negative checks. The audit adds 16 exact general witnesses
from existing modules 37 and 39. M005 is covered at the sealed model scope;
three obligations remain partial, 79 remain unreviewed and 164 acceptance
criteria still need audit.

The whole-state unowned callback theorem and arbitrary-prefix receipt/release
equalities witness every M005 terminal reason, duplicate and mismatched or
arbitrarily stale callbacks, unrelated-slot preservation and restoration of
the corresponding pending occupancy baseline. Source debt and spent credits
stay consumed. Internal receipt authority, index stability, atomicity and
nonwrapping generations remain explicit model premises. External obligation
E013 owns their runtime refinement.

M004 now records an exact R03 proof gap: zero total pending availability must
imply selected-token absence for every index before the existing admission
no-op and no-receipt results can be composed. Held-slot and missing-slot
refusal alone do not state that implication. No proof declaration is added.
A new mutation makes an unowned admission callback release a live slot without
an owned receipt. Linked mutation hashes preserve the controls; the full run
records their actual rejection sites, including failures in earlier modules.

The receipt pins current proof inputs and tooling. The 29 witness-audit, 40
source-disposition, 15 scope and full-qualification guard regressions pass.
Audit complete coverage and full qualification still return blocked exit 2.
Implementation links were not checked in this run. R02 remains active after
two of its three planned turns; seven of the overall 50 turns are used. All
43 external obligations remain open. See [the current audit](../docs/R02-AUDIT.md).
