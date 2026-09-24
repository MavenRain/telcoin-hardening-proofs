# Remaining proof and evidence work

The requested final result is complete coverage of the hardening claims against
the pinned implementation and an explicitly qualified deployment envelope.
The current repository checks finite transition proofs for generation-tagged
pending ownership, shared handshake credits, a discrete burst-plus-rate bound,
weighted resource composition, poll continuations, committee-record deduplication
and epoch reset, versioned policy publication and receipts, mixed policy/resource
traces, critical service after enough completed rounds, and bounded source-table
churn that preserves existing rate debt and bans under registration and eviction
without increasing slot capacity. Source-system traces now compose keyed lookup,
churn, bounded charging, simultaneous debt and bans, and independent trusted
expiry while preserving slot capacity and each resident's debt bound. Atomic
source admission now couples validated source quota, shared handshake credit and
selected pending ownership, with indexed completion receipts and bounded mixed
traces. Accepted starts counted from those receipts now satisfy shared-credit
conservation and a discrete burst-plus-rate envelope, lifted to per-start cost.
Enabled admission, exact receipt emission, accepted-start counting, matching
completion, stale and duplicate callback protection, and held or missing slot
refusal now hold for arbitrary finite pending prefixes and suffixes. Current
policy receipts now gate the same source admission transition. Mixed
policy/source traces retain the indexed admission equations, resource bounds
and receipt-counted burst-plus-rate and per-start cost envelopes. An independent
policy-work budget now charges processed attempts and publications, including
denials, and composes its discrete cost envelope with accepted handshake work.
Cleanup bypasses work exhaustion. Budgeted ingress now constructs policy receipts
internally from the current pre-state; its mixed traces retain the work and
handshake envelopes with query production included in the assumed operation
weight. Fueled policy-ingress polls now count every dispatched event, preserve
the exact ordered continuation and state semantics, and compose a conditional
dispatch-overhead bound with the selected prefix's policy and handshake
envelopes. Concrete dispatch and query costs, work outside dispatched events
and executor progress remain open.
Their contracts and boundaries are in [MODELS.md](MODELS.md).

1. Decompose every normative source unit into atomic claims, assumptions and
   completion criteria. Resolve differences between the original drafts,
   modified packet and current source. Context and superseded requirements need
   explicit dispositions. The current 34 groups and 76 atomic model obligations
   are not the final atomic list.
2. Extend budgeted policy/source admission with established resources and live
   per-source pending attribution. Establish concrete bounds for budgeted policy
   queries and receipt production, justify the per-dispatch guard and maintenance
   weights, and bound queue construction, pre-dispatch work and executor overhead
   outside the finite-poll envelope. Refine queue persistence, positive poll fuel
   and wakeup scheduling, including cleanup progress under sustained arrivals.
   Refine canonical source extraction, key uniqueness, indexed internal receipts,
   runtime receipt provenance from authenticated internal policy queries and atomic
   policy/source/global/pending enforcement against one pre-state.
   Verify expiry authority, current restriction generations, clock correspondence,
   bounded retention time and restart persistence. Extend the
   transition systems to resource-cap changes, authoritative policy ordering,
   reconnect/bootstrap, timestamp freshness and full rotation/reload behavior.
   Refine the committee threshold, any cache-preserving policy updates and the
   queue scheduler. Cover the Hub, Rotation and Later tiers as well as Launch,
   with counterexamples for weakened invariants.
3. Define a refinement relation from the exact Rust implementation and resolved
   transport dependencies to those systems. Prove simulation and invariant
   preservation for relevant callbacks, polls, timers, errors and cancellations.
   Source hashes and matching names are insufficient. First address the
   aggregate connection-limit gap recorded as B01.
4. Formalize parser/authentication boundaries and optimization equivalence:
   certificate and token checks, payload signatures, early refusal, repeated
   verification removal, gossip ordering and proof-of-possession prerequisites.
   Model cryptographic assumptions explicitly and disclose them.
5. Resolve D01-D12 before calling affected results passing: attack envelope,
   honest population, per-process budget, liveness and latency thresholds,
   admission semantics, quota scope, compatibility, test lanes, maintenance,
   cryptographic policy, provider topology and key/rollback ownership.
6. Collect M1a-M6 evidence with configuration and dependency hashes. Include
   representative NICs, firewall-disabled spoofed and real-address traffic,
   both swarms, Retry-only progress, shared NAT, committee reconnects, bulk sync
   with votes, storage persistence, hub loss, cold startup and URL migration.
7. Add verified evidence readers and complete release-gate evaluation. Treat a
   threshold change as a new qualification. Only replace the currently blocked
   full-qualification result when semantic coverage, implementation refinements
   and all applicable empirical/operator gates have evidence.

The input documents already require these distinctions. Numeric candidates such
as 1,024 incoming attempts, 16 KiB buffers, 5-second inbound and 8-second dial
timeouts are not accepted production settings in this repository.
