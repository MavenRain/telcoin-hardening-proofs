# Proof meaning and trust boundary

The checked terms inhabit dependent types in mechanism-lang. `Count`, `Flag`,
equality and the indexed `AtMost` relation are defined in source. `AtMost` lives
in `Type 0` and carries constructive witnesses. This avoids assuming a numeric
axiom or a proposition erasure feature that the checker does not provide.
The equality family lives in `Prop`.

Some results follow by reduction of a pure decision function. Arithmetic
composition, finite transition traces, generation-safe cleanup, committee
deduplication and service-round bounds use structural induction. The checker
rejects nontermination, unequal boolean endpoints and an impossible bound.
The 1106 additional semantic mutations must
invalidate the corresponding proofs. These controls provide evidence that the
intended definitions matter; they are not a soundness proof of the checker.

The finite occurrence ledger projects to the variable-allowance handoff outputs
and reconstructs chronological input by recording retained-prefix boundaries.
This trace equality preserves order and value multiplicity without assigning
runtime identities to equal-valued events. It does not bound history storage or
reconstruction costs, and it does not establish admission, delivery or latency.

Finite schedule composition resumes the second ledger from the first segment's
exact deferred suffix at unchanged capacity. It preserves ledger projections and
chronological reconstruction, including repeated equal-valued events. The model
handoff equations identify deferred and overflow fields only. Arbitrary raw
ledger splices need a compatible continuation for the chronology claim.
Module 61 covers complete model state composition; runtime ownership transfer,
construction and history storage still require refinement.

Module 61 proves complete model execution composition at schedule boundaries,
including deferred work, admitted queue, policy/resource state, ordered
overflow and dispatched history. Both segments use the same weights, limits,
capacity and configuration. No initial-fit premise is needed for the
equalities. Runtime simulation, atomic ownership transfer, parameter changes,
concrete costs and output-history storage still require refinement.

Module 62 preserves the existing six-weight symbolic cost across schedule
splits, using the complete actual handoff state and fixed parameters. The sum
of both segment costs inherits one whole-schedule envelope under the original
work and handshake credit bounds. No fresh burst or credit premise is added
at the split. All 34 new controls reject against universal statements, without
closed witnesses. This establishes neither concrete cost domination nor runtime
ownership transfer, bounded history storage, changed-parameter behavior or
wall-clock service.

Module 63 models an explicit deferred-capacity boundary. Partition conservation
and same-capacity idempotence preserve occurrence order and multiplicity while
carrying the admitted queue and complete policy/resource state. Resumed
execution accounts for boundary overflow before later overflow, including an
empty schedule, and its deferred bound requires no initially fitting input.
The admitted entry and payload bounds still require their initial-fit premises.
Authorization, atomic runtime state transfer, actual overflow cleanup, resize
costs and storage remain open. Other limits and configuration do not change;
the earlier fixed-parameter cost and ledger composition laws do not apply
across this boundary without further proof.

Module 64 reconstructs the exact chronological input across one such boundary
and its following variable-scan segment. The ledger records zero examination,
the actual retained-prefix length and the removed suffix before the continuation.
Its examined projection matches the resized input's execution trace; deferred
and overflow projections equal the actual resized-execution handoff fields.
No initially fitting deferred input is required. Finite witnesses cover pauses,
later multi-item examination and repeated equal-valued occurrences. The ledger
record does not deliver a scheduler turn or implement cleanup. Module 65
composes a preceding ledger with this boundary and its following segment,
preserving exact chronological reconstruction and segment-ordered projections.
It carries the exact first remainder and requires no initial fit. Module 66
connects this ledger to complete execution across one deferred-capacity change.
Module 68 separately proves deferred accounting across finite repeated capacity
changes, module 69 adds their admitted queue/resource execution and module 70
adds their symbolic costs. Concrete resize cost domination, runtime ownership
and bounded history storage remain open.

Module 66 carries the complete first execution handoff through the resize and
the second segment. Queue and policy/resource execution equals the concatenated
filtered schedule, dispatched histories compose in order, and the ledger's
deferred and overflow fields match the actual handoff. The new deferred bound
requires no initial fit; admitted entry and payload bounds keep their respective
premises. The dispatch-cost envelope uses the original credit bounds. It excludes
administrative and resize costs and does not change admitted limits, weights or
configuration. All 27 controls typecheck as definitions and reject against
general theorems without concrete witnesses. Runtime refinement, cleanup, real
delivery and other parameter changes remain open.

Module 67 combines administrative, resize and dispatch costs across that one
boundary. It charges each logical retained or removed occurrence and one fixed
boundary cost, including empty input. The administrative limit retains the
actual resize-input charge and needs no initial deferred fit. The full envelope
uses the original work and handshake credit premises. Logical occurrence counts
do not establish the number of physical traversal passes. The new disclosed
`deferred_ingress_resize_costs` assumption requires concrete domination of all
partition, materialization, ownership and cleanup work in a common unit with
the existing costs. No new kernel axiom is introduced. Runtime cost domination,
repeated capacity changes, allocation and history-storage bounds, real service
delivery and elapsed time remain open.

The finite capacity-schedule layer adds induction over arbitrary finite
interleavings of resize boundaries and polling turns. Its chronological ledger
reconstructs offered occurrences and its terminal deferred bound uses the final
capacity. The general bound requires initial fit; a leading resize establishes
fit. Fixed-capacity and single-resize embeddings agree with the earlier ledgers.
Module 68 erases dispatch fuel and accounts only for deferred occurrences.
Authority, runtime ownership, overflow cleanup, history storage and real
service guarantees remain external.

Module 69 retains independent dispatch fuel and lowers arbitrary finite
resize/poll schedules to the existing payload-aware admitted execution. An
inductive equality ties its offered trace to the capacity ledger's examined
trace. Total dispatch fuel is preserved across arbitrary finite interleavings,
and another equality preserves the earlier fixed-capacity filtered schedule.
The runner obtains deferred and overflow fields from ledger projections by
construction; their equalities do not simulate a separate runtime executor.
The terminal deferred bound requires initial fit or a leading resize. Admitted
entry and payload bounds retain their respective initial-fit premises; pending
occupancy is bounded by the original lease capacity. Admitted limits, weights
and policy/resource configuration stay fixed. No new shared assumption or
kernel axiom is introduced.

Module 70 composes administrative, repeated-resize and dispatch charges in a
common eight-weight symbolic envelope. Each resize charges every input
occurrence plus fixed boundary work, including empty boundaries. Each poll
charges examination, all offered visits and fixed turn work, including pauses.
The administrative limit carries an upper bound on the initial suffix length
and then the active capacity after every boundary or turn. The combined bound
uses the actual initial suffix length and the original work and handshake
credit premises; it requires no initial deferred or admitted fit. Admitted
limits, payload weights and policy/resource configuration still stay fixed.
The existing runtime cost-domination assumptions now describe both fixed and
changing-capacity limits. They do not prove concrete traversal counts, measured
weights, allocation costs, bounded history storage or elapsed time. Runtime
ownership, cleanup, delivery and equality with earlier segmented costs remain
open. No kernel assumption is added.

Module 71 proves composition across arbitrary finite capacity execution
segments. The second segment receives the first segment's final deferred
capacity, terminal deferred suffix and complete admitted queue state. Ledger
and lowered schedule equalities imply identical final queue, deferred and
overflow projections, without an initial-fit premise. Admitted limits,
weights and policy configuration remain fixed. These are equalities between
pure model executions, not a proof of runtime serialization, cleanup or
service delivery. Invalid initial states do not acquire resource bounds from
these equalities. Module 73 proves the earlier single-boundary ledger,
lowering and final admitted queue equalities. Segmented cost equivalence remains
open. No shared assumption or kernel axiom is added.

Module 72 equates the concatenated execution cost with the sum of segment
costs at the actual handoff. The carried boundary includes the final deferred
capacity and suffix, admitted queue and post-prefix policy/resource state.
Administrative and dispatch equalities require no initial fit or credit bounds.
The combined envelope retains the original work and handshake credit premises
and counts a single initial burst across the concatenated schedule. Admitted
limits, payload weights, configuration and all eight symbolic weights remain
fixed. Runtime handoff serialization, concrete cost domination, ownership,
cleanup, storage and delivered service remain external. Module 74 establishes
compatibility with earlier fixed-capacity and single-boundary symbolic costs.
No shared assumption or kernel axiom is added.


## Trusted components

The trust base includes the pinned mechanism-lang frontend, kernel and vendored
Veil code, the OCaml compiler and dependencies, the host OS and hardware, and the
small repository scripts. The driver starts with its normal initial globals;
the proof source never references their numeric axiom or primitives. The
dependency disclosure for the complete proof bundle must be empty. No claim of
an independently verified empty-global checker run is made.

The bootstrap builds exact commits and records the resulting executable hash.
The verification command refuses an executable that differs from that build
receipt. This is reproducibility within the stated trust base, not a signed
third-party attestation. File hashes detect drift, not semantic correctness.

Module 73 embeds fixed-capacity and single-boundary schedules into arbitrary
capacity execution. Structural induction proves equality of the complete
occurrence ledgers and lowered schedules. Transport through payload-aware
execution preserves the complete final admitted queue of the earlier segmented
runner, under fixed admitted limits, immutable payload weights and configuration.
The statements do not require initial fit or credit bounds. They do not
establish bounds for invalid states or separately equate the full operational
handoff records. Fifteen controls corrupt the operational embeddings, including
segment loss and replay, misplaced boundaries, changed capacity and altered
scan or dispatch inputs. Module 74 establishes symbolic cost compatibility;
runtime refinement remains open.

Module 74 uses constructive arithmetic distribution and structural induction
to equate per-turn charges with the earlier aggregate formula. Administrative
composition charges the actual post-prefix resize input; schedule equalities
transport complete symbolic costs through payload-aware dispatch. All eight
weights stay fixed. Empty schedules, pauses and empty resize segments retain
their specified charges. Twelve operational mutations require type mismatches.
The equalities need no initial fit or credit bound. They neither validate a
concrete cost weight nor prove runtime refinement or deployment qualification.

## Unlocked executor lifetime and cost boundary

Module 79 bounds finite waiting and active ownership across arbitrary endpoint
and swarm event traces. Every event must route through the same banks; their
capacities cover the host allocation rather than separate private pools. The
model assumes atomic reservation and ownership transfer, internal callback
tickets and nonwrapping generations. It assumes no accept/endpoint mutex or
fair scheduling. Matching terminal callbacks release their selected owner;
stale callbacks preserve a newer generation.

E019 must refine actual worker lifetimes, cancellation and callback provenance.
An active terminal event must mean that execution has stopped and resident
resources have been released. A cancellation request alone must retain the
active charge until that terminal event. Supplied waiting and active resource
weights must dominate allocations in the same unit. Event work charges fixed
administrative cost, two passes over both banks and enforced capped execution
demand. Concrete scan, dispatch and cleanup costs must fit those charges.
The trace bounds do not establish worker fairness or service delivery.

## Open boundaries

- Natural scan allowances in module 58 are supplied per delivered turn,
  independently of dispatch fuel. Prefix protection requires that the original
  prefix fit the fixed deferred capacity; full examination also requires enough
  total scans. Terminal deferred and admitted-state bounds retain their initial
  conditions. These proofs establish examination progress and symbolic work
  accounting. Runtime scan delivery, exclusive ownership, admission, dispatch,
  changing capacities, concrete cost domination and latency require refinement.
- `Reachability.validated` must be connected to correct QUIC token semantics,
  return reachability and restart/key behavior. The model does not verify tokens.
- Authentication, policy freshness, committee membership and source attribution
  are inputs. The committee model rejects unverified or old-epoch records,
  deduplicates a fixed roster and clears resolution on epoch reset. Correct
  signature/epoch binding, stable member indices and freshness still need
  refinement. The positive recovery threshold is supplied as a model input;
  deriving committee size minus f remains open.
- The policy model orders complete views with nonwrapping generations. Real
  publication must be atomic. Receipt validation and authorization must linearize
  with publication, or retain equivalent protection through use. A separate
  version check followed by unprotected use is insufficient. Peer identifiers,
  receipt provenance, fault detection and external governance ordering need
  refinement; the local generation alone does not establish input freshness.
- Work units are symbolic. Weighted resource and handshake-cost bounds require
  runtime cost dominance and complete accounting of retained allocations.
  The shared token-bucket trace proves a discrete burst-plus-rate envelope;
  trusted ticks must correspond to the real clock.
- Module 42 charges processed attempts and publications from an
  independent shared balance before the delegated policy/source event. Its cost
  envelope includes denied operations but receives already constructed policy
  receipts. Receipt creation, authentication, pre-budget work, exhausted guards,
  maintenance, completion and established resources need separate cost bounds.
  Runtime evidence must justify fixed rates, capacities and per-operation weights,
  including payload and roster bounds, and the atomic pre-state ordering. Policy
  recovery and honest traffic can be delayed; no scheduling fairness is proved.
- Module 43 produces policy receipts internally after the work-credit guard,
  from the current policy view and attempted identity. Every processed query
  spends work credit, including denials. Mixed traces preserve the work and
  handshake cost envelopes if the operation weight also covers bounded query
  and receipt construction. Authentication flags, peer identity bindings,
  runtime entry-point discipline and atomic query/charge/admission still require
  refinement. Pre-guard authentication, exhausted guards, dispatch, cleanup and
  established-resource costs remain outside this envelope.
- Module 44 adds a finite poll fuel that charges every dispatched ingress event,
  including exhausted-credit guards, maintenance and completion. Exact queue
  reconstruction, prefix execution and resumption preserve the existing state
  semantics and pending bound. Its combined cost envelope assumes an event
  weight covering all per-dispatch work outside policy and handshake costs.
  Queue construction, pre-dispatch authentication, empty-poll costs, runtime
  wakers and executor overhead still need separate bounds. Cleanup bypasses
  exhausted policy work credit but requires poll fuel and actual scheduling.
  Positive fuel, executor fairness and cleanup priority are open refinements;
  the model does not supply a wall-clock latency or global polling-rate bound.

- Module 45 couples a persistent FIFO queue to the carried resource state.
  Under the explicit scheduler with one unit of fuel per delivered turn, any
  original prefix finishes after its length of turns despite finite arrivals
  before every turn. The exact suffix and arrival history remain queued.
  Repeated service preserves the dispatched-trace semantics, pending capacity
  and a combined cost envelope with each initial burst counted once. Runtime
  queue retention, concurrent producers, actual wakes, enough service turns and
  runtime simulation remain open. This supplies no wall-clock
  cleanup bound, queue-memory bound or bound on enqueue, empty-turn or executor
  overhead.

- Module 46 permits arbitrary finite varying-fuel turns, including zero. It
  preserves exact queue and dispatched-state semantics. An original prefix
  is serviced when cumulative delivered fuel equals its length plus natural
  slack; later dispatched events can further change the resource state.
  Dispatch count is bounded by summed fuel, pending capacity is preserved,
  and the cost envelope counts each initial burst once. Runtime fuel delivery,
  actual wakeups, queue growth, enqueue and empty-turn costs, and wall-clock
  latency remain separate obligations. The theorem does not guarantee enough
  fuel will be delivered or certify an infinite schedule.

- Module 47 admits only the arrival prefix that fits a fixed queue-entry cap
  before each poll, retains old backlog and reports an explicit rejected suffix.
  An initially fitting queue stays within its cap across finite schedules.
  Filtering preserves delivered fuel, conditional service of original queued
  prefixes, exact dispatched-state semantics and the combined dispatch-cost
  envelope. Entry count is not a byte bound. Offered-batch construction,
  admission, rejection and storage costs remain outside that envelope.
  Newly offered cleanup, maintenance, clock and publication events may be
  rejected; safe delivery or loss/retry semantics require runtime refinement.
  No service guarantee applies to rejected arrivals. Real fuel delivery,
  wall-clock latency, cap changes and restart remain open.

- Module 48 additionally bounds a fixed sum of immutable per-event payload
  charges, alongside the entry cap, before dispatch and across finite schedules
  when the corresponding initial bound holds. Exact overflow accounting,
  conditional original-prefix service and the execution envelope are preserved.
  Concrete storage dominance and non-forgeable charges remain assumptions.
  Offered and rejected batches, temporary selections, proof certificates,
  allocator overhead and charge/admission work are outside the retained-payload
  bound. Both limits can reject mandatory events. Safe delivery, runtime fuel,
  wall-clock progress, mutable payloads, cap changes and restart remain open.
- Module 49 bounds the number of arrivals selected for admission inspection
  before payload and entry filtering. Accepted, rejected and unexamined arrivals
  reconstruct each offered batch exactly. Unexamined arrivals are caller-owned
  and excluded from the retained-queue bound. Queue bounds and conditional
  service of existing backlog survive scanning; this gives no progress or
  resubmission guarantee for unexamined arrivals. The per-turn cost theorem adds
  a symbolic charge for each examined event, including rejected and zero-payload
  events, to the existing dispatch envelope. Concrete scan-cost dominance,
  backlog summation, offered-batch construction, external storage, rejection
  disposal and executor work remain open. Mandatory events need a delivery
  argument under both admission exhaustion and queue overload.

- Module 51 carries the unexamined FIFO with the admitted queue/resource state
  across finite turns. Fresh batches follow retained arrivals, and examined
  work plus the final suffix reconstructs all supplied arrivals in order.
  Enough delivered scan allowance guarantees examination of an original
  deferred prefix. Entry and payload admission may still reject it. Independent
  service-fuel guarantees apply to initially admitted queue prefixes. Admitted
  queue and pending bounds survive resumption; the deferred FIFO has no modeled
  capacity bound. A whole-schedule symbolic scan and execution envelope counts
  each resource burst once. Real suffix ownership and resubmission, wakeups,
  storage and traversal costs, cancellation, restart, wall-clock progress and
  mandatory-event delivery remain open.

- Module 52 adds a fixed caller-owned deferred capacity after scanning. The
  retained deferred prefix and explicit overflow reconstruct the unexamined
  suffix in FIFO order, and the bounded handoff preserves admitted queue,
  payload and pending bounds through one filtered poll. The overflow cost is
  symbolic and does not establish concrete storage, traversal or reporting
  dominance. Atomic ownership, overflow delivery, resubmission, cancellation,
  restart, fairness and mandatory-event handling remain open.

- Module 53 composes bounded handoffs across finite schedules with fixed
  deferred capacity and scan allowance, and per-turn service fuel. The final
  deferred entry bound requires initial fit because a schedule may be empty.
  Chronological overflow is returned as output history and is excluded from
  internal resubmission. Admitted entry/payload and pending bounds survive.
  Recursive disposition accounting counts examined occurrences, unexamined
  overflow occurrences and the final deferred FIFO; examined rejections are
  included. It does not prove unique event identities, external delivery,
  fairness, whole-process memory bounds or concrete cost. Output history may
  grow without bound. Ownership, restart and mandatory-event handling remain
  runtime obligations.

- Module 54 proves conditional examination of a fitting original deferred
  prefix through bounded handoffs with exactly one ingress scan per turn.
  An explicit turn-count premise supplies enough turns; the model does not
  deliver them. Arbitrary later arrivals can overflow, and dispatch fuel may
  be zero. Exact prefix equations preserve FIFO occurrences, but examination
  can still end in admission rejection and does not imply dispatch. The general
  fixed-allowance scan bound counts examined events, excluding concrete CPU,
  allocation, enqueue and overflow work. Runtime fuel delivery, ownership,
  storage, mandatory-event handling and real-time service remain unproved.
  Service with larger or varying scan allowances and changing capacity also
  remains outside this slice.

- Module 55 independently selects paused or one-scan turns. A pause still
  performs bounded deferred retention and overflow reporting. Exact prefix
  equations count delivered scans, and full examination requires enough scans
  as well as capacity fit. Dispatch fuel is preserved independently. The final
  deferred bound includes an initial-fit premise for an empty schedule.
  Occurrence-count bounds exclude concrete processing and storage costs.
  Runtime scan delivery, admission, dispatch, mandatory-event handling and
  latency remain unproved. Larger scans, changing capacity, cancellation and
  restart remain open for this paced schedule.
- Module 56 composes paced handoffs with abstract payload-filtered execution.
  Queue entry and payload bounds each require initial fit; the deferred bound
  also requires initial fit, including for an empty schedule. Pending occupancy
  remains bounded by the original pool capacity. Recursive examined, overflow
  and terminal deferred occurrence counts sum to the initial deferred count
  plus all fresh arrivals, without initial fit. This is a count identity; it
  does not prove unique event identities or trace-level conservation. Examined
  events can still be rejected by admission.
  The dispatched trace satisfies the existing conditional dispatch, policy-work
  and handshake cost envelope under initial credit bounds. Concrete scanning,
  admission, retention, overflow, output storage and real-time progress remain
  outside that envelope. The executor is an abstract model, with no new runtime
  refinement or deployment evidence.

- Module 57 composes symbolic examination/admission, offered-item handoff and
  per-turn charges with the paced dispatched-work envelope. Its visit bound
  uses actual initial deferred length and all fresh arrivals, then fixed
  deferred capacity for subsequent turns. It charges repeated retention during
  pauses and includes oversized overflow, without an initial-fit premise.
  All six weights require concrete domination in a common unit: admission and
  rejection, charge computation, all handoff passes, concatenation, retention,
  overflow transfer, fixed overhead and backlog measurement must be covered.
  Arbitrarily large offered batches can still require arbitrarily large work.
  The theorem does not establish runtime CPU, output-history storage, external
  batch construction, executor scheduling or latency bounds. The inherited
  execution envelope still requires initial work and handshake credit bounds.

- Source-table churn preserves supplied rate debt and bans in a fixed slot vector.
  Runtime refinement must establish canonical validated keys, unique initial
  bindings and complete security-state classification, including simultaneous
  restrictions. Selected-cell charging refuses missing and unvalidated sources,
  its tracked restriction refuses banned and exhausted sources, and a validated
  cell charge is the restriction-trace charge step; restriction traces preserve
  a fixed per-source debt bound. Trusted debt and ban expiry assume a validated
  source, current restriction generation and deadline; the model does not check
  timer provenance or stale callbacks itself. Keyed source-system traces now
  compose lookup, churn and restriction updates, preserving initial slot width
  and a debt bound for every resident supplied by the initial quota witness.
  Lookup and update select the first matching key; runtime canonical extraction,
  unique bindings and atomic enforcement before work still require refinement.
  Source-admission traces couple source charging, shared credits and pending
  reservation in one atomic step. Refusal leaves the state unchanged; completion
  preserves source restrictions and global credits. Internal receipts bind a
  slot index and generation to the successful attempt's pre-state. The raw plan
  and commit helpers are not separate runtime APIs. State bounds require fixed
  configuration and initial credit/debt bounds where stated. Cumulative starts
  counted from emitted receipts cannot exceed initial shared credit plus trusted
  issuance. The closed timed trace language issues exactly rate credits per
  trusted tick before clamping, giving a burst-plus-rate bound when initial
  credit is within burst. A supplied cost weight bounds accepted-start work;
  it does not account for rejected attempts or other resource classes.
  Arbitrary pending prefixes and suffixes now have enabled admission, exact
  receipt, counting, completion and refusal proofs. They preserve unselected
  leases and reject mismatched generations, including stale receipts after reuse.
  Fixed runtime slot identities, internal receipt provenance and atomic callback
  behavior still require refinement; the prefix representation is a model of
  indexing, not a proof about Rust storage or ConnectionId mapping.
  Policy/source traces now validate current policy receipts before that same
  admission step. They preserve the indexed admission equations, resource bounds
  and receipt-counted rate and cost envelopes across policy changes. Policy
  receipts and completion receipts have distinct internal provenance obligations;
  the composed model does not authenticate their raw constructors. Policy
  validation and resource enforcement must linearize together in the runtime.
  Live per-source pending attribution, established resources, real clock
  correspondence, bounded retention and restart persistence remain open.
  Overflow refusal does not prove honest-source admission or reconnect fairness.
- Poll fuel bounds processed events and conserves the retained backlog. A model
  wakeup flag does not establish correct waker registration, executor fairness,
  traffic admission opportunities or wall-clock progress.
- Pending slots carry generations. Arbitrary serialized traces preserve capacity,
  and stale completions cannot release a later generation. The Rust mapping must
  establish atomic transitions, owned callback tokens, complete terminal-path
  handling and safe machine-counter wrap behavior.
- Critical service progresses within a bound on completed service rounds.
  The implementation must preserve the modeled FIFO rank and perform the promised
  critical service each round. Consensus progress, catch-up performance, permit
  hold times and wall-clock scheduler fairness are separate obligations.
- RPC constructors represent already parsed requests and responses. Actual JSON
  parsing, proxy identity verification, HTTP status mapping, retry timing and
  origin isolation require implementation evidence.
- Firewall flags describe per-identity inclusion. Address expansion, ports,
  rule order, notrack behavior and mitigation products require their own checks.
- Gate booleans express a necessary evidence policy. No model term creates the
  measurements or establishes that an operator report is truthful.

The compiler proves the model statements actually written. It does not prove
that the statements fully capture prose, that Rust executes the model, or that
the network satisfies the environment assumptions. `--require-complete`
therefore remains blocked. Simply adding a JSON status or a theorem name cannot
promote a claim to implementation-proved or deployment-qualified.

## Pre-validation allocation and cost boundary

Module 78's pre-validation envelope assumes one finite queue shared by both
swarms and at most one active ingress workspace. Queue shape counts allocated
cells; occupied cells carry bounded packet payloads. `entryBytes` must dominate
cell metadata, and `byteCap` must dominate copied payloads and the entire active
packet/parsing/token workspace. The runtime must enforce packet, parsing, token
and poll-fuel budgets and serialize the shared queue. Queue examination is
charged at one abstract unit per cell; work units require runtime dominance.
Decision outcomes and outer-event flags are supplied classifications.

Arbitrary finite traces bound occupancy, retained payloads and explicit
metadata/payload/workspace allocations independently of pending and established
caps. All decision outcomes and silent paths receive parsing, token and queue
charges, and overflow arrivals receive packet and queue charges. Per-trace and
per-poll bounds do not establish wall-clock rate, eventual service, concrete
allocator bounds, protocol verification or runtime scheduling. These external
premises remain open in the sealed ledger after M002's model closure.

## Shared population allocation boundary

Module 80 grants each finite participant occurrence a separately owned vector
of weighted pools. The sum of all slices must fit the one supplied host vector.
Honest-peer, connection, worker and reconnect-burst capacities and per-entry
weights are explicit model parameters, with no selected production constants.
All routing paths must use these slices. Identity changes retain charges, and
population reconfiguration needs a new aggregate-fit witness.

Weights must dominate concrete allocations. Per-interval work must include
administrative, denial, overflow and cleanup work, and the runtime must enforce
the clipping budget before exceeding its slice. Work coordinates have their
own units and supplied host allocations. The model's per-interval work bound
does not prove cumulative rate or scheduling fairness. Supplied source labels
do not prove IP/prefix normalization. Concrete resource vectors, shared
runtime routing, calibration and deployment guarantees remain external or
separately open model obligations. Module 85 separately covers M013 timed
rate counts. M012 is covered at R03 turn 15.
E022 owns established-resource routing and work-budget enforcement. E013 owns
runtime pending accounting. E010 owns calibration and deployment guarantees.

## Endpoint routing refinement boundary

Module 81 assumes all listener/dial endpoints and swarms use one finite serialized
routing table. A connection identifier names a global slot and nonwrapping
generation. Internal callback provenance must prevent unowned reservation,
establishment and terminal transitions. The supplied validation flag must certify
the actual selected migration destination; generation matching alone grants no
address authority. Atomic migration retains the original endpoint owner.

Success retains established routing. Terminal cleanup represents actual
connection termination and removal of its routing state. A vacant slot holds one
fixed-width generation tombstone; migration replaces the current endpoint instead
of retaining old endpoint history. Fixed-width identifiers, generations and cell
metadata must dominate these retained-cell counts in concrete storage. Any extra
queued callbacks, routing aliases or endpoint histories require their own bound.

Arbitrary finite schedules bound live and discarded routing cells under every
event ordering. They do not prove fairness, eventual service, byte allocation,
runtime uniqueness or a selected socket layout. E019 owns refinement of these
premises and affected transport, maintenance, compatibility and deployment
regressions. The sealed external ledger remains open after M021 model closure.

## Normalized attribution refinement boundary

Module 82 accepts IPv4, mapped IPv4 and IPv6 address constructors with supplied
prefix and host components. The runtime must extract those components from the
actual address under a fixed prefix policy. The mathematical even/odd namespaces
are injective within each family and disjoint across families. Mapping machine
addresses to these keys requires nonwrapping encoding and a unique canonical
source table. Peer identity and caller-selected key inputs cannot change the
selected normalized key. Host components share their supplied prefix bucket.

Validated reachability must certify the actual address. Penalty classification,
eviction and trusted expiry are internal decisions for that same canonical key.
Clock issues and generation-owned completion receipts retain the existing
authority assumptions. Source quota and shared credit bounds require their
stated initial-fit witnesses; the aggregate pending bound holds for every initial
pool. All attributed events route through one serialized shared admission state.

Module 82 witnesses M003's normalized-attribution criterion. Module 83
composes trusted-exemption and privileged-allowance provenance and closes the
remaining model criterion. Module 84 closes M009 with multi-prefix overlap and restart/epoch security
lifetimes. Module 85 covers the distinct timed prefix buckets of M013. E014 owns runtime normalization,
validation, exemption and lifetime refinement. E013 owns concrete pending
accounting, receipt authority, atomicity and storage dominance.

## Trusted source authority refinement boundary

Module 83 accepts classified reachability, authentication and listing judgments
with captured normalized-key and identity bindings. Their construction must
certify the actual address and authenticated peer. These supplied judgments are
not cryptographic proofs or runtime certificate checks. E014 owns canonical
address parsing, validation, captured authority bindings and exemption rules;
E029 owns authentication/listing enforcement and runtime privilege provenance.
The allowance table is provisioned independently, shares the canonical source
namespace, and has a fixed supplied budget. Requests cannot register their own
allowance entries. Runtime provisioning, unique keys and serialization remain
refinement premises. Changing a caller-selected key confers no authority.

The load-pressure exemption preserves validated protocol penalties. Privileged
admission retains ordinary source quotas, shared credits and pending capacity;
only admitted receipts debit an allowance. E013 owns atomic resource/allowance
updates, receipt authority and concrete pending accounting. Initial-fit premises
are explicit for source debt, credit and allowance trace bounds. Aggregate
pending bounds hold for every initial pool. No timed prefix-rate or restart/epoch
claim follows from fixed-budget allowance accounting. Module 84 closes M009; module 85 later covers M013.

## Source security lifetimes

Module 84 grants a correctly classified fixed-prefix `SourceAddress` and one
shared, serialized finite security table for T4b and T8. The modeled restart
and epoch transitions preserve protected keys, debt payloads and bans and
advance natural-number lifecycle counters. Concrete persistence/restoration
across process restart, counter nonwrapping, prefix parsing and shared-table
storage refinement remain E014 obligations. E029 retains peer lifecycle
refinement. A model restart retaining an abstract table is no proof that the
deployed process restores that table.

Protected state cannot expire merely because an identity re-registers, a safe
eviction is attempted, a process restarts or an epoch changes. The churn trace
contains no authorized debt service, ban expiry or new penalties. Those
transitions require the earlier trusted policy and runtime release authority;
the lifetime proof neither defines wall-clock expiry nor grants release to
untrusted callers. The initial protected cells and payloads may be arbitrary.
Correctly restoring their projection is necessary for the proved persistence.
Rate fairness and production limits remain separate model/external work.

## Joint source-rate refinement boundary

Module 85 supplies distinct aggregate and per-canonical-prefix start-count
envelopes for arbitrary serialized traces, shared across both swarms, trusted
traffic and fresh identities. Each view requires its stated initial-credit fit.
Burst/rate policy and the finite source-slot allocation stay fixed in a trace.
The zero-source refusal theorem explicitly locates the selected slot using a
normalized-key/index equality. An allocation-miss theorem locates any absent
key through a normalized-key equality with array width plus an offset.
Source-slot misses deny rather than allocate.

`SourceAddress` and `Reachability` must certify actual fixed-prefix parsing and
validation. The runtime's sparse ledger must refine the mathematical canonical
array's lookup, debit and capped refill. Prefix-bucket identities and spent
credits must survive churn; replacing a slot or process epoch cannot create
unmodeled credit. Only actual trusted ticks may issue the supplied per-tick
allowances. Untrusted timestamps, completion and failure cannot issue credit.
The runtime must preserve the other admission guards represented by eligibility
and commit the aggregate/source debit atomically with its admitted receipt.

E014/E013/E010 retain their source, accounting and calibration refinements.
Clock authority, serialization and initial fits are explicit premises, not
validated deployment evidence. The bounds count admitted starts; pre-accept
work, resident bytes/tasks, real-time fairness and critical scheduling have
separate resource/refinement obligations. M012 was the open R03 model work
until turn 15.

## Established resource-vector refinement boundary

Module 86 witnesses M012's resource and resident-domination criteria
under explicit runtime premises. Every connection, QUIC stream/credit,
request-response, negotiating/Kademlia substream, byte and task allocation must
route through the corresponding bank and direction in the one finite owned
population. Runtime objects must have unique peer/bank/slot ownership, and all
swarms and trusted traffic must use the same composed process allocation.
Changing trust, identity or swarm labels must retain the charged banks.

Internal terminal and shedding receipts must carry the correct peer, bank,
slot and generation token. Updates must be serialized, generations must not
wrap, and freeing a slot must end the associated resource lifetime. Otherwise
the abstract exact-owner release and resident occupancy bounds cannot refine
runtime cleanup. The established path must preserve independently owned pending
leases and pre-accept work. The process-state witness holds by construction and
does not model stage interaction.

Reserved byte/task weights must dominate supplied actual per-active-slot cost
upper bounds, including transient overlap. Fixed/shared storage, idle containers
and process tasks have separate symbolic overhead bounds and domination
certificates. Their reserved overhead plus every peer's resource vector must
fit the same finite process resident allocation. Runtime measurement must
justify the unit and overhead upper bounds. Advertised receive credit supplies
no premise for resident bytes or tasks; those are separate coordinates.

E022 retains established-resource classification, routing, cleanup and cost
refinement. E013 retains runtime pending/phase accounting and receipt/atomicity
boundaries. E010 retains production cost calibration and deployed domination.
All remain external. Modules 87-89 witness M012 criterion 1 stage accounting
between pending, pre-accept and established resources. Criterion 2 required
a modeled critical-service guarantee under explicit workload/scheduling
premises until turn 15. Module 90 supplies it, and R03 closes.

## R03 turn 12: stage-accounting boundary

Module 87 assigns each modeled resource one phase-scoped, generation-owned
reservation. A handoff conserves the reservation and moves its stage charge;
completion requires the current stage and generation. The partition and trace
bounds cover arbitrary finite ledgers. Their runtime interpretation requires
unique event routing, serialized transitions, trusted receipt provenance and
nonwrapping generations. Any resident-cost interpretation also requires the
supplied unit certificate to dominate the resource throughout all three
phases, including overlap or transient storage at a real handoff.

One carried reservation is not a proof of release and acquisition between the
existing distinct stage pools. Modules 88-89 supply that model bridge,
including generation consumption, replay refusal and stale callback behavior.
Criterion 2 retains scheduling service. E013, E022 and E010 continue to own
runtime accounting, cost domination and calibration. No external obligation
or qualification guard closes in this turn.

## R03 turn 13: distinct-stage promotion boundary

Module 88 couples the existing distinct pending, pre-accept and established
states. A single serialized promotion checks pending generation ownership and
established vacancy against the original state. Its model transition preserves
pre-accept work, completes the pending lease and reserves the selected distinct
established slot. Repeating the actual guarded promotion preserves the whole
resulting state. Raw successful pending callbacks cannot release pending
ownership independently; they must use the guarded promotion event.

Runtime classification and routing must send every stage event through these
accounts. Internal generation receipts, nonwrapping counters, atomic guard and
update execution, actual resource termination and cost domination for supplied
stage weights remain premises owned by E013, E019, E022 and E010. The model
does not establish a runtime implementation bridge or calibration.

Successful head promotion pins independent generations and arbitrary suffixes.
Module 89 adds arbitrary-prefix/suffix promotion and all absent-index operational
witnesses, closing M012 criterion 1; critical workload/scheduling service remains
criterion 2. No external obligation or qualification guard closes.

## General promotion boundary

Module 89 derives promotion success and refusal at arbitrary positions in the
existing coupled process. Guard equality is a proved intermediate fact for the
operational witnesses. The stale case explicitly assumes that the supplied
generation differs from the held generation; it does not assume refusal.
The success equation preserves every unselected account and the executor.

Runtime classification/routing across pending, pre-accept and established
resources remains E013, E019 and E022. Atomic execution, receipt authority,
nonwrapping generations, actual resource termination and stage-cost domination
(including E010) remain external. M012 criterion 1 closure provides no critical
scheduling guarantee. Module 90 witnesses criterion 2 at turn 15. Deployment
qualification remains open.

## R03 turn 15: protected critical-service boundary

Module 90 derives FIFO service for every target in a finite captured window.
The premises are: each target and its predecessors already occupy slots of the
selected kind and direction; no arrival overtakes a target; the targets stay
eligible; each delivered tick has a budget that covers the scan and job charges
of every peer; the scheduler delivers at least the workload maximum in ticks.
The model treats each delivered tick of a funded eligible peer as one completed
service round. Runtime job completion is not proved.

Bulk, pending and pre-accept work runs in the module-88 coupled process. The
schedule projection keeps bulk events off the critical fleet, and critical
ticks do not change a bank. These separations hold by construction of the
model. They are premises for the runtime, not results.

Runtime routing, nonaliasing, atomicity, receipt authority, nonwrapping
generations, cost domination, resource termination, tick delivery and scheduler
conformance remain external (E010, E013, E017, E019, E021 and E022). M012 is
covered and R03 is closed. No external obligation or qualification guard
closes.

## R04 turn 1 policy-union boundary

Module 91 checks exact five-source membership construction for each modeled
node role and primary/worker swarm, authenticated Closed admission, Open defaults,
verified targeted updates and complete-state preservation under provisional
updates. Its membership vectors already represent verified identities.
The runtime must preserve identity indexing and correctly classify every
committee, trusted and bootstrap input; an `on` verification flag is a supplied
judgment. Profile-change events represent authorized operator configuration.

Generation advances on every role replacement and on every verified roster
update, but the module has no receipt or compare-and-publish protocol. It queries
a current immutable view in a serialized model. Module 92 adds the distinct
inbound/outbound gates and intervening revisions in R04 turn 2 (see below).
M006, M039 and M042 retain fallback isolation, recovery closure and consistent
reload/removal lifecycles. Extending the finite worker configuration does not
prove a bounded runtime allocation cost. E029 retains policy and record
refinement. Turn 1 covers M022; R04 and all external obligations remain open.

## R04 turn 2 lifecycle-revision boundary

Module 92 checks distinct inbound admission, outbound dial and outbound
established decisions against the current immutable authority. Each decision
receives that authority atomically in an ordered model execution. An approved
dial carries its generation, role, swarm and identity. Establishment refuses a
receipt that does not match the current generation and query context, and it
queries the current authenticated policy again.

The runtime must capture the current authority atomically and publish views
without a stale-use race. It must keep identity indexing faithful, supply
current authentication, classify roster updates correctly and authorize profile
events. Model generations are unbounded natural numbers. The runtime must
persist generations and must not wrap or roll them back. An approved dial
constructor is not a receipt provenance certificate. E029 retains these runtime
obligations. M024 retains independent bounded privileges. M040 retains
live-connection sweeps. M022 and M023 are covered; R04 and all external
obligations remain open.
