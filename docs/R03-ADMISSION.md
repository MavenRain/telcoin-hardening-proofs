# R03 admission boundary, turn 1

R03 is active after one execution turn. This batch closes M004 at
its sealed model scope. M001 keeps an identity and privilege gap. M005 was
already covered by R02. The audit now covers
two of 83 model obligations, retains 81 exact gaps, and leaves all 43 external
obligations open. No frozen requirement, obligation, packet assignment or
qualification guard changes.

| Obligation | General evidence | Scope and assumptions |
|---|---|---|
| M001 | Existing unvalidated Retry refusal; module 76's invalid-evidence complete-state no-op, unvalidated-address preservation, valid reachability update, single-step identity/privilege preservation and arbitrary finite evidence-trace preservation. | Evidence tags correctly classify runtime address evidence. Criterion 0 is met. Criterion 1 stays a gap because no modeled transition writes identity or privilege, so their preservation is vacuous. Cookies and signatures are granted token and cryptographic premises; E008 and E020 own their runtime semantics. M014 to M017 own the authentication transitions. E029 owns runtime authority checks. |
| M004 | Module 75's arbitrary-pool and arbitrary-index exhaustion bridge, composed complete-state admission refusal and receipt absence; existing arbitrary PoolTrace and SourceAdmissionTrace bounds, conservation and fixed structural capacity. | Exhaustion means zero total leaseAvailability, including empty pools and missing indices. It is not a selected-held-slot premise. Runtime receipt authority, stable indices, serialization, nonwrapping generations and storage dominance remain external. E013 owns them. |

The saturation proof recurses over the entire LeasePool. A free cell contradicts
zero availability; a held cell permits either local refusal or induction into
the suffix at the predecessor index. This derives the missing total-to-local
bridge without a pool-shape assumption. Existing source admission and receipt
theorems then carry token absence to the complete modeled admission state.

The reachability model carries address validation, identity authentication and
privilege independently. Invalid evidence preserves all three fields. Valid
evidence updates only reachability. No modeled transition writes identity or
privilege, so the preservation proofs earn no M001 credit.
The classifier premise is explicit; these proofs do not implement evidence
verification or cryptographic authentication.

Eleven new mutation controls cover missing/incorrect saturation premises,
invalid validation and authority grants, valid-evidence authority grants,
failure to validate valid evidence, and loss of initial authority across a
trace. Controls must reject with semantic typechecking diagnostics, not parser
failures or crashes. They constrain these exact proof statements and modeled
transitions; they do not constitute runtime fault injection.

## Remaining R03 scope

Nine R03 obligations remain: M001, M002, M003, M007, M009, M011, M012, M013 and M021.
Their exact per-criterion work remains in proof-audit.json. It includes bounded
pre-validation state and cost, pending/established shared limits, handshake
credit, normalized source attribution and churn lifetimes, unlocked ownership
and aggregate/source rate composition. R03 remains active because those gaps
still prevent its three exit criteria from closing.

## Validation

The complete proof and mutation receipt is
[r03-admission-check.json](../evidence/r03-admission-check.json). The corpus has
1001 explicit proof declarations in 59 modules. The full run includes 949
negative checks (946 registered mutations plus three generic controls), empty
axiom disclosure and pinned compiler provenance. Disposition, scope, audit and
qualification regressions retain the fixed source and external boundaries.

Full qualification must still fail while the remaining model and external
obligations are open. The historical R02 receipt remains unchanged and keeps its
original 991-declaration, 57-module and 82-gap scope.
