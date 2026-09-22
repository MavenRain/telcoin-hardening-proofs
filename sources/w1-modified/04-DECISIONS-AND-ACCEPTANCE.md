# Decisions, measurements, and acceptance criteria

This document defines completion evidence for [the modified plan](01-MODIFIED-PLAN.md). Numeric inputs are deliberately unresolved where the source package supplied no valid measurement or maintainer decision. They must be recorded before the affected acceptance result is called a pass.

## 1. Decision register

Owner names are unassigned. The roles below identify who should supply a decision or investigation result; they do not delegate work or authorize deployments.

| ID | Input or decision | Suggested owner | Required before |
|---|---|---|---|
| D01 | Validator link speeds, RTT/loss profiles, effective MTU, host/NIC behavior, and the offered attack range below link saturation. | Operators and measurement owner | Interpreting M1a/M3/M4 as production qualification. |
| D02 | Honest peer population: committee, hubs, bootstrap/trusted peers, all workers, shared addresses, and supported concurrent reconnect/catch-up shapes. | Network maintainer and operators | Selecting rate, pending, and established limits. |
| D03 | Whole-process CPU, RSS, task/queue, and retained-state budgets, with consensus/storage headroom and allocation across swarms. | Network and consensus maintainers | Approving T4/T5/T8 production settings. |
| D04 | Permitted command/timer delay, commit gap or quorum shortfall, reconnect failure/time bounds, vote latency, catch-up regression, and persistence impact. | Consensus and release maintainers | Scoring the candidate configuration, after baseline characterization and before candidate acceptance. |
| D05 | One admission contract: role profiles, committee/trusted/bootstrap union, policy revisions, stale-input detection, minimum launch fallback, recovery/close condition, and treatment of live connections. | Network maintainer | Closed-profile implementation and any identity-dependent exemption or early refusal. |
| D06 | Address/prefix and aggregate budget design: IPv4/IPv6 handling, shared NAT, validation provenance, bounded table eviction, trusted exceptions, and fair opportunity for honest reconnects. | Network maintainer | T4b/T8 acceptance. |
| D07 | Supported release pairs and directionality. The specified 0.13.1/0.14.0 compatibility is required for this rollout; continued mixed-fleet support determines how long the matrix remains required. | Release and CI owners | Retry rollout and subsequent crypto/configuration changes. |
| D08 | Which networking tests run on ordinary CI, in an isolated privileged lane, and on representative real NICs; measured runner capabilities and reproducible setup. | CI and measurement owners | Assigning test cadence and qualifying the deployment. |
| D09 | Patch mirror, exact base/revision, named maintenance and advisory owners, update targets, advisory baseline, and the KeyLogFile production-behavior decision. | Dependency and release owners | Shipping a carried patch and completing N2. |
| D10 | Whether to change accepted cryptographic groups or verification implementation, using current-provider costs, compatibility, and explicit policy consequences. Recommended starting position: retain current policy while investigating. | Network maintainer with cryptographic review | T09/T11 implementation selection; T10 also needs a measured benefit and D05. |
| D11 | Provider choices, address-family choice, source-preserving mitigation, port/ACL capacity, diversity, and operational lead times. Treat the original vendor table as dated research. | Operators | Production placement and P3 completion. |
| D12 | Hub key custody, emergency removal/replacement, trusted/bootstrap configuration distribution, and rollback responsibility before reload exists. | DAO and validator operators | Closed-topology rollout. |

Existing questions about Adiri authorization, governance publication lead time, and proof of possession remain scoped to their actual uses. Select an approved rehearsal environment before running M2. Confirm governance/address timing before Rotation. Confirm proof of possession before S9. These do not hold up unrelated node fixes.

Implementation investigations such as runner privileges and advisory matching belong to the assigned engineering work. They are not fifty-two separate questions for one maintainer to answer before anything starts.

## 2. Release gates

| Gate | What it qualifies | Required evidence |
|---|---|---|
| Gate 1 | Minimum maintained Retry feature | T1a, T2a/T2b, integrated T6 progress checks, O1 observations, T3 source/maintenance receipt, and confirmation of the resolved dependency baseline. |
| Gate 2 | Selected resource and timeout configuration | A1 lifecycle tests, T4a/T4b/T5/T8 as selected, effective timeout tests, bounded bookkeeping, D02-D06, and M3b/M4b regressions. |
| Gate 3 | Validator resilience within the declared load range | M1a on representative hardware and actual node builds, firewall-disabled forged and real-address tests, progress/resource results, and relevant W3/W4 protections. |
| Gate 4 | Launch topology and transaction path | Final M2 scenarios, authoritative W2 behavior, seed/redial/bootstrap and record handling, W3 service isolation, R1-R9 behavior as applicable, and O5 convergence. |
| Gate 5 | Production operational placement and rollout | P1-P4, source-preserving mitigation-on tests, generated-rule tests, D11/D12, private health/metrics, rollback procedure, and the URL migration checkpoint. |
| Gate 6 | Storage behavior under the launch workload | D1 against the agreed persistence criterion, plus D2/D4 changes if the result makes them necessary. |

Passing Gate 1 permits releasing the feature under its stated checks. It is not a claim that Gates 2-6 have passed. Final launch qualification records all applicable gates and the exact build/configuration they cover.

A failed required result creates a remediation task. Optional architecture experiments may identify that remediation, but labeling the experiment optional does not waive the failure. Threshold changes require a recorded reason and a fresh evaluation, rather than adjustment solely to make a candidate pass.

## 3. Core regression matrix

| Scenario | Required property | Primary ownership |
|---|---|---|
| Unvalidated or spoofed-source attempts | Retry policy acts before full handshake acceptance; transient queues and work remain bounded; a claimed trusted address cannot spend that address's privileged quota. | T1a/T2b, T4b/T8 |
| Valid, expired, malformed, replayed, or wrong-binding tokens | Outcomes match the resolved protocol's intended semantics; invalid tokens do not become accepted reachability evidence. Exercise restart/key changes and loss/reordering. | T2b |
| Continuous Retry, Ignore, Refuse, and Accept outcomes | Transport polling returns control or yields appropriately; wakeups are preserved; command, refresh, heartbeat, and stream-sweep progress remain within the selected bounds. | T1a/T2b/T6 |
| Pending admission refused before reservation; failure after reservation; establishment; established-hook refusal; timeout/cancellation | Every owned slot is released once, no unowned slot is refunded, and the count returns to baseline. Counters distinguish rejection stages and failures. | A1/T4a/T4b/O2 |
| Many validated sources and rapidly changing PeerIds | Aggregate work/state limits still hold; accounting tables cannot grow without a bound or reset security state through unsafe eviction. | T4b/T8; A13/A14 where applicable |
| Full committee plus hubs reconnecting | Establishment, command progress, and consensus recovery meet D04; both swarms and all expected workers are exercised. | M4/T2b |
| Shared NAT or multiple honest swarms behind an address | Correct quota scope, no unintended collateral exclusion, and explicit accounting for the supported deployment. | T4b/T8/M5 |
| Catch-up or bulk sync alongside votes and epoch records | Critical-message latency and persistence meet the selected bounds; a bulk class cannot consume all service opportunity. | T5/S3-S6/M3/D1 |
| Empty, stale, contradictory, or changing policy inputs | The documented admission fallback operates; authentication, hard budgets, and class isolation stay active; recovery closes only under D05's valid-input condition. | A5 minimum launch fallback |
| Allowed identity claimed without valid proof; corrupted certificate or transcript signatures | No authenticated or trusted status is granted; selected optimizations preserve every required authentication rejection. | T09/T10/T11 |
| TLS resumption and policy changes | The authoritative admission gate continues to enforce current policy even where TLS callbacks are skipped or session state is reused. | A5/T10 |
| Previous/current release combinations, in both directions | Stock dialers retain the required connectivity and timeout behavior; the intended crypto policy is exercised without relying on a single dependency-unified build as sole evidence. | T2a/T2b/T11 |
| High-volume error paths | Logging, metrics, and diagnostic accounting have bounded work and memory, with useful aggregate outcomes still visible. | O1-O3/T8 |

Detailed token replay expectations must be established against the resolved quinn implementation and protocol behavior. Do not invent a stronger single-use guarantee than the implementation is intended to provide.

## 4. Shared measurement tasks

### M1a. Minimum launch flood qualification

Run actual node builds on representative production-class networking hardware in the controlled qualification environment. Record the link speed, effective MTU, topology, receive-buffer settings, offload settings, CPU allocation, and achieved traffic at the victim. Separate generator limits from victim limits.

Exercise one swarm at a time, then all swarms on a host together, while established committee traffic and fresh honest dials continue. Include well-formed spoofed Initials, relevant small/malformed packet cases, and real-address clients that complete Retry. The real-address case includes source diversity, not only a single address or prefix. Disable host firewall enforcement for the protocol-independence cases.

The sweep stays within the declared below-saturation range. Record actual received traffic and honest offered load. Do not use a historical collapse point beyond the deployment's link capacity as a required rate.

Report process CPU/RSS, relevant occupancy, kernel/socket drops, command and timer progress, established-connection tails, reconnect outcomes, and quorum/commit progress. Internal lock instrumentation is optional here if the node/host evidence is sufficient to score the required result. It must not force an unrelated permanent dependency API just to obtain a metric.

Gate 3 passes only when the recorded D03/D04 bounds hold across the required cases. Remaining uncertainty is recorded as uncertainty, not a pass.

### M1b. Bottleneck and architecture investigation

Reuse M1a's workload and baseline to attribute degradation among receive queues, driver work, endpoint locking, and swarm scheduling. Add targeted instrumentation or isolated variants with their overhead and patches recorded.

Compare receive-buffer tuning, a separate accept task, upstream lock changes, or socket layouts only where attribution justifies the comparison. Measure honest throughput and latency as well as attack tolerance. Removing serialization requires a new explicit concurrency bound. A scheduling change that retains the same contended lock is not assumed to fix contention.

Output: an evidence-backed decision for T07 and T12, including a valid no-change result. If M1a is failing, the selected remediation still has to pass it. Avoid choosing socket parallelism or a dedicated task solely because that name appears in the original tracking row.

### M3a and M3b. Established-resource calibration and regression

M3a measures honest peak connections, concurrent streams, receive/window behavior, service occupancy, RSS, catch-up completion, and vote latency on the baseline build. Include both swarms, trusted traffic, and any limit exemptions. Distinguish advertised credit from resident bytes.

Select T5/S4 settings using D02-D04. M3b repeats the same workload with those settings and hostile attempts to reach the ceilings. Account for the whole host and show that critical message classes retain service. Producing a lower constant without a passing M3b is incomplete.

### M4a and M4b. Retry recovery and pending calibration

M4a characterizes the minimum Retry build before choosing tightened production limits. Include full reconnects, restart, epoch-policy transitions, representative long paths, and the original 10-150 second blackout range where applicable. Measure pending peak, honest failure rate, timeout behavior, and handshake tails under load.

Document the effective inbound and outbound deadlines at every wrapping layer. Use measured behavior to select T1b/T4/T8 settings. M4b repeats the workload with the selected limits, including missing/stale policy inputs and the supported number of workers.

A baseline can use a controlled test configuration before final limits are selected. Its result does not authorize those settings for production. This is an intentional baseline, selection, regression sequence rather than a circular dependency between tests and their chosen constants.

### M2. Staged topology rehearsal

Run individual scenarios as their prerequisites become available. The final rehearsal is the complete set against one candidate release/configuration.

| Scenario group | Prerequisites to exercise it meaningfully |
|---|---|
| Direct connectivity and cold startup, including all hubs down and empty local data | A2-A6, bootstrap behavior A9/A10, launch seeding, primary/all-worker configuration, admission fallback, and progress observations. |
| Public second-ring gossip, sync, records, submit-URL refresh, and hub loss/replacement | A7/A8, appropriate hub configuration, W3/W4 launch protections, A12, and O5; introduce later hub capacity work where the population requires it. |
| Public RPC through submit fronts, including one throttled front | R1-R5, R9, correct proxy/source trust, readiness setup, and the relevant W2 record path. |
| Advertised endpoint migration and final worker-RPC isolation | O5 convergence, R6/R8, a passing submission path, and the operator rollout procedure. |

Check every primary and worker swarm, a fresh observer joining after genesis, blackout recovery, and the distinction between public-tier degradation and consensus health. Do not mark M2 complete based only on its original abbreviated dependency list.

### M5. Hub capacity and shared-source behavior

Retain the larger public-population test, including a hub restart with several hundred observers behind shared NAT, source/prefix accounting, trusted DAO observer slots, real-address handshake load, and serve/gossip budgets. M5 is Hub work; it does not replace M1a's validator real-address case.

### M6. Shared handshake cost profile

Use the resolved provider and dependency versions to profile full and resumed handshakes, work before and after the certificate becomes available, repeated parses/checks, accepted certificate signature schemes, and supported key-exchange groups. Record honest reconnect frequency and refusal frequency so per-handshake savings can be related to actual node load.

Include malicious certificates that claim an admitted identity without valid proof. An early parse is not an authenticated identity. Any candidate optimization must retain certificate, extension, and transcript verification semantics and the authoritative admission check.

Output separate decisions for T09, T10, and T11, pricing implementation and maintenance cost as well as CPU benefit. A current-provider profile does not by itself approve a cryptographic-policy change.

## 5. Evidence record for each run

Record the following in the test artifact, with full logs referenced rather than copied into every issue:

- Exact node revision, lockfile identity, upstream/patch revisions, feature selections, and configuration.
- Topology, roles, worker/swarm count, honest peers and workload, shared addresses, and policy state.
- Host/NIC/network characteristics, firewall condition, offered and achieved traffic, and generator limitations.
- Measurement definitions, sampling/aggregation, trial count, baseline, instrumentation overhead, and result distributions.
- Applicable threshold decisions and their owner/date, pass/fail/unknown outcome, and unresolved limitations.
- Relevant regression IDs, chosen remediation or no-change decision, and the release gate the evidence supports.

Baseline and candidate observations must be comparable. Record conditions that changed rather than treating unlike runs as a speedup or a proof of resilience.

## 6. What closes a task

An investigation closes with the reproducible result, its limits, and a named decision. A configuration task closes with a derivation and a passing regression. A behavior fix closes with the failure reproduced or otherwise concretely characterized and the required behavior demonstrated after the change. A release gate closes only on the complete applicable evidence.

No test in this document was run while writing this packet. Document validation checks structure, cross-references, and source freshness; it does not validate the runtime claims.
