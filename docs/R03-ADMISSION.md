# R03 admission boundary, turn 2

R03 is active after two execution turns. Turn 1 closed M004 at its sealed
model scope. Turn 2 closes M001 by composing reachability evidence with an
authentication transition that can grant identity and privilege. M005 was
already covered by R02. The audit covers three of 83 model obligations, retains
80 exact gaps, and leaves all 43 external obligations open. The frozen scope,
obligations, packet assignments and qualification guards remain intact.

| Obligation | General evidence | Scope and assumptions |
|---|---|---|
| M001 | Existing general unvalidated Retry refusal; module 76's invalid-evidence complete-state no-op and unvalidated-address preservation; module 77's authentication grants and clearing, arbitrary mixed-trace erasure and authority projections, post-authentication reachability traces and privilege-gate preservation. | Correct classification of runtime address and identity evidence is granted. Cookies and signatures are token-validation and cryptographic premises. E008 and E020 own their runtime semantics, M014 to M017 own detailed protocol authentication, and E029 owns runtime listing and privilege enforcement. |
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

## Remaining R03 scope

Eight R03 obligations remain: M002, M003, M007, M009, M011, M012, M013 and M021.
Their exact per-criterion work remains in proof-audit.json. It includes bounded
pre-validation state and cost, pending/established shared limits, handshake
credit, normalized source attribution and churn lifetimes, unlocked ownership
and aggregate/source rate composition. R03 stays active until its three exit
criteria close.

## Validation

The complete proof and mutation receipt is
[r03-authentication-composition-check.json](../evidence/r03-authentication-composition-check.json).
The corpus has 1021 explicit proof declarations in 60 modules. The full run
includes 967 negative checks (964 registered mutations plus three generic
controls), empty axiom disclosure and pinned compiler provenance. Disposition,
scope, audit and qualification regressions retain the fixed source and external
boundaries.

Full qualification must still fail while model and external obligations remain
open. The historical R03 turn-1 and R02 receipts retain their original counts
and input hashes.
