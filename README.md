# Telcoin hardening proofs

A mechanism-lang proof workspace for the validator network hardening packet in
`w1` and `w1-modified`, targeting
[Telcoin Network at 579aa551fe39593e32a48e1dbcfeccbccab64e3e](https://github.com/Telcoin-Association/telcoin-network/tree/579aa551fe39593e32a48e1dbcfeccbccab64e3e).

**Current status: checked abstract models, incomplete implementation proofs and
deployment qualification.** This repository does not yet prove every hardening
claim. It intentionally cannot produce a successful full-qualification result.
Production thresholds are unresolved in the input plan, implementation
refinements are missing, and required hardware/topology evidence is absent.

The 20 supplied documents are preserved byte-for-byte under [sources](sources/),
with a [hash manifest](sources/manifest.json). The modified plan is the target;
the original drafts retain provenance and unresolved details. The
[claim ledger](claims.json) contains 34 groups across W0 through W9, with
[186 atomic model obligations](atomic-claims.json) documenting theorem links,
assumptions, source ranges and open implementation obligations. The
[coverage table](docs/COVERAGE.md) and [source inventory](source-inventory.json)
retain all 1,383 source units. Textual coverage is complete; atomic semantic
decomposition is not.

## Run locally

The checkout used to create this repository already has the pinned checker built
in `.cache`. Run:

```sh
make dispositions
make disposition-regression
make check
make gate-regression
make qualify
```

`check` checks every model declaration, requires empty axiom disclosure, verifies
source hashes and coverage freshness, and requires 937 deliberately invalid
proof/model variants to be rejected. `gate-regression` checks the blocked result.
`qualify` exits **2** because full qualification is incomplete. Exit **1** means
validation itself failed. A passing `check` is only a model-checking result.

`dispositions` checks the pinned [source ledger](source-ledger.json), and
`disposition-regression` rejects weakened source and reconciliation links.
The [ledger format and current audit scope](docs/SOURCE-LEDGER.md) describe the
R01 work. Pending dispositions block source closure, and candidate theorem
links receive no proof credit from this check.

Independent negative cases can use up to eight checker workers. For example,
`python3 -I tools/check_gate.py --jobs 4` runs the full qualification guard with
four workers. `tools/check.py` accepts the same option. The default is one
worker, report ordering is deterministic, and all worker failures and the
existing checker timeouts remain enforced.

For a fresh checkout, install OCaml 5.2.1, Dune 3.24.2 and Zarith 1.14, then run
`make bootstrap`. This clones the locked mechanism-lang revision and its pinned
Veil dependency and builds `bin/mech.exe`. To reuse an existing local source:

```sh
python3 -I tools/bootstrap.py --local-source /path/to/mechanism-lang
```

The bootstrap command requires an absent `.cache/mechanism-lang` directory. It
does not update or reset an existing cache. See [toolchain.lock.json](toolchain.lock.json).

Check source links against the actual pinned Telcoin checkout with:

```sh
python3 -I tools/check.py --implementation /path/to/telcoin-network
```

The command checks the revision and file hashes in
[implementation-map.json](implementation-map.json). Matching hashes establish
which code was inspected; they do not establish program refinement.

## What the model proves

All proof terms and models are `.mech` source. Python handles reproducibility,
bookkeeping and checker invocation. There are no source axioms, admitted proofs,
imported Lean proofs, or external solver assertions. The current bundle contains
991 explicit equality and order proof declarations across 57 modules. This count
includes supporting lemmas; it is not a count of hardening claims proved.

| Module | Checked model properties |
|---|---|
| `00-foundation.mech` | Symbolic work caps, monotonicity and additive composition. |
| `05-arithmetic.mech` | Constructive order composition, generation comparison and remaining-capacity witnesses. |
| `10-transport.mech` | Retry-before-accept decisions, source/aggregate accounting separation, all-outcome poll bounds and outer deadline dominance. |
| `15-poll-continuation.mech` | Processed work plus retained backlog equals initial backlog; retained work requests another wakeup. |
| `20-accounting.mech` | Fixed slot capacity, idempotent release, release locality, stage/swarm composition and a permit policy. |
| `21-pending-lifecycle.mech` | Generation-tagged ownership, five terminal cleanup paths, duplicate and stale callback safety, and arbitrary finite pool traces. |
| `22-weighted-resources.mech` | Weighted queue, pending and established resource bounds composed across both swarms. |
| `25-handshake-budget.mech` | Shared handshake-credit conservation and capacity under admission, refill, eviction, identity changes and fallback. |
| `26-discrete-rate-envelope.mech` | Handshake starts and weighted cost bounded by burst plus rate times trusted ticks. |
| `27-source-table.mech` | Fixed-capacity source registration and eviction traces preserve existing rate debt and bans, refuse unknown sources on overflow, and require validated registration. |
| `28-source-enforcement.mech` | Selected-cell quota charging, simultaneous debt and bans, independent trusted expiry, and finite restriction traces bounded by a fixed source quota. |
| `29-source-system.mech` | First-match keyed lookup and charging, unchanged slot capacity and per-resident debt bounds across mixed churn and restriction traces. |
| `30-admission-and-service.mech` | Invalid-policy fallback, mandatory authentication, bounded trusted work, resolution deficit and independent class budgets. |
| `31-committee-records.mech` | Current-epoch authenticated record guards, distinct-member counting, duplicate idempotence and epoch reset. |
| `32-policy-snapshots.mech` | Whole-view generations, guarded publication, explicit policy faults and recovery updates. |
| `33-policy-readers.mech` | Coherent captured readers and admission receipts bound to generation, epoch and peer identity. |
| `34-policy-traces.mech` | Generation bounds over finite traces, callback replay safety, recovery reset and enabled valid-record updates. |
| `35-critical-service.mech` | A queued critical request completes after enough service rounds despite subsequent bulk or critical arrivals. |
| `36-governed-resources.mech` | Shared handshake credits and pending conservation survive arbitrary finite interleavings with policy changes. |
| `37-source-admission.mech` | Atomic source/global/pending admission, indexed completion receipts, refusal without side effects, and bounded mixed admission and maintenance traces. |
| `38-source-admission-rate.mech` | Receipt-counted accepted starts, shared-credit conservation, trusted tick issuance and a coupled burst-plus-rate and per-start cost envelope. |
| `39-indexed-source-admission.mech` | Arbitrary-slot enabled admission and counting, exact receipts, completion locality, stale and duplicate callback protection, and held or missing slot refusal. |
| `40-ingress-and-operations.mech` | Parsed submit-only policy, overload demotion rules, proxy attribution, firewall inclusion, migration gates and a finite metric domain. |
| `41-policy-source-admission.mech` | Current policy receipts gate atomic source admission; indexed receipt and count equations, mixed trace state bounds, and the burst-plus-rate and cost envelopes survive policy publication. |
| `42-policy-work.mech` | An independent work budget charges processed attempts and publications, preserves cleanup and source invariants, and composes policy-work and handshake cost envelopes. |
| `43-policy-ingress.mech` | Work credit gates internal current-view policy queries; authentication denials, mixed-trace projection, pending capacity and combined cost envelopes are checked. |
| `44-policy-ingress-poll.mech` | Poll fuel charges every dispatched ingress event, preserves ordered continuation and state, and bounds assumed dispatch overhead together with policy and handshake work. |
| `45-policy-ingress-queue.mech` | Persistent FIFO queue and resource state, ordered arrivals, conditional target progress across service turns, and a combined cost envelope over the dispatched trace. |
| `46-policy-ingress-schedule.mech` | Varying-fuel turns, exact state and FIFO conservation, prefix service from sufficient cumulative fuel, pending capacity and a combined cost envelope. |
| `47-policy-ingress-overload.mech` | Fixed queue-entry cap with FIFO admission before each turn, explicit rejected suffixes, entry occupancy within the cap when the initial queue fits, conditional service of original queued prefixes, pending capacity and the combined dispatch/policy/handshake cost envelope across filtered schedules. |
| `48-policy-ingress-payload.mech` | Retained-payload bounds (sum of immutable per-event charges) and entry caps preserved across finite schedules when the initial queue fits each bound, exact FIFO rejection, fitting-head acceptance, a closed freed-payload reuse witness, conditional prefix service and the execution envelope. Runtime storage dominance remains open. |
| `49-policy-ingress-scan.mech` | A separate admission allowance bounds each examined arrival prefix, partitions accepted, rejected and caller-owned unexamined arrivals, preserves queue bounds and conditional backlog service, and adds symbolic admission charges to the per-turn dispatch envelope. Concrete scan costs and external suffix handling remain open. |
| `50-qualification.mech` | Missing evidence blocks a conjunction of qualification conditions. |
| `51-policy-ingress-resumption.mech` | Caller-owned FIFO resumption conserves examined and deferred arrivals, conditionally examines original deferred prefixes, preserves admitted queue bounds and service, and composes scan and execution costs across a finite schedule. Deferred storage, runtime resubmission and mandatory-event delivery remain open. |
| `52-policy-ingress-deferred.mech` | A fixed caller-owned deferred capacity retains the earliest unexamined prefix, reports explicit overflow, preserves the three-way FIFO disposition, and carries the bounded handoff through filtered queue/resource execution and symbolic overflow cost. Runtime ownership, storage and delivery remain open. |
| `53-policy-ingress-handoff-schedule.mech` | Finite bounded handoff schedules carry retained FIFO and resource state across turns, report chronological overflow without internal replay, preserve admitted bounds, and conserve the recursive examined/overflow/final-deferred occurrence count. Runtime delivery, output storage and progress remain open. |
| `54-policy-ingress-handoff-service.mech` | A fitting original deferred prefix is examined in FIFO order with one ingress scan per delivered turn and enough turns, despite later arrivals and overflow. Exact prefix equations, scan-count bounds and boundary examples keep runtime delivery, admission, dispatch and concrete costs explicit. |
| `55-policy-ingress-handoff-pauses.mech` | Paused and one-scan turns preserve a fitting original FIFO prefix. Exact examination equations count delivered scans independently of dispatch fuel, with full-prefix examination given enough scans, bounded deferred retention and chronological overflow. Runtime delivery remains open. |
| `56-policy-ingress-paced-execution.mech` | Paced handoffs compose with payload-filtered queue/resource execution, retain conditional queue bounds and pending capacity, conserve recursive examined/overflow/deferred occurrence counts, and inherit the dispatched-work cost envelope. Concrete scanning, storage, delivery and latency remain open. |
| `57-policy-ingress-paced-cost.mech` | Weighted examination, all offered-item handoff visits and fixed per-turn work compose with the dispatched-work envelope. Pauses, repeated retention, oversized overflow and zero dispatch fuel remain charged. Runtime cost dominance and latency remain open. |
| `58-policy-ingress-variable-scans.mech` | Independent natural scan allowances examine a fitting original deferred prefix in FIFO order, and examine all of it given enough total scans. They keep conditional deferred and admitted-state bounds, separate dispatch fuel, and the combined symbolic cost envelope. A mixed 2, 0, 3 allowance schedule checks fresh arrivals and overflow across a pause. Runtime scan delivery, cost dominance and latency remain open. |
| `59-policy-ingress-accounting.mech` | A finite ledger projects to the actual examined, final-deferred and overflow traces. Recorded retained-prefix lengths place each overflow block before later arrivals, reconstructing the exact chronological input and its occurrence count. Witnesses cover pauses, interleaved overflow, repeated equal-valued events and zero deferred capacity. Runtime history storage, identity and costs remain open. |
| `60-policy-ingress-composition.mech` | Concatenated schedules produce the same ledger as two segments joined through the exact deferred suffix at fixed capacity. Examined and overflow traces concatenate, final deferred work comes from the second segment, and chronology preserves both arrival histories. Deferred and overflow projections match the model handoff fields. Full model state composition is covered by module 61; runtime ownership transfer and storage costs remain open. |
| `61-policy-ingress-execution-composition.mech` | Concatenated schedules equal sequential execution carrying the complete handoff state at fixed parameters. Deferred work, admitted queue, policy/resource state, ordered overflow and dispatched histories compose without an initial-fit premise. Runtime refinement, changing parameters and concrete costs remain open. |
| `62-policy-ingress-cost-composition.mech` | All six symbolic cost components add across schedule segments carrying the actual handoff state. Their sum inherits one whole-schedule envelope under the original credit bounds, without a fresh resource burst at the split. Parameters and weights stay fixed; concrete costs and runtime refinement remain open. |
| `63-policy-ingress-capacity-handoff.mech` | An explicit deferred-capacity change retains a bounded FIFO prefix, reports the removed suffix and carries the admitted queue and policy/resource state unchanged. Repeating the limit preserves the resized state without further overflow; resumed execution reports boundary overflow first and satisfies the new deferred bound. Runtime authority, cleanup and resize costs remain open. |
| `64-policy-ingress-capacity-accounting.mech` | A boundary ledger reconstructs the original deferred input followed by every later arrival, preserving occurrence order and multiplicity across a resize. Its projections match examined work and the resized execution's deferred and overflow fields, including empty schedules and zero capacity. Runtime ownership, history storage and resize costs remain open; module 65 supplies preceding-ledger composition. |
| `65-policy-ingress-capacity-composition.mech` | A preceding segment ledger composes with one capacity boundary and a following segment. Exact chronological reconstruction preserves occurrences without initial fit; examined and overflow histories concatenate in segment order, and final deferred work comes from the resized segment. Module 66 links this ledger to the actual execution handoff. |
| `66-policy-ingress-capacity-execution.mech` | Complete queue and policy/resource execution composes across one deferred-capacity change, preserving dispatch order and matching ledger outputs. The new deferred bound is unconditional; admitted bounds retain initial-fit premises. The dispatch-cost envelope excludes administrative and resize costs. |
| `67-policy-ingress-capacity-cost.mech` | Administrative, resize and dispatch costs share an eight-weight envelope across one deferred-capacity change. Resize charges count retained and rejected occurrences plus one fixed boundary charge. The bound retains the actual resize-input cost and uses the original credit premises. |
| `68-policy-ingress-capacity-schedule.mech` | Finite resize/poll interleavings preserve chronological occurrence accounting and the final deferred-capacity bound. Fixed-capacity and single-resize embeddings match the earlier ledgers; mixed shrink, growth and pause witnesses preserve disposition order. |
| `69-policy-ingress-capacity-schedule-execution.mech` | Arbitrary finite resize/poll schedules preserve independent scan and dispatch fuel and execute the ledger-examined occurrences through payload-aware admission. Deferred, admitted entry, payload and pending-resource bounds retain their stated premises. Empty, resize-only and mixed shrink/growth/dispatch witnesses preserve carried state. |
| `70-policy-ingress-capacity-schedule-cost.mech` | Arbitrary finite resize/poll schedules have an eight-weight administrative and dispatch cost envelope. The administrative limit charges the actual initial suffix and propagates the active capacity after each resize or poll. Pauses charge offered visits, each resize charges its input and fixed boundary work, and the envelope retains the original credit premises. |
| `71-policy-ingress-capacity-schedule-composition.mech` | Arbitrary capacity execution segments concatenate associatively and carry their final deferred capacity across cuts. Ledger and lowered schedule composition preserve the final admitted queue, deferred suffix and ordered overflow under fixed admitted limits, payload weights and policy configuration. |
| `72-policy-ingress-capacity-schedule-cost-composition.mech` | Administrative and dispatch costs add across arbitrary capacity execution cuts at the actual handoff. The segment sum inherits one concatenated-schedule envelope under the original credit bounds, with no second initial burst or initial deferred/admitted fit premise. |
| `73-policy-ingress-capacity-schedule-compatibility.mech` | Fixed-capacity variable-scan schedules and two segments separated by one resize embed into arbitrary capacity execution with equal ledgers and lowered schedules. The embedded single-boundary runner preserves the earlier executor's complete final admitted queue without initial-fit or credit-bound premises. |
| `74-policy-ingress-capacity-schedule-cost-compatibility.mech` | Per-turn and aggregate administrative charges agree at fixed capacity and across one resize. Complete symbolic costs agree with the earlier executors without fit or credit premises; pauses retain handoff and turn charges, and empty segments retain resize charges. |

These statements quantify over model inputs, including arbitrary natural-number
caps and event lists. An abstract finite poll trace is not an operating-system
scheduling theorem. An authenticated flag is not a cryptographic proof. A fixed
slot vector is not a verified Rust connection map. Each claim's `model_scope`
states the remaining boundary. [Model contracts](docs/MODELS.md) explain the
transition systems, theorem premises and implementation obligations.

## Implementation observations

The pinned connection-limit builder sets a per-peer ceiling of eight while
leaving its pending and total dimensions unset. The model's aggregate-bound
theorem therefore cannot certify that builder. The current QUIC builder does
forward `handshake_timeout`; older draft observations must be rechecked against
the pinned source. Both observations and their exact ranges are in
[the implementation map](implementation-map.json).

See [the trust boundary](docs/TRUST.md) and [remaining proof work](docs/ROADMAP.md).
Run results, the combined `.mech` bundle and negative-case diagnostics are saved
under `.build`. The GitHub workflow checks models and the blocked gate; it does
not run a validator flood or declare launch readiness.
