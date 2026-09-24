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
[76 atomic model obligations](atomic-claims.json) documenting theorem links,
assumptions, source ranges and open implementation obligations. The
[coverage table](docs/COVERAGE.md) and [source inventory](source-inventory.json)
retain all 1,383 source units. Textual coverage is complete; atomic semantic
decomposition is not.

## Run locally

The checkout used to create this repository already has the pinned checker built
in `.cache`. Run:

```sh
make check
make gate-regression
make qualify
```

`check` checks every model declaration, requires empty axiom disclosure, verifies
source hashes and coverage freshness, and requires 265 deliberately invalid
proof/model variants to be rejected. `gate-regression` checks the blocked result.
`qualify` exits **2** because full qualification is incomplete. Exit **1** means
validation itself failed. A passing `check` is only a model-checking result.

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
492 explicit equality and order proof declarations across 28 modules. This count
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
| `50-qualification.mech` | Missing evidence blocks a conjunction of qualification conditions. |

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
