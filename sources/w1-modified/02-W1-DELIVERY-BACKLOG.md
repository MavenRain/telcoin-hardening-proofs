# W1 delivery backlog

This backlog implements the proposed boundaries in [the modified plan](01-MODIFIED-PLAN.md). See [acceptance criteria](04-DECISIONS-AND-ACCEPTANCE.md) for shared decisions, test definitions, and release gates. Supporting source drafts remain under ../w1.

## Assignment and release rules

- Assign an owner to each behavioral slice and one owner to the shared admission/accounting contract. These roles do not imply parallel edits to the same files without coordination.
- Prefer one behavior change and its meaningful regressions per PR. A research card closes with a decision; a behavior card closes with demonstrated behavior.
- Develop T2a and T3 readiness while T6/A1 and other independent fixes proceed. Build T1a with its T2b/O1 co-deliverables.
- Baseline measurements and implementation may proceed together, but production parameter approval requires the calibration and regression results.
- T1a code, T2b tests, T3 maintenance readiness, and O1 observations jointly release the Retry feature. T1a landing does not make later tests or maintenance optional.
- Keep A5's authoritative admission and launch fallback in W2. T10 is an optional earlier enforcement point with a real dependency on that contract and gate.
- M1a qualifies the deployment. M1b and M6 decide whether additional implementation is justified. Failed required qualification still requires remediation.

## Dependency outline

T2a and T3 preparation run alongside T6 and A1. They enable T1a and the completed T2b suite. A1 enables total pending accounting in T4a. T1a provides validated-address integration for T4b/T8. M3a and M4a calibrate T5 and T4/T8 settings; M3b and M4b validate the selected settings. A5's contract informs exemptions, and implemented A5 precedes any T10 early-refusal feature. M6 independently selects T9/T10/T11 work. M1b independently selects T7/T12 work. The full launch configuration then passes the applicable release gates.

This outline distinguishes starting work, finishing code, approving configuration, and qualifying a release. It is not an instruction to wait for every investigation before beginning any fix.

## T2a: Reusable listener and interoperability fixtures

Status: Launch foundation; start immediately. Suggested owner: CI and network maintainers.

Build reusable fixtures around the node's real listener configuration, with separately built old/current peers where needed. Record honest reconnect baselines and distinguish ordinary CI from tests needing controlled networking. Keep traffic generation and measurement reusable across T1, T4, T5, T8, and W9.

Prerequisites: No new runtime feature is required to begin. Pin the reported N1 baseline and the supported release pairs from D07. Investigate D08 as engineering work.

Completion evidence: Both required cross-release directions are exercised; failures and effective deadlines are observable; one reproducible baseline and test-lane inventory exist. Fixture creation does not itself claim flood resilience.

Original material: T02; W9 M3/M4; source plan sections W7/W9.

## T3: Make the carried patch identifiable and maintainable

Status: Launch prerequisite for releasing a patch. Suggested owner: Dependency and release owners.

Record the mirror, upstream tag/base, 40-hex revision, patch diff, Cargo source/feature resolution, advisory coverage, maintenance owner, update expectations, and upstream submission plan. Coordinate N2a/N2b instead of creating a second advisory process. Extend the receipt if a later change also modifies libp2p-tls or quinn.

Prerequisites: Basic ownership and source decisions precede release. Exercise the procedure on the first real patch; completion is not deferred until upstream accepts it.

Completion evidence: A reviewer can identify exactly what is built from tracked information; matching against a known relevant advisory is demonstrated for the actual source form; source pins and honest compatibility checks pass. The record includes the required behavior on the next dependency update. Large synthetic no-op topology exercises are not a separate prerequisite for all W1 work.

Original material: T03; N2; W1 fork conditions.

## T6: Keep the node's event loop making progress

Status: Launch; independent runtime fix. Suggested owner: Network runtime maintainer.

Characterize and fix the reported unbounded run between task yields. Use the actual command/timer behaviors and continuous ready events, not only a count of accepted connections. Keep the node-side change focused; coordinate later transport work through a shared regression.

Prerequisites: Can start without the fork. The integrated T2b suite must rerun the progress checks after T1a adds Retry/Refuse/Ignore branches.

Completion evidence: Commands and all relevant timers continue to progress under sustained arrivals; honest gossip and request-response latency stay inside the selected regression bound. Record whether the failure was reproduced and under which conditions. A count of one accept per poll is not the success criterion.

Original material: T06; source plan W1 policy and corrected T6 row.

## A1: Define inbound outcomes and release pending ownership correctly

Status: Launch; shared W2 dependency. Suggested owner: Network peer-lifecycle maintainer.

Handle the relevant inbound failure events and expose bounded outcome counters. Establish which component owns a reservation and when that ownership begins and ends. Share this lifecycle definition with T4a/T4b rather than adding independent counters that disagree.

Prerequisites: Can start independently. Coordinate O2 and the selected connection-limits implementation.

Completion evidence: Tests cover refusal before reservation, failure after reservation, establishment, established-hook refusal, timeout, and cancellation. No double release or refund of an unowned slot occurs; occupancy returns to baseline and reasons are distinguishable.

Original material: A1; T04 implementation details; O2.

## T1a: Minimum pre-accept hook, Retry policy, and queue controls

Status: Launch core. Suggested owner: Transport maintainer.

Add the minimum incoming decision/configuration surface and apply always-on Retry before accepting unvalidated sources. Expose the incoming queue controls needed to bound temporary state. Preserve the manifest's resolved feature/provider selections. Keep processing bounded on all decision outcomes, including when no connection event is emitted.

Prerequisites: T2a fixtures and T3 preparation; confirm the resolved N1 baseline. O1 and T2b are release co-deliverables. T6's integrated result is required for Gate 1.

Completion evidence: Gate 1 passes: required stock peers connect, token behavior is covered, all decision paths make progress, temporary work/state is accounted for, production observations are bounded, and the patch is identifiable. Candidate queue settings are recorded with their per-swarm scope; full deployment qualification remains Gate 3.

Original material: T01; T02/T03; O1; source plan W1.

## T2b: Prove Retry behavior and integrated fairness

Status: Launch release requirement. Suggested owner: CI and transport maintainers.

Implement the Retry-specific integration cases from the shared acceptance matrix: token edges, controlled spoofing, all filter outcomes, honest mass reconnect, supported release pairs, and effective timeout behavior. A Retry-only flood must exercise progress without depending on an accepted-connection event reaching the outer loop.

Prerequisites: Can develop alongside T1a; the complete suite runs against T1a plus T6. Controlled networking capability comes from D08, with representative hardware qualification separately owned by M1a.

Completion evidence: The required integration cases pass on the candidate build, with test cadence and environments recorded. Tests demonstrate the intended changed behavior rather than permanently asserting that the old unconditional accept behavior is correct.

Original material: T02; T06; W1 production conditions; Gate 1.

## T1b: Separate effective inbound and outbound deadline control

Status: Launch when needed for the selected timeout configuration. Suggested owner: Transport and node configuration maintainers.

Trace the real wrapper deadlines and expose or correctly apply the settings needed to control directions independently. Avoid bundling receive-buffer tuning, socket parallelism, or TLS policy into this change. Add a receive-buffer knob separately only if M1 shows repository control is required beyond host configuration.

Prerequisites: T2a for deadline/compatibility tests. Select production values from M4a and D01-D04. T4a's total-cap implementation need not wait for a new timeout value.

Completion evidence: Tests demonstrate the deadline that actually fires in each direction, correct setting propagation, and honest behavior with Retry and loss. Proposed 5 s/8 s values are not accepted solely because they occur in the old plan. Any selected change passes M4b.

Original material: T01 timeout scope; T04; source plan W1/W2.

## T4a: Bound total pending occupancy

Status: Launch; separate from source attribution. Suggested owner: Network peer-lifecycle maintainer.

Set and observe an effective total pending-incoming bound. Account for memory, tasks, and all swarms on the host. Use the existing limits interface where it meets the requirement. This controls retained pending state after acceptance and does not substitute for pre-accept Retry or CPU protection.

Prerequisites: Code/lifecycle work needs A1. Production settings need M4a and D03/D04; initial implementation and fixtures can proceed before those values are final.

Completion evidence: The cap holds under sustained unfinished handshakes; cleanup is exact; memory/state remains within the selected bound; honest reconnects pass M4b. Record that a total cap alone does not establish fair admission for honest peers under attack.

Original material: T04; A1; M4.

## T4b: Attribute pending occupancy to validated sources

Status: Launch. Suggested owner: Network admission maintainer.

Add bounded source or prefix accounting for pending occupancy after address validation. Share key normalization, validation provenance, eviction, and exemption rules with T8. Preserve aggregate bounds and never charge a spoofed validator address before validation.

Prerequisites: T1a's validated-address integration; A1/T4a ownership model; D05/D06 shared admission and quota contract; M4a calibration.

Completion evidence: Source churn, multiple prefixes, shared NAT, restart, policy transitions, and all release paths preserve both attribution and aggregate limits. One source filling its allowance does not invalidate the required honest-connectivity result. No unbounded per-source metric labels are introduced.

Original material: T04; T08; W2; W7.

## T8: Bound validated handshake-start work across the node

Status: Launch for validators; extended hub profile in M5. Suggested owner: Network admission maintainer.

Control handshake-start work after Retry using source/prefix and aggregate budgets, with bounded bookkeeping and explicit treatment of trusted traffic. Address validation is not committee authentication. Use the shared T4b accounting definitions, but keep rate and occupancy counters distinct. Export aggregate outcomes, not arbitrary address labels.

Prerequisites: T1a; shared accounting and policy contract with T4b/A5; M4a for honest bursts. Coordinate A13/A14 for later peer-manager accounting and security-state eviction behavior.

Completion evidence: Both swarms satisfy the process budget under traffic distributed across many validated sources and new identities. Honest reconnect and shared-source cases pass. M1a verifies validator behavior with the firewall disabled; M5 later qualifies the larger hub population.

Original material: T08; original Launch tier; W2 Hub items; M5; Gate 3.

## T5: Set established-peer limits from a whole-process budget

Status: Launch; parallel with admission work. Suggested owner: Network and consensus maintainers.

Measure the honest use of connections, streams, window credit, retained bytes, and service capacity. Select limits that compose across peers, exemptions, and swarms. Coordinate trust treatment with A3 and message-class isolation with S4; distinguish credit from resident memory.

Prerequisites: M3a and D02-D04 for selected production values. Does not require T10 or a cryptographic optimization.

Completion evidence: M3b passes for catch-up plus critical traffic and for hostile attempts to reach the ceilings. The budget derivation includes trusted/exempt peers and both swarms. Any request/stream shedding is observable and does not violate the required critical-message bound.

Original material: T05; M3; A3; S4.

## M6: Profile shared handshake costs on current dependencies

Status: Shared investigation; starts alongside core work. Suggested owner: Transport measurement owner.

Produce one cost profile for T09/T10/T11, separating first-flight, certificate, repeated verification, refusal-dispatch, full/resumed, and key-exchange costs. Include adversarial certificate choices and claimed admitted identities without valid proof. Record current versions and realistic reconnect/refusal frequency.

Prerequisites: Resolved baseline and reusable T2a fixtures. Instrumented experiments can precede a permanent production accessor; record their patches and overhead.

Completion evidence: A reproducible report supports separate go/no-go or policy decisions for T09/T10/T11. Historical ring-provider timings are not reused as current measurements. An unknown or small benefit can close the investigation without creating a runtime change.

Original material: Measurements in T09, T10, and T11; new consolidated W9 task.

## T10: Move identity refusal earlier only where justified

Status: Conditional optimization; authoritative closed admission remains Launch. Suggested owner: Admission and TLS maintainers.

If M6 and qualification justify it, introduce an early refusal using the same admission contract as W2. Keep the authoritative established gate and current-policy enforcement on resumed connections. An identity read before signature verification is untrusted and cannot grant exemptions.

Prerequisites: D05, implemented/tested A5, M6 decision, and T3 coverage for any additional modified crate. T1a alone is insufficient.

Completion evidence: The selected workload shows the required benefit; invalid proofs still fail; claimed admitted identities gain no privileges; stale-input fallback and resumed-session policy changes are covered. Required stock peers and honest reconnects still pass.

Original material: T10; A5; source plan W1/W2; M6.

## T9: Remove repeated certificate work without changing authentication

Status: Conditional optimization. Suggested owner: TLS maintainer with cryptographic review.

Implement only the repeated work selected by M6. Preserve certificate, extension, transcript, and PeerId semantics across callbacks and concurrent handshakes. Shared verifier state or caching requires explicit lifetime and isolation reasoning.

Prerequisites: M6 and T3 if a dependency patch ships. There is no mandatory dependency on implementing T10 merely to start this investigation or change.

Completion evidence: Measured benefit is recorded; each required signature-corruption case still fails; concurrency/session isolation and stock-peer compatibility pass; repeated-work counts change as intended without weakening verification.

Original material: T09; T02 compatibility fixtures; M6.

## T11: Select any cryptographic group change explicitly

Status: Conditional policy/performance change. Suggested owner: Network maintainer with cryptographic review.

Retain the resolved accepted-group policy unless D10 selects a change. If narrowing is chosen, document its purpose, current-provider evidence, removed support, and interoperability consequences. Do not treat server list reordering as a solution to the reported client-order selection behavior. A permanent negotiated-group metric is a separately justified observability feature.

Prerequisites: M6, D10, T2a/T2b release matrix, and T3 coverage for any modified TLS/configuration crate.

Completion evidence: Selected groups and supported peers behave as intended; current-provider CPU and honest timing meet the decision criteria; authentication regressions pass. The task does not force a permanent fork/API solely to close a metric requirement after a no-change decision.

Original material: T11; W7; source plan's X25519-only proposal; M6.

## M1b: Attribute socket and endpoint contention once

Status: Conditional architecture investigation. Suggested owner: Transport measurement owner.

Reuse M1a and add targeted observations to distinguish queue overflow, driver work, endpoint lock contention, and swarm scheduling. Compare only justified variants and include the honest throughput/latency trade-off. Return separate decisions for T7 and T12.

Prerequisites: Representative baseline with T1a and integrated T6 behavior. Temporary instrumentation is versioned and its overhead recorded.

Completion evidence: The report identifies a supported intervention or an explicit no-change result. It does not infer that moving work to another task removes a shared lock. If launch qualification fails, the selected remedy must subsequently pass M1a.

Original material: T07 and T12 investigations; original M1.

## T7 / T12: Implement the transport restructuring selected by evidence

Status: Conditional implementation; keep separate PRs for separate mechanisms. Suggested owner: Transport maintainer.

Implement an accept/locking change for T7 or a socket-layout/configuration change for T12 only after M1b selects it. Preserve explicit concurrency bounds when serialization changes. Exercise routing, loss, restart, and honest traffic for any new socket layout.

Prerequisites: M1b decision, T3 patch scope, and the relevant compatibility/qualification fixtures. These are not prerequisites for writing or releasing the minimum Retry feature when its own gates pass.

Completion evidence: The targeted bottleneck improves and all affected M1a/M3/M4 and interoperability cases pass. Record whether host configuration alone is sufficient instead of requiring a repository change. A no-change investigation is not mislabeled as an implemented fix.

Original material: T07/T12; M1a/M1b; T03.
