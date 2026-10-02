# R03 admission boundary, turn 3

R03 is active after three execution turns. Turn 1 closed M004, turn 2 closed
M001 with authentication and reachability composition, and turn 3 closes
M002 with a pre-validation queue, allocation and processing-work envelope.
M005 was already covered by R02. The audit covers four of 83 model
obligations, retains 79 exact gaps, and leaves all 43 external obligations
open. The frozen scope,
obligations, packet assignments and qualification guards remain intact.

| Obligation | General evidence | Scope and assumptions |
|---|---|---|
| M001 | Existing general unvalidated Retry refusal; module 76's invalid-evidence complete-state no-op and unvalidated-address preservation; module 77's authentication grants and clearing, arbitrary mixed-trace erasure and authority projections, post-authentication reachability traces and privilege-gate preservation. | Correct classification of runtime address and identity evidence is granted. Cookies and signatures are token-validation and cryptographic premises. E008 and E020 own their runtime semantics, M014 to M017 own detailed protocol authentication, and E029 owns runtime listing and privilege enforcement. |
| M002 | Module 78's arbitrary mixed-trace queue, retained-byte and transient-allocation bounds; exact packet/queue/parsing/token charges and arbitrary finite-fuel poll work bounds. | Finite shared allocation and enforced budgets are modeled. Runtime storage/work dominance, serialization, workspace lifetime and supplied outcome classifications remain external. E008 owns the transport queue, budget, serialization, workspace and outcome premises. E010 owns deployed storage and work dominance. Later pending and established caps supply no premise. |
| M004 | Module 75's arbitrary-pool and arbitrary-index exhaustion bridge, composed complete-state admission refusal and receipt absence; existing arbitrary PoolTrace and SourceAdmissionTrace bounds, conservation and fixed structural capacity. | Exhaustion means zero total leaseAvailability, including empty pools and missing indices. Runtime receipt authority, stable indices, serialization, nonwrapping generations and storage dominance remain external. E013 owns them. |

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

## Remaining R03 scope

Seven R03 obligations remain: M003, M007, M009, M011, M012, M013 and M021.
Their exact per-criterion work remains in proof-audit.json. It includes
pending/established shared limits, handshake
credit, normalized source attribution and churn lifetimes, unlocked ownership
and aggregate/source rate composition. R03 stays active until its three exit
criteria close.

## Validation

The complete proof and mutation receipt is
[r03-prevalidation-envelope-check.json](../evidence/r03-prevalidation-envelope-check.json).
The corpus has 1054 explicit proof declarations in 61 modules. The full run
includes 1004 negative checks (1001 registered mutations plus three generic
controls), empty axiom disclosure and pinned compiler provenance. Disposition,
scope, audit and qualification regressions retain the fixed source and external
boundaries.

Full qualification must still fail while model and external obligations remain
open. The historical R03 turn-1, turn-2 and R02 receipts retain their original counts
and input hashes.
