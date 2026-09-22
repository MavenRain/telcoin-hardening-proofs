# Validator network hardening: proposed modified plan

Date: 2026-09-21. Status: proposed revision for review and assignment.

This packet retains the original single-node validator architecture and W0 through W9 workstreams. It changes delivery boundaries, dependencies, measurement requirements, and the distinction between launch requirements and conditional improvements.

The target is a validator that remains within agreed resource and liveness bounds under the declared external-attacker load, including with its host firewall disabled. Provider protection remains responsible for traffic that saturates the uplink.

## Read in this order

1. [Modified plan](01-MODIFIED-PLAN.md): architecture, policy, workstreams, milestones, and rollout.
2. [W1 delivery backlog](02-W1-DELIVERY-BACKLOG.md): implementation slices, prerequisites, and completion evidence.
3. [Change rationale and original-item crosswalk](03-RATIONALE-AND-CROSSWALK.md): what changes, why, and where every original tracking ID goes.
4. [Decisions and acceptance criteria](04-DECISIONS-AND-ACCEPTANCE.md): outstanding inputs and the tests that determine readiness.
5. [Source manifest](05-SOURCE-MANIFEST.json): source identities and hashes.
6. [Document checks](06-DOCUMENT-CHECKS.md): structural validation and its limits.

## How to use this packet

The modified plan is the proposed target. The backlog defines delivery tasks. The acceptance document defines the evidence required to qualify a release. The original T01 through T12 drafts remain supporting research and disclosure material; their alternative approaches and open questions do not override the proposed requirements here.

Original IDs are retained for traceability. Suffixes such as T4a and T4b distinguish separately deliverable parts of an original issue. M1a/M1b, M3a/M3b, and M4a/M4b separate qualification or baseline work from experiments or regression runs. M6 is a new shared handshake-cost measurement assembled from the existing T09, T10, and T11 measurement requirements.

These slices do not imply one PR each or a smaller total PR count. The intended saving is shared investigation, explicit dependencies, and fewer unrelated changes in each review.

## Status and evidence

The source plan was supplied in the conversation, revised 2026-09-21. Its W1 findings refer to main at 9b2a06b7; most other findings still refer to fa255f2a. The thirteen files in ../w1 were reviewed previously, and their hashes were checked unchanged when this packet was prepared.

This work produced planning documents. It did not implement fixes, run the proposed benchmarks, independently revalidate repository findings, or verify current provider products. At implementation time, confirm the relevant source and dependency versions for each assigned slice. The old benchmark figures are historical evidence, not release thresholds.

Owner roles in this packet are proposed responsibilities. Named people, numeric acceptance thresholds, network characteristics, and the decisions marked unresolved still need to be recorded. Their absence does not prevent reviewing this packet or starting independent fixes; it prevents claiming the affected acceptance gate has passed.

The packet combines material from public issue drafts and private advisory drafts. Use the original disclosure classifications when extracting outward-facing issues. This packet is an internal planning document, not a public issue body.

The original documents have not been replaced. Relative links to ../w1 point to that original collection.
