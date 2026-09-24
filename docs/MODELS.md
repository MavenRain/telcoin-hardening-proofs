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

## Negative controls

The checker rejects 200 invalid variants: three direct checks of equality,
ordering and termination, plus 197 semantic mutations. Mutations exercise such
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

Passing these controls tests that the definitions constrain the proof terms.
It does not prove the checker sound, the Rust implementation refined, or the
deployment qualified. `make qualify` therefore continues to reject completion.
