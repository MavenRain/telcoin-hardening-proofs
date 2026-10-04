# Transition-model contracts

The [atomic ledger](../atomic-claims.json) links each obligation below to exact
source ranges, checked theorems, shared assumptions and remaining implementation
work. All counts are unbounded mathematical naturals. All traces are arbitrary
finite lists, not enumerated test cases. Supporting definitions and proofs are
checked together by the pinned mechanism-lang compiler.

## Pending connection ownership

[21-pending-lifecycle.mech](../proofs/21-pending-lifecycle.mech) models a fixed pool
whose cells are free or held at a particular generation. Reservation succeeds
only in a free cell. Completion releases a held cell only when its owned token
matches that cell's generation. Release advances the generation before reuse.

The proofs cover failure, establishment, established-hook refusal, timeout and
cancellation. A callback without ownership cannot refund a slot. Repeating a
terminal callback is idempotent, and an old callback cannot release a slot after
release and reuse, including arbitrarily later generations. Over every finite
reserve/complete trace, occupancy is bounded by the initial pool capacity and
occupied plus available cells equals that capacity.

The implementation obligations include the `ConnectionId` mapping, atomic
reserve/complete operations, callback-token provenance, every real terminal path,
and counter wrap behavior. The model does not permit an attacker to forge an
internal completion token.

## Handshake rate and resource cost

[25-handshake-budget.mech](../proofs/25-handshake-budget.mech) gives both swarms one
shared balance. Every accepted validated handshake consumes a credit. Refill is
clamped to capacity. Identity changes, source eviction and admission-policy
changes do not replenish it; a claimed clock event cannot issue credits.

For arbitrary event traces, accepted starts are at most the initial balance plus
all trusted credits issued. Given an initially bounded balance, it remains
bounded by bucket capacity. [26-discrete-rate-envelope.mech](../proofs/26-discrete-rate-envelope.mech)
adds a fixed number of credits per trusted tick and proves:

```text
accepted handshake starts <= burst + trusted ticks * credits per tick
```

This proof counts traffic from both swarms and every represented identity,
including trusted identities. It has no trust exemption from the shared budget.
An actual per-second envelope requires a bound relating trusted ticks to elapsed
time, including clock jumps, suspend/resume and refill rounding. Restart handling,
composition with module 28's per-source charging/expiry, and honest reconnect
fairness require further models.

[22-weighted-resources.mech](../proofs/22-weighted-resources.mech) composes queue,
pending and established counts using separate cost weights, including both swarm
pools and arbitrary pending traces. The rate model similarly lifts the start
bound to a weighted handshake-cost bound. Actual memory or CPU bounds require
evidence that the selected weights dominate costs and that no resource category
is omitted. A concurrency bound does not by itself establish a rate bound.

## Bounded source-table churn

[27-source-table.mech](../proofs/27-source-table.mech) uses a fixed vector of
vacant or keyed cells. Registration requires validated return reachability,
checks the entire table for an existing key before allocation, and fills only
a vacant cell. A known key leaves the table unchanged. A full table cannot
allocate and refuses registration for an unknown key. Registration permission
is bookkeeping permission, not handshake authorization or committee identity.
`refusedRegistrationIsNoOp` ties that permission to the registration transition,
and `fullTableRefusesUnknownRegistration` states overflow refusal on the
transition itself.

Cells are clear, carry a rate-debt marker, carry a ban, or carry both debt and a
ban. Eviction removes only matching clear entries. Even a zero-valued debt
marker remains protected until a separate trusted expiry transition clears it.
`protectedSources` retains the key, complete restriction payload and position
of every protected entry. `sourceChurnPreservesProtection` proves that this
projection is unchanged over any finite interleaving of registration and
eviction, including simultaneous restrictions. `sourceChurnCardinalityBound`
bounds the final resident count by the initial slot capacity. These statements
hold for arbitrary starting tables, including already protected entries.

Positive theorems also exercise registration into a vacant head slot and
eviction of a matching clear head entry, both directly and through singleton
traces. The no-op behavior for known registrations prevents registering a
second clear copy ahead of a protected entry, even when an earlier slot is
vacant. Runtime refinement must still prove canonical source/prefix
normalization and initial key uniqueness.

This model isolates churn around supplied security state. Module 28 adds
separate charging and expiry transitions over that restriction type, and
module 29 composes them with keyed-table churn. Integration with global
handshake and pending accounting, capacity changes and restart remains open.
A protected full table may refuse
every new source; bounded retention time, honest reconnect fairness, shared-NAT
behavior and real memory cost require additional proofs and qualification
evidence.

### Source quota and independent expiry

[28-source-enforcement.mech](../proofs/28-source-enforcement.mech) counts admitted
operations as debt against a fixed per-source quota. Unbanned restrictions may
charge only below capacity. A permitted charge consumes exactly one unit;
`sourceWithRoomIsCharged` proves this for every debt and every additional amount
of spare capacity. A full quota or either banned state refuses admission.
`chargeSourceCell` additionally guards return reachability and cell presence.
Its refusal theorem connects permission to an unchanged cell, while
`clearSourceCellIsCharged` witnesses the first charge on a validated clear cell.
The cell has already been selected: canonical key lookup and atomic consumption
before performing actual work are implementation obligations.
A validated charge on a tracked cell is the validated charge step of the
restriction trace, so the cell theorems and the trace bound describe one
transition.

Installing a ban preserves debt and blocks charging. Debt and ban expiry are
separate events: trusted debt expiry removes all debt in one event, and trusted
ban expiry removes only the ban. The model has no partial decay and no clock.
`banExpiryPreservesAllDebt` and `debtExpiryPreservesBanStatus`
prevent clearing one restriction from removing the other. The existing
eviction function keeps a cell while either restriction remains, including a
zero-valued debt marker. Expiry of the sole restriction permits a clear state;
untrusted claimed expiry leaves all state unchanged. Trace-level positive
theorems exercise charging, ban installation and both expiry branches, so
dropping an event does not satisfy the proof contract.

`sourceRestrictionTraceBound` quantifies over arbitrary finite interleavings of
validated or unvalidated charges, ban installation and claimed or trusted
expiry. Given an initial debt within a fixed quota, the final debt remains
within that quota. This is a per-source debt invariant. It does not bound
cumulative work across trusted expiries, establish a wall-clock rate, or compose
the restriction trace with global resource traces. Module 29 composes these
restriction events with source-table churn as described below.

Trusted expiry constructors assume an internal decision checked against the
correct canonical source, current restriction generation and deadline. The
model does not itself verify timer provenance, reject stale timers or establish
clock correspondence. Time-based retention, scheduling of expiry, quota changes,
counter overflow, restart persistence and honest-source progress remain open.

### Keyed source-system composition

`29-source-system.mech` uses `lookupSource` and `restrictSource` to select the
first matching canonical key. Both skip vacant and nonmatching cells. Lookup
returns `vacantSource` when no resident matches; updates never allocate, remove
or rekey a resident. A matching update keeps the entire tail unchanged, even if
an initial table contains duplicate keys. Runtime key uniqueness and canonical
source extraction remain refinement obligations.

`sourceTableChargeAllowed` consults the selected cell. The general
`refusedSourceTableChargeIsNoOp` theorem connects this decision to the keyed
charge transition. `unvalidatedSourceTableChargeIsRefused` states that the
table decision refuses unvalidated sources. Missing and unvalidated sources
leave the table unchanged; the selected restriction enforces the existing ban
and quota checks. `sourceTableRefusesAtQuota` shows on a closed table that the
decision refuses a matching resident at its quota.
`sourceTableHeadChargesWithRoom` proves an exact one-unit charge with room and
preserves the tail. `sourceSystemTraceChargesBeyondOtherHead` additionally
exercises a charge behind a nonmatching resident and a vacant cell.

`SourceQuotaBound` supplies a debt bound for every initial resident. Registration,
eviction and keyed restriction updates each preserve that witness, and
`sourceSystemTraceQuotaBound` lifts it over arbitrary finite mixed traces at a
fixed quota. `sourceSystemTraceSelectedQuota` exposes the resulting bound for
any looked-up key. The charge bound still uses the bounded charge operation in
module 28; refusal and exact charging are separate properties. The slot-width
and cardinality theorems need no initial debt witness and bound final resident
count by the original table width. These results do not bound cumulative work
across trusted debt expiries or establish a wall-clock rate.

Concrete mixed traces cover registration followed by charging, refusal of
unvalidated registration, protected debt surviving eviction and replacement
attempts, independent expiry of joint restrictions, and replacement after both
restrictions expire. Claimed expiry is a no-op for every table. Trusted events
still assume the correct source, restriction generation and deadline; the model
does not authenticate timers. Module 37 connects these source transitions to
global credits and pending ownership. Policy integration, quota changes,
restart persistence and honest-source progress remain open.

## Poll continuation and critical service

[15-poll-continuation.mech](../proofs/15-poll-continuation.mech) proves that bounded
poll work plus retained backlog equals the original backlog. Exhausted fuel
retains the rest, and any remaining event requests a wakeup, including Retry-only
backlogs and every transport outcome. The implementation must register and use a
real waker correctly. The model cannot force an executor to schedule it.

[35-critical-service.mech](../proofs/35-critical-service.mech) tracks the number of
critical requests ahead of a target. Each completed service round removes one
predecessor or serves the target. Later arrivals do not increase its rank. If
the trace contains at least `initial rank + 1` completed rounds, the target has
been served. Once served, it stays served.

This is a conditional progress theorem. It requires a queue implementation with
the stated FIFO projection and a scheduler that performs the critical step each
round. It does not prove enough rounds occur before a wall-clock deadline, nor
does it establish consensus liveness under arbitrary network failure.

## Committee recovery

[31-committee-records.mech](../proofs/31-committee-records.mech) represents each
current committee member by one fixed slot. A record can mark its slot only when
it is authenticated and matches the current epoch. Old-epoch and unverified
records leave resolution unchanged. Repeated records are idempotent, preserve
roster size, and cannot advance the closure decision. Resolved members cannot
outnumber the fixed roster.

An epoch reset clears every resolution bit while preserving roster size. With a
positive required threshold, the new epoch cannot close using those cleared
records. These proofs assume authenticated binding of identity and epoch, and a
unique stable slot for each member. Signature verification, timestamp freshness,
membership changes, the committee-minus-f threshold and atomic snapshot ordering
remain implementation or additional modeling obligations.

## Versioned policy publication and receipts

[32-policy-snapshots.mech](../proofs/32-policy-snapshots.mech) puts configuration and
recovery records in one immutable view. An action carries the generation it
observed. Publication compares that generation with the current one, installs a
complete replacement only on a match, and advances the generation. Callbacks from
an older view cannot change the current view. Generation identifies the complete
view, including derived recovery state; an epoch number alone is insufficient.

Missing, stale and contradictory input faults select Grace. The fault
constructors mirror the three fault classes of the plan; the fault theorems are
universal over the class, so no consumer inspects the payload. A positive
recovery threshold prevents an empty resolution set from closing the profile.
The planned update for a replacement or an invalidation starts from cleared
resolution evidence. Clearing evidence on every replacement, including updates
within an epoch, is a conservative model choice. A variant that retains cached
records needs a proof that their authentication, membership and freshness remain
valid for the new view.

Records must be verified, match the current epoch and identify an unresolved
roster slot. An unverified or duplicate record yields a retained update, and a
retained update does not advance the generation.

[33-policy-readers.mech](../proofs/33-policy-readers.mech) gives admission, peer
management and the optional TLS consumer one authenticated query over a captured
view. Their decisions agree for that view. Internal receipts carry the view
generation, epoch, peer identity and decision. Receipt validation checks all
three bindings. A current receipt preserves its decision; changing the view or
using a mismatched identity rejects it. `stalePolicyReceiptDenied` and
`oldEpochPolicyReceiptDenied` state the later-generation and later-epoch cases
of `receiptDecision` directly. A replacement that installs a lower epoch is also
rejected: `installPolicyUpdate` advances the generation on every
`replacePolicyCore`, and `everyPolicyChangeInvalidatesReceipt` rejects the
captured receipt for any replacement core, so the generation binding covers
epoch changes in both directions. Receipt provenance and the binding of the
authentication flag to the actual peer remain implementation obligations.

[34-policy-traces.mech](../proofs/34-policy-traces.mech) proves that generations
never decrease and grow by at most the number of policy events in an arbitrary
finite trace. Given a limit above that event-count bound, the final generation
stays within the limit. A real fixed-width counter still needs such a bound or a
safe exhaustion protocol. Local generations do not establish the freshness or
ordering of external governance proposals.

The same module proves the committed recovery properties. A committed policy
replacement or invalidation clears resolution evidence, and a replacement uses
the new roster's size. Committed callbacks with unverified, epoch-mismatched or
duplicate records do not publish a new view, and a duplicate callback cannot
advance the generation. The proofs also show an enabled update for any verified
unresolved member at the current epoch, so recovery does not satisfy its safety
properties by rejecting every record. Delivery, contention retries and eventual
recovery still need progress proofs.

The Rust implementation must publish views atomically and linearize receipt
validation through authorization, or retain equivalent protection through use.
Checking a generation and then using the result without protection permits a
race with a later publication. The model's serialized transitions exclude that
race, so an implementation refinement must justify this boundary explicitly.

## Policy and resource interleavings

[36-governed-resources.mech](../proofs/36-governed-resources.mech) combines a policy
view, shared handshake balance and pending pool. A finite trace may interleave
policy replacement, invalidation and recovery with arbitrary rate and pending
events. Projection proofs show that each resulting component agrees exactly
with its earlier individual transition model.

Policy changes preserve credits and pending ownership. Across the mixed trace,
handshake starts stay within initial credit plus trusted issuance, bounded
credits remain within capacity, and pending occupancy and conservation retain
their initial pool bound. The shared rate events include both swarms.

Bucket and pool capacities are fixed within this model. Runtime cap changes,
restart persistence, per-source security-state eviction and the allocation or
processing cost of policy data require additional models. Real callback
interleavings, all resource allocations and clock-derived issuance still need
implementation and environmental evidence.

## Source admission with shared resources

`37-source-admission.mech` combines the keyed source table, one shared handshake
credit balance and a fixed pending lease pool. `planSourceStart` requires a
validated resident with no ban and source quota room, a nonzero global balance,
and a free selected slot. `sourceAdmissionStep` uses that plan to charge the
source once, spend one credit and reserve the slot in one atomic transition.
Both swarms use the same state. Unknown sources require a separate successful
validated registration before attempting admission.

Refusal preserves the entire state. General theorems cover unvalidated sources,
source refusal, exhausted global credit and unavailable selected leases. The
enabled head-slot theorem requires source permission and proves the exact
charge, credit decrement and reservation together. Concrete witnesses check
missing sources, bans, exhausted source quota, missing or held pending slots,
and successful non-head source and slot selection. Source debt counts admitted
starts since trusted debt expiry, not simultaneous pending connections.

`admissionAttemptReceipt` reads the same pre-state as the atomic transition and
returns the selected slot index and generation on success. These internal
receipts are distinct from policy authorization receipts. Completion takes
the receipt as input and applies the existing generation check at its slot.
The model does not make a receipt single-use; the generation check is the only
replay guard. For every terminal reason, a matching head receipt releases its lease; an arbitrarily old
head receipt preserves a newer owner. A concrete non-head completion checks
index locality, and a mixed trace covers admission, completion, expiry, refill,
reuse by the other swarm and replay of the old callback. Completion leaves both
source restrictions and global credits unchanged; an unowned callback is a
no-op. Receipt provenance, atomic emission and the runtime slot mapping remain
assumptions, not cryptographic or implementation proofs.

Source maintenance permits registration, eviction, bans and expiry. It neither
issues handshake credit nor changes pending ownership, and has no independent
source-charge constructor. Only trusted clock events refill global credit,
clamped to fixed capacity. Mixed witnesses exercise registration then admission,
protected churn, independent expiry and refusal after completion without debt
expiry. Claimed expiry leaves the source table unchanged for every key and
state, and debt expiry cannot refill the global balance or release a pending
lease.

Over arbitrary finite traces, source-table width and pending capacity retain
their initial values. Resident count and pending occupancy stay within those
initial capacities. Credits remain bounded given an initial credit bound;
selected debt remains bounded given `SourceQuotaBound` for all initial
residents. The inherited clamp proves the debt bound; admission refusal and
exact charging are separately checked. These are state bounds; the cumulative
count and discrete rate envelope are established by the next module. Module 41
adds policy receipt validation to the same admission step. Per-source live
pending attribution and established resource accounting remain open.

Eligibility, commit and receipt emission must linearize against one pre-state;
the raw plan and commit helpers are not separate runtime entry points. Canonical
unique keys, internal receipt provenance, stable slot identities, nonwrapping
generations, fixed capacities and quotas, and trusted issuance/expiry require
refinement. The model does not validate timer generations or deadlines, establish
restart persistence, or prove honest admission and reconnect fairness.

## Coupled source-admission rate envelope

`38-source-admission-rate.mech` counts accepted starts from the indexed receipts
emitted by `admissionAttemptReceipt`. Every step observes the same pre-state as
`sourceAdmissionStep`, and the recursive count continues with that step's full
updated state. A successful receipt contributes one; refusal, maintenance, clock
issuance and completion contribute zero. The count therefore follows source
restrictions and pending ownership as well as shared credit. It never counts a
completion receipt as a new start.

`sourceAdmissionCreditConservation` proves, for arbitrary finite mixed traces,
that starts are at most initial shared credit plus total trusted issuance.
It requires no initial credit, source-debt or pending-occupancy bound. The
continuation proof covers both swarms, arbitrary keys and pending indices, and
every completion reason. `sourceAdmissionNoRefillBound` specializes this to
initial credit alone when total issuance is zero. Source churn, expiry and
completion cannot replenish the allowance. The receipt/commit correspondence
still relies on the atomic admission contract from module 37.

The closed `TimedSourceAdmissionTrace` language retains attempts, maintenance
and completion, maps each trusted tick to exactly `rate` issued credits, and
discards claimed ticks. It has no arbitrary-credit constructor. Only trusted
ticks contribute to `sourceAdmissionTrustedTicks`; `sourceAdmissionUniformIssuance`
equates total issued credit with `ticks * rate`. Issuance is counted before the
bucket clamps credit; discarded credit cannot increase accepted starts.

For any bucket capacity, given initial credit at most `burst`,
`sourceAdmissionBurstRateEnvelope` bounds
the actual composed admission count by `burst + ticks * rate`. The parameters
include zero burst and zero rate. `sourceAdmissionCostEnvelope` multiplies this
bound by a supplied per-start cost. That weight must dominate real accepted-start
work; prevalidation, refused attempts, retained resources and other work require
separate accounting. No numeric production budget is selected here.

Module 38 proves enabled counting for an eligible head slot. Closed witnesses
also check a non-head source and slot, two accepted starts across both swarms,
completion and reuse, replay preserving a newer owner, zero-rate refusal, bans,
occupied slots, quota retention, expiry without credit, and clamped refill.
These witnesses prevent the upper-bound proof from hiding an undercount or a
disabled admission path. Module 39 extends enabled admission, counting and
completion guarantees to arbitrary pending indices, as described below.

Real monotonic time, tick provenance and replay prevention, one runtime balance,
checked arithmetic and atomic receipt emission require refinement. The theorem
is a discrete rate envelope, not a wall-clock, honest-admission or fairness
guarantee. Module 41 composes current policy receipts with this rate envelope.
Runtime policy authority, live per-source pending attribution, established
resources, changing configuration and restart persistence remain open.

## Source admission at arbitrary pending indices

`39-indexed-source-admission.mech` represents a selected slot by an arbitrary
finite prefix, that slot, and an arbitrary suffix. The selected index is the
prefix length. Neither surrounding pool is restricted to free slots or fixed
generations. `availableLeaseTokenAfterPrefix` and `updateLeaseAfterPrefix`
relate lookup and update at any suffix offset to the existing pool operations.
The prefix equations preserve each preceding lease and identify an empty
suffix with the original finite pool.

`indexedSourceAdmissionChargesAndReserves` proves enabled admission for every
such selected free slot, in either swarm, given source permission and a positive
shared credit balance. It gives the exact charged source state, one spent credit
and one reserved lease while retaining the entire prefix and suffix.
`indexedSourceAdmissionOwnsReceipt` proves both fields of the emitted receipt,
and `indexedAdmissionCountsOne` connects that receipt to the existing accepted
start count. These extend the head-slot results without changing the transition.

`indexedSourceCompletionActsOnSelectedLease` gives the exact effect of any
completion on the selected lease while preserving all other leases, source
state and shared credits. Matching completion releases and advances the
generation for every terminal reason. Any mismatched generation preserves the
held owner, including arbitrarily old receipts after reuse. A free slot ignores
every receipt generation; duplicate matching completions with any two terminal
reasons release once and advance once.

Held-slot selection and every index at or beyond the finite pool length refuse
without changing state or emitting a receipt. These results quantify over all
sources, keys, credit balances and both swarms. They do not promise an eligible
source, a free slot, honest admission, scheduling fairness or live per-source
pending attribution. Atomic transitions, internal receipt provenance, stable
runtime slot identities and nonwrapping machine generations still require
implementation refinement. Module 41 preserves these indexed admission results
under a policy receipt gate. Established resources, restarts and configuration
changes remain separate obligations.

## Policy receipts coupled to source admission

`41-policy-source-admission.mech` pairs one `VersionedPolicy` with the complete
`SourceAdmission` state. Its closed event language permits receipt-bearing
attempts, generation-guarded policy publication, source maintenance, indexed
completion, trusted ticks and untrusted time claims. Policy receipt validation
and source admission use the same serialized pre-state. An attempt carries the
actual peer identity separately from its canonical source key and pending index.

The receipt gate checks the current policy generation, epoch, identity and
captured decision through `policyReceiptAllowed`. A denied receipt leaves the
entire state unchanged and emits no pending receipt. Separate proofs reduce
unauthenticated query results, mismatched identities or epochs, and receipts
from any earlier generation, after one or more successful policy installations,
to the no-op resource event (`changedPolicySourceReceiptEvent`,
`stalePolicySourceEvent`).
`freshAllowedPolicySourceAttempt` connects an allowed query of the current view
to the original source transition. This does not give policy permission an
exemption from source quota, shared credit or pending capacity.

For an allowed receipt and validated source permission, the three indexed
theorems prove the exact source charge, single credit consumption, selected
reservation, index/generation receipt and count of one accepted start for every
finite pending prefix and suffix. The inherited transition still refuses a
missing, exhausted or banned source, zero credit, or a held or missing slot.
Completion delegates to the original indexed receipt lifecycle regardless of
later policy changes, preserving cleanup for work admitted under an older view.
Publication applies `commitPolicyAction` and preserves the entire resource
state, including debt, bans, credits and lease generations.

`erasePolicySources` follows the evolving policy and resource state and produces
a `SourceAdmissionTrace`. `policySourceErasureState` equates the resource result
with the composed execution; `policySourceErasureStarts` equates the erased
receipt count with the independently recursive composed count. These bridge
proofs carry the credit, resident-quota, pending-occupancy and source-table bounds
to arbitrary finite mixed traces under the original initial-bound premises.
`policySourceUniformIssuance` proves that only trusted ticks issue credit and
that each issues exactly `rate` before clamping. For any bucket capacity and
initial credit at most `burst`, `policySourceBurstRateEnvelope` bounds accepted
starts by `burst + trustedTicks * rate`; `policySourceCostEnvelope` multiplies
that bound by a supplied per-start cost. `policySourceTickUsesClock` proves
that a trusted tick keeps the policy view and applies only the source clock.
Claimed ticks produce neither state changes nor time credit.

This is model composition. `PolicyReceipt` values must come from authenticated
internal policy queries; `AdmissionReceipt` values must come from successful
internal reservations. Raw constructors do not establish either provenance.
Runtime receipt validation and resource enforcement must linearize together
with policy publication, with correct peer/source/slot binding and protection
through use. Authoritative input validation, external governance ordering,
canonical source extraction, fixed pool identity, nonwrapping counters, trusted
clock and expiry correspondence still require refinement. Live per-source
pending attribution, established resources, resource-cap changes and restarts
are not added here. The cost envelope excludes rejected attempts, policy
processing and maintenance; honest admission and scheduling fairness remain open.

## Bounded policy-processing work

`42-policy-work.mech` adds one independent policy-work balance to the complete
policy/source state. Its fixed configuration contains the source quota,
handshake capacity and rate, and policy-work capacity and rate. Both swarms,
all identities, all source-validation states and all policy views share the
same work balance. A processed attempt or publication spends one work credit
before delegating to the existing policy/source transition, including denied
attempts and stale publications. Work credit does not imply admission.

An exhausted attempt or publication preserves the complete state, and an
exhausted attempt emits no admission receipt. With credit available, the
original event is retained, including its receipt, identity, source, key and
slot. Maintenance and completion
remain enabled at zero work credit and preserve that balance. Trusted ticks
refill the two balances at their independently configured rates; claimed time
is a complete no-op. A single serialized pre-state governs the work check,
charge, policy check and source admission. This is a model transition, not a
proof that the Rust paths have that ordering.

`PolicyWorkReceipt` records whether a policy operation was processed. It is
separate from the indexed admission receipt and grants no authority. The
receipt-counted work trace agrees with a projection into the existing credit
system. Its synthetic validated rate attempt denotes one unit of policy work,
even for an unvalidated network source; it does not upgrade network validation.
The source-trace erasure preserves the entire underlying state, the accepted
start count and exactly the original trusted ticks. Arbitrary finite mixed
traces preserve both credit capacities, resident debt bounds and initial pending
and source-table occupancy limits, with the corresponding initial witnesses.

For initial balances within their capacities, let `P` be processed policy work,
`H` receipt-counted accepted starts and `T` trusted ticks. The model proves:

```text
P <= policy_capacity + T * policy_rate
H <= handshake_capacity + T * handshake_rate
P * policy_cost + H * handshake_cost
  <= (policy_capacity + T * policy_rate) * policy_cost
     + (handshake_capacity + T * handshake_rate) * handshake_cost
```

The cost weights are supplied upper bounds in a common unit. Runtime evidence
must cover every processed operation, including failed policy checks and
publications, and bound input and roster sizes sufficiently to justify those
weights. This model receives already constructed policy receipts. Receipt
creation and authentication, work before the budget check, exhausted-budget
guards, maintenance, completion and established resources require separate
accounting. Trusted clock correspondence, nonreplayed ticks, checked arithmetic,
fixed configuration and atomic integration remain implementation obligations.
The budget can delay policy recovery; no fairness, successful admission or
wall-clock availability result follows from these upper bounds.

## Budgeted internal policy queries

`43-policy-ingress.mech` moves policy query and receipt production into the
positive-work-credit branch. An ingress attempt carries an authentication flag,
identity, validated-source classification, swarm, canonical key and pending
index. It has no caller-supplied policy receipt. `budgetedPolicyQuery` returns
`noPolicyQuery` at zero credit; otherwise it calls `readPolicy admissionConsumer`
with the current immutable policy view and that same identity.

`creditedPolicyQueryPreservesDecision` and
`policyIngressUsesCurrentDecision` connect the generated receipt to the existing
authenticated policy query and source-admission gate over arbitrary inputs.
`everyPolicyIngressQuerySpendsWork` deducts one credit even when authorization,
authentication or resource eligibility denies the attempt. An exhausted attempt
preserves the complete state and emits no admission receipt. An unauthenticated
attempt with credit preserves the policy and resource state, emits no admission
receipt, and still spends its work credit.

Mixed traces contain queries, observed-generation publications, source
maintenance, completion, trusted ticks and claimed ticks. `erasePolicyIngress`
compiles each event using the evolving pre-state, including all preceding
publications. The independent runner and compiled trace have equal final states.
Compilation also preserves trusted tick counts. Completion and maintenance
delegate to the existing cleanup transitions at every work balance; claimed
ticks do not change state. Final pending occupancy retains its initial capacity
bound.

`policyIngressProcessed` and `policyIngressStarts` count the existing work and
admission receipts on that compiled trace. With both initial balances within
their capacities, the work, handshake and combined cost envelopes above hold
over `policyIngressTrustedTicks`. The policy-operation weight must now include
internal query and receipt construction as well as the delegated processed
operation. This is a symbolic cost assumption that requires bounded inputs,
bounded rosters and runtime evidence.

The event type closes caller-supplied policy receipts for this model entry point.
It does not authenticate the input flag or identity, prohibit runtime callers
from bypassing this entry point, or prove atomic execution. Pre-guard
authentication, exhausted guards, dispatch, maintenance, completion, established
resources and live per-source pending attribution remain outside the cost
envelope. The result establishes neither scheduling fairness nor wall-clock
availability.


## Fueled policy-ingress polls

`44-policy-ingress-poll.mech` wraps the ingress transition in an explicit finite
poll loop. Each dispatched queue element consumes one unit of poll fuel,
independently of policy work credit. This includes denied or exhausted-credit
attempts, stale publications, maintenance, completion, trusted ticks and
untrusted claimed ticks.
The loop stops at zero fuel or an empty queue. Zero fuel leaves the state and
queue unchanged and selects no prefix.

`policyIngressPollWorkBound` bounds dispatched events by fuel.
`policyIngressPrefixCountsWork` connects that count to the selected prefix.
`policyIngressPollReassemblesQueue` preserves the exact event sequence, not only
its length; `policyIngressPollBacklogConservation` also accounts for every event.
The wake flag describes the remaining queue. Backlog requests another turn,
and a drained queue does not request a backlog wake.
`policyIngressShortPollRequestsWake` and `policyIngressFullPollStopsWake` prove
this for every queue, not only the one-unit examples.

The runner applies each event to the current state before proceeding.
`policyIngressPollProjectsPrefix` proves equality with the existing ingress
runner on the selected prefix. `policyIngressPollResumePreservesExecution`
proves that running the remainder from the poll result equals uninterrupted
execution of the original queue. Thus saving a continuation cannot justify
dropping, reordering or replaying an event.
`policyIngressPollPendingBound` transports the existing pending-capacity bound
to the actual poll result. Completion and maintenance execute at zero policy
work credit when poll fuel is available. These equations do not establish
cleanup priority or bounded waiting time.

For initially bounded policy and handshake balances,
`policyIngressPollCombinedCostEnvelope` proves:

```
dispatches * eventCost + processed * policyCost + starts * handshakeCost
  <= fuel * eventCost
     + (policyCapacity + ticks * policyRate) * policyCost
     + (handshakeCapacity + ticks * handshakeRate) * handshakeCost
```

Here `processed`, `starts` and trusted `ticks` refer to the selected prefix.
The added `eventCost` must dominate all per-dispatched-event work outside the
other two weights, including dispatch, exhausted guards, maintenance, completion
and clock handling. `policyIngressPollExhaustedGuardCost` proves that a single
exhausted-credit attempt still incurs this weight; zero fuel incurs zero modeled
event cost. Input, queue and table size bounds must justify the supplied weights.
This is a conditional per-poll bound, not measured CPU use or a wall-clock rate.

Atoms C37-C40 record these obligations. Runtime queue materialization, memory
bounds, producer interleavings, authentication before dispatch, empty-poll
entry/exit costs, actual waker registration and executor overhead remain open.
Progress additionally requires positive fuel and eventual scheduling. Module 45
adds conditional FIFO service under continued arrivals; runtime cleanup latency
and queue growth remain open. Established resources, live
per-source pending attribution, concrete query/dispatch costs, restart and
configuration changes remain outside this slice.

Eighteen poll mutations drop or change selected events, lose or replay the
remainder, undercount or overcount work, charge fuel on an empty queue, exempt
attempts or cleanup from fuel, run at zero fuel, skip or replay a transition,
suppress or misdirect wakeups, drop the wake for a deep backlog, spin on
drained queues, omit dispatch cost or charge unprocessed backlog.
All must fail with semantic mismatches, alongside the existing negative checks.


## Persistent FIFO ingress service

`45-policy-ingress-queue.mech` stores an ordered ingress queue together with its
current policy-work/resource state. Enqueue appends a finite arrival batch behind
retained events without changing that state. Wake flags cover both retained
backlog and arrivals into an empty queue; an empty queue has no backlog wake.
An arbitrary-fuel queue poll preserves the exact continuation and the existing
execution semantics. Zero fuel preserves the entire queued state.

For repeated service, each modeled round appends its arrival batch and polls
with exactly one unit of fuel. The arrivals function supplies arbitrary finite
batches at successive round indices. `policyIngressQueueRoundsExecuteTrace`
relates the carried resource state to the actual ordered dispatched trace,
including events that arrived after the initial queue was created.
`policyIngressQueueDispatchBound` bounds its length by delivered rounds, and
`policyIngressQueueRoundsPendingBound` preserves initial pending-slot capacity.
The model does not reset resource balances between turns.

`policyIngressQueueServesPrefix` proves the following exact equation for any
original prefix, suffix and arrival schedule, with `n = length(prefix)`:

```
service(n, arrivals, queue(prefix ++ suffix, current))
  = queue(suffix ++ arrivalsThrough(n), run(prefix, current))
```

Thus an original prefix is serviced in its own length of delivered rounds even
when every round adds more work. The original suffix and all intervening arrival
batches remain queued in order. `policyIngressQueueEventTurnCount` and
`policyIngressQueueEventProgress` reach a target after its preceding prefix
length plus one, measured in delivered rounds. The target can be any ingress event, including
completion or maintenance. Those events retain their existing work-credit
bypass semantics; a stale completion can still correctly preserve a newer owner.

`policyIngressQueueCombinedCostEnvelope` assumes initially bounded policy and
handshake balances and proves:

```
dispatches * eventCost + processed * policyCost + starts * handshakeCost
  <= rounds * eventCost
     + (policyCapacity + ticks * policyRate) * policyCost
     + (handshakeCapacity + ticks * handshakeRate) * handshakeCost
```

All counters and trusted ticks come from the actual dispatched trace, evaluated
from the initial resource state. Each initial burst appears once across the
whole sequence of rounds. `policyIngressQueueExhaustedGuardCost` also charges
dispatch cost for an exhausted-credit attempt that arrives into an empty queue.
The weights have the same conditional dominance requirements as module 44.

Atoms C41-C44 record these obligations. Runtime queue retention, producer
serialization, exactly-once enqueue, real wakeups and delivery of the required
service turns need refinement. The progress theorem concerns this explicit
one-event scheduler. Module 46 generalizes finite service to varying fuel;
a wall-clock bound remains open. Finite batches may arrive on every turn, but total queue growth,
overload loss, cancellation, allocation and enqueue cost are not bounded here.
Arrival construction, empty turns, pre-dispatch work and executor overhead lie
outside the dispatched-event cost envelope. Established resources, per-source
pending attribution, restart and resource-cap changes remain open.

Twenty queue mutations lose, reorder or replay backlog or arrivals, change
resource state on enqueue, reuse a stale state, execute an extra event, suppress
or invent a wake, remove service fuel, skip arrivals, reuse an arrival batch,
fail to advance its index, alter arrival history, drop a dispatched trace event,
omit its cost or drop the dispatch allowance from its limit. All must be rejected with semantic mismatches.


## Varying-fuel ingress schedules

`46-policy-ingress-schedule.mech` generalizes persistent FIFO service to any
finite list of delivered turns. Each turn has an independent natural-number
fuel and finite arrival batch, which is appended before polling. Zero fuel
retains the new arrivals and current state. Fuel left unused by an empty queue
does not carry into later turns. `policyIngressUnitScheduleAgrees` connects the
unit-fuel specialization to module 45, and `policyIngressScheduleMixedTurns`
checks a 0/2/0-fuel sequence over arbitrary events and arrival batches.

`policyIngressScheduleExecutesTrace` equates the carried resource state with
execution of the actual dispatched trace. `policyIngressScheduleReassembles`
proves exact ordered conservation across all turns:

```
dispatched(schedule, initialQueue) ++ finalQueue
  = initialQueue ++ arrivals(schedule)
```

The prefix relation contains an explicit suffix and an equality of whole event
sequences. `policyIngressScheduleServiceEquation` constructs that witness from
delivered fuel, rather than assuming successful service. For any original
prefix, original suffix and natural-number slack, it proves:

```
totalFuel(schedule) = length(prefix) + slack
  implies dispatched(schedule, prefix ++ suffix)
            = prefix ++ serviceSuffix
```

`policyIngressSchedulePrefixExecution` then equates the final resource state
with execution of the prefix followed by `serviceSuffix`. Surplus fuel may
dispatch further work, so the final state need not equal the state immediately
after the target prefix. A target event can be placed at the end of that prefix,
including completion or maintenance. Later arrivals cannot overtake it. Zero
turns are allowed, but the theorem requires enough cumulative delivered fuel.
It does not establish delivery of that fuel, eventual service on an infinite
schedule, or a wall-clock deadline. A stale completion still need not release
the current slot owner.

The dispatch count is at most total delivered fuel, and final pending occupancy
stays within initial slot capacity. With initially bounded work and handshake
balances, the combined cost envelope is:

```
dispatches * eventCost + processed * policyCost + starts * handshakeCost
  <= totalFuel * eventCost
     + (policyCapacity + ticks * policyRate) * policyCost
     + (handshakeCapacity + ticks * handshakeRate) * handshakeCost
```

Counters and trusted ticks come from the actual dispatched trace. Each initial
burst appears once across the entire schedule. An exhausted-credit attempt
still costs one dispatch. A lower bound shows that the cost includes the
processed policy work and accepted starts. Supplied weights must dominate
concrete operation costs; enqueue, queue storage, pre-dispatch work, empty
turns and executor costs remain outside this envelope.

Atoms C45-C48 record these obligations. Runtime fuel delivery, FIFO retention,
concurrent producers, real wakeups, overload and cancellation require
refinement. Module 47 below bounds queue entries under explicit overflow
rejection. Runtime queue storage, established resources, per-source pending
attribution, restart, resource-cap changes and wall-clock cleanup latency
remain open.
Twenty-five schedule mutations alter fuel accounting, arrival order, the
enqueue-before-poll order, queue or state retention, dispatched work, the
service suffix, unit-schedule fuel or indexing, or cost terms. They must be
rejected by semantic type mismatches.

## Bounded ingress admission under overload

`47-policy-ingress-overload.mech` filters each finite arrival batch before the
turn's poll. The queue-entry limit is fixed. Existing backlog has priority;
only the earliest arrivals that fit its remaining capacity are admitted.
`rejectedPolicyIngress` reports the remaining suffix as an abstract trace.
For every backlog and arrival batch:

```
room = max(limit - length(backlog), 0)
admitted = take(room, arrivals)
rejected = drop(room, arrivals)
admitted ++ rejected = arrivals
ready = backlog ++ admitted
```

`boundedPolicyIngressUsesFreeSlots` and `boundedPolicyIngressReportsOverflow`
give the exact split when `limit = length(backlog) + room`.
`boundedPolicyIngressFullRetainsQueue` proves a full queue keeps exactly its
backlog. A zero limit rejects all arrivals. Admission precedes dispatch, so a
slot freed during the current turn becomes available to later turns.
`boundedPolicyIngressReusesFreedSlot` checks this with limit one: two one-fuel
turns with one arrival each dispatch both events.

Given `length(initialQueue) <= limit`, `boundedPolicyIngressReadyBound`,
`boundedPolicyIngressTurnBound` and `boundedPolicyIngressQueueBound` bound
occupancy before dispatch, after a turn and after any finite schedule.
An initially overfull queue is retained, so the occupancy theorem requires
the initial bound. There is no eviction or capacity-shrink transition.

`boundedPolicyIngressSchedule` retains each delivered fuel value and replaces
each arrival batch with its admitted prefix. Later admission uses the queue
remaining after the current poll. `runBoundedPolicyIngress` runs that filtered
schedule through module 46. General equalities cover zero-fuel turns and taking
the current head before any newly admitted work. The lifted results prove:

```
dispatched ++ finalQueue = initialQueue ++ admittedArrivals
finalWorkState = run(actualDispatchedTrace, initialWorkState)
totalFuel = length(originalPrefix) + slack
  implies originalPrefix is a prefix of actualDispatchedTrace
```

Thus overflow cannot evict an already queued prefix or consume its service
fuel. Dispatch count is bounded by the original schedule's total fuel, pending
occupancy stays within initial pending capacity, and the combined cost envelope
from module 46 holds over the filtered dispatched trace. Each initial burst is
counted once; rejected ticks do not refill budgets. A lower bound checks that
the cost includes processed policy work and accepted handshake starts.

Atoms C49-C52 describe this abstract extension. The cap bounds queued event
entries only. Payload bytes, offered batches, admission and rejection work,
overflow reporting, retained allocations, empty turns and executor costs need
separate bounds. The rejected suffix is not a proved runtime notification or
retry mechanism. Uniform overload handling may reject newly offered completion,
maintenance, trusted-tick or policy-publication events. A runtime refinement
must protect their delivery or justify loss and retries before claiming cleanup
or control-plane progress. Rejected arrivals have no service guarantee. Fuel
delivery, wall-clock latency, infinite-arrival fairness, cancellation, restart
and cap changes remain open.

Twenty-one overload mutations bypass free-space accounting, select the wrong
arrival segment, lose or reorder backlog, alter delivered fuel, forget the
post-poll queue, bypass the filtered runner, trace or cost schedule, or remove
cost components.
All must fail with semantic type mismatches; no parser failure counts.


## Payload-aware ingress admission

`48-policy-ingress-payload.mech` adds a second fixed budget to module 47.
`policyIngressPayload weight queue` sums an immutable natural-valued charge
for every queued event. Charges may differ between events and may be zero.
The entry cap remains independent, so zero-charge entries still consume slots.

`reservePolicyPayload` computes either a strict-overflow witness or an exact
remaining-capacity witness. `selectPayloadIngress` uses those witnesses to
construct a certificate containing a FIFO prefix, its rejected suffix and a
checked payload bound. It accepts a fitting head and continues with the
remaining payload capacity, stopping at the first oversized head. The general
`payloadIngressSelectsFittingHead` theorem holds for arbitrary charge functions,
heads, tails and remaining capacity. Zero-charge selection is proved for every
finite offered trace, so the bound does not rely on rejecting all arrivals.

Admission first selects against the payload space left by existing backlog,
then applies module 47's free-entry limit to that candidate prefix:

```
payload(queue) = sum(weight(event) for event in queue)
payloadRoom = max(payloadLimit - payload(backlog), 0)
candidates ++ payloadExcess = arrivals
admitted ++ slotExcess = candidates
rejected = slotExcess ++ payloadExcess
admitted ++ rejected = arrivals
ready = backlog ++ admitted
```

`payloadIngressPartitionsArrivals` proves the complete ordered split, and
`payloadIngressBacklogEquation` retains the original backlog first. Separate
theorems prove `length(ready) <= slots` and `payload(ready) <= payloadLimit`
under the respective initial bound. Polling cannot increase retained payload.
`payloadIngressQueueEntryBound` and `payloadIngressQueuePayloadBound` lift both
invariants to arbitrary finite varying-fuel schedules. Overfull initial queues
are retained; the corresponding bound requires an initially fitting queue.
There is no capacity-shrink or mutable-charge transition.

Filtering uses the post-poll queue for the next turn.
`payloadIngressReusesFreedPayload` is a closed witness (charge 1, two slots,
payload limit 1, a one-fuel turn then a zero-fuel turn, quantified only over
the two events): dispatching the held event frees its payload for the later
arrival. No general space-after-poll law is proved. Zero-fuel turns admit and
retain events without executing
them. The filtered schedule preserves total delivered fuel, exact FIFO
conservation and dispatched-state semantics. `payloadIngressServiceEquation`
proves that an original queued prefix is dispatched when total delivered fuel
equals its length plus natural slack. Pending capacity and the combined
dispatch/policy/handshake cost envelope also survive the additional filter.
Payload charges and execution weights are distinct quantities.

Atoms C53-C56 cover these results. The retained charged sum is not a proved
total-memory bound. A runtime refinement must establish that immutable charges
conservatively cover retained payloads, cannot be understated by peers, and
account correctly for ownership and sharing. Entry and allocator overhead need
their own dominance bounds. Offered batches, rejected suffixes, temporary
candidates and proof certificates are logical values outside the retained-queue
budget. Selection may inspect an entire finite offered batch even when few
entries can be admitted. Charge computation, admission, rejection reporting,
deallocation and other work outside dispatch need separate bounds.

Both limits may reject newly offered completion, maintenance, trusted-tick or
publication events. Safe delivery, notification and retry remain runtime
obligations. Rejected arrivals have no service guarantee. Actual fuel delivery,
wall-clock latency, infinite-arrival fairness, concurrent producers, cancellation,
restart and cap changes remain open.

Twenty payload mutations erase or duplicate charges, create extra room, ignore
backlog, deny all arrivals, lose or reorder the split, bypass entry filtering,
retain the wrong post-poll queue, change delivered fuel or bypass execution and
trace filtering. They must produce type mismatches, including failures of the
selection certificates and laws over variables; parser failures do not count.


## Bounded admission scanning

`49-policy-ingress-scan.mech` adds an admission allowance independent of the
queue entry cap, payload budget, service fuel and policy/handshake balances.
`scannedPolicyIngress scanFuel arrivals` selects at most `scanFuel` offered
events. `unscannedPolicyIngress` is the exact remaining suffix. Payload and
entry filtering sees only the selected prefix:

```
examined ++ unexamined = arrivals
accepted ++ rejected = examined
(accepted ++ rejected) ++ unexamined = arrivals
ready = backlog ++ accepted
length(examined) <= scanFuel
```

`scannedPayloadIngressPartitionsArrivals` proves this ordered three-way split
for arbitrary batches, weights, caps and fuel. The scan allowance is consumed
by event count independently of payload charges or admission success. The
one-event laws accept a zero-charge head when an entry is free, reject an
oversized head, and leave the original tail unexamined. These are laws over
arbitrary head events and tails with fixed small limits. Zero scan allowance
leaves every offered event unexamined.

Unexamined arrivals remain outside the retained queue. The schedule transform
selects a bounded prefix from each independently supplied batch; it does not
automatically carry the unexamined suffix into a later turn. The caller must
define ownership, release or resubmission and must avoid duplicate submissions.
The model supplies no bound on external suffix storage and no eventual-admission
or arrival-fairness theorem.

`scannedPolicyIngressSchedule` preserves every service-fuel allowance.
`scannedPayloadIngressRunsTurn` equates one scheduled turn with polling the
bounded ready queue and retaining its exact remainder. Across finite schedules,
the final work state executes the actual dispatched trace. Independent entry
and payload invariants hold whenever the corresponding initial queue fits its
fixed cap. `scannedPayloadIngressServiceEquation` exposes the dispatched trace
as an initially queued prefix followed by a suffix whenever delivered service
fuel equals that prefix's length plus natural slack. The admission allowance
may be zero without invalidating this conditional backlog-service guarantee.

The separate symbolic cost accounting is:

```
scanCharge = length(examined) * scanCost
scanCharge <= scanFuel * scanCost
turnCharge = scanCharge + dispatchPolicyHandshakeCharge
turnCharge <= scanFuel * scanCost + dispatchPolicyHandshakeLimit
```

`policyIngressScanChargesEachHead` adds scanCost for each examined head at any
allowance, and `policyIngressScanChargesHead` charges an examined head
independently of its event kind, payload weight or outcome. `scannedPayloadIngressZeroPollChargesScan`
retains the scan charge when service fuel is zero. The combined envelope uses
the actual bounded ready queue and requires initial work and handshake balances
to fit their capacities. It is a per-turn theorem; a cumulative admission-cost
envelope over a whole schedule is still open.

These natural-valued charges do not establish implementation time or bytes.
The runtime must justify dominating scan, dispatch, policy and handshake weights,
including payload charge computation and comparisons. Offered-batch construction,
backlog measurement, concrete prefix/suffix traversals, rejected-event disposal,
temporary allocation, empty turns and executor overhead need separate bounds or
an explicit refinement into dominating costs. Mandatory cleanup, trusted ticks
and policy-control delivery remain open under both scan exhaustion and overload.

The 19 new semantic mutations remove or inflate scan fuel, lose or replay the
unexamined suffix, bypass scanning in acceptance, rejection, ready queues,
schedules, execution or trace projection, hide examined rejections, lose
backlog or future turns, erase service fuel, and corrupt scan charges or their
combined envelope. Each must be rejected with a proof type mismatch; parse
errors and crashes do not count.

## Persistent admission resumption

`51-policy-ingress-resumption.mech` retains the caller-owned unexamined suffix
from module 49 across a finite schedule. `PolicyIngressResumeState` pairs that
deferred FIFO with the admitted queue and its resource state. A turn:

1. Appends the fresh batch after the deferred FIFO.
2. Examines at most the fixed `scanFuel` allowance.
3. Offers only that prefix to payload and entry admission.
4. Polls the admitted queue with the turn's independent service fuel.
5. Retains the unexamined suffix and the resulting queue/resource state.

`resumedPayloadIngressRunsTurn` proves this recursive transition over arbitrary
events, states and remaining schedules. `resumedPayloadIngressRetainsDeferred`
connects the returned state to the pure suffix calculation. Examined admission
rejections leave this FIFO; they are not retried automatically.

`resumedPolicyIngressConservation` proves exact ordered conservation:

```
complete examined trace ++ final deferred FIFO
  = initial deferred FIFO ++ all fresh batches
```

The scan-trace bridge reuses the varying-fuel FIFO scheduler for examination,
with each turn's service fuel replaced by the fixed scan allowance. This is a
proof projection; examining an arrival does not execute its resource event.
Zero scan fuel examines nothing and retains all arrivals. Two-turn laws over
event and suffix variables check that older deferred heads precede fresh work,
the remaining tail is retained, and idle scan allowance is not banked.

`resumedPolicyIngressExaminationEquation` proves that an original deferred
prefix occurs at the start of the examined trace when the sum of delivered
scan allowances equals its length plus natural slack. Later arrivals cannot
overtake it. This also covers turns with zero service fuel. The independent
`resumedPayloadIngressServiceEquation` preserves conditional dispatch of an
initially admitted queue prefix when summed service fuel covers that prefix.
These premises concern fuel actually delivered in the finite schedule; neither
theorems nor the model deliver real wakeups or establish wall-clock latency.
Examination does not imply admission or dispatch.

Across the schedule, the admitted queue retains its entry and immutable-payload
bounds when the respective initial bound holds. The carried resource state
equals execution of `resumedPayloadIngressTrace`, and pending occupancy stays
within initial capacity. These bounds exclude the deferred FIFO, which has no
capacity limit in this model. It can grow even when the admitted queue is empty.

The symbolic cost envelope covers the entire finite resumed schedule. Write
`Q` for the examined trace, `T` for the filtered dispatched trace, `A` for the
sum of scan allowances, and `F` for the sum of service fuel:

```
length(Q) * scanCost
  + length(T) * eventCost
  + processed(T) * policyCost + starts(T) * handshakeCost
<= A * scanCost + F * eventCost
  + (workCapacity + trustedTicks(T) * workRate) * policyCost
  + (handshakeCapacity + trustedTicks(T) * handshakeRate) * handshakeCost
```

Initial work and handshake balances must fit their capacities. The two resource
bursts are counted once across the complete dispatched trace. Every examined
arrival receives a scan charge, including rejected and zero-payload events.
The cost-counting equations prevent erased scan, dispatch, policy or handshake
charges from satisfying the specification merely by weakening the cost.

The 24 `policy_resume_*` controls perturb FIFO order, continuation retention,
fresh arrivals, service and scan fuel, returned state, admission filtering and
cost accounting. Their mutated definitions are well typed; subsequent equality
or order proofs reject the changes. The complete gate also checks all earlier
controls and empty axiom disclosure.

Runtime refinement must establish atomic ownership across both queues, actual
suffix resubmission, bounded or lazy offered batches, and enough delivered turns.
It must separately bound deferred storage, concatenation and traversal, backlog
measurement, charge computation, rejection disposal, empty turns and executor
work. Symbolic weights need concrete cost dominance. Cancellation, restart,
concurrent producers, changing limits and delivery of mandatory events through
admission rejection remain open. C61-C64 record these boundaries.

## Bounded deferred handoff

`52-policy-ingress-deferred.mech` adds a fixed caller-owned capacity to the
unexamined suffix. The offered trace is the retained deferred FIFO followed by
the fresh arrival batch. Scanning produces an examined prefix and an unexamined
suffix. The suffix is then split into a retained deferred prefix and an explicit
overflow suffix:

```
offered = examined ++ retainedDeferred ++ overflow
length(retainedDeferred) <= deferredCapacity
length(overflow) <= length(unexamined)
```

`boundedResumedPolicyIngressDisposition` proves the exact three-way FIFO
partition. Zero scan retains the whole offered trace as unexamined. Zero deferred
capacity retains no deferred prefix and reports the full unexamined suffix as
overflow. These equations keep examined admission rejections separate from
unexamined overflow.

`boundedResumedPolicyIngressExaminationEquation` exposes an original deferred
prefix at the start of the examined trace when this single turn supplies its
length plus natural slack in scan fuel. It does not establish cumulative
progress across bounded handoffs: overflow is removed from the continuation.
`boundedResumedPolicyIngressRetainsOldHead` checks that a one-entry deferred cap
keeps the oldest head when scan fuel is zero.

`runBoundedResumedPayloadIngress` carries the bounded deferred prefix together
with the admitted queue and its resource state. It scans the offered trace with
`scanFuel`, applies payload and entry filtering to the scanned ready trace, polls
that trace with independent service `fuel`, and retains the poll remainder.
`boundedResumedPayloadIngressQueueEntryBound`,
`boundedResumedPayloadIngressQueuePayloadBound` and
`boundedResumedPayloadIngressPendingBound` preserve the admitted bounds under
their initial-fit premises. `boundedResumedPayloadIngressExecutesTrace` ties the
returned resource state to the actual filtered dispatched trace.

`handoffBoundedPayloadIngress` returns both the overflow and that continuation
in `BoundedPolicyIngressHandoff`. Its projection equations connect those fields
to the overflow calculation and runner. The handoff conservation theorem uses
the returned fields, and its deferred-entry bound needs no initial deferred
bound. The entry and payload assumptions for the admitted queue remain separate.

The explicit disposition cost is:

```
dispositionCharge = length(examined) * scanCost
  + length(overflow) * overflowCost
dispositionCharge <= scanFuel * scanCost
  + length(unexamined) * overflowCost
```

The overflow term depends on the unexamined input length, so this is not a
fixed per-turn work bound. The deferred entry cap does not bound deferred
payload, overflow storage or total memory. The model still abstracts allocation
and ownership. Runtime work
must define atomic transfer, concrete retained storage, offered-batch traversal,
overflow reporting and disposal, resubmission and delivery across cancellation
and restart. It must also preserve mandatory cleanup and control events when
admission or deferred capacity is exhausted. C65-C68 record these boundaries.

The 25 new controls change executable definitions for FIFO order, capacity,
scan and service fuel, continuation retention, payload admission, overflow
reporting and cost accounting. Each changed definition must type-check before
a later proof rejects the mutation. Parser failures do not count.

## Bounded deferred handoff schedules

`53-policy-ingress-handoff-schedule.mech` composes the module-52 handoff over
finite caller-supplied schedules. Deferred capacity and scan allowance are
fixed; each turn supplies its own service fuel and fresh arrival batch.
`boundedDeferredIngressSchedule` examines the old deferred FIFO followed by
the new batch, then passes only the capped unexamined prefix to the next turn.
`boundedDeferredIngressRemainder` is the final retained FIFO.
`boundedDeferredIngressOverflow` appends each turn's unexamined overflow in
chronological order. That trace is output history, with no modeled storage cap.

`runBoundedDeferredIngress` returns the overflow history with the final
deferred FIFO, admitted queue and resource state. `boundedDeferredIngressOneTurn`
and `boundedDeferredIngressContinuesHandoff` identify its state with the existing
single-turn handoff and continuation. Entry and immutable-payload bounds retain
their separate initial-fit premises; the pending-capacity bound also survives.
The examined-arrival schedule preserves service fuel. The arbitrary-schedule
deferred bound requires initial fit, since the empty schedule keeps its input.
The existing single-turn bound still applies regardless of initial deferred size.

The whole-schedule disposition counter uses this recurrence:

```
accounted(done, deferred) = length(deferred)
accounted(turn, deferred) = length(examined) + length(overflow)
  + accounted(rest, retainedDeferred)
accounted(schedule, initialDeferred)
  = length(initialDeferred ++ allFreshArrivals)
```

`boundedDeferredIngressArrivalConservation` proves the last equation over
arbitrary schedule and trace variables. It counts supplied occurrences,
including examined candidates subsequently rejected by entry or payload
admission. It is a scalar recurrence, not an event-identity uniqueness,
acceptance, execution or delivery theorem. The exact overflow equations and
two-turn boundary laws separately detect reordering and internal replay.

The 27 new controls mutate scan selection, service fuel, continuation input,
the carried deferred input, terminal deferred resubmission, the carried
admitted queue, deferred capacity, overflow order/reporting, admitted limits,
execution and occurrence accounting. Every mutated executable definition
type-checks in isolation before a later proof rejects it. C69-C72 record the
claims and their remaining ownership, storage, overflow disposal/delivery,
cancellation, restart, cost and mandatory-event obligations. No cumulative
progress theorem for retained prefixes or concrete runtime bound is added by
this slice.

## Service through bounded deferred handoffs

`54-policy-ingress-handoff-service.mech` extracts the chronological examined
trace from the actual module-53 schedule. `policyIngressScheduleTurns` counts
delivered turns independently of dispatch fuel. The service theorems fix the
ingress scan allowance at one per turn; dispatch fuel and fresh finite arrival
batches remain arbitrary, including zero dispatch fuel.

An original deferred input is split into `prefix ++ suffix`. Natural slack
witnesses express the two separate premises:

```
capacity = length(prefix) + capacitySlack
turns(schedule) = length(prefix) + turnSlack
```

Only the original prefix must fit capacity. The suffix and later arrival
batches may overflow. `boundedDeferredIngressRetainsPrefix` gives an exact
equation for retaining that prefix followed by the portion of the suffix that
fits. `boundedDeferredIngressOneScanRetains` applies this equation to the old
tail after a scan, preserving its position before the previous suffix and
fresh arrivals.

`boundedDeferredIngressUnitEquation` proves, over arbitrary finite schedules,
that the first `min(turns(schedule), length(prefix))` original occurrences form
a prefix of the examined trace. Its constructed suffix makes this an exact
append equation. With both premises above,
`boundedDeferredIngressServiceEquation` includes the entire original prefix.
These statements preserve occurrence order even when event values repeat.
They establish examination, which can still be followed by admission rejection.
They do not establish successful admission or dispatch.

For any fixed scan allowance, `boundedDeferredIngressScanBound` bounds examined
occurrences by the sum of delivered scan allowances. With one scan per turn,
`boundedDeferredIngressUnitScanBound` bounds them by the turn count. Zero scan
allowance and an empty schedule examine nothing. These are event-count bounds;
queue construction, overflow processing, storage, CPU and allocation costs
remain outside them.

A two-turn example with zero dispatch fuel examines the original two entries,
reports two overflowing arrivals in order, and retains the first fresh entry.
Separate boundary examples show loss of service without capacity fit or enough
turns. The 19 new controls corrupt examined-trace extraction, capacity or scan
allowance, turn counting, retained suffixes, the unit and service suffixes or
the finite overflow example. All must produce proof type mismatches. Seventeen
exercise general statements; two exercise the finite example with variable
events.

C73-C76 record these contracts. Runtime delivery of scan turns, exclusive FIFO
ownership, overflow delivery or disposal, examined rejection handling, concrete
costs, storage and wall-clock latency remain open. This slice does not extend
the service theorem to larger or varying scan allowances, changing capacity,
cancellation or restart.

## Pauses in bounded deferred handoffs

`55-policy-ingress-handoff-pauses.mech` gives each finite scheduled turn an
independent zero-or-one ingress scan allowance. Dispatch fuel and fresh finite
arrival batches remain arbitrary. A paused turn examines nothing, but still
appends arrivals after the deferred FIFO, retains only the fixed-capacity prefix
and reports overflow. Overflow histories are outputs with no storage bound.

`pacedDeferredIngressTurn` identifies each compiled turn, and
`pacedDeferredIngressPreservesFuel` preserves cumulative dispatch fuel.
`pacedDeferredIngressBound` bounds the final deferred FIFO, including an empty
schedule, when the entire initial deferred input fits. The prefix examination
results require only the selected original prefix to fit; its suffix may
overflow. `pacedDeferredIngressPauseRetains` proves exact retention through a
pause, while the one-scan case reuses the module-54 tail-retention theorem.

`pacedDeferredIngressPrefixEquation` places the first
`min(scans(schedule), length(prefix))` original occurrences at the start of the
examined trace, with an explicitly constructed suffix. Pauses add no scans.
Given `capacity = length(prefix) + capacitySlack` and
`scans(schedule) = length(prefix) + scanSlack`,
`pacedDeferredIngressServiceEquation` includes the whole original prefix.
`pacedDeferredIngressScanBound` bounds all examined occurrences by delivered
scan allowances independently of dispatch fuel.

A four-turn example alternates pauses and scans. It examines the original two
events, retains a fresh event, and reports overflow from both pauses in order.
A zero-capacity paused turn reports its entire offered FIFO as overflow.
A second example scans a fresh arrival on its own turn and retains only one of
two paused arrivals at capacity one.
The 25 negative controls corrupt scan selection and counting, dispatch fuel,
input order, retention, overflow, prefix witnesses, the scan bound and the
mixed example. Each must fail with a proof type mismatch.

C77-C80 record these contracts. Enough delivered scans is an explicit premise;
arbitrarily many pauses do not establish progress. Runtime wakeups, ownership,
admission, dispatch, mandatory-event handling, concrete costs and latency remain
open. Larger scan bursts, changing capacity, cancellation and restart remain
outside this slice. Module 56 supplies abstract queue/resource composition and
a recursive whole-schedule occurrence-count identity.

## Paced handoff execution

`56-policy-ingress-paced-execution.mech` runs the examined schedule through
payload and entry admission, then dispatches according to each turn's service
fuel. It returns chronological unexamined overflow separately from the final
deferred FIFO and admitted queue/resource state. `pacedDeferredIngressEmpty`,
`pacedDeferredIngressOneTurn` and `pacedDeferredIngressContinuesHandoff` identify
empty execution, the single-turn handoff and exact state transfer to later
turns. These equations quantify over the scan flag, so paused turns still
retain arrivals and service the existing admitted queue. Their overflow comes
from `pacedDeferredIngressReportsOverflow` with the module-55
`pacedDeferredIngressOverflowStep`.

`pacedDeferredIngressExecutesQueue` projects exactly the payload-filtered
runner. Entry and immutable-payload bounds each require their own initial-fit
premise. The deferred bound also requires initial fit because an empty schedule
does not trim the initial FIFO. Pending occupancy remains bounded by the
original pending pool capacity. These are separate model bounds, not a bound
on total process memory, deferred payload or output-history storage.

`pacedDeferredIngressAccounted` recursively adds the examined and unexamined
overflow occurrence counts at each turn, ending with the terminal deferred
count. `pacedDeferredIngressConservation` equates this total with the initial
deferred count plus all fresh arrivals; `pacedDeferredIngressArrivalConservation`
states the same input side as a concatenated trace length. Neither theorem
requires initial fit. Examined occurrences include candidates subsequently
rejected by admission. This accounting does not assert successful admission,
external delivery or a bound on the storage of output traces.

`pacedDeferredIngressExecutesTrace` identifies the resource state with execution
of the actual payload-filtered dispatched trace. The combined cost theorem
reuses that trace's dispatch/policy/handshake envelope, counting each initial
burst once and requiring the corresponding initial credit bounds. Scanning,
concatenation, admission, deferred retention and overflow costs remain omitted.
C81-C84 record the statements, assumptions and remaining runtime obligations.

The 18 new negative controls corrupt overflow and deferred state, compute
overflow without the deferred FIFO, skip queue execution, erase the existing
queue, bypass scans, change capacity, ignore deferred input, enlarge admission
limits, omit occurrence counts or recursion, count examined occurrences with
the wrong scan allowance and overclaim the dispatched cost bound. Each must fail with a proof mismatch.
One older queue-erasure target gains context to remain unique; it still
constructs exactly the same mutated bundle as before.

## Paced handoff administrative costs

`57-policy-ingress-paced-cost.mech` extends the paced executor's cost ledger.
`pacedDeferredIngressScanCost` charges every examined occurrence with an
independent `scanCost`. `pacedDeferredIngressScanCostBound` bounds that total by
delivered zero-or-one scan allowances times the weight, regardless of dispatch
fuel or whether subsequent admission accepts or rejects the examined event.

`pacedDeferredIngressVisits` counts the full offered FIFO on every delivered
turn, then recurses with the actual retained suffix. `VisitsOffered` identifies
the first summand with the length of the concatenated deferred and fresh FIFO.
Here and below, abbreviated theorem names have the `pacedDeferredIngress`
prefix. Retained occurrences are counted again on later turns, including
pauses; overflow is included on the turn that reports it. Duplicate event
values remain separate occurrences. This is neither a unique-event count nor
a storage bound on accumulated overflow output.

`pacedDeferredIngressVisitLimit capacity schedule initial` uses the recurrence
`L(done, initial) = 0` and
`L(turn(arrivals, rest), initial) = initial + length(arrivals) + L(rest, capacity)`.
`VisitBound` proves visits are at most that limit. The first turn uses the
actual initial deferred length, with no initial-fit premise. Later turns may
each retain a full buffer. Every fresh batch is charged in full, even when scan
allowance, dispatch fuel or deferred capacity is zero. A fixed deferred cap
therefore does not imply bounded work for arbitrarily large fresh batches.

`AdminCountsWork` gives the exact symbolic administrative sum:

```
examined occurrences * scanCost
  + offered-item visits * handoffCost
  + delivered turns * turnCost
```

`AdminBound` replaces examined count with delivered scan allowances and visits
with the visit limit. `AdminStopped` charges no work without turns, even with
an initial suffix. `EmptyTurnCost` charges fixed overhead for an empty paused
turn. The retention, oversized-overflow and zero-dispatch witnesses show that
these costs persist during pauses, at zero deferred capacity and without
dispatch fuel. The witnesses complement the arbitrary-schedule inequalities.

`CostCountsWork` adds this administrative ledger to the cost of the actual
payload-filtered dispatched schedule. `CostEnvelope` composes their bounds
under the same initial policy-work and handshake-credit premises as module 56.
The dispatched envelope counts each initial resource burst once across the
whole schedule. No new initial queue or deferred fit premise is needed for
this cost inequality; their separate storage invariants still require fit.

Runtime interpretation requires six dominating weights in a common unit.
`scanCost` covers examined admission decisions, charge computation and rejection.
`handoffCost` covers all per-offered-item passes, concatenation, retained suffix
handling and overflow materialization/transfer. `turnCost` covers remaining
per-turn work, including empty turns and any backlog measurement not charged
per item. Execution weights retain their existing dispatch, policy and
handshake obligations. Concrete domination, external batch construction,
uncharged allocations, output-history storage, scheduling and real-time latency
remain open. The natural-number ledger is not a measured CPU bound.

The 24 new controls erase turn, deferred, arrival and recursive visit charges;
charge a finished schedule for a turn or for occurrences still deferred after
the final turn; mis-thread retained suffixes, scan allowances or capacity;
weaken initial, arrival or repeated-retention limits; alter examination
counting; and omit administrative or execution components and their limits.
Each mutated definition bundle type-checks before the module-57 proof
declarations are restored; all 24 complete bundles fail with semantic
mismatches.

## Natural scan allowances across handoffs

`58-policy-ingress-variable-scans.mech` replaces the paced scan flag with a
natural allowance on each finite scheduled turn. Scan allowance, dispatch fuel
and the fresh arrival batch are independent. Each turn appends fresh arrivals
behind the retained FIFO, examines its allowance-limited prefix, retains the
earliest unexamined suffix up to fixed deferred capacity, and reports the rest
as chronological overflow. Zero-allowance turns still perform the handoff.

`variableDeferredIngressTurn`, `variableDeferredIngressOverflowStep` and
`variableDeferredIngressPausedExamined` specify these equations over variables.
`variableDeferredIngressScanBound` bounds examined occurrences by the sum of
delivered allowances. `variableDeferredIngressPreservesFuel` separately preserves
the sum of dispatch fuel. The mixed witness uses allowances 2, 0 and 3 with fuel
0, 1 and 0: original events `a,b,c` precede fresh `d,e`, pause-time arrival `f`
overflows, and final arrival `g` remains deferred at capacity three.

`variableDeferredIngressPrefixStep` inducts over the current natural allowance.
Its successor consumes one original event; its zero case transfers the retained
prefix to the remaining schedule. `variableDeferredIngressPrefixEquation`
extracts an explicit suffix after the original prefix selected by total scans.
The original prefix must fit deferred capacity; arbitrary later arrivals and
overflow do not overtake it. `variableDeferredIngressServiceEquation` gives the
whole-prefix equation when total scans cover that prefix with a natural slack
witness. These statements concern examination, with admission and dispatch
remaining separate obligations.

`runVariableDeferredIngress` passes the actual examined schedule to the existing
payload/entry admission and resource executor. The corresponding deferred,
queue-entry, payload and pending-resource bounds retain their individual initial
conditions. In particular, a schedule with no turns does not repair an initially
oversized deferred buffer. There is no bound on accumulated overflow history.

The administrative ledger charges examined occurrences by `scanCost`, every
offered occurrence on every delivered turn by `handoffCost`, and every turn by
`turnCost`. Its limit uses total scan allowances, actual initial deferred length
on the first turn, fixed deferred capacity thereafter, and all fresh arrivals.
It therefore includes repeated retention, oversized first offers, empty turns
and pauses. `variableDeferredIngressCostEnvelope` composes this bound with the
actual payload-filtered dispatch/policy/handshake envelope under initial credit
bounds. Each initial execution burst is counted once. Concrete domination by
all six weights, external batch construction, changing capacities, delivery,
cancellation, mandatory events and real-time latency remain unproved.

C89-C92 record these contracts. The 33 new semantic mutations alter scan totals,
scan/fuel separation, FIFO order, retained capacity, replay, overflow, executor
overflow reporting, admitted limits, initial and repeated visit charges, the
turn count, each cost component and each cost limit component. They must
fail with semantic mismatches; parser failures and crashes do not count.

## Chronological occurrence accounting

`59-policy-ingress-accounting.mech` records a finite `PolicyIngressLedger` for
the existing natural-allowance handoff model. Each turn records its examined
block, the length of its retained prefix, its overflow block and the next ledger.
The terminal node records the final deferred trace. Retained events are carried
to the next turn, rather than copied into a second event-history field.

`variableDeferredIngressLedgerExamined`, `variableDeferredIngressLedgerDeferred`
and `variableDeferredIngressLedgerOverflow` identify these projections with the
existing examined, final-deferred and chronological-overflow traces. The two
handoff projection theorems identify deferred and overflow with the actual fields
returned by `runVariableDeferredIngress`, for arbitrary execution parameters.
Examination remains separate from admission and dispatch.

The input chronology is not generally the concatenation of the three output
projections. At capacity one, a paused first turn offering `a,b` retains `a` and
reports `b`; a later turn offering `c` with allowance two examines `a,c`.
Chronological input is `a,b,c`, although examination order is `a,c` and overflow
is `b`. `variableDeferredIngressLedgerInterleaving` records this ledger and
`variableDeferredIngressChronologicalInterleaving` reconstructs its input.

`insertPolicyIngressOverflowAfterPrefix` inserts an overflow block after the
retained prefix of a reconstructed continuation, before later arrivals.
`insertPolicyIngressOverflowShortContinuation` fixes the short-continuation case:
overflow follows the whole continuation.
`reconstructPolicyIngressRound` combines that equation with the exact one-turn
partition, ordered as examined, retained and overflow. Structural induction over
the schedule gives `variableDeferredIngressChronological`: reconstruction from
the ledger equals the initial deferred trace followed by every fresh batch in
schedule order. `variableDeferredIngressChronologicalCount` applies trace length
to this equality. No initial-fit premise is needed for accounting; an empty
schedule preserves even an oversized initial FIFO and does not repair its bound.

The mixed 2, 0, 3 allowance witness retains the original FIFO ahead of fresh
arrivals and records overflow on the paused turn. Further witnesses cover three
equal-valued events split across all three outputs and zero deferred capacity.
Trace equality preserves value multiplicity and order; it does not assign unique
runtime identities to equal-valued occurrences.

C93-C96 link these contracts. All 25 new mutation controls also reject with the
five fixed-schedule witnesses removed. They alter splice position and contents,
projection order, terminal state, scan/fuel separation, carried state and capacity.
Rejection must be a type mismatch. Existing controls and gate logic are unchanged.
Ledger storage, reconstruction cost, runtime occurrence identity, cancellation,
restart, mandatory events and real-time delivery remain implementation obligations.

## Composition across ingress schedules

`60-policy-ingress-composition.mech` concatenates finite variable-scan schedules
without changing their scan allowances, dispatch fuel or arrival batches.
Schedule identity and associativity laws preserve the complete turn structure.
`appendPolicyIngressLedger` replaces the first ledger's terminal node with a
second ledger, preserving all earlier examined blocks, retained-prefix lengths
and overflow blocks. Its terminal identity uses the first ledger's own final
deferred trace; an arbitrary empty terminal is not a right identity.

`composedVariableDeferredIngressLedger` builds the second segment from the first
segment's exact deferred remainder at the same capacity.
`variableDeferredIngressLedgerAppend` proves that this splice equals the ledger
generated for the concatenated schedule. The final-remainder equation separately
identifies the deferred handoff across that boundary. All these equations range
over arbitrary finite schedules, capacities and initial deferred traces.

The examined and overflow projections concatenate the two segment projections
in order. The final deferred projection comes only from the second ledger.
The two composed handoff theorems identify deferred and overflow with the fields
returned by `runVariableDeferredIngress` for the concatenated schedule, under
arbitrary execution parameters. They do not assert equality of every execution
state field or composition of concrete runtime executions.

`composedVariableDeferredIngressChronological` reconstructs initial deferred work
followed by the first segment's fresh arrivals and then the second's. It requires
no initial-fit premise. This theorem is for generated ledgers with the exact
continuation, not arbitrary raw ledger pairs. Concatenating their independently
reconstructed histories would count the carried deferred suffix twice.

The two fixed-schedule witnesses begin with `a,b` at capacity one. A paused turn
with dispatch fuel two receives `c`, retains `a`, and reports overflow `b,c`.
The second segment receives another `a` and scans two occurrences with zero
dispatch fuel. The composed ledger examines `a,a`, while its reconstructed input
is `a,b,c,a`. Event values remain arbitrary and may coincide.

C97-C100 link these contracts. The 22 new mutation controls corrupt schedule
segments and budgets, ledger fields and terminal replacement, or the resumed
schedule, capacity and deferred suffix. All reject with proof type mismatches
even after removing both fixed-schedule witnesses; the remaining positive bundle
also checks. Existing mutation rows are unchanged.

These are finite mathematical ledger equations. Runtime ownership transfer,
changing deferred capacity, construction and output-history storage costs,
overflow delivery, admission and dispatch after examination, and real-time
service remain open.

## Execution across ingress schedule boundaries

`61-policy-ingress-execution-composition.mech` extends the ledger equations to
the complete execution result. Ordinary schedule concatenation preserves every
turn's dispatch fuel and arrival batch. `runPolicyIngressScheduleAppend` carries
the complete queue state into the second segment. `runPayloadIngressAppend`
establishes the same equation with payload and slot admission applied at each
turn, using the evolving admitted backlog.

`variableDeferredIngressScheduleAppend` proves that scanning a concatenation is
the same as concatenating the filtered schedules, with the second starting from
the first exact deferred remainder. `variableDeferredIngressOverflowAppend`
preserves the order of both overflow histories. These equations support
`variableDeferredIngressStateAppend` and `runVariableDeferredIngressAppend`:
`composedVariableDeferredIngress` runs the second segment with the first complete
handoff state, joins the overflow outputs in order, and returns the second state.
Equality includes deferred work, admitted queue and every policy/resource field.

All composition theorems quantify over arbitrary finite schedules and initial
states, including empty schedules, oversized initial deferred work, zero
capacities and paused turns. They require no initial-fit premise. Both segments
use the same weight function, slot and payload limits, deferred capacity and
policy configuration. Initial-fit premises remain necessary for the separate
capacity bounds; these equalities do not supply them.

`variableDeferredIngressDispatchedAppend` concatenates the actual model dispatch
histories after scanning, admission and polling. The second history starts from
the first resulting queue, and `variableDeferredIngressExecutesDispatched`
identifies its resource execution with the final handoff's policy/resource state.
Examined work that admission rejects is not part of that dispatched history.

The boundary witness starts with queued `a`, admits `b` during a turn with zero
dispatch fuel, then dispatches `a` on a turn with zero scan allowance. That turn
receives `c,d`, retains `c` at deferred capacity one, and reports `d` as overflow.
The final admitted queue is `b`, and the resource state reflects the dispatch of
`a`. Event values, initial resource state and configuration remain arbitrary.

C101-C104 link these contracts. The 29 new controls corrupt schedule fuel,
arrivals or tails; overflow order, retention or duplication; carried deferred,
queue or resource state; continuation parameters, configuration or boundary
capacity; and dispatch projection or admission parameters.
Every control rejects with a type mismatch even with the boundary witness
removed, and that reduced positive bundle also checks. Existing controls are
unchanged. The new module adds 14 equality proofs and four operational definitions.

Runtime simulation, atomic ownership transfer, changes to configuration or
capacity, concrete construction and storage costs, overflow delivery and real
executor service remain open. Output-history storage has no bound here. The
symbolic administrative and execution costs now compose in module 62 without
charging initial resource bursts again at schedule boundaries.


## Cost accounting across ingress schedule boundaries

`62-policy-ingress-cost-composition.mech` proves that the existing symbolic
six-weight cost is unchanged by splitting a finite variable-scan schedule and
resuming its exact intermediate state. The module adds 21 equality and order
proofs and five operational definitions, linked by C105-C108.

`variablePolicyIngressTurnsAppend`, `variableDeferredIngressVisitsAppend` and
`variableDeferredIngressExaminedLengthAppend` add the three administrative
counts. The second segment starts with the first exact deferred remainder.
An occurrence retained across the split is visited again on subsequent turns;
empty and paused turns still incur their fixed charge. Initial deferred work
may exceed capacity. `variableDeferredIngressAdminCostAppend` distributes the
scan, handoff and turn weights over these counts.

`policyIngressProcessedAppend` and `policyIngressStartsAppend` add the
processed-policy and accepted-handshake counts across arbitrary ingress traces.
The second trace uses the resource state obtained by executing the first.
`policyIngressTraceCostAppend` combines those equalities with dispatched trace
length to distribute event, policy and handshake charges.

`variableDeferredIngressCostBoundary` is the actual first handoff state, and
`variableDeferredIngressCostBoundaryWork` identifies its resource state with
execution of the actual dispatched history. The admitted backlog also passes
through this boundary. `variableDeferredIngressDispatchCostAppend` therefore
uses the second segment's actual dispatch history and resulting starting state.
Examined work rejected by admission is charged administratively but does not
receive a dispatch charge.

`variableDeferredIngressExecutionCost` packages module 58's existing cost with
the resume state. `variableDeferredIngressExecutionCostCountsWork` checks its
identity with the administrative and dispatched charges, and
`variableDeferredIngressExecutionCostAppend` proves equality with their sum
across both segments. All six weights, the payload weight function, limits,
deferred capacity and configuration stay fixed. The equality holds for empty
segments, zero weights or capacities, pauses, repeated values and oversized
initial work. It requires neither initial-fit nor initial-credit premises.

`composedVariableDeferredIngressCostEnvelope` transports the existing single
whole-schedule bound to the sum of the two actual costs. It requires only the
original work-credit and handshake-credit bounds. It does not add a fresh
resource burst or another credit premise at the split. The same whole-schedule
visit limit accounts for the actual initial deferred length just once.

The 34 controls corrupt carried state or boundary limits, change the
second-segment payload weight or configuration, erase queued or deferred work
and individual cost weights, or supply incorrect induction and composition
arguments. They all fail with type mismatches against universally
quantified statements; this module contains no closed example proofs. The
argument mutations test proof constraints, not distinct runtime transitions.
Existing mutation rows and their rejection criteria are unchanged.

Runtime simulation, concrete domination of the six weights, construction and
output-history storage, parameter changes, mandatory-event delivery and real
executor service remain open. These are finite symbolic cost equalities and a
conditional bound, not measured cost or latency evidence.

## Deferred-capacity changes at handoff

`63-policy-ingress-capacity-handoff.mech` adds an explicit boundary operation
before a variable-scan segment: 21 equality and order proofs, two operational
definitions and C109-C112. The new limit applies only to the deferred,
unexamined FIFO. Admitted entry and payload limits, weights and policy/resource
configuration remain unchanged.

`resizeDeferredPolicyIngress` returns a `BoundedPolicyIngressHandoff`: the
old deferred trace is split into its earliest capacity-sized prefix and an
explicit overflow suffix. The new state carries the entire admitted queue and
policy/resource state. The retained prefix always fits the new limit, and
appending its overflow reconstructs the original trace in order, including
repeated equal-valued occurrences. Zero capacity retains nothing and reports
all deferred occurrences. These statements require no old capacity or
initial-fit premise.

Structural induction proves that selecting the same prefix twice is
idempotent and that the selected prefix has no overflow at that capacity.
Consequently, applying the same resize to its returned state leaves deferred
work unchanged and produces no second rejection report. This requires using
the returned state, rather than replaying the original input. The theorem does
not cover arbitrary sequences of different capacities.

`runResizedDeferredIngress` starts the existing variable-scan execution from
the exact resized state. Its overflow is boundary overflow followed by the
segment's chronological overflow. Even a stopped schedule retains the
boundary disposition. The terminal deferred bound is unconditional because
resizing establishes initial fit; admitted entry and immutable-payload bounds
retain their own initial-fit premises. The pending bound refers to the
original lease capacity.

Finite reductions check shrinking two events to one, retaining both at
capacity three, paused-turn overflow following boundary overflow with a
repeated event value, and retention of a fresh arrival after a one-item scan.
Event values and the carried queue are variables. These witnesses do not
establish general growth laws, admission, dispatch or eventual delivery.

Twenty-one controls alter the two operational definitions: erase or misreport
boundary overflow, retain the wrong suffix or too many events, erase admitted
work, reorder or lose later overflow, resume from the original input, or change
the execution capacity, schedule, slots, payload limit, charge function or
configuration.
Each must be rejected with a type mismatch under the existing gate criteria.

This is an abstract atomic boundary, not a runtime configuration protocol.
Authority to change limits, serialization, ownership, mandatory cleanup and
control delivery, persistence, traversal and allocation costs, rejected-event
storage and real-time latency remain open. The fixed-parameter cost and ledger
composition results in modules 60-62 do not extend across this resize. Module 64
supplies chronological reconstruction for this boundary and its following
segment. Module 65 supplies preceding-ledger composition. Module 67 adds
symbolic resize charges and module 68 adds deferred accounting across arbitrary
finite capacity schedules; module 69 adds their admitted execution.
Module 70 adds repeated-change symbolic costs; Rust refinement remains open.

## Occurrence accounting across a deferred-capacity boundary

`64-policy-ingress-capacity-accounting.mech` adds 18 equality proofs, one
operational definition, one witness schedule and C113-C116.
`resizedDeferredIngressLedger` represents the boundary using a ledger record
with an empty examined trace, the length of the actual retained prefix and the
removed suffix. Its continuation is the existing variable-scan ledger at the
new capacity, starting from that retained prefix. This administrative record
neither delivers a scheduler turn nor consumes scan or dispatch fuel.

The chronological projection reconstructs exactly the original deferred input
followed by every fresh arrival in the subsequent segment. The proof combines
the existing continuation reconstruction with the boundary partition law and
the overflow insertion lemma. Inserting the removed suffix after the retained
prefix puts original overflow before later arrivals, even if retained events
are examined in later turns. The equality preserves order and multiplicity,
and applying trace length yields occurrence-count conservation. Neither proof
requires an initially fitting input or distinct event values.

The examined and final-deferred projections equal the existing variable-scan
traces from the resized prefix. The overflow projection is boundary overflow
followed by subsequent overflow. Deferred and overflow also equal the actual
`runResizedDeferredIngress` handoff fields for arbitrary admitted limits,
weights, configuration and state. These parameters remain fixed during the
post-resize segment. Examination alone does not establish admission or dispatch.

An empty schedule still reports the removed suffix and retains the selected
prefix without examining anything. Its chronological projection recovers the
entire original input. At zero capacity all original occurrences precede later
overflow, and an empty schedule leaves no deferred work. Finite witnesses shrink
two events to one, overflow fresh arrivals during a pause, then examine two
events and retain the final fresh arrival. Their separate projections constrain
overflow order, examination and final retention. A repeated-value witness keeps
all three occurrences.

Sixteen controls change boundary examination, retained-prefix metadata,
overflow selection or the continuation's input, capacity or schedule. Each
altered definition typechecks in isolation from the new proofs; the full
bundle rejects each at a statement over variables with a proof type mismatch.
These checks constrain the definitions and proof terms, without asserting that
every altered term denotes an extensionally different chronological trace.

Runtime authority, serialization, exclusive occurrence ownership, cleanup,
history storage, construction and traversal costs remain open. This result
covers one resize and its following finite segment. Module 65 extends ledger
accounting to a preceding segment. Module 67 adds symbolic resize charges and
module 68 extends this ledger to arbitrary finite capacity schedules and
module 69 adds their admitted execution. Module 70 adds repeated-change costs;
other resource-limit changes and wall-clock delivery require further work.

## Ledger composition across a deferred-capacity change

`65-policy-ingress-capacity-composition.mech` adds 13 equality proofs, one
operational definition and C117-C119. `capacityComposedDeferredIngressLedger`
appends the first segment's ledger to the existing resize ledger, passing the
exact first segment remainder into the boundary. The old capacity applies to
the first segment and its remainder; the new capacity applies to the boundary
and the following segment. Scan allowances and dispatch fuel remain independent.

A recursive congruence lemma allows a ledger continuation to be replaced by
another continuation with the same chronological projection. Combining that
lemma with the existing boundary reconstruction and fixed-capacity composition
proofs reconstructs the initial deferred trace followed by the first and second
arrival histories. Trace length preserves the corresponding occurrence count.
The statements require neither initial fit nor distinct event values.

Examined and overflow projections concatenate the two segment-ledger projections
in order; final deferred work is the second ledger's deferred projection.
The resize ledger contributes no boundary examination and reports boundary
overflow before subsequent turn overflow. The empty-first identity reduces the
construction to module 64, including oversized initial inputs and empty second
schedules. These are ledger projection laws, not a new full execution theorem.

Closed witnesses over arbitrary event values exercise examination and overflow
in both segments with a shrink between them. They distinguish first-segment,
boundary and second-segment overflow order. Additional witnesses cover a zero
boundary after earlier overflow and capacity growth with empty schedules.
Twelve controls alter history retention, capacities, schedules, carried input or
the resize itself. Their definitions must typecheck before the full proofs
reject them with type mismatches.

Module 66 supplies the corresponding full queue and policy/resource execution
composition across this deferred-capacity change. Module 67 adds symbolic
administrative and resize cost composition. Module 68 separately proves
deferred accounting across finite resize schedules, module 69 adds their
admitted execution and module 70 adds their symbolic costs. Concrete cost
domination, runtime ownership, mandatory-event delivery, wall-clock progress
and bounded output-history storage remain open.

## Execution across a deferred-capacity change

`66-policy-ingress-capacity-execution.mech` adds 16 equality and order proofs,
three operational definitions and C120-C123. `runCapacityComposedIngress` runs
the first segment at the old deferred capacity, passes its complete handoff
state to the explicit resize, and runs the second segment at the new capacity.
Admitted entry and payload limits, weights and policy/resource configuration
remain fixed. The combined generated schedule uses the exact first deferred
remainder, trimmed at the new capacity before the second segment begins.

Execution of that combined schedule equals the final admitted queue and complete
policy/resource state of the sequential operation. The dispatched trace is the
ordered concatenation of both segments' dispatched traces, using the actual
carried queue for the second segment. Running that trace produces the actual
final policy/resource state. These equalities require no initial-fit premise.

The final deferred length is bounded by the new capacity even for oversized
initial deferred input or empty schedules. Admitted entry and payload bounds
retain their respective initial-fit premises, and final pending occupancy is
bounded by the original lease capacity. The capacity-composed ledger's deferred
and ordered overflow projections equal the actual execution handoff fields.

Empty schedules reduce to the existing empty resized execution. A zero-capacity
boundary carries the admitted queue unchanged. Finite witnesses check a shrink
with later arrivals and overflow, repeated equal-valued occurrences, growth with
empty schedules and dispatch of admitted backlog before newly examined work.
The combined payload-filtered schedule inherits the symbolic dispatch-cost
envelope under the original work and handshake credit bounds, without an extra
credit premise at the boundary.

Twenty-seven controls alter capacities, schedules, second-segment limits,
weights and configuration, resizing, carried deferred input, overflow, queue or
resource state, and dispatch filtering. Each altered
definition typechecks by itself; general theorems reject every control without
the concrete witnesses. The dispatch envelope excludes scanning, admission,
retention, overflow handling and the resize itself. Module 67 adds a combined
symbolic administrative, resize and dispatch bound. Module 68 adds deferred
accounting and module 69 adds admitted execution across finite repeated
capacity changes. Module 70 adds repeated-change costs. Concrete cost
domination, other parameter changes, runtime ownership, cleanup, real service
delivery and bounded history storage remain open.

## Costs across a deferred-capacity change

`67-policy-ingress-capacity-cost.mech` adds ten equality and order proofs,
six cost definitions and C124-C126. Resize work counts the retained prefix and
removed suffix. Their lengths sum to the complete pre-resize input length,
preserving repeated occurrences. A per-occurrence weight charges that sum and
one independent fixed weight charges the boundary, including empty input.
The handoff theorem connects this charge to the actual first execution's
deferred field. Empty-input, zero-capacity and repeated-value witnesses pin the
boundary cases.

The administrative cost adds the first segment at its old capacity, the resize
of its exact remainder, and the second segment at its new capacity starting
from the retained prefix. Its bound combines the two existing administrative
limits and the exact resize charge. It permits arbitrary natural capacities,
finite variable-scan schedules and initial deferred input, without initial fit.
In particular, the bound retains the actual boundary input size; it is not a
constant bound in the new capacity alone.

The complete cost adds the payload-filtered composed schedule's dispatch cost.
The eight independent natural weights cover scans, handoff occurrences, turns,
resize occurrences, fixed boundary work, events, policy work and handshakes.
The envelope uses only the original work-credit and handshake-credit bounds.
It adds no fresh credit premise at the boundary and no initial deferred or
admitted fit premise. Admitted limits, payload weights and policy/resource
configuration remain fixed, as in module 66.

Twenty-six controls remove retained or overflow counts, change resize weights,
omit boundary or segment work, use the initial deferred input at the boundary,
reuse an untrimmed or wrong-capacity second input, replay the first segment,
change the dispatch weight, slots or payload limit, drop the carried deferred
input of the dispatched schedule, or undercount administrative and dispatch limits. The changed definitions
typecheck independently; general proofs reject every control without the three
concrete witnesses.

These are symbolic costs. The logical occurrence count does not prove a single
physical traversal. The disclosed `deferred_ingress_resize_costs` assumption
requires the weights to dominate all partition passes, materialization,
ownership transfer and mandatory cleanup in the same unit as the existing
costs. Concrete domination, repeated reconfiguration, external construction,
uncharged allocation, bounded history storage, actual service delivery and
wall-clock bounds remain open.

## Finite schedules of deferred-capacity changes

`68-policy-ingress-capacity-schedule.mech` extends deferred occurrence accounting
to a finite sequence of resize boundaries and polling turns. A resize retains
the earliest prefix at the new capacity, records the removed suffix as overflow,
and continues at that capacity without examining any event. A turn appends its
fresh batch behind the current deferred FIFO, examines the earliest prefix up
to its scan allowance, and retains the earliest remaining prefix at the current
capacity. Zero-scan turns still accept offered batches and record overflow.

The recursive ledger reconstructs the initial deferred FIFO followed by every
fresh batch in offered order, for arbitrary schedules and event values. The
corresponding occurrence count agrees as well. These equalities require no
initial-fit premise. The terminal deferred length is at most the last configured
capacity when the initial FIFO fits the initial capacity, including an empty
schedule. A leading resize establishes this bound without initial fit.

Embedding the earlier variable-scan schedule gives exactly its fixed-capacity
ledger. A leading resize followed by that embedding gives exactly the earlier
single-resize ledger. Dispatch fuel is erased by the embedding because this
layer accounts only for deferred occurrences; it does not execute admitted work.

One operational witness starts with `a,b,c`, shrinks from capacity three to two,
polls one event with arrivals `d,e`, shrinks to one, grows to three, offers `f`
on a zero-scan turn, then polls one event. It reconstructs `a,b,c,d,e,f`, examines
`a,b`, emits overflow `c,e,d` in disposition order, and retains `f`. Event values
are universally quantified and may coincide. Separately, shrinking to zero and
then growing retains none of an arbitrary initial waiting trace.

The 30 controls alter the recursive ledger, offered-arrival projection, final
capacity and fixed-schedule embedding. They omit or reorder arrivals, drop or
replay retained and rejected work, fabricate examination or retained lengths,
keep an old capacity, stop a continuation, or erase scan allowances. Each must
be rejected with a proof type mismatch. These controls constrain the written
definitions and proof terms; they do not establish checker soundness.

This layer closes finite repeated-change deferred accounting. Module 69 adds
admitted queue/resource execution and module 70 adds repeated-change costs.
Authority and serialization, cleanup, mandatory event delivery, bounded history
storage, runtime refinement, service guarantees and wall-clock latency remain
open.

## Execution under finite deferred-capacity schedules

`69-policy-ingress-capacity-schedule-execution.mech` adds an execution schedule
whose polling turns carry separate scan and dispatch allowances. Its accounting
projection erases dispatch fuel and retains each resize, scan and offered batch
for module 68. Its admitted schedule applies each resize to the deferred FIFO,
continues at the new capacity, and passes each turn's examined prefix to the
existing payload-aware admission and dispatch model. A resize produces no
admitted polling turn and never clears the carried admitted queue.

For arbitrary finite schedules, induction proves that the lowered schedule's
offered trace equals the ledger's examined trace in order and multiplicity.
The lowered schedule also preserves the total dispatch fuel across every finite
resize/poll interleaving; resize boundaries contribute no dispatch allowance.
Embedding any earlier variable-scan schedule preserves the full filtered
schedule, including independent dispatch fuel. The runner executes this lowered
schedule and constructs its terminal deferred and ordered overflow fields from
the ledger projections. The field equalities are by construction; they are not
refinement proofs for an independently implemented executor.

The final deferred length fits the last configured capacity when the original
deferred FIFO fits the initial capacity. A leading resize removes that premise.
The admitted queue's entry and payload bounds each retain their own initial-fit
premise, and pending occupancy remains bounded by the original lease capacity.
The admitted limits, payload weights and policy/resource configuration stay
fixed throughout the execution. Empty execution preserves the entire input;
a single resize agrees with the earlier resize handoff for arbitrary state.

Three concrete schedules quantify over event values and resource state. One
shrinks, scans, reaches zero capacity, regrows, retains a zero-scan arrival and
later examines it, preserving the old admitted head. Another reports successive
resize and zero-scan overflow in disposition order. The third dispatches one
carried admitted event after a zero-capacity resize despite zero scan fuel.
These witnesses permit equal event values and do not establish general service
or liveness guarantees.

The 32 controls mutate the accounting projection, admitted schedule, fuel total,
runner and fixed-schedule embedding. They drop or replay input, lose resize or
turn continuations, swap fuel or queue limits, restore rejected work, clear
admitted state or corrupt handoff fields. Each must fail with a semantic proof
mismatch. Runtime authority, exclusive ownership, overflow delivery, cleanup,
bounded history storage and wall-clock service remain open. Module 70 supplies
the repeated-change symbolic cost envelope.

## Capacity schedule cost

`70-policy-ingress-capacity-schedule-cost.mech` adds symbolic administrative and
dispatch work for the arbitrary finite execution schedules of module 69.
All eight weights are natural numbers in one common unit: scan, handoff, turn,
resize, boundary, event, policy and handshake costs. Admitted limits, immutable
payload weights and policy/resource configuration remain fixed.

`capacityIngressPollAdminCost` charges the examined occurrence count at
`scanCost`, every waiting and fresh offered occurrence at `handoffCost`, and
one `turnCost`. A zero-scan turn still charges all offered visits and fixed
turn work, independently of dispatch fuel. Its limit replaces examination by
scan fuel and the initial waiting length by a supplied upper bound.

`capacityScheduledIngressAdminCost` follows the same deferred transitions as
the execution schedule. At a resize it adds the module-67 charge for every
boundary input occurrence and one fixed boundary charge, then recurses on the
retained prefix at the new capacity. At a poll it adds the polling charge and
recurses on the bounded unexamined suffix at the current capacity. The empty
schedule costs zero. Resize overflow is charged once at its boundary and is
not carried into later visit charges.

`capacityScheduledIngressAdminLimit` needs only the schedule, the current
capacity and a scalar initial suffix bound. After a resize it propagates the
new capacity as the next suffix bound; after a poll it propagates the current
capacity. The inductive `capacityScheduledIngressAdminBound` requires only
that the initial suffix length is below the supplied bound. It therefore
covers oversized initial input, empty boundaries, pauses, and arbitrary
finite shrink/growth interleavings. The limit can be conservative when a
growth leaves fewer retained occurrences than the new capacity.

`capacityScheduledIngressCost` adds this administrative cost to dispatch over
the exact `capacityExecutionSchedule`, passed through payload-aware admission
with the carried admitted queue. Its envelope uses the actual initial deferred
length and the original work-credit and handshake-credit bounds. It needs no
fresh credit premise at a boundary and no initial deferred, entry or payload
fit premise. Those occupancy properties retain their separate premises.

The empty-cost theorem is general. Two concrete schedules quantify over event
values and cost weights: a pause retaining one of two equal occurrences before
a zero-capacity resize, and shrink-then-growth charging two occurrences at the
first boundary and only the retained one at the second. They supplement the
general bound without claiming runtime liveness or arbitrary cost equivalence.

The 33 controls change six operational cost/limit definitions. They omit
scans, offered visits, turn work, boundary work or continuations; confuse scan
and dispatch fuel; restore overflow; propagate the wrong capacity or suffix
bound; and omit or misdirect administrative or admitted dispatch work. Every
control must produce a semantic proof mismatch. These are constraints on the
stated proof terms, not independent measurements of runtime costs.

Runtime domination of all eight weights, physical traversal counts, authority,
ownership, cleanup, allocation, bounded history storage and service delivery
remain open. The bound depends on the finite schedule and offered batch sizes;
it does not bound how many resizes or arrivals the environment supplies.
Module 74 establishes equality with earlier segmented symbolic cost models.

## Composition across capacity execution schedules

`71-policy-ingress-capacity-schedule-composition.mech` adds concatenation of
arbitrary finite execution segments, preserving resize boundaries, arrivals,
scan allowances and dispatch fuel. Its right identity and associativity are
proved by structural recursion. `capacityExecutionLimitAppend` carries the
first segment's final deferred capacity into the second segment, including
cuts after polls, pauses, resize-only prefixes and empty segments.

`capacityExecutionLedgerAppend` identifies the complete ledger of concatenated
execution with the appended segment ledgers. The second ledger starts with the
first ledger's terminal deferred suffix at the carried capacity. Projecting
this equality proves terminal deferred equality and ordered overflow
concatenation. Occurrences retain their order even when event values are equal.

`capacityExecutionScheduleAppend` connects the exact lowered dispatch schedules
at the same boundary. `runComposedCapacityScheduledIngress` passes the first
execution handoff's entire state into the second execution, and appends their
overflow traces. Three general theorems equate the final deferred suffix,
overflow and admitted queue with uninterrupted execution. The queue equality
includes policy/resource state. The queue proof uses `runPayloadIngressAppend`,
so it accounts for admitted backlog and payload filtering across the cut.

All equalities quantify over both schedules and the initial state. They require
fixed admitted limits, immutable payload weights and policy configuration, with
no initial-fit premise. They do not supply resource bounds for an invalid
initial state. The ten new proof declarations are linked by atoms C139-C141.

The 18 controls change five operational definitions: concatenation, the carried
capacity, the deferred remainder, ledger composition and execution composition.
They drop or alter a resize, turn, arrival or continuation; confuse scan and
dispatch fuel; restart or discard the deferred input; use stale capacity; lose
overflow; restart the admitted queue; or skip the second segment. Each must
produce a semantic proof mismatch. These controls constrain the model and its
proof terms; they are not a runtime executor test.

Runtime serialization, resize authority, occurrence ownership, mandatory
cleanup, storage dominance and delivery of service remain open. Module 73
connects the earlier single-boundary ledger, lowered schedule and admitted queue
to capacity execution. Module 74 establishes segmented symbolic cost
compatibility. No shared assumption or kernel axiom is added.

## Cost composition across capacity execution schedules

`72-policy-ingress-capacity-schedule-cost-composition.mech` proves that the
cost of arbitrary concatenated capacity execution segments equals the sum of
their costs at the actual handoff. The second segment inherits the first
segment's terminal deferred capacity, exact deferred suffix, admitted queue
and policy/resource state. Admitted limits, payload weights, configuration
and all eight cost weights stay fixed across the cut.

`capacityScheduledIngressAdminCostAppend` adds the five administrative charges
by structural recursion over resize and polling steps. It uses the exact
retained suffix, including after pauses, zero-capacity resizes and repeated
shrink/growth. Empty segments and initially oversized input require no special
fit premise. `capacityScheduledIngressBoundaryDeferred` and
`capacityScheduledIngressBoundaryWork` identify the actual handoff fields;
`capacityScheduledIngressDispatchedAppend` preserves the ordered dispatched
trace across the cut. `capacityScheduledIngressDispatchCostAppend` charges
the second trace using the work state produced by the first trace.

The total-cost equality combines those administrative and dispatch equalities.
`composedCapacityScheduledIngressCostEnvelope` transports the module-70 bound
to the sum of the two actual segment costs. It uses the original work-credit
and handshake-credit bounds and one concatenated-schedule limit, so it does
not add a second initial burst. Initial deferred and admitted fit are not
premises. `capacityScheduledIngressExecutionCostEmpty` proves zero total cost
for an empty schedule. Atoms C142-C144 link the nine new proof declarations.

The 20 controls mutate five operational definitions. They skip execution,
use zero or stale capacity, drop queued or deferred work, omit event, policy,
handshake, resize or boundary charges, discard a segment, or restart the
boundary's deferred input or work state. Each must produce a semantic proof
mismatch. They constrain the abstract model and proof terms.

Module 74 establishes compatibility with earlier fixed-capacity and
single-boundary symbolic costs. Runtime serialization, cost domination, ownership,
cleanup, history storage and actual service delivery also remain open. This
slice adds no shared assumption or kernel axiom.


## Compatibility with earlier capacity execution models

Module 73 embeds arbitrary finite `VariablePolicyIngressSchedule` values using
`capacityExecutionFromVariable`. Structural induction proves equality of the
complete fixed-capacity occurrence ledger, including retained-prefix counts,
examined occurrences, terminal deferred input and ordered overflow. The earlier
`capacityExecutionVariableSchedule` theorem supplies the corresponding lowering
equality, preserving independent scan and dispatch allowances.

`capacityExecutionSingleBoundary` concatenates the embedded first segment with
one explicit resize and the embedded second segment. Induction on the first
segment equates its ledger with `capacityComposedDeferredIngressLedger` and its
lowered schedule with `capacityComposedIngressSchedule`. The resize uses the
exact suffix left by the first segment. Projection equalities retain examined
occurrences, terminal deferred input and overflow order and multiplicity. An
empty prefix still performs the boundary resize, and a zero-capacity boundary
rejects every waiting occurrence when both segments are empty.

`capacityScheduledIngressSingleBoundaryQueue` transports the lowering equality
through payload-aware execution and the earlier segmented execution theorem.
Its endpoints are the actual runners' complete final admitted queue states,
including queued payload and policy/resource state. Payload weights, admitted
entry and payload limits and policy configuration stay fixed. All these
equalities quantify over arbitrary inputs and schedules without initial-fit
or credit-bound premises. They do not grant resource bounds to invalid initial
states, and the queue equality does not separately state equality of the full
handoff records.

The 15 new controls alter operational definitions. Eleven corrupt the boundary
embedding by dropping, replaying or reordering segments or resize steps, or
changing the boundary capacity. Four alter the earlier variable-schedule
embedding by changing or dropping scan allowance, or dropping or incrementing
dispatch fuel. The latter can be rejected by earlier module-69 proofs;
the eleven boundary controls exercise the new general compatibility statements.
Every control must produce a type mismatch, rather than a parser failure,
crash or timeout. No shared assumption or kernel axiom is added.

Module 74 establishes compatibility of the per-turn administrative sum with
the earlier segmented symbolic cost formulas. Runtime simulation, serialization,
resize authority,
occurrence ownership, mandatory cleanup, bounded history storage and delivery
of service also remain open.

## Capacity schedule cost compatibility

Module 74 equates `capacityScheduledIngressAdminCost` on an embedded arbitrary
variable-scan schedule with `variableDeferredIngressAdminCost`. The proof first
distributes the aggregate scan, handoff and turn charges over one turn, then
uses structural induction over the schedule. Scan cost counts examined
occurrences; handoff cost counts all waiting and arriving occurrences, including
retained visits during pauses; fixed turn cost is independent of dispatch fuel.
Empty schedules cost zero even when initial deferred input is oversized.

`capacityScheduledIngressSingleBoundaryAdminCost` combines the exact prefix
charge, resize charge on the actual post-prefix suffix and suffix charge on its
resized retained prefix. It uses the earlier administrative append equality and
the ledger's exact remainder projection. Empty segments still pay the resize
cost, including its fixed boundary overhead. No initial-fit premise is used.

`capacityScheduledIngressVariableCost` and
`capacityScheduledIngressSingleBoundaryCost` transport the lowered schedule
equalities through payload-aware dispatch costs. They equate the complete
earlier cost expressions, including event, policy and handshake charges, under
fixed admitted limits, immutable payload weights, configuration and eight
symbolic weights. These are equalities, without credit-bound premises, and do
not establish resource bounds for invalid initial states. C148-C150 record the
contracts. No shared assumption or kernel axiom is added.

Three boundary statements cover arbitrary empty schedules, paused scans with
independent dispatch fuel and empty segments around an arbitrary resize.
Twelve controls mutate operational costs: omitted scan, handoff, resize or
dispatch charges; replayed scan, turn or resize charges; changed turn weight;
omitted waiting or arrival visits; trimmed prefix cost input; and charging
only retained occurrences instead of the complete resize input. Existing proofs can reject
these controls before module 74. Rejection must be a semantic type mismatch.
Concrete runtime cost domination, serialization, resize authority, occurrence
ownership, cleanup, bounded history storage and delivered service remain open.

## Pre-validation queue, allocation and work envelope

`proofs/78-prevalidation-envelope.mech` closes M002 at its sealed model scope.
One finite queue serves both primary and worker ingress before address validation.
Each cell is vacant or holds a packet payload with an explicit byte-capacity
witness. Arrival fills the first vacancy with at most `byteCap` copied bytes;
it discards overflow without allocating another cell. Decision cleanup searches
past vacant cells and releases the first occupied payload for every Retry,
Refuse, Ignore and Accept outcome, including Accept without an outer event.
Queue shape represents allocated cells, so cleanup releases payloads while
preserving the finite cell allocation. No pending or established cap appears
in this model or its allocation and cost proofs.

For every arbitrary finite trace, allocated cell count remains equal to its
initial value `slots`. Occupancy is at most `slots` and retained payload bytes
are at most `slots * byteCap`. Explicit transient allocation counts every
allocated cell's metadata, actual retained payloads and one active ingress
workspace. Its bound is `slots * entryBytes + slots * byteCap + byteCap`.
`entryBytes` must dominate all cell metadata, and the workspace `byteCap` must
dominate the entire active packet, parsing and token workspace. These storage
dominance and single-workspace lifetime premises require runtime evidence.

Arrival charges bounded packet capture and queue examination, even on overflow.
Each decision charges queue examination, parsing and token processing whether
or not it emits an outer event. Queue examination costs at most one abstract
unit per allocated cell. Packet capture, parsing and token work stop at their
supplied budgets. A trace with `events` incoming transitions therefore costs at
most `events * (byteCap + slots + parseCap + tokenCap)`. A poll processes at most
its finite `fuel` count and costs at most the same per-event envelope times
`fuel`; zero fuel performs no work. This is a finite trace and poll envelope,
not a wall-clock rate, fairness or eventual-service result.

The module adds 33 general proof declarations: eight arbitrary-trace witnesses
and 25 general-transition witnesses. Its 37 mutation controls cover overflow
allocation, uncapped payloads, deep queue searches, packet release on each
outcome and silent paths, worker admission, retained-byte and metadata/workspace
accounting, missing or excessive packet/parsing/token/queue charges, understated
budgets, skipped trace transitions and charges, and fuel-prefix errors. Every
control must fail with a semantic type mismatch rather than a parse failure.

Outcomes and event-emission flags are supplied classifications. Runtime queue
sharing, serialization, allocation layout and lifetimes, cost dominance and
enforcement of the byte, parsing, token and poll budgets remain external.
The model does not verify evidence classification, protocol acceptance,
cryptography, scheduling or actual object allocation.

## Unlocked handshake executor and shared host allocation

`79-unlocked-handshake-executor.mech` discharges M011 using separate finite
waiting and active LeasePools. Events carry an arbitrary endpoint identifier and
either swarm classification; every event routes through the same two banks.
An arrival reserves its selected waiting slot. Dispatch requires a held waiting
generation that matches its internal ticket and a real vacant active slot.
Missing indices refuse transfer. At the head slot, a free or stale waiting
ticket and an occupied active target also refuse transfer. Atomic dispatch
releases the waiting owner and acquires the active owner. Waiting and active
terminal events apply generation-owned release for all five PendingEnd reasons. Work events preserve ownership.

`executorWaitingTraceBound` and `executorActiveTraceBound` quantify arbitrary
finite event schedules and initial banks. `executorTraceCapacity` preserves
both declared widths. `executorRejectedDispatchPreservesBanks` and
`executorPermittedDispatchTransfers` specify both outcomes at arbitrary indices
and generations. Deep-slot witnesses preserve arbitrary surrounding cells and
tails; their fixed generation/index limits are recorded in the audit. Stale
callback lemmas cover the head slot, every immediate predecessor generation and
every terminal reason. The model permits arbitrary event interleavings without fair scheduling
or an accept/endpoint mutex premise.

For any resource dimension with waiting weight w and active weight a,
`executorHostResourceTraceBound` bounds w times waiting occupancy plus a times
active occupancy by w times waiting capacity plus a times active capacity. The
same allocation covers every endpoint and swarm. Independent private pools must
be routed or refined into that allocation before the theorem applies.

Every event charges fixed administrative cost, two full passes over each finite
bank and capped execution demand. `executorHostWorkTraceBound` bounds a trace by
its event count times the initial shared event budget. Denial, overflow and
terminal events remain charged. `executorZeroDemandStillCharges` and
`executorSingletonWorkCharged` prevent empty demand or short schedules from
silently erasing administrative work.

E019 owns concrete worker and callback refinement. Terminal active events must
represent actual task termination and resident release; a cancellation request
alone must retain the active charge. Atomic transfer, complete routing, internal
callback tickets, nonwrapping generations, resource dominance and execution
budget enforcement remain explicit premises. These bounds do not establish
service delivery or fairness. The 24 executor controls exercise dispatch
authority, missing/deep indices, ownership transfer, terminal cleanup, resource
allocation and work charging.

## Arbitrary population and host-vector composition

`80-shared-host-composition.mech` closes M007. A finite HostFleet contains
arbitrary honest, worker, reconnect and distributed members with supplied
swarm/source/identity labels. Each member owns a finite vector of weighted
LeasePools. Every occurrence contributes its capacity-weight product to each
aggregate coordinate. The declared host vector is a separate parameter, with
an explicit premise that the sum of all allocations fits it.

Indexed pool actions preserve every allocation coordinate. Churn retains the
bank vector, including its occupied leases, while replacing labels. Arbitrary
mixed traces therefore preserve aggregate allocation and keep weighted use
within the initial sum. Missing members and coordinates allocate nothing.
Complete-state equations constrain event routing and all head/suffix charges.

`hostFleetWorkBound` composes arbitrary per-member demands clipped to their
slices. `sharedHostWorkAfterTraceBound` keeps this per-interval sum within its
initial host allocation after any mixed trace. Separate resource/work units
use separate vectors. Runtime clipping, complete work/storage accounting and
production calibration remain premises. E022 owns established-resource clipping
and work accounting. E013 owns runtime pending accounting. E010 owns production
calibration and storage dominance. Membership is fixed during the allocation
interval; changing population requires a new aggregate-fit witness.
Source normalization, resource-specific established vectors, rates and service
remain separate obligations. Thirty controls include omitted populations,
duplicated allocations, charge-resetting identity churn and work bypasses.

## Negative controls

The checker rejects 1109 invalid variants: three direct checks of equality,
ordering and termination, plus 1106 semantic mutations. Mutations exercise such
faults as stale-owner release, skipped terminal cleanup, growing pool capacity,
uncapped refill, forged or duplicated credits, lost poll backlog, missing
wakeups, skipped service, unauthenticated committee records and stale epoch
resolution. Failure must be a semantic checker diagnostic; syntax errors and
crashes do not count as a successful negative control.

Policy mutations additionally bypass generation, epoch, identity or record
authentication checks; preserve obsolete resolution; suppress valid updates;
diverge a consumer; skip recovery; or change resource state during reload.

Source-table mutations grow capacity, never recognise a resident key, register a
known key again, bypass validation, permit unknown sources on overflow, hide a
vacant slot from admission, evict debt or bans, forget a protected debt or ban
entry in the protection projection, evict an unrelated clear entry, suppress
matching eviction or head-slot allocation, or drop a churn event. Two further
source-table controls evict a simultaneous debt-and-ban entry or forget it in
the protection projection. Both safety and enabled transitions have negative
controls.

Source-enforcement mutations bypass zero or exhausted quotas and bans, suppress
permitted charges, omit debt increments, reset a refused source, charge an
unvalidated cell, allow a vacant cell, drop bans or debt during ban
installation, drop a ban on a clear source, trust claimed expiry, erase the
other restriction during expiry, clear a lone ban on debt expiry, retain
expired state, shift the trace charge quota, or drop charge, ban and expiry
trace events. The checker rejects all 27 additional controls (2 source-table,
25 source-enforcement) with semantic mismatches.

The 18 source-system controls fabricate or hide lookup results, ignore keys or
validation, shift quotas, allocate during restriction updates, stop searching at
a vacancy, drop an update or tail search, update duplicate-key tails, and omit
churn, enforcement or trace steps. Every control must fail with a semantic
mismatch, including controls aimed at enabled behavior.

The 32 source-admission controls bypass validation, source quota or refusal,
start without global credit or a free slot, fabricate missing, past-end or
held-slot tokens, misdirect slot lookup, spend on refusal, omit or misdirect
source charges and pending reservations, omit the global charge, alter receipt
indices or generations, emit a receipt on refusal, corrupt completion, mint
credit or erase pending state during maintenance, uncap clock refill, erase
source state on refill, drop bans or churn, ban the wrong key, trust claimed
expiry, or drop a composed trace event. All must be rejected with semantic
mismatches.

The 25 source-admission rate controls omit or fabricate receipt counts, hide
issuance, drop the counting or issuance tail, reuse the old state, change attempt
validation or selected keys and slots, drop maintenance or completion, overissue
or drop trusted ticks, issue credit on attempts, maintenance, completion or
claimed ticks, append refill credit at the end of the erased trace, count a start
on an empty trace, or count attempts, maintenance, completion and claimed ticks
as trusted time. Exact-count witnesses check enabled admission as well as the
universal upper bounds.

The 16 indexed lifecycle controls drop or corrupt pool prefixes, misplace the
selected index, disable or alias lookup and update after the second slot, grant
a slot two or more places past the pool end, misbind deep-slot receipts or
reservations, alter a receipt generation after the second slot, and redirect
completion or alter its generation at deeper indices. Each changed definition
was checked independently through its declaration before the full model
rejected it at a proof. Module-39 theorems reject the 11 prefix, position,
lookup, missing-slot and receipt controls. The two update controls fail at
`updateLeaseCapacity` in module 21. The reservation control fails at
`sourceStartPoolCapacity` and the two completion controls fail at
`sourceAdmissionStepPoolCapacity`, both in module 37. These capacity proofs name
the exact update, reservation and completion arguments, so they reject any
change at these sites. These five controls do not test the module-39 theorems.

The 19 policy/source controls bypass or suppress the receipt gate, misbind peer
identity, upgrade source validation, change the selected key or slot, issue
credit on publication, ignore publication or its generation guard, suppress
maintenance or completion, change the policy view on a trusted tick, overissue
trusted credit, trust claimed time, drop
an erased event, reuse an old trace state, omit a receipt count, or emit a
receipt without the policy gate. All changed definitions were type-checked
through their declarations before the module-41 proofs rejected the full
mutants. These rejections are at statements over variables, not only closed
examples.

The 27 policy-work controls remove charges, trusted refills or budget gates,
suppress funded events or cleanup, fabricate trusted time, turn unfunded work
into trusted clock ticks, change refill rates or capacity, alias the work and
handshake balances in the work charge or in the work gate, corrupt processing
receipts and counts, reuse initial credit during a trace, use post-charge credit
for the admission gate, or emit an admission receipt without checking the work
budget. Their
full mutants must fail with proof type mismatches, rather than parser failures,
crashes or timeouts. The new statements range over variables and finite traces.

The 20 policy-ingress controls gate queries on the handshake credit, bypass or
suppress query production, bypass authentication, change the queried or
attempted identity, replace source validation, corrupt keys or pending indices,
change publication generations, drop cleanup or trusted ticks, fabricate trusted
ticks, miscount trusted ticks in the ingress counter, skip runner events, or
reuse an old pre-state while compiling the trace. They must fail with proof type
mismatches on statements over variables or finite traces.


Passing these controls tests that the definitions constrain the proof terms.
It does not prove the checker sound, the Rust implementation refined, or the
deployment qualified. `make qualify` therefore continues to reject completion.

## Endpoint routing and generation-owned migration

Module 81 models listener/dial endpoints with swarm and socket identifiers and
one finite shared table. Its connection identifier contains the global slot and
generation. General lookup uniqueness and indexed-update laws prevent one
connection from selecting two destinations or changing another slot.

Migration requires both validated destination evidence and the matching
generation. It preserves the original owner and pending/established phase.
Success retains established routing; every matching terminal reason clears the
route and advances its generation before reuse. Unvalidated, mismatched and
repeated-vacant callbacks preserve complete cells. Old routing identifiers are
absent after actual cleanup and replacement reservation.

Arbitrary finite schedules preserve table capacity and bound live routes and
discarded generation tombstones by the initial allocation. Their sum is exactly
that allocation. These proofs require no fair scheduling. The 22 routing
controls weaken charges, reservation, migration validation/generation/ownership,
handshake generation and vacant-slot checks, terminal release/reuse, lookup,
indexed updates and event execution. Every full mutant must fail with a proof
type mismatch.
Runtime routing, callback authority, destination validation, atomicity,
fixed-width storage and nonwrapping generations remain E019 premises.

## Normalized source attribution

Module 82 models IPv4, mapped IPv4 and IPv6 addresses as supplied prefix/host
components under one fixed policy. Native and mapped IPv4 share an even-key
namespace; IPv6 uses an odd-key namespace. Comparison laws preserve each family's
prefix distinctions, and actual normalized addresses remain disjoint across
families. Host changes under a shared prefix retain the same accounting key.
Runtime extraction and the selected prefix lengths remain E014 obligations.

Attributed admission, registration, penalties, eviction and expiry select the
normalized address key. Caller-selected keys and fresh identities cannot redirect
an attempt. Unvalidated admission, registration and penalties preserve the full
state. Receipt equations retain the normalized-key plan and selected pending slot;
clock and completion equations retain issued credit and callback evidence.

An independent recursive execution translates exactly to the existing admission
trace for every finite attributed schedule. The shared pending bound follows for
every initial state. Per-source debt at any normalized address and shared credit
also remain bounded with their explicit initial-fit premises. Arbitrary schedules
include all swarms, registration/eviction churn, penalties, expiry, clock issues
and generation-owned completion. No identity receives a new copy of the bucket.

The 29 controls test namespace stride and collisions, host/prefix substitution,
mapped/native disagreement, caller-key/identity substitution, validation bypasses,
wrong pending slots or swarms, maintenance keys, lost clock/callback evidence,
omitted or duplicated execution and an inflated step quota or capacity. Every mutant must fail through a proof type
mismatch. General namespace equations were added after a control exposed an
unconstrained IPv6 normalization branch.

Module 82 witnesses M003 criterion 1; module 83 supplies trusted-exemption and
privileged-allowance provenance for criterion 0. Fixed quota is distinct from M013's timed
prefix rates. M009 owns multi-prefix overlap and restart/epoch security lifetimes.
E014 and E013 retain runtime normalization, authority and pending refinement.

## Trusted source authority and allowance composition

Module 83 composes one normalized-source admission state with a separately
provisioned source-keyed allowance table. `trustedAuthorityAllowed` requires
validated reachability, authenticated and listed identity, a captured normalized
key matching the actual supplied address, and a captured identity matching the
peer. `trustedRequestAllowed` also checks the selected allowance's fixed budget,
residency and ban status. Caller-selected keys cannot select authority or debt.

A permitted privileged request uses the ordinary source quota, credit and lease
plan. `trustedAllowanceStep` debits only its actual pre-state admitted receipt,
at that same normalized key. Complete-state refusal theorems cover unvalidated,
unauthenticated, unlisted and mismatched authority and unavailable allowances.
Resource admission refusal preserves the allowance table. Ordinary events and
classified penalties cannot debit it. Mapped/native IPv4 share complete state.

Classified load-pressure penalties consult the same authority gate; an exact
validated/authenticated/listed binding is exempt. Validated protocol violations
always select the normalized ban, and unvalidated penalties are complete-state
no-ops. Authentication and listing inputs are supplied authority judgments, not
caller claims. Authority minting and allowance provisioning remain runtime
refinement premises. No privileged request bypasses source quota, global credit
or pending limits; the exemption concerns load-pressure penalties.

`trustedSourceAdmissions` computes the exact resource trace using the evolving
combined state, independently of `runTrustedSources`. Their general execution
bridge preserves arbitrary finite schedules. Trace bounds cover initial shared
pending capacity without an initial-fit premise, and source debt, shared credit
and every selected allowance key with their explicit initial-fit premises.
`SourceQuotaBound` helper proofs are structural proof functions; the 36 counted
new declarations are explicit equality/order statements.

Thirty-seven registered controls each change one complete operational
definition. They test validation/authentication/listing and key/identity binding
bypasses, forged penalty reachability, allowance-gate and key substitution,
denied admission, wrong slots/swarms/keys, forged load exemptions and protocol
exemptions, dropped ordinary/penalty events, refused or fabricated receipts,
missing or collateral allowance debits, changed shared capacity, and dropped or
stale trace state. Every control must fail over quantified inputs. M003 is
covered by modules 82 and 83 together. Module 84 later covers M009, and module 85 covers M013 timed rates.
E014/E029/E013 retain their runtime authority/accounting boundaries.

## Normalized source security lifetimes (module 84)

`SourceLifetimeState` contains a boot generation, epoch and one fixed-width
`SourceTable`. Registration and eviction always use `normalizedSourceKey`;
fresh identities, claimed keys and T4b/T8 users cannot select another namespace.
Mapped/native IPv4 share a prefix key, and IPv6 hosts share their fixed prefix.
Security lookup selects retained debt/ban payloads from one protected table.

Restart advances the boot generation; epoch change advances the epoch. Both
retain the other counter, discard clear residents and preserve all protected
cells. Protected debt and bans persist until authorized service or expiry in a
separate trusted transition system. No clock event or arbitrary lifecycle
boundary authorizes release in this churn-only model. Runtime restoration of
protected cells across process restart is an E014 premise.

The idempotent protection projection and unchanged structural width compose
with every registration, eviction and lifecycle event. Arbitrary finite mixed
traces preserve the entire protected table and each normalized restriction,
and cardinality never exceeds the initial table width, including empty/full
tables and arbitrary initial debt/ban payloads. First-slot re-registration is a
complete-state no-op. This is persistence and bounded storage evidence; it
does not establish rate fairness or a concrete implementation.

Thirty-one counted proof declarations and 26 semantic controls cover this
slice. Controls include same-width security erasure, shared-state separation,
wrong keys, incorrect restriction selection and skipped/replayed trace steps.
M009 is covered; module 85 later covers M013, leaving M012 in R03. E014 and E029 retain the runtime
prefix, storage-restoration, lifetime-counter and release-authority refinements.

## Joint normalized-source rate envelopes (module 85)

`ComposedRateState` stores one aggregate balance and one finite canonical-key
array of source balances, shared across both swarms and all trusted/untrusted
and fresh-identity metadata. IPv4, mapped IPv4 and IPv6 addresses reuse module
82's disjoint normalized prefix namespace. A missing slot denies admission.
Allocation and burst/rate policy parameters stay fixed throughout a trace.

An attempt uses validated reachability, supplied eligibility, aggregate credit
and its actual canonical-prefix credit. Each successful receipt removes exactly
one credit from both buckets. `composedAttemptSelectedChargeEqualsAggregate`
connects the selected-prefix count to the aggregate receipt. Generic selected
debit and continuation bounds compose these counts over every finite mixed
trace. `composedBurstRateEnvelope` proves the distinct burst-plus-trusted-ticks
rate envelopes for the aggregate and every selected prefix, under their explicit
initial-fit premises. The source and aggregate rates need not be equal.

Unvalidated claims, supplied denials, empty aggregate balances, missing slots and
selected zero-credit slots preserve the complete rate state. The zero-source
theorem quantifies over any prefix/suffix around its selected cell and states
the necessary normalized-key/index equality. The allocation-miss theorem
locates any key at or beyond array width and preserves every counter. Changing
swarm, trust, identity,
caller key or host within one supplied prefix cannot alter a transition.
Completion and failure events preserve spent credits. Claimed clock values do
not refill or advance trusted time. Trusted ticks alone refill capped balances.

There are 42 counted proof declarations and 34 semantic controls. Controls
weaken source/global debits, receipt counts, canonical attribution, eligibility,
trust/identity independence, refill caps/rates, terminal paths and trace state.
One control debits a neighboring prefix on a zero-credit refusal and is rejected
by the whole-state zero-source witness. One control appends a slot when a debit
misses the allocation. Every new rejection occurs in a module
whose proof statements quantify over inputs; it has no closed example proofs.

M013 is covered. Sparse runtime indexing, address validation, persistent prefix
identity, eligibility refinement, serialization/atomic admission, trusted clock
authority and production burst/rate calibration remain explicit premises.
E014/E013/E010 retain runtime source/accounting/calibration work. These proofs
bound admitted-start counts, not resident-resource allocations, CPU costs,
continuous-time scheduling fairness or critical-class service. M012 remains open.

## Established resource vectors (module 86)

`EstablishedFleet` holds one finite population of peers with independently
owned `EstablishedBanks`. A bank has one of five protocol kinds and either
incoming or outgoing direction, an `EstablishedUnit` and a finite `LeasePool`.
All protocol/direction counts, byte/task reservations and advertised receive
credit are projections of this same population. Category/direction roundtrips
prevent aliases, and the slot classifier requires both labels to match.

An arbitrary indexed `PoolAction` changes one peer, bank and slot. Grants take
a free slot's generation and refuse a held slot. All terminal reasons use the
same generation-owned release. `EstablishedTerminal` explicitly
names close, cancellation, failure, timeout and shedding. Its wrapper binds
every owner coordinate before lowering to the generic lease primitive. Exact
update shapes quantify over arbitrary
prefixes and suffixes at each ownership level. The composed release frees only
the matching held generation, advances it and preserves all other peers, banks
and slots. `EstablishedOwner` binds the peer, bank, slot and internal token;
runtime provenance of that receipt remains a premise. Shedding uses this same
terminal path. Unowned and preceding-generation tokens preserve their pools.

Finite mixed grant, terminal and trust/swarm/identity-churn traces preserve
every coordinate of the initial allocation. Each use coordinate stays below
that allocation, and an explicit initial-fit premise composes all peer vectors
into one supplied finite process allocation. Relabeling retains complete owned
banks. Arbitrary simultaneous occupancy models overlapping resource lifetimes
across the finite population. `EstablishedProcess` preserves its complete pending
lease pool and its separate pre-accept work field through every established trace.
This holds by construction because no established event can change those fields.

Advertised receive credit is an independent weight. It changes neither reserved
resident byte/task weights nor symbolic actual unit costs. `EstablishedUnit`
requires explicit domination certificates for both actual cost upper bounds.
These lift through all occupied slots, banks and peers to trace-wide resident
bounds. `establishedResidentWithOverheadBound` additionally charges independently
bounded fixed/shared resident overhead, including idle containers and process
tasks, even at zero occupancy. Its premise reserves that overhead together with
the population's complete allocation vector in the same process budget.

The module has 35 counted proof declarations and 36 new semantic controls.
Controls weaken category/direction distinctions, resident/advertised axes,
actual costs, overhead, bank/peer sums, indexed isolation, trust charging, churn
retention, trace execution, receipt coordinates and unrelated-phase preservation.
Two controls specifically skip the established close and shedding releases.
Each must fail over quantified inputs with a type mismatch.

M012 criteria 0 and 3 are witnessed. Criterion 1 retains stage accounting
between pending, pre-accept and established resources. Criterion 2 has finite-vector composition
evidence but still requires critical-class service under explicit workload and
scheduling premises. E022/E013/E010 retain runtime classification, unique slot
routing, atomicity, receipt authority, nonwrapping generations, actual resource
termination, cost domination and production calibration. Symbolic costs and
overhead certificates are supplied model evidence, with runtime refinement open.

## R03 turn 12: unified reservation stage accounting

`87-stage-resource-accounting.mech` adds 32 counted proof declarations. One
finite ledger stores each resource's phase, lease, protocol, direction and
certified unit. `stagedBanks` erases phase labels into module 86's resource
banks. `stagedLedgerPartition` equates the sum of pending, pre-accept and
established charges with that erased vector for every population and axis.
`stagedPartitionTraceBound` bounds that sum after arbitrary acquisition,
handoff and terminal traces. An initial-fit premise supplies a process budget.

Handoffs require a held matching generation and expected phase. They conserve
the underlying lease and all resource coordinates. The explicit pending to
pre-accept theorem prevents skipping the intermediate stage; two handoffs
reach established. A matching handoff at established keeps the resource
established. Unowned, free and stale handoffs preserve the resource.
Matching completions release and advance the generation; repeated completion
is idempotent. Receipts from an earlier stage cannot release a later stage.
Focused update and trace-dispatch statements preserve arbitrary surrounding
populations. The 25 new controls cover these rules, missing trace events,
wrong-cell updates and missing or duplicate stage charges.

The phase ledger reserves the same unit throughout a resource lifetime. It
does not establish separate pool admission, pending-generation refund on
distinct established allocation, pre-accept execution coupling, or scheduling
service. Modules 88-89 supply coupled stage accounting and that promotion
bridge; criterion 2 retains critical service. Runtime receipt provenance, atomicity, routing and phase-wide
cost domination remain external premises.

## R03 turn 13: coupled distinct stage process

`88-coupled-stage-process.mech` adds 40 counted proof declarations. The process
contains the existing pending lease pool, pre-accept executor and established
fleet. Each nonpromotion event changes only its own account. Promotion checks
pending generation ownership and the selected established vacancy before an
atomic pending completion and distinct established grant. Refusal preserves
the whole process; promotion preserves the executor. A raw successful
pending callback preserves its lease and must use guarded promotion. Explicit
routing witnesses retain failed completion and reservation effects.

General generation-consumption and idempotence statements prevent the same
promotion from releasing or allocating twice. A successful head witness pins
independent pending and established generations, classifications and arbitrary
surrounding suffixes. Free or preceding-generation pending owners, occupied
destinations and a missing population refuse without changing accounts.
Lookup-tail statements constrain peer and bank selection.

Arbitrary mixed traces preserve all three stage allocations and their weighted
sum for every established resource axis. Coordinate-wise initial fit supplies
one finite process-vector bound. The 31 new controls constrain ownership,
vacancy, coordinate routing, release/grant effects, other-stage isolation,
trace dispatch and allocation accounting. They reject proof-term weakening;
they do not validate runtime behavior.

Module 89 supplies successful promotion at arbitrary prefixes/suffixes
and all absent-index operational refusal witnesses, closing M012 criterion 1.
Module 88's generic granted/refused statements assume their guard equality.
Criterion 2 retains critical scheduling
service. Runtime classification, routing, receipt provenance, serialized
atomicity, actual termination and per-stage cost domination remain external.

## General operational stage promotion

Module 89 uses the unchanged coupled process from module 88. Its 24 proof
declarations derive lookups after arbitrary prefixes, absence at every index
beyond a collection, exact pending release and established acquisition, and
complete-state promotion/refusal equations. `coupledPromotionAtPrefixes`
quantifies every pending, peer, bank and slot prefix and suffix, both independent
generations, the executor, resource kind/direction, and trust/swarm labels.
It assumes no guard equality. The stale refusal theorem requires only a
generation-mismatch equality; all other operational cases derive their guard
from the concrete state shape. M012 criterion 1 is witnessed.

The process remains a serialized abstract transition system. Runtime routing
and classification (E013, E019, E022), atomicity, receipt authority, actual
termination and cost domination (including E010) are external obligations.
Critical-class scheduling service remains M012 criterion 2 for turn 15.
