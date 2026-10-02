# R03 admission boundary, turn 7

R03 is active after seven execution turns. Turn 1 closed M004, turn 2 closed
M001 with authentication and reachability composition, turn 3 closed M002
with a pre-validation envelope, and turn 4 closes M011 with unlocked handshake
execution, ownership and host envelopes. Turn 5 closes M007 with arbitrary
population and resource/work composition. Turn 6 closes M021 with endpoint
routing, migration ownership and finite discarded-state bounds. Turn 7 witnesses
M003's normalized-attribution criterion while retaining its exemption-provenance
gap. M005 was already covered by R02.
The audit covers seven of 83 model obligations, retains 76 exact gaps, and leaves all 43 external obligations
open. The frozen scope,
obligations, packet assignments and qualification guards remain intact.

| Obligation | General evidence | Scope and assumptions |
|---|---|---|
| M001 | Existing general unvalidated Retry refusal; module 76's invalid-evidence complete-state no-op and unvalidated-address preservation; module 77's authentication grants and clearing, arbitrary mixed-trace erasure and authority projections, post-authentication reachability traces and privilege-gate preservation. | Correct classification of runtime address and identity evidence is granted. Cookies and signatures are token-validation and cryptographic premises. E008 and E020 own their runtime semantics, M014 to M017 own detailed protocol authentication, and E029 owns runtime listing and privilege enforcement. |
| M002 | Module 78's arbitrary mixed-trace queue, retained-byte and transient-allocation bounds; exact packet/queue/parsing/token charges and arbitrary finite-fuel poll work bounds. | Finite shared allocation and enforced budgets are modeled. Runtime storage/work dominance, serialization, workspace lifetime and supplied outcome classifications remain external. E008 owns the transport queue, budget, serialization, workspace and outcome premises. E010 owns deployed storage and work dominance. Later pending and established caps supply no premise. |
| M004 | Module 75's arbitrary-pool and arbitrary-index exhaustion bridge, composed complete-state admission refusal and receipt absence; existing arbitrary PoolTrace and SourceAdmissionTrace bounds, conservation and fixed structural capacity. | Exhaustion means zero total leaseAvailability, including empty pools and missing indices. Runtime receipt authority, stable indices, serialization, nonwrapping generations and storage dominance remain external. E013 owns them. |
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
fixed-quota results; distinct timed prefix buckets remain M013 work.

The module adds 28 explicit proofs and 29 semantic controls. All controls fail
with proof type mismatches over variables, including wrong host/key selection,
family aliasing, validation bypasses, altered clock/completion evidence,
omitted or duplicated schedule events and an inflated step quota or capacity. The frozen M003 criterion 0 remains a
gap because trusted exemptions and privileged-allowance provenance are absent.
E014 owns runtime parsing, prefix-policy selection, validated-address evidence,
key uniqueness, trusted exemptions and lifetime rules. E013 owns runtime pending
refinement, receipt authority, serialization and storage dominance.

## Remaining R03 scope

Four R03 obligations remain: M003, M009, M012 and M013.
Their exact per-criterion work remains in proof-audit.json. It includes
trusted-exemption and privileged-allowance provenance, normalized source
churn and restart/epoch lifetimes, established resource
vectors and aggregate/source rate composition. R03 stays active until its three exit
criteria close.

## Validation

The complete proof and mutation receipt is
[r03-normalized-source-attribution-check.json](../evidence/r03-normalized-source-attribution-check.json).
The corpus has 1169 explicit proof declarations in 65 modules. The full run
includes 1109 negative checks (1106 registered mutations plus three generic
controls), empty axiom disclosure and pinned compiler provenance. Disposition,
scope, audit and qualification regressions retain the fixed source and external
boundaries.

Full qualification must still fail while model and external obligations remain
open. The historical R03 turn-1 through turn-6 and R02 receipts retain their original counts
and input hashes.
