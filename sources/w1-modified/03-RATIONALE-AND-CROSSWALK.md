# Rationale and crosswalk to the original plan

This document explains the proposed changes to the user-supplied validator network hardening plan, revised 2026-09-21, and the original W1 drafts. It does not independently confirm the underlying repository findings. The proposed result is [the modified plan](01-MODIFIED-PLAN.md).

## 1. What the added parent-plan context changes

The parent plan already supplies a coherent architecture, launch topology, W0-W9 workstreams, priority tiers, and much of the sequencing. The W1 drafting pass also corrected significant source assumptions, including T6's scheduling mechanism and the effective handshake timeout.

Consequently, this revision preserves that organization. It does not replace it with a new architecture or an unrelated hierarchy of workstreams. The execution changes are aimed at aligning requirements, assigning shared work once, separating implementation boundaries, and making qualification explicit.

The intended closed-validator policy is specified in sections 3 and W2 of the parent, although the open questions still ask whether unknown peers should be refused. That is an inconsistency to resolve against the proposed target, rather than a reason to design admission from scratch. Likewise, the selected Retry fork makes basic T3 maintenance readiness a requirement, and W7/W9 already provide the correct homes for shared observations and experiments.

## 2. Changes and reasons

| Change | Original position | Proposed revision | Rationale and consequence |
|---|---|---|---|
| R01. Preserve architecture and workstreams | Single validators, QUIC, hubs, W0-W9, and four priority tiers. | Retain them and use smaller delivery slices within the existing structure. | The architecture is substantially specified. Another taxonomy would add coordination work without resolving implementation dependencies. |
| R02. Establish a governing requirement | Parent policies and draft investigation outcomes sometimes disagree. | Treat the modified plan as the proposed target, the backlog as assignments, and the acceptance document as closure criteria. Retain originals as research/disclosure evidence. | Prevents different implementers choosing incompatible answers from different documents. |
| R03. Release Retry with tests, metrics, and ownership | T2/T3 appear as followers of T1, while W1's production conditions already require them. | Develop them together and make them co-requirements of Gate 1. | Code availability and release readiness are different dependencies. This makes the existing production conditions operational. |
| R04. Narrow the initial fork | W1 includes Retry, knobs, timeouts, TLS refusal, key-exchange policy, and possible socket changes under a small code-size estimate. | T1a supplies the minimum hook/queue controls; T1b handles effective deadline control; other changes remain separate. | Keeps the first upstream and local review small, with independent failure and rollback boundaries. The hook's line count does not price all integration work. |
| R05. Verify fairness after changing the path | Corrected T6 yields in the node's run loop; W1 also requires processing Retry traffic. | Ship the focused T6 fix, then require Retry/Ignore/Refuse progress tests in T2b. | New rejection branches may not emit the event that reaches the outer-loop yield. This is an integration risk to test, not a claim about an implemented fork defect. |
| R06. Clarify validation and aggregate bounds | The policy says caps count validated addresses only and Retry holds no state. | Apply that rule to source quotas; keep aggregate bounds on unvalidated queues/work and account for transient state. | Avoids spoofed-source quota poisoning without leaving the pre-validation queues unbounded. Retry avoids expensive acceptance, not every packet-handling cost. |
| R07. Split T4's responsibilities | One issue includes total occupancy, attribution, failures, and timeout choices, with dependencies on T1/A1/M4. | T4a delivers a total cap/lifecycle; T4b adds validated-source attribution; T1b addresses timeout control. | The pieces protect different properties and can be developed at different times. An early total cap must not be presented as proving honest admission under a flood. |
| R08. Size established limits at host scope | T5 focuses on per-peer multipliers; the parent notes two swarms and exemptions. | Derive T5 from M3 and an explicit process-wide budget including trusted traffic. | A small per-peer number can still exceed the host budget after multiplying by peers, connections, streams, and swarms. |
| R09. Make real-address validator protection a launch test | T8 is Launch, but several defenses/tests are described under Hub, and the coverage table credits the firewall for real-address attacks. | Keep T8's validator control at Launch and include a multiple-real-address case in firewall-disabled M1a. Keep the larger M5 hub profile later. | Aligns validation with the rule that a validator stays live when its firewall is absent or wrong. A single-address test does not exercise the botnet assumption. |
| R10. Resolve the metrics contradiction | W7 forbids address labels; T08's goals/closure require export per source address. | Bounded internal attribution, aggregate production labels, and bounded diagnostic evidence. | Avoids creating another attacker-controlled memory surface and makes W7's existing rule binding across tickets. |
| R11. Separate qualification from optimization | M1 runs alongside Launch and gates nothing, while the shared-socket residual remains unmeasured. | M1a qualifies the declared launch load range; M1b investigates optimizations. | Independent fixes need not wait for a broad experiment, but the resilience claim needs evidence. Failed qualification cannot be waived by calling its investigation optional. |
| R12. Remove measurement/parameter ambiguity | Limits depend on M3/M4, which are also expected to run with the resulting changes. | Baseline/calibration, parameter selection, then regression: M3a/b and M4a/b. | Makes the sequence runnable and keeps initial numeric suggestions from turning into unsupported acceptance criteria. |
| R13. Give T10 its actual dependency | Tracking lists T1 while the text says the admission policy/gate is missing. | Require D05 and implemented/tested A5. Make earlier TLS refusal conditional on a benefit or required qualification outcome. | Authoritative admission is required for the topology; an earlier refusal point is a separate cost reduction. The early parsed identity is not authenticated authority. |
| R14. Separate crypto decisions | T9 ships with T10; T11 prescribes X25519-only using superseded cost figures; drafts permit no-change outcomes. | Share M6 profiling, remove the automatic T9-to-T10 coupling, and explicitly decide any accepted-group change. | Sharing a crate is not a sufficient dependency. Current costs, negative authentication tests, and cryptographic policy consequences are required before selecting the change. |
| R15. Avoid a metric forcing an unrelated fork | T11 closes only with a production negotiated-group metric that current node-owned code cannot expose. | Treat a permanent accessor/metric as separately justified; allow targeted measurement for the decision. | A no-change result should not automatically require maintaining a dependency modification only to finish a metric requirement. |
| R16. Provide launch fallback before full rotation automation | Fail-open is a general rule; A18's automatic grace window is Rotation. | Put the minimum stale/missing-input fallback and recovery test in A5; retain full automatic rotation work in A18. | The launch invariant and manual re-key procedure can justify deferring automation, but cannot silently defer a rule the launch behavior claims to satisfy. Hard budgets and authentication remain active. |
| R17. Make N2 accountable | A small row combines a red audit baseline, non-scanner advisory coverage, an inert dependency declaration, and key logging. | Split N2a-d with owners and shared T3 maintenance evidence. | These have different outputs and risks. A completed scanner job does not establish the rest are handled. |
| R18. Expand M2 prerequisites by scenario | The table names only a subset of the features its end-to-end rehearsal exercises. | Stage M2 by connectivity, public data, submission, and endpoint migration, then require a full final run. | A passing basic topology run cannot establish throttled forwarding, URL convergence, or every-worker startup. Tests can begin without waiting for every feature, while closure remains complete. |
| R19. Use distinct firewall/admission projections | W8/P2 assert equality; section 3.6 pre-permits governance-admitted validators before committee activation. | Require necessary protocol connectivity and explicitly test permitted future sources at the firewall. | The broader firewall set is deliberate during rotation. Equality may hold for a seeded launch configuration but is not the general invariant. |
| R20. Preserve evidence limits | W1 was re-established at 9b2a06b7; most other findings are older; provider and benchmark data are dated. | Pin references, confirm touched source at implementation, and requalify provider claims before use. | Avoids presenting this document rewrite as a fresh code audit, benchmark run, or provider verification. |

## 3. Original W1 crosswalk

Disclosure class below is the original draft's class. Grouping related engineering work does not merge public issue text with private advisory material.

| Original ID | Source draft | Proposed destination | Disposition |
|---|---|---|---|
| T1 | [T01](../w1/T01-quic-initial-unvalidated-cost.md) | T1a core Retry; T1b effective deadlines; selected configuration work. | Launch core narrowed; buffer/socket/TLS additions selected separately. Original private advisory. |
| T2 | [T02](../w1/T02-quic-listener-interop-tests.md) | T2a reusable fixtures; T2b Retry integration; shared M3/M4 and M1a. | Required release evidence, developed with the feature. Original public issue. |
| T3 | [T03](../w1/T03-patched-transport-crate-upkeep.md) | T3 plus shared N2 maintenance procedure. | Required before shipping the chosen fork. Original public issue. |
| T4 | [T04](../w1/T04-pending-inbound-unbounded.md) | A1, T4a total cap, T4b validated attribution, T1b deadlines, M4a/b. | Separate independently testable concerns; all selected launch bounds qualified. Original private advisory. |
| T5 | [T05](../w1/T05-per-peer-ceilings.md) | T5 with M3a/b and A3/S4 contracts. | Launch; measured whole-process budget. Original public issue. |
| T6 | [T06](../w1/T06-accepts-unbounded-per-poll.md) | T6 node fix and T2b integrated progress regression. | Early Launch fix; no transport fork prerequisite. Original private advisory. |
| T7 | [T07](../w1/T07-endpoint-driver-contention.md) | M1b investigation, then T7 implementation if selected. | Conditional; not an assumed dedicated-task solution. Original private advisory. |
| T8 | [T08](../w1/T08-validated-address-handshake-rate.md) | T8 with T4b accounting, M1a validator qualification, M5 hub profile. | Launch protection; bounded labels and aggregate work. Original public issue. |
| T9 | [T09](../w1/T09-redundant-cert-verification.md) | M6, then T9 if justified. | Conditional optimization; no automatic T10 dependency. Original public issue. |
| T10 | [T10](../w1/T10-late-refusal-of-strangers.md) | A5 contract/gate prerequisite; M6; optional earlier T10 refusal. | Authoritative admission remains Launch; earlier TLS placement is conditional. Original public issue. |
| T11 | [T11](../w1/T11-dialer-chosen-kx-group.md) | M6 and explicit D10 decision, then T11 if selected. | Conditional policy/performance change; no metric-only release obligation. Original public issue. |
| T12 | [T12](../w1/T12-single-inbound-socket.md) | M1b investigation, then T12 if selected. | Conditional socket/configuration change; honest-path trade-off required. Original private advisory. |

The original draft's closure as an investigation must be distinguished from implementing a remediation. If a no-change result is selected, record that result and whether the launch qualification still passes.

## 4. Remaining original tracking IDs

All other original work is retained below. Original prerequisites remain applicable unless this packet explicitly refines them. The descriptions here are a scope ledger, not replacement evidence for the original source findings. The complete inventory contains 102 original IDs, including the twelve T rows above.

### W0 dependencies

| ID | Scope retained | Tier or change |
|---|---|---|
| N1 | Patched dependency baseline. | Reported complete; confirm resolved baseline at implementation start. |
| N2 | Audit baseline/CI, advisory subscriptions, unused declaration, key logging. | Launch; split N2a-d and share evidence with T3. |

### W2 admission and peers

| ID | Scope retained | Tier or change |
|---|---|---|
| A1 | Inbound failure events and pending lifecycle. | Launch; shared with T4 and O2. |
| A2 | Trusted-peer config, all identities, startup dialing and lifetime redial. | Launch. |
| A3 | Three-way trust split. | Launch; define budget/exemption interfaces early. |
| A4 | Launch-committee identity seeding and bootstrap union. | Launch. |
| A5 | Authoritative inbound and outbound closed admission on every swarm. | Launch; include minimum fail-open fallback/recovery and shared contract. |
| A6 | Quiet-when-closed discovery, kad, and peer-exchange behavior. | Launch. |
| A7 | Bounded kad storage policy, independent identity confirmation, replication off. | Launch. |
| A8 | Periodic and failure-driven committee record refresh, verified results. | Launch. |
| A9 | Confirm merged bootstrap override/dial behavior. | Launch confirmation, not a request to recreate merged PRs. |
| A10 | Epoch bootstrap reseeding and retry/not-ready startup on every worker. | Launch. |
| A11 | Protect admitted peers from IP-collateral bans. | Launch; preserve bounded work and genuine protocol-violation handling. |
| A12 | Trusted slots for the DAO's public-RPC observers. | Launch. |
| A13 | Peer-manager IP/prefix accounting. | Hub; coordinate definitions with T8 without postponing validator qualification. |
| A14 | Correct eviction/Unbanned and admission counting. | Hub. |
| A15 | Per-peer connection-map leak and upstream fix. | Hub; confirm against resolved crate before implementation. |
| A16 | Peer exchange, dial-failure backoff, and quieter dial logs. | Hub. |
| A17 | Measured hub capacity profile. | Hub. |
| A18 | Automatic grace window and close condition. | Rotation; minimum launch fallback resides in A5. |
| A19 | Sweep existing connections on committee updates. | Rotation; launch live-connection policy documented in D05. |
| A20 | Timestamp clamp and repair path. | Rotation. |
| A21 | Recover stale mappings after repeated committee dial failure. | Rotation. |
| A22 | Record request for the push-LRU hazard. | Rotation. |
| A23 | Hub-mediated validator join test and timing. | Rotation. |
| A24 | Trusted/bootstrap config reload. | Rotation; manual launch procedure retained. |
| A25 | Explicit-peer lifecycle and removal. | Rotation. |
| A26 | Remove global ScoreConfig coupling. | Later. |
| A27 | Advertise/listen split, multi-address records, DNS support. | Later. |

### W3 serve path

| ID | Scope retained | Tier or change |
|---|---|---|
| S1 | Remove sleeps while holding serve permits. | Early Launch. |
| S2 | Gate Vote before task spawn. | Early Launch. |
| S3 | Epoch-pack progress floor and hold-time bound. | Launch. |
| S4 | Per-class budgets, per-peer slots, committee reserves. | Launch; M3 acceptance includes trusted bulk traffic. |
| S5 | Bound per-gossip task creation. | Launch. |
| S6 | Event-queue drop accounting. | Launch. |
| S7 | Priority lane for committee events. | Hub. |
| S8 | Scale and parallelize sync probes. | Hub. |
| S9 | fast_aggregate_verify after proof-of-possession confirmation. | Later; prerequisite preserved. |

### W4 gossip

| ID | Scope retained | Tier or change |
|---|---|---|
| G1 | Incoming RPC/frame and verification-work bounds. | Launch. |
| G2 | No-blocking-publish invariant and test. | Launch. |
| G3 | Honest per-topic message rates. | Hub. |
| G4 | Per-connection/class budget charged to propagation source. | Hub. |
| G5 | Role-aware gossipsub scoring. | Hub. |
| G6 | Freshness against replay beyond duplicate retention. | Hub. |
| G7 | Bound invalid-signature warning volume. | Hub; coordinate with O3's early log limiter. |

### W5 storage

| ID | Scope retained | Tier or change |
|---|---|---|
| D1 | Measure pack-actor contention and persistence latency. | Launch measurement; Gate 6 records the decision. |
| D2 | Queue bound/read isolation for live pack. | Conditional on D1; required if needed to pass its criterion. |
| D3 | Bound recent-pack thread/descriptor churn. | Hub. |
| D4 | Equivalent treatment for EpochRecordDb. | Conditional on D1. |

### W6 transaction ingress

| ID | Scope retained | Tier or change |
|---|---|---|
| R1 | Submit-only method profile and refusal status behavior. | Launch. |
| R2 | Reject batches in submit-only mode; screen where another profile requires it. | Launch. |
| R3 | Trusted proxy/source attribution. | Launch. |
| R4 | HAProxy/CDN reference, origin restriction, no interactive submit challenge. | Launch. |
| R5 | Correct 429/503, Retry-After, and endpoint demotion behavior. | Launch; explicit M2 prerequisite for throttled-front scenario. |
| R6 | Submit URL migration, convergence wait, worker-RPC isolation. | Launch rollout checkpoint. |
| R7 | Reference readiness URL. | Launch. |
| R8 | Configurable private health/metrics binds. | Launch. |
| R9 | Trusted-forwarder rate tiers. | Launch. |
| R10 | Observer read-pool cost and readiness/staleness profile. | Hub. |
| R11 | Node-side RPC rate limit. | Later. |
| R12 | Selectable tn_* RPC namespace. | Later. |
| R13 | Fee-cap default, forwarded protocol handling, HTTPS upstreams. | Later. |

### W7 observability

| ID | Scope retained | Tier or change |
|---|---|---|
| O1 | Retry/filter outcomes and bounded occupancy observations. | Launch; release with T1a/T2b. |
| O2 | Rejection reasons and listener failures. | Launch; integrate with A1. |
| O3 | Constant-size logging control and remotely driven site sweep. | Early Launch. |
| O4 | Quorum-shortfall and commit-gap signals. | Launch; required for scoring resilience. |
| O5 | Unresolved committee keys and submit-URL convergence. | Launch; required for final endpoint migration. |
| O6 | Per-class serve occupancy and offered/admitted work. | Launch; integrate with S4. |
| O7 | Anchor/peer-class handshake and ingress observations. | Hub, unless a bounded launch observation is needed earlier. |
| O8 | Peer-score and scoring-threshold observations. | Hub. |
| O9 | Host dashboards and alerts. | Launch operations. |

### W8 operations

| ID | Scope retained | Tier or change |
|---|---|---|
| P1 | Operator runbook and manual re-key procedure. | Launch. |
| P2 | Shared-source firewall/admission generator and namespace tests. | Launch; distinct projections and deliberate future-validator allowance. |
| P3 | Provider qualification. | Launch; reverify dated product claims before use. |
| P4 | Hub deployment and replacement for all worker identities. | Launch. |
| P5 | Rotation procedure and publication lead time. | Rotation. |
| P6 | Incident runbook and drill. | Hub. |

### W9 measurement

| ID | Scope retained | Tier or change |
|---|---|---|
| M1 | Real-NIC flood and transport bottleneck work. | Split M1a launch qualification and M1b conditional investigation. |
| M2 | Complete launch-topology rehearsal. | Launch; scenario prerequisites expanded and final complete run required. |
| M3 | Vote-under-sync and honest established-resource peaks. | Launch; M3a baseline, M3b selected-setting regression. |
| M4 | Blackouts, Retry reconnect, and handshake tails under load. | Launch; M4a baseline, M4b selected-setting regression. |
| M5 | Real-address hub flood and shared-source capacity. | Hub; validator real-address coverage belongs to M1a. |

M6 is a new measurement ID consolidating existing T09/T10/T11 investigations. It does not introduce a new transport or cryptographic mechanism.

### Later items

| ID | Scope retained | Tier or change |
|---|---|---|
| X1 | Pairwise-secret pre-crypto admission token research. | Later; cryptographic review prerequisite retained. |
| X2 | Fail-open pre-crypto address-filter research. | Later. |
| X3 | TCP bulk-sync pull surface for hubs through a gateway. | Later; not a second validator transport in the minimum plan. |
| X4 | Multiple raced published validator endpoints. | Later. |
| X5 | Range requests and constrained sync-peer selection. | Later. |
| X6 | Identity-weighted QoS after message-class budgets. | Later. |
| X7 | Runtime priority and execution/queue timeout questions. | Later; an actual failed launch criterion may explicitly promote required remediation. |
| X8 | Stable congestion-control adoption and a future fork knob. | Later; conditional on availability and observed need. |

## 5. Evidence and publication boundaries

The source plan's dated measurements and code citations remain references, with their stated limits. This packet avoids restating them as new validation. The manifest records hashes for the actual supplied W1 files; the parent plan is identified as the user-provided conversation text rather than assigned an invented file hash.

No issues, advisories, commits, upstream submissions, or deployments are created by this packet. Its internal grouping is for delivery ownership. Public issue extraction continues to require the original disclosure boundaries, and does not inherit private figures or attack-path detail simply because two items share an engineering milestone.
