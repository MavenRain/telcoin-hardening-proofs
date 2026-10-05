# R04 policy, source churn and recovery

R04 turn 3 closes M024 in the sealed source-obligation ledger. Module
[93-independent-bounded-privileges.mech](../proofs/93-independent-bounded-privileges.mech)
adds 38 proof declarations and 40 semantic weakening controls. M022 and M023 were
closed in turns 1 and 2. R04 remains active: its other 22 model obligations retain
their recorded gaps. The repository has used 28 of its 50 execution turns.
This turn does not change
the sealed scope, packet allocations or external-obligation boundary. R02 and
R03 used 12 turns more than planned. This is two more than the ten-turn
reserve. The R04 to R10 allocations still project 52 of 50 turns. The owner
must revise them ([roadmap](ROADMAP.md) rule 6).

## Authoritative membership construction

`CommitteePolicyUnion` retains five separate finite membership vectors:
previous, current and next committee identities, configured trusted identities,
and bootstrap identities. For every identity index, `committeeUnionMember`
returns their Boolean union. This uses disjunction, so overlap neither changes
eligibility nor requires a peer to belong to every source. Empty membership
and absent workers grant no membership.

`AuthoritativeUnionPolicy` has distinct validator, hub and observer views. These
are the peer-to-peer node roles in the source plan. Submit fronts and public RPC
are HTTPS services and do not introduce peer-to-peer policy roles here. Each
view has its own profile, primary union and a finite list of worker unions.
`NodePolicySwarm` selects the primary or a worker at any natural-number index.

Every role initially uses Open, including validators. An authorized operator
configuration can select Closed or Grace for one role. Closed admission equals
authenticated identity AND membership in exactly the five-source union for the
selected role and swarm. A verified listed identity is admitted; an absent or
unverified identity is refused. Open and Grace retain the authentication gate
while allowing authenticated identities independently of membership.

## Updates and trace composition

A correctly verified roster update replaces the selected role/swarm union,
preserves its requested profile and every other role, and advances the policy
generation. Primary updates preserve every worker. Worker updates preserve the
primary. At an existing worker index, exact prefix/suffix replacement preserves
every unrelated worker. An authorized update may extend the finite worker list.
The extension keeps every existing worker. Every other new index, before or
after the target, has the empty union. This is a configuration model, with no
claim about an implementation's allocation or resize cost.

An unverified update preserves the complete policy, including generation,
profiles and all five membership sources at every role and swarm. Any finite
trace of provisional updates is likewise a complete-state no-op.

Mixed traces execute explicit roster and operator-profile changes. After any
finite trace, the current query still requires authenticated identity. If the
selected final profile is Closed, it uses exactly the final selected union.
Singleton trace proofs also check that verified updates and profile changes
actually execute, rather than making an invariant vacuous by dropping events.
A step proof fixes the execution order. A non-empty trace applies its first
change and then runs the rest on the result. The two mixed-trace proofs are
per-state statements at the final state. They do not relate the final policy
to the individual events.

## Source and witness audit

The sealed M022 property and required scope remain unchanged in
[source-ledger.json](../source-ledger.json). The construction is required by
the modified plan, especially lines 21, 27, 65 and 121, and the reconciled A5
unit U1168. [proof-audit.json](../proof-audit.json) retains the earlier flat-list
witnesses with their local limitations and adds the new exact statements,
premises, scope classifications and controls. Both M022 criteria are witnessed.
The turn-1 census was 12 covered and 71 partial model obligations.

| Ledger criterion | Principal general witnesses (the audit records the complete witness list of each criterion) |
|---|---|
| 0: Closed-profile admission uses the documented previous/current/next committee, trusted and bootstrap union. | `committeeUnionExactMembership`, `authoritativeClosedUsesExactUnion`, `authoritativeClosedUnlistedRefused`, `authoritativeClosedVerifiedMemberAdmitted`, `everyRoleDefaultsOpen`, `everyDefaultSwarmUsesOpen` |
| 1: General witnesses quantify over the admissible states and transitions in the required scope; conditional premises and failure branches remain explicit. | `verifiedCommitteeUpdateSelectsExactUnion`, `verifiedCommitteeUpdateKeepsProfile`, `verifiedCommitteeUpdateKeepsOtherRoles`, `workerReplacementKeepsPrefixAndSuffix`, `paddedWorkerUnionIsEmpty`, `workerExtensionKeepsExistingWorkers`, `workerBeyondExtensionIsEmpty`, `unverifiedCommitteeUpdateIsNoOp`, `everyProvisionalUnionTraceIsNoOp`, `mixedClosedChangesUseExactUnion`, `mixedUnionChangesRequireIdentity` |

All five omission controls target the membership construction. Other controls
replace union with intersection, misroute roles or swarms, overwrite unrelated
views/workers, skip authentication, force Open, retain a stale generation, admit
unverified updates, discard trace events or run a trace in reverse order. Two
controls give a padded or extra worker index the incoming union. The checker
requires type mismatch rejection for these controls; parser failures and
crashes do not count.

## Validation and boundary

The combined full gate is `python3 -I tools/check_gate.py --jobs 4`. It runs
`tools/check.py --require-complete --jobs 4`, checks the complete corpus and
requires the expected qualification-blocked exit 2. Its turn-1 checked receipt is
[r04-authoritative-policy-union-check.json](../evidence/r04-authoritative-policy-union-check.json):
74 modules, 1478 explicit proof declarations, empty axiom disclosure and 1388
rejected negative checks, including all 34 new controls. The disposition,
scope, witness-audit and qualification-gate regressions also pass.

Identity indices faithfully map runtime network identities to vector entries.
The verification flag correctly classifies all incoming membership sources,
including trusted/bootstrap configuration. The initial policy contains only
such verified inputs. Operator-profile changes are authorized configuration
events. These are explicit model premises, not cryptographic or runtime proofs.
E029 retains runtime policy/record validation and projection obligations.
E030 retains launch deployment qualification.

Module 91 queries the current immutable view. A policy snapshot is one
immutable `AuthoritativeUnionPolicy` value. `authoritativeUnionQuery` does not
read the generation counter. Module 91 does not model inbound,
outbound-dial or outbound-established lifecycle gates; module 92 adds them in
turn 2. E029 retains receipt provenance and compare-and-publish races. Module 91
also does not discharge M006's
fault isolation, M026's cold-start connectivity, M039's recovery threshold or
M042's reload/removal lifecycle. All 43 external obligations remain open, and
full implementation/deployment qualification remains blocked.

## Lifecycle decision revisions (turn 2)

Module 92 implements distinct `InboundUnionDecision`, `OutboundUnionDialDecision`
and `OutboundUnionEstablishedDecision` result types. Inbound admission and
outbound dialing query the current immutable authority selected by node role
and swarm. An approved dial carries its generation, role, swarm and identity.
Establishment first checks all four fields against the current authority and
query context, then independently reruns the current authentication and policy
query. Every refusal branch produces an explicit refusal result.

`allUnionLifecyclePointsCheckCurrent` relates all three implementations to the
same current authority for every role and primary/arbitrary-index worker swarm.
Its established branch uses a supplied current-context approved receipt. The
Closed, Open and Grace theorems retain exact union membership and independent
authentication as appropriate. Open/Grace allow authenticated nonmembers;
neither fallback authorizes an unauthenticated identity or a stale receipt.
Generation, role, swarm and identity mismatch theorems cover arbitrary receipt
fields. The worker comparison uses the complete natural-number index.

`unionChangesGeneration` proves the exact revision count of any finite mixed
roster/profile trace. Verified roster and authorized profile changes each
advance generation. Provisional roster changes leave it unchanged. After an
effective revision and any following mixed trace, a previously captured receipt
remains stale and cannot establish. This includes revisions to another role or
swarm, deliberately using conservative global invalidation.

`runUnionOutboundExchange` is an executable dial/establish composition. It dials
after an arbitrary prefix, then establishes after the intervening trace using
separate authentication inputs. Its ordering theorem pins both policy values
and inputs. `unionOutboundExchangeAfterEffectiveChangesRefused` refuses the
actual dial result for every intervening trace that holds a verified roster
update or an authorized profile change at any position, for both dial branches.
`unionOutboundExchangeAfterVerifiedUpdateRefused` is the first-event case.
`freshUnionDialCanEstablish` proves a fresh allowed authenticated dial succeeds,
so the lifecycle is not always refusing.

Both sealed M023 criteria are witnessed by 35 new audited statements. The older
module-33 witnesses retain their supplied-snapshot limitations. The turn-2
census was 13 covered and 70 partial model obligations. The 44 declarations
include supporting equality and selection lemmas; those do not independently
receive source-obligation closure credit. The 32 new controls remove stamp
checks, corrupt captured receipt fields, alias roles/workers, query the default
policy or a wrong role or swarm, bypass authentication or
policy, drop successful branches, grant refusals, reorder/drop intervening
events, reuse dial authentication and miscount revisions. Every control must
produce a type mismatch; parser errors and crashes do not count.

The full qualification guard and checked receipt
[r04-policy-lifecycle-revisions-check.json](../evidence/r04-policy-lifecycle-revisions-check.json)
record 75 modules, 1522 proof declarations, no disclosed axioms and 1420 rejected
negative checks. Disposition, scope and witness-audit regressions also pass.

Each decision atomically receives its current immutable authority in the model's
ordered execution. Runtime authority capture and publication linearization are
E029. Authentication and source-verification flags are correctly classified
current judgments; profile changes are authorized operator events. Generations
are unbounded natural numbers. Runtime wrapping, persistence and rollback
refinement remain external. An approved dial constructor is not a receipt
provenance certificate; E029 retains runtime receipt provenance. Independent
bounded privileges and live-connection sweeps remain M024/M040. Fault isolation,
source/resource attribution, expiry and reload/removal keep their separate
ledger gaps. All 43 external obligations remain open.

Turn 3 closes M024 below. The next R04 work is M025 trusted startup
dialing/lifetime redial, preserving authentication, fallback, finite retry
budgets and explicit fair timer/transport premises.

## Independent bounded privileges (turn 3)

Module 93 represents admission, retention/mesh preference and exemption from
load-induced penalties as three separate finite recipient lists with independent
capacities. Truncation bounds each effective list. An entry contains an arbitrary
symbolic identity, so capacity does not restrict the numeric identity range.
Duplicate entries consume capacity. Every query also checks current authentication
and the current authoritative union of the selected role/swarm. This union contains
the previous, current and next committee, configured trusted and bootstrap identities.
Ordinary Open/Grace admission remains the existing authority contract.

An authorized allocation event replaces exactly one class and advances the
authority generation. All six cross-class equalities quantify over arbitrary
roles, primary/worker swarms, identities, authentication judgments and allocations:
the other two effective privileges are unchanged. An unauthorized allocation
event leaves the entire state unchanged. Mixed traces also execute the existing
authoritative roster/profile transitions. They retain the allocation lists while
rechecking current membership, so removing membership revokes effective privileges
even when allocation entries remain. Positive head-membership and successful-query
witnesses rule out an always-refuse model.

After every finite mixed revision trace, allocations remain finite and
unauthenticated identities receive no privilege or privileged service. Load
exemption suppresses only a load-pressure ban. Genuine protocol violations remain
bannable. Every successful service request returns the smaller of demand and its
CPU, memory or bulk service-turn limit; refusal returns zero. Resource-coordinate
witnesses rule out aliasing one limit to another. These limits are previously
reserved allocations. Aggregate reservation and runtime cost domination keep
their M012/E022 boundary; this model does not mint budgets or prove cumulative
uncharged service.

The source audit covers the trust split in U0918/U1166, authenticated current-policy
updates in U0913/U0941/U1080/U1323, bounded trusted traffic and genuine violations
in U1062/U1174/U1291, and the same privilege boundary for the role/QoS clauses
U1210/U1274. Broader source clauses retain their separately assigned obligations.
Both M024 criteria are witnessed by 38 new audited general statements; the older
module-30 scalar witnesses retain their narrower scope. The census is now
14 covered and 69 partial model obligations.

The 40 new semantic controls weaken class selection, allocation truncation,
membership lookup, authorization, authentication, current role/swarm authority,
revision advancement, trace execution, load-only exemptions, resource-coordinate
selection and successful/refused service branches. Every one must fail with a
type mismatch; parser failures and crashes do not count. The full qualification
guard and [checked receipt](../evidence/r04-independent-bounded-privileges-check.json)
record 76 modules, 1560 proof declarations, no disclosed axioms and 1460 rejected
negative checks. Disposition, scope and witness-audit regressions also pass.

Atomic authority capture, identity mapping, verification and authorization remain
E029. Runtime enforcement and cost domination remain E022. Generations are
unbounded naturals; wrapping, persistence and rollback remain external. Genuine
protocol violations and load causes are correctly classified judgments. All 43
external obligations remain open. M025 startup and lifetime redial is next;
M040 live sweeps and the other policy/source/resource gaps remain unchanged.
