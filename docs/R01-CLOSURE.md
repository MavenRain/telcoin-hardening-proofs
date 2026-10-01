# R01 source scope closure

R01 seals the requirements that R02 must audit against the existing proof corpus.
The pinned source snapshot is unchanged. All 1,383 source units have reviewed
dispositions: 672 context, 681 obligation and 30 superseded units. None is pending.
The ledger fixes 83 model obligations and 43 external obligations, with all 102
original tracking IDs and all D01-D12 decisions retained.

The closure evidence is [the source ledger](../source-ledger.json),
[the scope seal](../proof-scope.json) and
[the checked receipt](../evidence/r01-closure-check.json). `make dispositions`,
`python3 -I tools/dispositions.py --require-complete` and `make scope` check the
source pins, exhaustive dispositions, reconciliation links and frozen scope.
`make disposition-regression` and `make scope-regression` reject weakening.

## Audited exit criteria

1. Every pinned source unit has a disposition and review rationale. Original
   normative clauses reconcile to reviewed modified-plan clauses retaining their
   obligations. Structural labels, source-era facts, archived drafting history,
   benchmark history and non-goals have explicit context rationales. Historical
   posting and delegation instructions grant no current action authorization.
2. Every normative destination has fixed obligation IDs, a property, required
   scope, acceptance criteria, required evidence and an R03-R08 assignment. The
   seal pins the complete ledger and obligation content, and records the exact
   source unit and obligations for each tracking ID and decision. Model witnesses
   require general statements with explicit premises; finite examples alone do
   not close an obligation. Source tiers and conditions remain in scope.
3. The disposition checker establishes source completeness. Closing R01 now
   requires a valid scope seal rather than the legacy proof-corpus coverage flag,
   which remains false. The report derives claim decomposition from checked
   source dispositions and reports model coverage separately. CI runs both sets
   of weakening controls. The full-qualification gate still rejects incomplete
   model, implementation and deployment qualification.

## Reconciliations and boundary

The final audit retains the original maintenance investigation and ten-validator
carried-versus-registry comparison, shared-source handshake accounting, honest
reconnect and current-provider cost/compatibility measurements. Mandatory
arbitrary-address production labels are replaced by bounded attribution and
exports. A negotiated-group observation does not force a metric-only fork.
Cryptographic changes and early refusal remain conditional decisions; certificate
self/extension/transcript checks, verified PeerId extraction, session isolation
and authoritative current admission after TLS resumption remain model obligations.

The remaining workstreams retain their individual contracts: admission and peer
lifecycle, record verification/recovery, serve ownership and class isolation,
gossip limits/freshness, conditional storage isolation, RPC profiles/forwarding,
bounded observability, distinct firewall/protocol projections and release gates.
Hub, Rotation and Later work is deferred by tier rather than erased. External
refinement, measurement, cryptographic review, operator and provider evidence
remains required, including all unresolved inputs and conditional remediation.

The abstract models use explicit cryptographic, clock, cost, availability and
fairness premises. The primary threat envelope excludes link saturation and
adversarial validators; it retains bounded admitted-hub load. A source disposition
or scope check does not establish the correctness of a theorem or a runtime claim.

R01 adds no mechanism-lang proof and grants no theorem or external closure credit.
R02 must record exact witness and assumption audits separately against these
frozen source IDs, then identify the remaining gaps. Changing a sealed source
requirement requires an explicit new scope baseline; witness records do not
silently rewrite the sealed ledger. R01 uses five execution turns of its planned
five. R02 has not consumed an execution turn.
