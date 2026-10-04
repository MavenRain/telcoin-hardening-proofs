# R03 admission boundary, turn 14

R03 is active after fourteen execution turns. Turn 1 closed M004, turn 2 closed
M001 with authentication and reachability composition, turn 3 closed M002
with a pre-validation envelope, and turn 4 closes M011 with unlocked handshake
execution, ownership and host envelopes. Turn 5 closes M007 with arbitrary
population and resource/work composition. Turn 6 closes M021 with endpoint
routing, migration ownership and finite discarded-state bounds. Turn 7 witnesses
M003's normalized-attribution criterion. Turn 8 closes M003 with trusted exemption
and privileged-allowance provenance. Turn 9 closes M009 with normalized source
churn, shared T4b/T8 security and explicit restart/epoch lifetimes. Turn 10
closes M013 with joint aggregate and canonical-prefix timed rate envelopes.
Turn 11 witnesses M012 criteria 0 and 3 with established resource vectors,
owner-specific release and resident domination. Turn 12 adds a unified
reservation ledger with exact stage partitions and phase-scoped receipts.
Turn 13 couples the existing distinct pending pool, pre-accept executor and
established fleet. General nonpromotion isolation, guarded refusal and promotion
idempotence hold; a focused successful promotion pins the release and grant.
Turn 14 closes criterion 1 with arbitrary-prefix/suffix successful promotion and
all absent-index operational witnesses. Criterion 2 retains critical
workload/scheduling service as its exact remaining gap.
M005 was already covered by R02.
The audit covers ten of 83 model obligations, retains 73 exact gaps, and leaves all 43 external obligations
open. The frozen scope,
obligations, packet assignments and qualification guards remain intact.

| Obligation | General evidence | Scope and assumptions |
|---|---|---|
| M001 | Existing general unvalidated Retry refusal; module 76's invalid-evidence complete-state no-op and unvalidated-address preservation; module 77's authentication grants and clearing, arbitrary mixed-trace erasure and authority projections, post-authentication reachability traces and privilege-gate preservation. | Correct classification of runtime address and identity evidence is granted. Cookies and signatures are token-validation and cryptographic premises. E008 and E020 own their runtime semantics, M014 to M017 own detailed protocol authentication, and E029 owns runtime listing and privilege enforcement. |
| M002 | Module 78's arbitrary mixed-trace queue, retained-byte and transient-allocation bounds; exact packet/queue/parsing/token charges and arbitrary finite-fuel poll work bounds. | Finite shared allocation and enforced budgets are modeled. Runtime storage/work dominance, serialization, workspace lifetime and supplied outcome classifications remain external. E008 owns the transport queue, budget, serialization, workspace and outcome premises. E010 owns deployed storage and work dominance. Later pending and established caps supply no premise. |
| M003 | Modules 82 and 83 compose normalized source attribution, complete-state unvalidated and mismatched privilege refusal, admitted-receipt allowance debits, trusted load exemptions, active protocol penalties and arbitrary mixed-trace accounting/pending bounds. | Classified reachability, authentication/listing, captured key/identity bindings and allowance provisioning are supplied judgments. E014, E029 and E013 retain runtime authority, privilege and pending refinement. Initial source/credit/allowance fit is explicit; pending bounds hold for every initial pool. |
| M004 | Module 75's arbitrary-pool and arbitrary-index exhaustion bridge, composed complete-state admission refusal and receipt absence; existing arbitrary PoolTrace and SourceAdmissionTrace bounds, conservation and fixed structural capacity. | Exhaustion means zero total leaseAvailability, including empty pools and missing indices. Runtime receipt authority, stable indices, serialization, nonwrapping generations and storage dominance remain external. E013 owns them. |
| M009 | Module 84's arbitrary normalized-source lifecycle traces preserve complete protected debt/ban cells and selected T4b/T8 restrictions, bound cardinality by initial fixed width, and make registration identity-independent and restart/epoch lifetimes explicit. | One shared fixed-width table, classified fixed-prefix addresses and serialized transitions are modeled. Protected state survives restart/epoch boundaries; debt service and ban expiry are outside these churn-only traces. E014 owns runtime restoration, prefix classification, release authority and nonwrapping lifecycle counters. E029 owns peer lifecycle refinement. |
| M013 | Module 85 supplies joint aggregate and normalized-prefix burst-plus-trusted-ticks envelopes over arbitrary mixed traces, with exact paired receipts and whole-state refusal/terminal witnesses. | Fixed finite canonical-key allocation, correctly classified address/reachability, supplied eligibility, serialized atomic updates, trusted ticks and each view's initial-credit fit are explicit. Runtime refinement and calibration remain external; resident resource vectors and scheduling remain M012. |
| M012 | Module 86 derives protocol/direction and resident coordinates from one finite peer/bank/slot population; arbitrary mixed traces preserve one process vector, exact arbitrary-prefix releases isolate the owner, and certified byte/task domination includes separately reserved overhead. Advertised receive credit is independent of resident weights and costs. | Correct runtime classification/routing, internal receipt authority, serialized updates, nonwrapping generations, actual resource termination, symbolic unit/overhead domination and initial vector-plus-overhead fit are premises. E022/E013/E010 retain runtime refinement. Critical service under workload/scheduling premises remains a model gap in criterion 2. |
| M011 | Module 79's arbitrary endpoint/swarm trace bounds for separate waiting and active banks, conditional refused/permitted dispatch transitions, generation-owned terminal releases, shared weighted host allocation and charged work envelope. | All endpoint work routes through the same banks. Atomic transfer, internal callback provenance, nonwrapping generations, actual task termination on terminal release, and runtime resource/work dominance remain E019 premises. No mutex or fair scheduling is assumed. |
| M007 | Module 80's arbitrary finite population and weighted-coordinate bounds, allocation preservation under mixed ownership/churn traces, retained charges on identity changes, and per-interval clipped work composition. | Every participant receives a separately owned slice whose sum fits the one supplied host vector. Connection and reconnect-burst parameters are member counts, bank weights and bank capacities in this arbitrary fleet. A burst in one interval is any finite trace of hostEvent and hostChurn steps over the fixed population. M013 owns burst-plus-rate budgets across intervals. Runtime routing, weight dominance, work-budget enforcement and production calibration remain external. E022 owns established-resource routing, weight dominance and work-budget enforcement. E013 owns runtime pending accounting. E010 owns production calibration and deployed storage and work dominance. Labels do not establish source normalization; specific established resource vectors remain M012 work. |
| M021 | Module 81's unique connection lookup, exact indexed update and other-slot preservation; generation-owned migration, establishment and terminal cleanup; arbitrary schedule capacity, live-cell and discarded-tombstone bounds and exact conservation. | All endpoints and swarms share one finite serialized routing table. Internal callback authority, destination validation, nonwrapping generations and fixed-width storage dominance remain E019 premises. Migration preserves the original endpoint owner; handshake success retains established routing. No fairness or concrete socket restructuring is proved. |

The saturation proof recurses over the entire LeasePool. A free cell contradicts
zero availability; a held cell permits either local refusal or induction into
the suffix at the predecessor index. Existing source admission and receipt
theorems carry token absence to the complete modeled admission state.

Authentication replaces the identity flag with its classified verification
result and sets privilege only when verification and listing status both hold.
Rejected authentication clears both flags. Accepted authentication of a listed
identity grants both flags. Authentication preserves address reachability.
These general complete-state statements ensure that authority can change in
the model and that mixed-trace preservation has substantive granting behavior.

An arbitrary finite authority trace can interleave valid and invalid address
evidence with authentication successes and failures. Erasing address
reachability from its result produces exactly the authentication-only execution
from the same initial identity and privilege flags. Thus reachability events
contribute no authority changes, including between authentication transitions.
Any finite reachability trace after authentication retains that authentication
result. A privilege-requires-identity invariant also survives arbitrary mixed
traces when it holds initially. Arbitrary inconsistent initial flags do not
receive this last invariant without its explicit premise.

Module 76's local preservation results still concern a reachability-only model.
Module 77 supplies the composition needed to close M001. Its classified flags
do not implement evidence verification, cryptographic authentication or runtime
privilege enforcement.

Eighteen new mutation controls cover verification and listing bypasses, lost
authentication grants, authentication changing reachability, incorrect mixed
event dispatch, skipped trace events, projection errors and lost initial
authority during erasure. Together with turn 1's eleven controls, they must
reject with semantic typechecking diagnostics. They constrain the modeled
transitions and proof statements; runtime fault injection remains external.

## Pre-validation queue, allocation and work envelope

`proofs/78-prevalidation-envelope.mech` closes M002 at its sealed model scope.
One finite queue serves both primary and worker ingress before address validation.
Each cell is vacant or holds a packet payload with an explicit byte-capacity
witness. Arrival fills the first vacancy with at most `byteCap` copied bytes;
it discards overflow without allocating another cell. Decision cleanup searches
past vacant cells and releases the first occupied payload for every Retry,
Refuse, Ignore and Accept outcome, including Accept without an outer event.
Queue shape represents allocated cells, so cleanup releases payloads while
preserving the finite cell allocation. No pending or established cap appears
in this model or its allocation and cost proofs.

For every arbitrary finite trace, allocated cell count remains equal to its
initial value `slots`. Occupancy is at most `slots` and retained payload bytes
are at most `slots * byteCap`. Explicit transient allocation counts every
allocated cell's metadata, actual retained payloads and one active ingress
workspace. Its bound is `slots * entryBytes + slots * byteCap + byteCap`.
`entryBytes` must dominate all cell metadata, and the workspace `byteCap` must
dominate the entire active packet, parsing and token workspace. These storage
dominance and single-workspace lifetime premises require runtime evidence.

Arrival charges bounded packet capture and queue examination, even on overflow.
Each decision charges queue examination, parsing and token processing whether
or not it emits an outer event. Queue examination costs at most one abstract
unit per allocated cell. Packet capture, parsing and token work stop at their
supplied budgets. A trace with `events` incoming transitions therefore costs at
most `events * (byteCap + slots + parseCap + tokenCap)`. A poll processes at most
its finite `fuel` count and costs at most the same per-event envelope times
`fuel`; zero fuel performs no work. This is a finite trace and poll envelope,
not a wall-clock rate, fairness or eventual-service result.

The module adds 33 general proof declarations: eight arbitrary-trace witnesses
and 25 general-transition witnesses. Its 37 mutation controls cover overflow
allocation, uncapped payloads, deep queue searches, packet release on each
outcome and silent paths, worker admission, retained-byte and metadata/workspace
accounting, missing or excessive packet/parsing/token/queue charges, understated
budgets, skipped trace transitions and charges, and fuel-prefix errors. Every
control must fail with a semantic type mismatch rather than a parse failure.

Outcomes and event-emission flags are supplied classifications. Runtime queue
sharing, serialization, allocation layout and lifetimes, cost dominance and
enforcement of the byte, parsing, token and poll budgets remain external.
The model does not verify evidence classification, protocol acceptance,
cryptography, scheduling or actual object allocation.

## Unlocked handshake execution and host envelopes

Module 79 models waiting jobs and active executors in separate fixed-width
LeasePools. Every endpoint identifier and either swarm uses the same two banks.
Dispatch requires a matching held waiting generation and a vacant active target.
The atomic transition releases that waiting owner and reserves the active slot.
A refused dispatch preserves both banks at arbitrary indices and generations.
For each terminal reason, the audited proofs show that release at the second
slot with generation zero frees only that owner. Stale waiting and active
callbacks preserve the newer owner at the head slot against its immediate
predecessor generation. General trace bounds cover every finite interleaving and
initial bank state; the proofs require no accept/endpoint mutex or fairness
premise.

For arbitrary waiting and active resource weights, the summed resident charge
stays within the two banks' single host allocation. Each event charges fixed
administrative work, two passes over both finite banks, and capped execution
demand. Zero-demand and one-event witnesses prevent silent charge deletion.
The arbitrary trace work theorem uses the initial host event budget and counts
every event, including denial, overflow and terminal cleanup.

E019 must establish complete endpoint routing, atomic reservation/transfer,
internal token provenance and nonwrapping generations. It must also show that
weights dominate actual allocations and work, and that active terminal release
means the worker has stopped and released its resident resources. Cancellation
requests must retain their charge until that terminal event. The model proves
bounded ownership and accounting; executor fairness and service delivery remain
outside this obligation. The 24 new controls reject weakened lookup, dispatch,
terminal release, allocation and work accounting.

## Arbitrary population and shared host composition

Module 80 models an arbitrary finite list of honest, worker, reconnect and
distributed participants. Each carries supplied swarm/source/identity labels
and an arbitrary finite vector of weighted LeasePools. Pool capacities and
weights expose connection, worker, honest-peer and reconnect-burst parameters
without choosing production constants. Every occurrence contributes to the
aggregate allocation, including repeated labels. Missing coordinates use zero.

Indexed reserve/completion actions update one member and one coordinate.
Churn changes labels while retaining the entire bank vector and its charges.
Arbitrary mixed traces preserve the sum of all slices and bound resource use
by that initial sum. A separate premise requires that sum to fit the declared
host vector at every coordinate. Fresh identities never receive an independent
copy of the host budget. Membership is fixed for the declared allocation
interval; reconfiguration must supply a new sum-of-slices witness.

Per-interval work demands are arbitrary functions of the participant index.
Each demand is clipped to its declared slice and all participants are counted.
The work allocation can use a separate fleet and host vector in its own unit.
After any mixed ownership/churn trace, these demands still fit the initial
shared host allocation. This is a budget-interval bound; runtime enforcement,
all administrative work, storage dominance, normalization, service delivery
and cumulative rate accounting need their own evidence. Thirty new controls
reject omitted swarms, duplicated slices, identity charge resets, routing and
trace omissions, incorrect weights and work-budget bypasses.

## Endpoint routing and migration ownership

[81-endpoint-routing.mech](../proofs/81-endpoint-routing.mech) closes M021 at
its sealed model scope. Listener and dial endpoints carry explicit swarm and
socket identifiers. Every connection uses one global slot/generation identifier
in a finite shared routing table. A lookup returns at most one destination.
Indexed updates change the selected existing slot and preserve every other slot.

Reservation records the same endpoint as original owner and current destination.
Validated matching migration changes the destination while retaining that owner
and pending/established phase. Unvalidated or mismatched migration preserves the
complete cell. Handshake success retains the route in the established phase.
Refusal, timeout, cancellation, failure, peer close and shedding erase only the
matching route and advance its generation before reuse. Old routing identifiers
remain absent after actual cleanup and replacement reservation.

Every finite schedule preserves the initial allocation, bounds live routes and
discarded generation tombstones separately, and conserves their sum exactly.
Vacant cells retain one tombstone each; migration retains one current endpoint
instead of an endpoint history. These are retained-cell bounds for every event
ordering. They supply no fairness, delivery or concrete byte-bound conclusion.
E019 retains runtime routing, internal callback authority, destination validation,
serialization, nonwrapping generations, storage dominance and regressions.

## Normalized source attribution

[82-normalized-source-attribution.mech](../proofs/82-normalized-source-attribution.mech)
witnesses M003 criterion 1. Addresses carry prefix and host components under one
fixed normalization policy. Native and mapped IPv4 use the same even prefix
namespace. IPv6 uses an odd namespace. General comparison laws preserve all
within-family prefix distinctions and reject every cross-family pair. Host
components never select the bucket, so shared-address peers share its debt.

Admission, registration, penalties, eviction, expiry and admission receipts use
the normalized address key. Caller-selected keys and fresh peer identities cannot
change the admission result. Unvalidated attempts, registration and penalties
preserve the complete admission state for every initial state, including its
source table, shared credit and pending pool. Clock and completion translations
retain their exact issued credit, receipt and terminal reason.

The attributed schedule has its own recursive execution. A general equality
connects every event and suffix to the existing source-admission schedule.
Every finite attributed schedule bounds aggregate pending occupancy by the
initial shared pool capacity. Selected normalized-source debt and shared credits
also stay bounded when their explicit initial-fit premises hold. These are
fixed-quota results; distinct timed prefix buckets are supplied by module 85.

The module adds 28 explicit proofs and 29 semantic controls. All controls fail
with proof type mismatches over variables, including wrong host/key selection,
family aliasing, validation bypasses, altered clock/completion evidence,
omitted or duplicated schedule events and an inflated step quota or capacity. Module 83 supplies the
trusted exemption and privileged-allowance provenance composition for criterion 0.
E014 owns runtime parsing, prefix-policy selection, validated-address evidence,
key uniqueness, trusted exemptions and lifetime rules. E013 owns runtime pending
refinement, receipt authority, serialization and storage dominance.

## Trusted source authority and privileged allowances

[83-trusted-source-authority.mech](../proofs/83-trusted-source-authority.mech)
closes M003 criterion 0. The authority record carries classified reachability,
authentication and listing judgments together with a captured normalized source
key and peer identity. All five checks must permit a privileged request. Caller
claims select neither binding nor accounting key. Unvalidated, unauthenticated,
unlisted, foreign-key and foreign-identity requests preserve the entire combined
resource and allowance state. Mapped and native IPv4 under one prefix produce
the same complete request result.

An independently provisioned allowance table supplies a fixed budget at each
normalized key. Missing, banned or exhausted allowance entries refuse without
resource work or a debit. A permitted request still uses the ordinary source
quota, global credit and pending-slot plan. Its actual pre-state admission
receipt determines the allowance debit, so refused resource admission consumes
no allowance. Ordinary registration, churn, expiry, clock and completion events
and both classified penalty causes preserve this table.

Load-pressure exemption requires the same validated, authenticated, listed,
key-bound and identity-bound authority. Every validated protocol violation still
selects the normalized ban. Unvalidated penalties preserve the full state. The
independent mixed-trace execution bridge composes every event with one evolving
resource and allowance state. General trace proofs retain the shared pending
bound for every initial pool and source debt, shared credit and selected
allowance bounds under their explicit initial-fit premises.

Thirty-seven controls weaken authority and allowance gates, bindings, normalized
keys, selected slots and swarms, exemption rules, admission receipts, state
updates and evolving trace execution. All are rejected by general proof
statements. E014 retains runtime parsing, validated-address authority, captured
bindings and exemption enforcement. E029 retains authentication and listing
enforcement. E013 retains serialized admission, receipt authority and pending
accounting. These classified inputs and allowance provisioning are supplied
model judgments. Trusted authority does not bypass aggregate pending, source
quota or shared credit caps. Module 85 now supplies M013 timed prefix rates.

## Normalized source security and lifecycle closure

Module 84 closes M009 by composing normalized IPv4, mapped IPv4 and IPv6 prefix
keys with the existing safe source-table registration and eviction transitions.
The same bounded table serves T4b and T8. Complete-state registration ignores
fresh identity and caller-key claims, refuses unvalidated registration and
preserves a first-slot normalized resident without duplication. Exact lookup
theorems select arbitrary first-slot debt, bans and joint debt/ban payloads.

A restart increments the boot generation and retains the current epoch. An
epoch boundary increments the epoch and retains the boot generation. Both
discard unprotected residents and keep all protected cells with their original
keys and payloads. Protected debt and bans live across these boundaries;
authorized debt service and ban expiry are separate trusted transitions, outside
this churn-only event alphabet. These rules assume runtime restoration of the
protected table across a process restart, as an E014 refinement obligation.

For every finite mixed registration, eviction, restart and epoch trace, the
complete protected projection is unchanged and table width equals its initial
width. Cardinality is bounded by that initial width for every initial table.
For every source address and either T4b/T8 user, the selected security
restriction is unchanged. Mapped/native IPv4 hosts share one key, and IPv6 host
changes within the fixed prefix cannot bypass the selected restriction.

Twenty-six new controls weaken normalized attribution, validation, resident
uniqueness, eviction, lifecycle retention/counters, shared T4b/T8 state, selected
restriction lookup and head/tail execution. Two controls erase debt and bans
while keeping exactly the same table width. Every control must produce a
semantic type mismatch in a statement over quantified inputs. E014 and E029
retain runtime refinement. Rate envelopes and fair shared-source opportunity
remain outside this persistence theorem; module 85 now covers M013.

## Joint aggregate and normalized-prefix timed rates

Module 85 closes both M013 criteria. `composedBurstRateEnvelope` quantifies
over either the aggregate view or any selected canonical prefix, every finite
mixed trace and every initial finite bucket array. Each view has a distinct
supplied burst and rate, and requires its explicit initial-credit fit:

- Total admitted starts are at most aggregate burst plus trusted ticks times aggregate rate.
- Starts at any selected prefix are at most source burst plus trusted ticks times source rate.

The same state transition supplies both counts. A granted attempt debits one
aggregate credit and one source credit. Missing or exhausted buckets deny;
source-slot allocation stays fixed through the trace. The array uses module 82's
IPv4, mapped/native IPv4 and fixed IPv6 prefix namespace. Changing swarm, trust
classification, peer identity, host within a prefix or a caller-selected victim
key cannot create a new bucket or avoid the debit.

Unvalidated and ineligible attempts, an empty aggregate, a missing source and a
zero-credit source preserve the complete rate state. The zero-source witness
locates the selected cell after an arbitrary prefix and before an arbitrary
suffix through an explicit normalized-key/index equality. An allocation-miss
witness quantifies over every finite table and every offset, with the normalized
key equal to table width plus that offset; it preserves every existing counter.
Completion receipts,
all pending-end reasons and downstream outcomes cannot refund rate credits.
An arbitrary claimed timestamp neither refills nor advances trusted time.

Only a serialized trusted tick refills both capped budgets. The eligibility flag
represents the other admission guards; these rate bounds quantify over every
flag rather than deriving those separate guard judgments. Runtime address
validation, sparse-index refinement, prefix-ledger persistence, atomic admission
and trustworthy clock authority remain explicit premises. Concrete costs,
resident-resource domination and critical-class scheduling remain outside these
start-count envelopes. E014/E013/E010 retain source, accounting and calibration
refinement work. Module 86 supplies M012 resource vectors and resident
domination; critical-class service remains open.

Module 85 adds 42 counted proof declarations and 34 semantic controls, all
checked against quantified statements. M013 is covered; R03 remains active.

## Established resource vectors and resident domination

Module 86 witnesses M012 criteria 0 and 3. Each finite resource bank has a
protocol kind, incoming/outgoing direction, one generation-tagged slot pool,
reserved byte/task weights, an independent advertised credit weight, and
symbolic actual byte/task unit costs with domination certificates. Connections,
QUIC streams, request-response, negotiating and Kademlia substreams each have
their own directional coordinates. Every coordinate is derived from the same
owned population, including all peers and swarms.

Every finite mixed grant, terminal and label-churn trace preserves the
allocation vector and bounds use by the initial allocation. Per-peer vectors
fit one supplied finite process vector. Trust, identity and swarm changes keep
the owned banks and their charges; no fresh population allocation is introduced
by churn. These traces model overlap through simultaneously held distinct slots.

The release proofs quantify over arbitrary peer, bank and slot prefixes and
suffixes. A matching-generation terminal releases exactly its selected held
slot, advances that slot's generation and preserves every other owner. The
wrapper binds the supplied peer, bank, slot and token. `EstablishedTerminal`
explicitly names close, cancellation, failure, timeout and shedding; all dispatch
the same owned terminal transition. Unowned and preceding-generation tokens preserve
their complete slot pools. Every established trace also preserves the complete
pending lease pool and the separate pre-accept work field. This holds by
construction because no established event can change those fields.

Advertised credit has an exact independent coordinate. Changing it cannot
change reserved or actual symbolic resident byte/task unit costs. Per-slot
domination lifts through every bank and peer to arbitrary-trace resident bounds.
Fixed/shared storage, idle containers and process tasks have separate supplied
overhead bounds and reserved capacity; they are charged even with zero occupied
slots. The overhead theorem requires its explicit domination certificate and
initial overhead-plus-vector fit. E022/E013/E010 retain runtime routing,
receipt, termination, cost and calibration refinement.

The module adds 35 counted proof declarations and 36 semantic controls. The
controls weaken category/direction distinctions, coordinate selection, resident
costs and overhead, complete bank/peer sums, indexed update isolation, trust
charging, churn retention, trace execution, receipt binding and pending/pre-accept
field pass-through. Every control must fail with a semantic type mismatch over quantified inputs.

## Unified reservation stage accounting

Module 87 carries one reservation through pending, pre-accept and established
phases. Each cell retains its protocol, direction, certified unit and
generation-tagged lease. Acquisition starts a free cell in pending; acquiring a
held cell preserves it. Handoff requires the expected phase and the current
owned generation. Two adjacent successful handoffs reach established without
changing the underlying lease or its resource charge.

`stagedLedgerPartition` proves that the three stage totals equal the erased
resource-vector charge for every finite population. `stagedPartitionTraceBound`
and `stagedProcessVectorBound` bound arbitrary mixed traces. The latter requires
the initial allocation to fit the supplied process budget. Handoff preserves
the complete erased bank population, and arbitrary-prefix/suffix theorems bind
acquisition, handoff and terminal dispatch to the selected cell.

Completion requires the matching stage and generation, advances the free
generation and is idempotent across terminal reasons. Old pending receipts do
not release pre-accept resources, and old pre-accept receipts do not release
established resources. Unowned, free and preceding-generation handoffs preserve
their resources. The 25 controls test these operational rules, trace routing,
ledger isolation and stage partitioning against general statements.

This ledger moves one reservation between phases. Modules 88-89 connect the
existing pending pool, pre-accept executor and established fleet, and release a
pending lease while granting a distinct established lease. Their combined
evidence closes M012 criterion 1. Runtime interpretation requires atomic transitions,
correct receipt routing and cost bounds that dominate every phase. Advertised
credit remains separate from resident bytes and tasks.

## Coupled distinct stage accounts

Module 88 uses the existing `LeasePool`, `ExecutorBank` and `EstablishedFleet`
as three distinct accounts. Pending, pre-accept and established events dispatch
only into their own account, for arbitrary actions including refusal and
generation-owned terminal callbacks. Promotion checks both the pending owner
and the selected established vacancy in the original process, then atomically
releases the pending generation and reserves the distinct established slot.
A raw pending callback marked `connectionEstablished` preserves pending
state and must use promotion to release it. Failed callbacks and reservations
retain the original pending transitions. A denied guard preserves the complete process. Promotion always preserves the
pre-accept executor.

The successful head witness quantifies both independent generations, peer and
bank classifications, and arbitrary pending, bank and peer suffixes. It frees
the pending generation and retains every suffix while granting the established
generation. Completing any selected pending slot clears that generation's
ownership test. Consequently the actual guarded promotion is idempotent for
arbitrary process states and receipt coordinates.

Arbitrary mixed traces preserve pending capacity, both executor capacities and
every established allocation coordinate. Their weighted stage charges compose
under one process-vector initial-fit premise. Stage weights, runtime receipt
authority, routing, serialization, nonwrapping generations, actual resource
termination and resource-cost domination remain explicit premises. No
critical scheduling service is derived.

## General operational stage promotion

Module 89 derives the promotion guard from owned pending and vacant established
slots at arbitrary pending, peer, bank and slot prefixes/suffixes. Its exact
success equation frees the selected pending generation and increments it,
acquires the distinct established generation unchanged, and preserves the
executor and every surrounding account. All resource kinds, directions, trust
labels and swarm labels remain universally quantified.

Operational refusal preserves the complete process for free pending slots,
any mismatched generation, occupied destination slots, and every absent pending,
member, bank or slot index. Absent indices range over each collection's length
plus an arbitrary offset. The stale case assumes only the explicit generation
mismatch. No operational witness assumes the promotion guard's result.

The new evidence closes M012 criterion 1 together with the established release
isolation and coupled mixed-trace accounting in modules 86-88. The 24 new
controls reject false input ownership, loss of any prefix/suffix, incorrect
generation consumption, executor loss, wrong member/bank grants and false
refusal claims at present or available indices.

## Remaining R03 scope

One R03 obligation remains: M012. Criteria 0, 1 and 3 are witnessed. Criterion 2
still requires critical-class service under explicit workload and scheduling
premises within the finite composed process allocation. Turn 15 must discharge
that claim under the [two-turn closure requirement](M012-CLOSURE.md).
R03 stays active, and all 43 external obligations remain open.

## Validation

The complete proof and mutation receipt is
[r03-general-stage-promotion-check.json](../evidence/r03-general-stage-promotion-check.json).
The corpus has 1409 explicit proof declarations in 72 modules. The full run
includes 1322 negative checks (1319 registered mutations plus three generic
controls), empty axiom disclosure and pinned compiler provenance. Disposition,
scope, audit and qualification regressions retain the fixed source and external
boundaries.

Full qualification must still fail while model and external obligations remain
open. The historical R03 turn-1 through turn-13 and R02 receipts retain their original counts
and input hashes.
