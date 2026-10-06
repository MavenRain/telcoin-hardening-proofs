# R02 existing proof audit, complete witness census

This document records the R02 closure baseline. [R03 turn 15](R03-ADMISSION.md)
subsequently closes M012 and R03. [R04 turn 1](R04-POLICY.md) closes M022, R04 turn 2 closes M023, R04 turn 3 closes M024, R04 turn 4 closes M025, and R04 turn 5 closes M026;
the current ledger covers sixteen obligations and retains 67 gaps. The R02 receipt keeps its original corpus and
82-gap scope.

R02 closes after five execution turns, within the user's five-turn cap.
The [batch plan](R02-BATCHES.md) records the reviews against the frozen R03-R08
assignments. Turns 1-2 established the census and indexed admission witnesses;
turn 3 reviewed R03/R04; turn 4 reviewed R05/R06/R07. Turn 5 reviews the final
22 R08 obligations and classifies all 44 remaining criteria.

[proof-audit.json](../proof-audit.json) records all 83 reviewed model obligations,
zero unaudited criteria, one fully covered obligation (M005) and 82 partial
obligations with exact model gaps. Every remaining gap retains its sealed
R03-R08 assignment. The 83 model and 43 external obligations, source requirements
and 57-module, 991-declaration proof corpus are unchanged in this batch.

The witness census is complete. Model coverage is incomplete: a reviewed `gap`
records a missing general statement at the sealed scope. This closure assigns
no coverage credit from theorem names, finite examples or turn-budget use.

## Reviewed statements and remaining work

| Obligation | Existing evidence reviewed | Remaining work |
|---|---|---|
| M004 | General pool bound/conservation, complete SourceAdmission trace bound and fixed pool capacity, arbitrary-prefix held/missing-slot refusal and no-receipt results. | R03 proof gap: derive selected-token absence for every index from zero total lease availability, then compose admission refusal and receipt absence. |
| M005 | Whole-admission unowned no-op; indexed receipt ownership, correct-slot release for all terminal reasons, unrelated-slot preservation, duplicate completion and all mismatched or arbitrarily old generations. | Both criteria witnessed at the sealed model scope. External obligation E013 owns runtime callback authority, index stability, atomicity and nonwrapping generations. |
| M009 | General source-system trace slot bound, source-table churn protection and protected-cell eviction. | R03 gap: compose re-registration churn with normalized multiple-prefix attribution, restart/epoch lifetimes and shared T4b/T8 debt/ban retention. |
| M013 | General aggregate burst-plus-trusted-ticks envelope and a closed two-swarm reuse example. | R03 gap: distinct timed source/prefix and aggregate envelopes, validated IPv4/IPv6 attribution, fresh identities, trusted traffic and victim-address rejection. |

The new R03 reviews distinguish earlier transient bounds from pending and
established allocations. Retry, scalar work, two-swarm allocation and source
charge witnesses retain their local scopes. Missing normalized attribution,
arbitrary-population host composition, unlocked executor ownership and
established-resource vectors remain exact R03 model gaps. The unvalidated Retry
criterion of M001 receives general transition credit; reachability-evidence and
identity composition still need a witness.

The R04 reviews distinguish a supplied policy snapshot from the documented
committee/trusted/bootstrap union and real decision/lifecycle transitions.
Module 91 now supplies the exact five-source union for all node roles and
primary/worker swarms, targeted verified updates and general provisional/mixed
trace witnesses, closing M022. The
three `PolicyConsumer` constructors do not model separate inbound, outbound-dial
and outbound-established operations. Snapshot agreement and stale receipt
rejection alone therefore do not close M023. Module 92 adds the distinct
transitions and closes M023 in R04 turn 2. General authentication, policy fault,
resource preservation, record resolution and protected-expiry results receive
their recorded local scopes. Peer retry/discovery, timestamp repair, observer
reservation, role-score configuration, address projection and race ownership
state machines remain explicit R04 gaps. Finite trusted-ban examples never
close a general criterion.

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

## Composition, service and authentication review

| Obligations | Existing statements and premises | Exact remaining model work |
|---|---|---|
| M008 | Every finite Accept/Retry/Refuse/Ignore trace examines at most its supplied fuel. Exhausted polls preserve backlog and request a wake; resuming the policy-ingress suffix preserves execution. Critical service needs at least one more completed service round than the initial waiting rank; the trace supplies those rounds. | Derive cumulative command/timer service and age bounds from readiness, work costs, wake delivery, cooperative budgets and fair scheduling. |
| M010 | A source with strictly available quota advances its debt by one. | Protect honest opportunity under shared NAT, hostile populations, reconnect bursts, aggregate load and policy transitions. |
| M046-M047 | `noSleepUnderPermit` is a closed sleeping-constructor equality; there is no vote-to-task transition. | Add owned serve-permit grant/release/sleep/retry and pre-spawn vote admission, including failures and cancellations. |
| M048-M049, M053 | Generic critical service requires at least one more completed service round than the initial waiting rank. New arrivals cannot worsen that rank; a scalar critical cap ignores bulk demand. | Derive rounds from protocol eligibility, availability, scheduling and costs; compose epoch-pack hold/progress bounds, hub priority, critical classes and catch-up service. |
| M050-M051 | Weighted stage costs assume supplied occupancy bounds; two-swarm lease traces retain fixed capacities; bounded ingress schedules preserve an initially bounded queue. | Add per-peer/class reserve ownership, resizing and aggregate spawned/waiting task work across all swarms. |
| M052 | General arrival partition and chronological resize-ledger reconstruction preserve the policy-ingress event trace; exact suffix resumption preserves execution. | Model completed task outcomes and class-stage retry/drop ownership in the proper unit. Examined events do not establish completed work. |
| M054, M081 | No probe fanout, constrained peer/range selection or committed range-result machine is present. | Add bounded parallel probe/request work, owned results, valid coverage and cancellation/failure handling. |
| M014-M018, M020, M055 | No certificate-content, signed extension, transcript, verifier-result store, group-negotiation or aggregate-key proof-of-possession machine is present. | Add the sealed authentication and optimization transitions with explicit signature/hash/verification assumptions and general failure cases. |
| M019 | Supplied authentication is required and stale policy selects the grace profile. | Compose full/resumed sessions, skipped callbacks and old tickets with the current established gate under revision and revocation. |
| M029 | An unverified record flag preserves the roster; a current verified flag invokes the selected record-marking operation. | Derive independent BLS verification and bind actual NodeRecord identities/endpoints through retrieval, origin gossip, hub forwarding and later joins. |
| M059-M060 | The ban abstraction preserves genuine violations; load exemption is a closed example. No gossip replay/cache-validity machine is present. | Model role-aware hub scoring/topology and message freshness after duplicate-cache eviction. Policy/record freshness is a separate abstraction. |
| M082-M083 | Scalar caps and critical-count isolation retain local scope. Matching pending callbacks release their own lease; unowned callbacks cannot refund it; the deadline minimum respects the supplied outer bound. | Compose authenticated QoS weights and runtime queue/execution priority/timeouts, finite class reserves, fair progress and waiter/executor ownership. |

The completed-service-round premise is explicit. No theorem in this audit
derives it from a real scheduler, a wall clock or command/timer readiness.
`holdsPermit sleeping = off` describes one constructor, with no preceding
grant or release transition, and receives finite-example credit only.
Supplied authentication and record-verification flags do not prove certificate,
transcript or BLS checks. These missing abstractions remain in their sealed
R05/R06/R07 packets. The audit adds no new proof domain or semantic mutation.

## Remaining abstraction review

The final batch inspects the operations and qualification definitions together
with generic admission, source, queue, service and weighted-resource candidates.
Every R08 criterion remains a model gap; no new domain or proof is added.

| Obligations | Existing statements and premises | Exact remaining model work |
|---|---|---|
| M056-M058 | `fullPublishRefuses` is a closed validated/no-capacity transport example. Source charges and ingress counts have no gossip author, propagation-source, frame parser or publish queue. | Model pre-processing limits, bounded publish return/service and propagation-connection/class charges, including duplicates, failed verification and backpressure. |
| M061-M063 | Generic finite occupancy/cost bounds and supplied service rounds have no live-pack or EpochRecordDb state, read/write permit ownership, task/thread or file-handle lifecycle. | Under the selected D1 remediation, bind database-specific queues and persistence service; bound recent-pack retained work and handle churn through completion/cancellation. |
| M064-M065 | `onlySubmitMethod` handles either capacity flag; `batchesRejected` handles every abstract method/capacity pair. Both consume supplied two-constructor methods and batch flags. `overloadIsDistinct` is a closed example. | Bind parsed method names, HTTP non-2xx outcomes, profiles and every batch member, including malformed/empty/mixed collections and profile switches. |
| M066, M069, M071 | `forgedForwardingHeaderIgnored` quantifies over either header flag when the supplied proxy flag is off. Generic rate envelopes have no verified configured-proxy identity or RPC method-work state. | Bind source matching and victim allowances to verified proxy authority; compose finite selected-forwarder tiers and independent node-side per-source/aggregate budgets. |
| M067-M068, M077 | Fixed 429/503/rejection constructors preserve every failure Count. `noEarlyRetirement` handles either new-path flag when supplied convergence is off; `failedNewPathKeepsOld` is a closed example. | Model endpoint-local Retry-After/status/retry state, verified URL/key convergence and old/new rollout/rollback, preserving unrelated endpoints and blocking premature readiness. |
| M070, M072-M073 | Weighted cost arithmetic requires supplied occupancy and per-entry weights. The RPC abstraction contains no observer read pool, namespace set/aliases, fee-cap or trusted HTTPS/protocol-header state. | Model bounded heterogeneous observer reads and freshness, enabled tn_* dispatch, and selected fee-cap/upstream contracts over arbitrary configurations and failures. |
| M074-M076 | `metricDomainBound` bounds every index in the three-constructor MetricStage domain by two. No source-keyed diagnostic eviction, remote log limiter, quorum snapshot or commit-gap clock exists. | Model bounded diagnostic retention/exports and constant-size remote logging, plus distinct faithful quorum-shortfall and commit-gap observations. |
| M078 | `protocolPeersPermitted` handles either future flag for a supplied current member. Two closed examples demonstrate future pre-permission and separate protocol admission. | Model one-source protocol/firewall address projections, all primary/worker addresses and rotation revisions, proving containment without unconditional set equality. |
| M079 | `anyMissingGateBlocks` quantifies over arbitrary finite gate-list prefixes/suffixes around an off gate. General qualification blockers consume supplied flags. | Derive applicable feature/deployment gates and failed/unknown evidence classification across conditional remediation, thresholds and rollout checkpoints. |

The proxy, membership, convergence, readiness and qualification flags are
authoritative model inputs. Their boolean equalities do not establish that
runtime observations produced those flags. MetricStage bounds a fixed label
domain, not diagnostic retention or arbitrary attacker-key storage. Generic
network queue/cost/service results receive no automatic database or RPC credit.

## R02 exit evidence

| Criterion | Audited evidence | Result |
|---|---|---|
| 0: Every frozen obligation has exact witnesses or missing proofs. | `proof-audit.json` retains every sealed obligation and criterion, exact extracted statements, reviewed premises and missing statements. | 83 reviewed obligations; zero unaudited criteria. |
| 1: Scopes and assumptions remain distinct. | The audit records arbitrary traces, general transitions, conditional liveness and finite examples separately; the statement reviews in this document explain their limits. | Finite and partial candidates receive only their actual scope; supplied service/authority premises remain explicit. |
| 2: Remaining gaps are routed to R03-R08 without redundant proof additions. | Every remaining audit entry keeps its sealed closure packet; all proof-module hashes match the prior corpus. | 82 remaining model obligations, all routed to R03-R08; no new helper, example or domain in this turn. |

`proof-roadmap.json` pins the current audit/document hashes for all three
criteria and retains closed R01 as a prerequisite. R02 spends five turns rather
than its original three-turn allocation, consuming two reserve turns. Overall
use is 10/50 turns, with two of ten packets closed (20%). This measures packet
closure, not model completeness or deployment qualification.

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

`make audit` checks sealed scope and ledger pins, the proof census, every
obligation/criterion index, exact statements, scope labels, premises and
semantic-control hashes. Audit regressions reject stale evidence, finite-only
credit and unsupported closure. They now construct an unaudited criterion
explicitly, and check that complete witness review permits R02 closure while
model coverage remains incomplete. All 30 witness-audit, 15 scope and 40
source-disposition regressions pass. Inventory and coverage are regenerated
and checked against the closed roadmap and its fresh evidence hashes.

The current batch receipt is
[r02-closure-check.json](../evidence/r02-closure-check.json). Earlier R02 receipts
retain their historical scopes. All 88 inputs of the turn-4 receipt matched
before edits. Compiler, empty axiom disclosure and 938 semantic-mutation
rejections are reused through turn 4 from the turn-3 full proof run. The
compiler binary, proof modules, source scope, source ledger and proof-check
tooling remain unchanged. The receipt identifies these inputs separately from
changed audit, regression, roadmap and documentation metadata. It records fresh
audit/scope/disposition checks and the blocked complete-model audit command;
it claims no fresh full model or qualification-guard run.

These checks establish provenance and bookkeeping. Semantic entailment, scope
classification and adequate premises still require the source reviews above.
`audit.py --require-complete` returns exit 2 because it requires full model
coverage, even though witness review is complete. Full qualification retains
its independently blocked status and all 43 external obligations remain open.
R03-R08 now have the exact remaining proof inventory; Rust refinement,
deployment measurements and operator decisions receive no closure from R02.
