# R02 existing proof audit, through composition and authentication

R02 is active after four execution turns. The user capped R02 at five total
turns, including the first two. The [remaining batch plan](R02-BATCHES.md) groups
all obligations by their frozen R03-R08 assignments. Turn 3 completes the
R03/R04 witness reviews, including admission, attribution, resource composition,
policy revisions, source/peer lifetimes and recovery. It adds 32 obligation
reviews and completes the outstanding M009/M013 criterion classifications.
Turn 4 audits all 25 R05/R06/R07 obligations and classifies their 51 criteria.
The outcome-independent poll-work bound witnesses M008's first criterion;
the remaining requirements retain explicit composition and lifecycle gaps.

[proof-audit.json](../proof-audit.json) records 60 partially covered audited
obligations, one fully covered obligation (M005) and 22 unreviewed obligations.
There are 44 unaudited criteria, all in the final R08 batch. The sealed source
requirements and all 83 model assignments stay fixed; the proof corpus is
reused unchanged.
Every acceptance criterion has an explicit disposition. A `gap` identifies a
missing general proof statement in the audited path; `unreviewed` identifies
outstanding audit work that may already have a witness elsewhere.

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
committee/trusted/bootstrap union and real decision/lifecycle transitions. The
three `PolicyConsumer` constructors do not model separate inbound, outbound-dial
and outbound-established operations. Snapshot agreement and stale receipt
rejection therefore do not close M023. General authentication, policy fault,
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

The current batch receipt is
[r02-composition-auth-audit-check.json](../evidence/r02-composition-auth-audit-check.json).
The admission/policy, indexed and first-pass receipts remain historical
snapshots. This batch runs audit, scope and disposition checks and their
regressions afresh. Compiler, axiom and semantic-mutation evidence is reused
from turn 3, with unchanged proof modules, compiler identity and proof-check
tooling. Regression fixtures now expect the current census and construct their
unreviewed negative case explicitly. The receipt identifies the reused inputs
and the changed audit, regression, roadmap and documentation inputs separately.
It does not claim a fresh full
model or qualification-guard run.
The audit complete command
and full qualification command retain blocked exit 2 while coverage is
incomplete. All 43 external obligations remain open. The remaining R02 work is
to review the final 22 R08 obligations and audit the packet's closure evidence;
neither partial witness coverage nor turn-budget use closes R02.
