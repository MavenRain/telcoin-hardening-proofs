# R04 policy, source churn and recovery

R04 turn 1 closes M022 in the sealed source-obligation ledger. Module
[91-authoritative-policy-union.mech](../proofs/91-authoritative-policy-union.mech)
adds 37 general proof declarations and 34 semantic weakening controls. R04
remains active: its other 24 model obligations retain their recorded gaps.
The repository has used 26 of its 50 execution turns. This turn does not change
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
The current census is 12 covered and 71 partial model obligations.

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
requires the expected qualification-blocked exit 2. Its checked receipt is
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

This module queries the current immutable view. A policy snapshot is one
immutable `AuthoritativeUnionPolicy` value. `authoritativeUnionQuery` does not
read the generation counter. The module does not model inbound,
outbound-dial or outbound-established lifecycle gates, receipt provenance or
compare-and-publish races. Those are M023. It also does not discharge M006's
fault isolation, M026's cold-start connectivity, M039's recovery threshold or
M042's reload/removal lifecycle. All 43 external obligations remain open, and
full implementation/deployment qualification remains blocked.

The next R04 work should compose these exact membership views with M023's three
decision points and intervening revisions, then preserve the independent
authentication, fallback, resource and source-lifetime premises.
