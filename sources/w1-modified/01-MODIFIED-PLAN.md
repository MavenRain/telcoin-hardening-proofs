# Validator network hardening: modified plan

Date: 2026-09-21. Status: proposed revision.

This is a replacement execution plan based on the supplied validator network hardening plan and its W1 drafts. It preserves W0 through W9 and the original tracking IDs. Changes are explained in [the rationale](03-RATIONALE-AND-CROSSWALK.md); concrete W1 slices are in [the backlog](02-W1-DELIVERY-BACKLOG.md).

## 1. Objective and readiness claim

An external non-validator with commodity attack resources must not take a validator outside agreed liveness and resource bounds at traffic rates inside the qualified deployment envelope. The envelope must specify packet and handshake rates, traffic types, source diversity, network conditions, and the honest traffic running alongside the attack.

Qualify that claim with the host firewall disabled. Provider protection covers uplink saturation and is qualified separately. Shipping an independently useful fix is permitted before full qualification; describing the resulting deployment as meeting this objective requires the launch gates to pass.

The attacker knows validator addresses, ports, PeerIds, and BLS keys, can spoof source addresses, and can use many real addresses. Adversarial validators and state-sponsored attackers remain outside the primary model. A broken or compromised admitted hub remains a residual load source that message-class and resource budgets must contain.

## 2. Architecture and launch topology

Validators remain single nodes using libp2p QUIC. There is no sentry tier, delegated validator identity, second validator transport, or on-chain registry change. The BLS-signed NodeRecord continues to bind network identity to the chain-published key.

| Role | Target admission | Connectivity and responsibility |
|---|---|---|
| Validator | Closed profile | Direct committee connectivity plus configured trusted and bootstrap peers; primary and every worker swarm. |
| Hub | Open | Ordinary observer with its own keys; public gossip, discovery, records, and sync bridge. |
| Observer | Open | Hubs and other observers; public reads and transaction forwarding. |
| Submit front | Public HTTPS | Operator-controlled front for one validator, allowing only eth_sendRawTransaction. |
| Public RPC | Public HTTPS | Observer reads and forwarding through validator submit fronts. |

Admission defaults to Open for compatibility. Operators explicitly select the closed validator profile during rollout. A closed validator admits the previous, current, and next committee, configured trusted peers, and bootstrap peers. The same policy governs inbound admission and both outbound decision points.

Every validator configuration seeds the other launch validators and its hubs with primary and all worker identities. Discovery through hubs is not a prerequisite for committee connectivity. The required rehearsal includes all ten validators starting cold with every hub unavailable.

Hubs carry no validator keys and cannot authorize payloads on a validator's behalf. Consensus payload authentication and forwarding attribution remain as in the original architecture. Direct validator connectivity sustains consensus when hubs disappear. Public bootstrap, record resolution, and the public live view can degrade during hub loss and must be observed as such.

Deploy at least five hubs across providers and ASNs, with configurable bootstrap replacement. Preserve direct submit-front access and test transaction paths during hub loss with the intended record/configuration state. Do not infer that a fresh observer can discover unavailable records merely because consensus continues.

The reference deployment is ten validators, each on Ubuntu with 8 CPUs and 32 GB RAM, one node process and two swarms. An honest reconnect includes nine other committee members per swarm plus configured hubs and other permitted peers. Swarm counts and the non-committee population must be explicit inputs to every budget.

### 2.1 Data flows and validator changes

Consensus travels directly between validators over the primary and worker QUIC ports. Hubs relay committee-origin gossip without acquiring signing authority; receivers continue to check the payload originator and required validator records. M2 proves that forwarding still reaches observers beyond the directly connected hubs.

Observers discover peers through hubs, kad, and peer exchange, and sync from connected hubs or observers. Consensus output carries the batch data needed by observers. A hub's primary swarm supports that public data path under the service budgets. Closed validators do not resume random public discovery or outbound dialing to strangers.

Validator records are available through their direct peers and hubs. Record resolution supports both gossip validation and discovery of submit URLs, so periodic refresh and O5 convergence are functional requirements. Public RPC observers forward transactions to the owning validator's advertised HTTPS submit front; validator worker RPC is reached only through its operator's approved front after migration.

At launch, production identities and addresses equal the distributed seeded configuration. Until the rotation workflow is qualified, distribute a changed validator entry and roll the other validators' configurations/restarts as required by the manual procedure, with no more than f validators changing concurrently. Periodic verified record refresh provides the planned recovery path, and the procedure must prove it works with the admission state in use.

For later joins, a governance-admitted validator first publishes its record through open hubs. Existing validators resolve it when it becomes relevant to the next committee. Publish addresses early enough for provider ACL changes before activation; the chain's notice alone is not assumed to cover that operational delay. Single-address/listen coupling remains a constraint until A27 is implemented.

## 3. Rules that implementations must share

### 3.1 Authentication, address validation, and resource limits

Address secrecy and IP allowlists do not establish authorization. A validated address establishes return reachability, not committee membership. Payload authentication remains mandatory.

Every unvalidated incoming attempt processed by the Retry policy is challenged before acceptance creates full handshake state. Account for transient packet, parsing, queue, and token-processing costs; do not describe Retry as eliminating all state or CPU work.

Apply per-source quotas and source-based penalties only after return reachability is validated. Aggregate queue, memory, and work bounds also cover traffic before validation. Unvalidated traffic must not consume a victim address's privileged quota or acquire an exemption by claiming that address.

Rate, occupancy, and established-resource limits protect different stages. Keep distinct accounting for attempts queued before acceptance, accepted but unfinished handshakes, and established connections. A cap in a later stage does not remove the earlier stage's cryptographic or queue cost.

Budgets must compose across swarms and across attacker-controlled identities and prefixes. A per-address or per-peer limit alone is not a whole-process bound. Explicitly test simultaneous attack traffic on both swarms and traffic distributed across many validated addresses.

### 3.2 Admission and fail-open behavior

Use one admission contract for the closed profile, peer management, and any later TLS prefilter. Define membership inputs, snapshot/version semantics, trusted and bootstrap peers, updates, and fallback behavior once.

Missing, stale, or contradictory admission-policy inputs relax the affected authorization decision to the documented Open/Grace behavior. They do not disable signature checks, protocol validity checks, finite resource budgets, or message-class isolation. An unauthenticated identity extracted from a certificate cannot grant trusted status or a resource exemption.

The minimum launch implementation must exercise fallback and recovery. Closing after fallback requires valid policy inputs and the documented resolution condition, based on at least committee size minus f current-committee records as proposed in the original grace design. Resolution, connected-peer count, and consensus readiness are separate observations. The exact stale-input and recovery conditions are recorded in the admission decision before enabling Closed.

The complete automatic rotation workflow may remain in the Rotation tier. It cannot be the only implementation of the fail-open behavior required at launch. Keep the seeded launch invariant and manual re-key procedure explicit until rotation automation is qualified.

### 3.3 Trust and scheduling

Split trust into admission, connection-retention/mesh treatment, and exemption from load-induced penalties. Protocol violations still count and may cause a ban. Admission and retention privileges do not authorize unbounded CPU, memory, or bulk service work.

Budget by message class so bulk sync cannot starve votes, certificates, or epoch records, including when every sender is legitimate. Measure consensus progress and catch-up together.

Task progress must hold on Accept, Retry, Refuse, and Ignore paths. An outer-loop yield fixes only paths that return control to it. Bound processing inside transport polling as necessary, preserve wakeups, and test a sustained Retry-only workload. Process eligible traffic fairly; do not require an unbounded drain of all arrivals in one poll.

### 3.4 Metrics and evidence

Use W7 for shared production metrics and W9 for shared measurements. Define each counter's stage and unit so a swarm-level pending event is not mistaken for the beginning of all earlier transport work.

Production labels are bounded. Do not label by arbitrary source address or attacker-generated PeerId. Any internal source-accounting table and diagnostic export has a cardinality, retention, and eviction bound. Committee/trusted-peer labels require a bounded lifecycle if used.

Record resolved dependency versions, configuration, hardware, traffic, and measurement overhead with each result. Earlier ring-provider timings and emulated-network flood results identify hypotheses; they do not determine production limits or prove current bottlenecks.

## 4. Workstreams

### W0. Dependency hygiene

N1 is reported complete through the dependency updates ending at 9b2a06b7. Confirm the resolved versions when creating the implementation branch; do not repeat the completed upgrade as new feature work.

Split N2 into accountable outputs: N2a, triage the reported audit findings and introduce an explicit CI baseline; N2b, cover repository advisories and carried patches as well as scanner-visible advisories; N2c, remove or clearly resolve the inert quinn-proto declaration; N2d, assign and resolve the KeyLogFile production-behavior question. A scanner's absence of a finding does not establish advisory coverage. Do not turn the reported eleven findings into an unexplained blanket waiver.

N2 and T3 share one dependency-maintenance procedure. Record the actual source selected by Cargo, upstream base, revision, patch owner, update expectations, and verification evidence.

### W1. Retry and transport hardening

Deliver a minimum maintained Retry patch first. T1a supplies the pre-accept decision hook and the configuration access needed for bounded incoming queues. Apply always-on Retry to unvalidated sources on every role and every swarm. Preserve stock-dialer interoperability and existing token semantics unless a separately justified change is selected.

Develop T2 tests, T3 maintenance readiness, and O1 metrics alongside T1a. They are requirements for releasing the patch. The source plan's 1,024 incoming attempts, 16 KiB per incoming buffer, and 16 MiB total are benchmark starting candidates, not approved production values. Record their per-swarm scope and include other retained state when comparing with a host budget.

T6 remains a focused node-side scheduling fix. It can ship independently against the current path, but its progress regression must also pass against the completed Retry fork, including rejection paths that may not produce a swarm event.

T1b separately makes inbound and outbound timeout behavior understandable and controllable where required. Verify the effective outer transport deadline and actual propagation of settings before changing values. The source plan's suggested 5 s inbound and 8 s dial values require M4 evidence; editing the ineffective 65 s configuration field is not sufficient.

Split T4 into a total pending-occupancy bound with correct lifecycle accounting, and validated-source pending attribution. T8 supplies handshake-start work budgets, with bounded bookkeeping, tested source diversity, and explicit treatment of trusted traffic. T5 sets established-peer ceilings from M3 and a whole-process budget. None of these controls substitutes for the others.

Keep early identity refusal, duplicate certificate-work removal, key-exchange policy changes, accept-task restructuring, and socket parallelism as separate changes. T10 requires the W2 admission contract and authoritative gate. T09/T10/T11 share M6 profiling; T07/T12 share M1b bottleneck investigation. A change becomes launch-required if the qualification result or an explicit policy decision requires it, rather than merely because it touches the same fork.

The proposed default is to retain the resolved cryptographic policy while measurements and any policy change are reviewed. X25519-only is not silently bundled into Retry. Any selected policy change records compatibility consequences and passes negative authentication tests. Server-side group reordering is not treated as a mitigation for the client-order behavior reported in the source plan.

A shipped patch has a 40-hex revision, mirrored source, and a named owner. Consolidate the carried minimum patch as a single auditable commit on its upstream tag/base, as required by the original plan. Keep libp2p upgrades separate from changes to the carried patch. Prepare upstream configuration and hook submissions as separately reviewable changes; an upstream merge is not assumed to arrive before launch. Additional modified crates get their own recorded patch scope and advisory coverage.

### W2. Admission, discovery, and peer lifecycle

Retain A1 through A12 as launch work. They cover inbound outcome handling, trusted-peer configuration and redial, the three-way trust split, launch seeding, authoritative inbound/outbound admission, quiet-when-closed behavior, the kad store gate and independent identity confirmation, committee-record refresh, bootstrap behavior, retry/not-ready startup behavior, collateral-ban protection, and reserved connectivity for the DAO's observers.

The minimum launch fallback described in section 3 is part of A5, even though the full automatic grace window remains A18. Establish the admission contract early so T4b, T8, and a conditional T10 use the same definitions. Test exemptions against real resource budgets and test policy updates without granting privileges to unverified identities.

Keep the original Hub work A13 through A17: source/prefix peer accounting, eviction and ban correctness, the per-peer map leak, peer-exchange/backoff/logging behavior, and a measured capacity profile. T8's validator protection and its firewall-disabled qualification remain Launch work; the larger hub-population exercise remains M5.

Keep A18 through A25 in Rotation, apart from the minimum A5 fallback already promoted to Launch. Preserve record timestamp repair, cached-mapping recovery, explicit-peer lifecycle, re-resolution, hub-mediated join testing, and configuration reload. A26 and A27 remain Later.

### W3. Serve-path resource bounds

Ship the independent S1 sleeps-under-permit and S2 Vote-admission fixes early. Retain S3 through S6 at Launch: progress and hold-time bounds, per-class budgets, bounded gossip task creation, and drop accounting. Attach occupancy and rejection metrics to the relevant behavior changes.

S4 must demonstrate that legitimate bulk traffic from admitted peers cannot starve consensus-critical classes. Use M3's catch-up and vote-latency workload. A lower numeric limit without that regression is incomplete.

S7/S8 remain Hub work. S9 remains Later and depends on the proof-of-possession prerequisite being established before changing aggregate verification.

### W4. Gossip control

Retain G1/G2 as Launch work: constrain incoming RPC/frame verification work and prove the no-blocking-publish property. Confirm the actual order in which the resolved library applies its limits.

G3 through G7 remain Hub work, preserving measured per-topic rates, propagation-source accounting, bounded per-class connection budgets, role-aware scoring, freshness, and log limiting. Scores are not a replacement for resource bounds, and load-induced penalties must not ban the honest hubs needed by the topology.

### W5. Storage measurement

D1 measures live-pack queueing and commit-persist latency under the actual closed-validator workload, including admitted hub reads. Set the acceptable persistence impact before selecting an intervention. D2 and D4 become required when those measurements fail the agreed criterion; otherwise record why no change is selected. D3 remains unconditional Hub work.

### W6. Transaction ingress

Retain R1 through R9 as Launch work: submit-only method screening, batch treatment, authenticated proxy/source attribution, the front configuration, overload-aware forwarding, endpoint migration, readiness configuration, private health/metrics binds, and trusted-forwarder rate tiers.

The front exposes only eth_sendRawTransaction to the validator worker RPC. It rejects batches in the submit-only profile, uses the specified non-2xx behavior for overload and refused methods, and avoids interactive CDN challenges. Tests must distinguish a transaction verdict from transport overload or refusal. Verify 429/503 handling and Retry-After without cascading endpoint demotions.

Keep the old advertised endpoint available until O5 shows the required record/URL convergence and the new submission path passes. Then complete the worker-RPC isolation step. R10 remains Hub work; R11 through R13 remain Later.

### W7. Observability

Keep O1 through O6 and O9 at Launch. Implement relevant metrics with their features rather than creating a later instrumentation bottleneck. O3's constant-size logging control is an early independent fix. O4's quorum/commit-gap signals are part of liveness qualification.

O7/O8 remain Hub work unless a specific launch test needs an earlier bounded observation. Respect the no-address-label rule and the distinction between internal attribution and exported time series. Bind health and metrics privately as part of the deployment profile.

### W8. Operator edge and configuration

Retain pass-through, source-preserving protection on consensus ports and proxy/CDN protection on RPC fronts. Preserve direct IP-literal consensus connectivity, primary and worker port coverage, source matching that permits required ephemeral ports, the host conntrack strategy, provider diversity, and mitigation-on interoperability qualification from the original runbook requirements.

Each operator provides a dedicated source-preserved IP-literal endpoint, without consensus-port NAT or an L4 proxy. Cover every primary and worker port at the provider and host. The host rules follow the original ingress/raw filtering and bidirectional notrack design, match addresses rather than connection-tracking state, and permit required ephemeral source ports. Test the generated rules functionally.

Do not apply per-source or global kernel rate limits to consensus ports or handshake packets: forged listed sources can consume those budgets. Do not count an edge source-rate limit as proof of protocol liveness. Require always-on volumetric protection with a stated capacity and no unqualified throttling of the supported consensus UDP traffic. No provider or ASN hosts more than f validators; evaluate hub diversity separately under the same rule.

Size requested socket buffers from measured honest and attack behavior, set the required host receive-buffer ceiling, and verify the host actually grants the requested setting. Put submit fronts on a different address, preferably a different uplink, and restrict their origins to the approved fronting path. Provider-specific product claims in the supplied plan are dated candidates; P3 verifies them before contracting or deployment.

P2 generates firewall and protocol configuration from one source of truth with distinct projections. Require every intended protocol peer's required address to be permitted. During rotation, governance-admitted future validators may be pre-permitted at the firewall before protocol admission, as section 3.6 of the source plan requires. Test that deliberate difference; do not assert unconditional equality of the two sets.

P1 through P4 remain Launch work, P5 Rotation, and P6 Hub. Document hub keys, removal, replacement, and the manual validator re-key procedure while reload is unavailable.

### W9. Shared measurement and qualification

Split M1 into M1a, minimum launch flood qualification on representative real networking hardware, and M1b, optional bottleneck/architecture investigation. M1a includes forged-source and multiple-real-address traffic against validators with host firewall enforcement absent, within the declared load range. M1b compares interventions only after attribution. A failed M1a blocks the resilience claim even while independent fixes continue to ship.

Split M3 and M4 into baseline/calibration and post-change regression runs. This removes the ambiguity where a benchmark waits for the limits that are supposed to be chosen from it. M3 covers vote latency during sync and honest resource peaks. M4 covers Retry reconnects, blackouts, timeout behavior, and handshake tails under load.

M2 is a staged topology rehearsal with explicit prerequisites for each scenario. Its final pass includes all primary/worker swarms, second-ring observers, records and URL refresh, throttled submission, cold hubs-down startup, an empty-data-dir restart, and hub loss/replacement. Record which cases cannot run until their W2, W3, W6, and observability prerequisites exist.

Keep M5 for the larger hub population, shared-NAT, and real-address capacity exercise. Add M6 to price handshake stages, certificate work, refusal placement, and key-exchange choices on current dependencies. See [the acceptance specification](04-DECISIONS-AND-ACCEPTANCE.md) for the required outputs.

## 5. Execution milestones

| Milestone | Outputs | Completion condition |
|---|---|---|
| A. Establish contracts and remove independent defects | Scoped source confirmation; N2 owners; admission/measurement definitions; T6, A1, S1/S2, O3 in separate changes. | Each change has its own regression; unresolved qualification inputs are recorded with owners. |
| B. Release the minimum maintained Retry patch | T1a, T2a/T2b, T3, O1; integrated progress checks. | Required behavior, token, compatibility, and maintenance checks pass. This qualifies the feature, not the entire deployment. |
| C. Enforce measured bounds and closed topology | T1b as needed, T4a/T4b/T5/T8, W2 launch behavior, W3/W4 launch bounds, W6 fronts. | M3/M4 regressions and relevant M2 scenarios pass with the selected configuration. |
| D. Qualify the launch configuration | M1a, final M2/M3/M4, D1 outcome, core observability, provider and operator qualification. | The declared liveness/resource limits hold, including firewall-disabled validator tests and hubs-down cold start. |
| E. Roll out and continue conditional work | Controlled validator closure, endpoint migration, Hub and Rotation tiers, justified transport/crypto changes. | Each rollout checkpoint passes; later work has its own qualification and rollback criteria. |

These are release outcomes, not a requirement that all work be serial. Start the minimum Retry work and its fixtures while independent fixes and operational inputs proceed. Run measurements early enough to inform limits. Keep optional experiments off the critical path unless a required qualification fails.

## 6. Rollout and rollback

1. Deploy compatible defect fixes and the qualified minimum Retry feature. Include source pins, metrics, and an operator-visible way to identify the build and configuration.
2. Provision validator, hub, primary, and worker identities. Establish trusted-peer redial and prove direct committee connectivity. Confirm hubs receive and forward the required public data.
3. Enable the qualified closed profile one validator at a time. Verify admission, records, quorum/commit progress, and reconnect behavior at each step. Keep a documented profile rollback with hard resource budgets intact.
4. Apply generated edge and host firewall configuration after protocol rejection has been demonstrated without it. Validate provider mitigation-on behavior before accepting a production placement.
5. Migrate advertised submit URLs. Maintain the old path until convergence and throttled-forwarding tests meet the release criterion, then isolate worker RPC as specified by the profile.
6. Record the final deployment manifest, test evidence, owners, and incident/rollback procedures. A failed gate pauses the affected rollout step rather than being relabeled as a passing optimization study.

Do not assume wire compatibility proves rollout liveness. The mixed-version, restart, bootstrap, configuration, and endpoint-migration scenarios establish the operational claim.

## 7. Residual risks and deferred scope

Provider capacity and diversity bound the price of overwhelming the uplinks of enough validators; the protocol does not remove that risk. Retry does not eliminate socket contention or prevent real-address attackers completing the challenge. The qualified load range and residual public-tier degradation must be stated with the release.

Keep the original Later scope X1 through X8, including exploratory admission mechanisms, bulk-transfer alternatives, multi-address records, sync improvements, QoS, execution/runtime queue questions, and congestion-control follow-up. No such item is silently promoted into the minimum Retry change. Any measured failure that makes one necessary is an explicit reclassification with an owner and acceptance test.

Unresolved provider, network, topology-population, timing, budget, and policy inputs are listed in [the decisions document](04-DECISIONS-AND-ACCEPTANCE.md). None is filled with an invented benchmark result or a presumed upstream delivery date.
