# R02 existing proof audit, second pass

R02 is active after two execution turns of its planned three. The sealed source
requirements and all 83 model obligation assignments remain unchanged. This pass
reviews the indexed admission and callback bridges in modules 37 and 39 for
M004 and M005. It adds 16 exact general witnesses to the audit, reuses the proof
corpus and adds no mechanism-lang declaration.

[proof-audit.json](../proof-audit.json) records three partially reviewed
obligations, one fully covered obligation (M005) and 79 unreviewed obligations.
Every acceptance criterion has an explicit disposition. A `gap` identifies a
missing general proof statement in the audited path; `unreviewed` identifies
outstanding audit work that may already have a witness elsewhere.

## Reviewed statements and remaining work

| Obligation | Existing evidence reviewed | Remaining work |
|---|---|---|
| M004 | General pool bound/conservation, complete SourceAdmission trace bound and fixed pool capacity, arbitrary-prefix held/missing-slot refusal and no-receipt results. | R03 proof gap: derive selected-token absence for every index from zero total lease availability, then compose admission refusal and receipt absence. |
| M005 | Whole-admission unowned no-op; indexed receipt ownership, correct-slot release for all terminal reasons, unrelated-slot preservation, duplicate completion and all mismatched or arbitrarily old generations. | Both criteria witnessed at the sealed model scope. External obligation E013 owns runtime callback authority, index stability, atomicity and nonwrapping generations. |
| M009 | General source-system trace slot bound and protected-cell eviction. | Audit re-registration, multiple-prefix attribution, restart/epoch lifetimes and shared T4b/T8 debt/ban retention. |
| M013 | General aggregate burst-plus-trusted-ticks envelope and a closed two-swarm reuse example. | Audit distinct source/prefix time envelopes, IPv4/IPv6 attribution, fresh identities, trusted traffic and unvalidated victim-address rejection. |

Both M005 criteria are now witnessed. An eligible admission
reserves only the selected free lease and returns its exact index and generation.
The terminal-release equality quantifies over every PendingEnd, including
failure, establishment, established-hook refusal, timeout and cancellation. It
preserves an arbitrary prefix and suffix, so every unrelated held lease remains
held. The selected lease becomes free at the next generation. Since a free
generation contributes zero pending occupancy, this returns occupancy to the
corresponding pre-reservation baseline. Source debt and spent shared credits
remain consumed; the whole pre-admission state is not restored.

The unownedAdmissionCompletionIsNoOp statement quantifies over every admission
state and terminal reason, so a refusal without a receipt cannot refund any
live slot. Indexed duplicate and mismatched/stale results preserve complete
states, including arbitrary unrelated held leases. M005 therefore receives
full model coverage. Held-slot and out-of-range refusals still do not state the
M004 implication from total pending saturation.

## Scope and weakening controls

The pinned census still contains 991 explicit proof declarations across 57
modules. Exact statements are extracted from their declarations and checked
against current source; module hashes also pin definitions and proof bodies.
Each witness records its established property, premises and limits. Indexed
results quantify over arbitrary finite prefixes and suffixes, source tables,
credits and nonwrapping Count generations. Internal receipt authority, stable
slot indexes and atomic runtime transitions remain explicit model boundaries.

The linked controls include prefix loss/change, wrong selected positions,
deep receipt and completion aliasing, changed generations, held or missing token
fabrication and refusal receipt creation. Some mutations in earlier definitions
fail before the indexed statements are checked. The full receipt preserves the
actual compiler rejection for every control; a link alone does not establish
that an indexed statement caused that rejection. A new control changes an
unowned admission callback to release a live slot without an owned receipt,
directly testing the whole-admission unowned guarantee.

The aggregate-rate theorem still requires initial credits at most the burst and
authoritative trusted ticks. The fixed two-swarm trace retains finite-example
scope and receives no general criterion coverage credit.

## Validation and boundary

`make audit` checks sealed scope and ledger pins, the complete proof census,
every obligation and criterion index, exact statements, scope labels, premise
records and semantic-control hashes. `make audit-regression` rejects stale
evidence, helper/finite-only credit, altered controls and unsupported closure.
These checks establish provenance and bookkeeping. Semantic entailment, scope
classification and sufficient premises still require source review. The full
model run checks the proof corpus, axiom disclosure and weakening controls.

The current receipt is
[r02-indexed-witness-audit-check.json](../evidence/r02-indexed-witness-audit-check.json).
The first-pass receipt remains a historical snapshot. The audit complete command
and full qualification command retain blocked exit 2 while coverage is
incomplete. All 43 external obligations remain open. The remaining R02 work is
to audit the other W0-W9 obligations and classify their exact R03-R08 gaps;
neither partial witness coverage nor turn-budget use closes R02.
