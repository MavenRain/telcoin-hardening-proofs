# Evidence still required

No runtime or deployment result has been supplied or synthesized. The `.build`
report records local model checking only. The current complete-qualification
command rejects all implementation and deployment certification.

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
