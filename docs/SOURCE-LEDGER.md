# Source disposition ledger
R01 now seals all 1,383 source dispositions and the 83 model/43 external
obligations in [proof-scope.json](../proof-scope.json). See the
[closure audit](../docs/R01-CLOSURE.md) and
[checked receipt](../evidence/r01-closure-check.json). Earlier batch receipts
record their historical snapshots. R02 must still audit exact theorem witnesses;
implementation and deployment evidence remains outstanding.



`source-ledger.json` is the R01 audit record for the pinned Markdown source
units. Run `make dispositions` to validate its links and `make
disposition-regression` to exercise weakening controls. `python3 -I
tools/dispositions.py --require-complete` exits 2 while any unit remains pending.
This command checks source dispositions; proof-package and full implementation
qualification still require their own evidence.

Every unit retains its exact source path, line range and text hash from the
inventory. The manifest hash pins the complete snapshot. Unit IDs follow the
manifest's inventory order. A changed snapshot requires an explicit new audit
baseline. The checker rejects missing, duplicated, reordered or changed units.

Each unit has one disposition:

- `pending`: the unit has not been fully audited. It grants no obligation or
  reconciliation credit. A rationale can record the outstanding question.
- `context`: a reviewed heading, locator or non-normative passage. Its rationale
  explains why it adds no obligation.
- `obligation`: one or more explicit model or external obligations consume the
  normative content. Several obligations can decompose a compound paragraph,
  and a mixed paragraph can reference both kinds.
- `superseded`: a reviewed original requirement is replaced by cited revised
  units. Its rationale explains the change. All targets must have reviewed
  normative dispositions, and reconciliation cycles are rejected.

An original normative unit must reconcile to reviewed modified-plan units,
which must retain its obligation IDs, directly or through their replacements.
Every reconciliation target must be a reviewed modified-plan unit.
The `reconciles` list records retained requirements as well as replacements;
the disposition and rationale distinguish them. A heading or pending unit
cannot serve as the replacement for a requirement.

Obligations have fixed IDs (`M` for model, `E` for external), a workstream,
an R03-R08 closure assignment, a property, required scope, acceptance criteria
and required evidence. Each is referenced by at least one source unit. Existing
atomic claims can be listed as `candidate_atoms` for model obligations only.
Candidates receive no proof credit here. R02 must audit exact theorem statements
and assumptions before assigning model witnesses. External obligations need
actual implementation, measurement or operator evidence.

The inventory derives its source-disposition completeness from the validated
ledger. Rationales remain semantic audit evidence: the checker verifies pins,
exhaustive indexing, link integrity and replacement structure; it cannot decide
whether a prose requirement was decomposed correctly. An exhaustive reviewed
ledger and the atomic-obligation audit are both required to close R01. Existing
atomic model coverage and full qualification remain incomplete.

## First audit batch

The initial batch covers the modified T3 maintenance section and selected
original T03 goals. E001-E007 retain source provenance, advisory matching,
update targets, ownership, release procedure, compatibility and extension of
the receipt as external requirements. The original no-op dry-run closure is
reconciled to the modified requirement to exercise the first real patch.
The original ten-peer compatibility exercise remains pending because its
relationship to the modified topology-exercise exclusion needs a separate
scope audit. No model requirement is reclassified by this batch.

## T1 and T4 audit batch

The second R01 execution turn audits every unit in the original T01 and T04
drafts, together with their revised T2a, A1, T1a, T2b, T1b, T4a and T4b backlog
sections and selected common rules, decisions and acceptance cases. This adds
186 audited units, bringing the total to 198 of 1,383; 1,185 remain pending.
Source text, ranges and hashes are unchanged.

The ten model obligations are retained as model work:

| ID | Required property | Closure packet |
|---|---|---|
| M001 | Pre-accept Retry and separation of reachability from authenticated privilege. | R03 |
| M002 | Bounded pre-validation queues, transient state and work on every decision path. | R03 |
| M003 | Validated source attribution and protection against spoofed privileged-quota consumption. | R03 |
| M004 | Finite total pending occupancy. | R03 |
| M005 | Reservation-owned cleanup, with no duplicate release or unowned refund. | R03 |
| M006 | Authorization fallback that retains authentication and resource invariants. | R04 |
| M007 | Whole-process composition across swarms, sources and prefixes. | R03 |
| M008 | Bounded polling, preserved wakeups and conditional command/timer/critical service. | R06 |
| M009 | Bounded source bookkeeping and preservation of protected security state. | R03 |
| M010 | Conditional honest connection opportunity under explicit quota/load/fairness premises. | R06 |

E008-E016 separately retain transport implementation and token tests, bounded
observations, hardware/configuration qualification, stock-release fixtures,
effective directional deadlines, pending-accounting refinement, the source
quota contract, a conditional receive-buffer knob and runtime fallback tests.
At the end of this batch, the ledger contained ten model and sixteen external
obligations. No theorem has been credited or model obligation closed: exact
witness/assumption auditing remains R02 work, and external evidence remains
outstanding.

Reconciliations preserve the original model requirements while recording the
modified plan's changes to experimental acceptance. Historical collapse rates
do not become production thresholds; M1a uses a declared below-saturation
real-hardware envelope. M4a/M4b replace standalone old-main and devnet experiments
with baseline, parameter selection and candidate regression. The original
unconditional zero-refusal guards are replaced by recorded D04 reconnect
failure/time bounds. T4b makes validated attribution a launch requirement,
rather than leaving it conditional on a later occupancy comparison. These
changes follow the pinned crosswalk and reviewed replacement clauses; they do
not establish candidate runtime safety or deployment qualification.

At the end of this batch, 1,185 source units remained pending and R01 was
active after two of its five planned turns. No exit criterion was closed,
and later packets remained pending.

## T6 and T7 audit batch

The third R01 execution turn audits all 99 units in the original T06 and T07
drafts, their revised T6/M1b/T7-T12 tasks, and selected crosswalk and acceptance
clauses. It adds 128 audited units, bringing the total to 326 of 1,383:
178 context, 131 obligation, and 17 superseded. 1,057 units remain pending.
All source bytes, ranges, hashes, and existing obligations are retained.

M008 now explicitly separates returning control to the runtime from serving
the oldest command and relevant timers. Its command-age and service claims
need stated queue/load, work-cost, and scheduler premises. M011 retains finite
active-handshake and waiting-work capacities when an accept or endpoint change
removes serialization, including whole-process composition. Its closure
assignment is R03. No theorem witness or candidate atom is credited here.

| ID | Required external evidence | Closure packet |
|---|---|---|
| E017 | Focused and integrated command/timer progress, bounded observations, recorded stall reproduction, and honest-path regressions on every incoming outcome. | R08 |
| E018 | Versioned bottleneck attribution on representative hardware, honest reconnect distributions, whole-process comparisons, and separate T7/T12 decisions. | R08 |
| E019 | Conditional selected restructuring, explicit runtime concurrency bounds, expanded maintenance scope, routing/loss/restart tests, and affected qualification/interoperability regressions. | R08 |

The original unconditional zero-refusal ten-member reconnect guard is replaced
by D04 failure/time bounds for the supported honest population and topology.
Historical container-bridge rate bands cannot select production thresholds.
Shared M1a/M1b evidence replaces standalone historical-host closure recipes;
honest-path measurements and below-saturation scope remain required. An
outer-loop yield does not establish progress on a path that never reaches it,
and moving accepts to another task does not establish reduced lock contention.
Removing serialization requires an explicit concurrency bound.

The joint revised T7/T12 task retains conditional socket routing, loss, restart,
and honest-traffic requirements. The original T12 draft remains pending.
Investigation, selected implementation, host-only changes, and a no-change
decision retain separate outcome labels. A failed required qualification result
still requires remediation and a passing subsequent evaluation.

At the end of this batch, the ledger contained eleven model and nineteen
external obligations. R01 was active after three of its five planned turns.
No exit criterion was closed, and later packets remained pending. Model checking
does not establish runtime refinement or deployment qualification.

## T2 and T5 audit batch

The fourth R01 execution turn audits every source unit in the original T02 and
T05 drafts and the revised T5 task, re-audits selected revised T2b clauses, and
audits selected resource, decision, crosswalk and regression clauses. It adds
131 audited units, bringing the total
to 457 of 1,383: 255 context, 176 obligation and 26 superseded. 926 units remain
pending. Source bytes, ranges, hashes and every existing obligation are retained.

E011 now explicitly retains negotiated-group, deadline, baseline-topology and
lane-cost observations for the required old/current release pairs. E020 records
the real-listener Retry integration matrix, including controlled spoofing,
token edges, policy changes and progress on paths that never reach the outer
event loop. Token replay expectations follow the resolved protocol semantics.
The historical unconditional-accept assertion is replaced by the candidate's
intended behavior; honest reconnect results use declared D02/D04 scope and bounds.

M012 requires established-resource grant/release accounting and composition,
including trusted or exempt peers, every swarm and distinct resource dimensions.
Receive credit is distinguished from resident bytes; concrete memory/task bounds
need explicit cost domination. Admission and retention trust do not remove hard
budgets or authorize bulk traffic to consume all critical-message service.

E021 requires calibrated concurrent occupancy, idle/data RSS comparisons with
uncertainty, window/catch-up sweeps and measurement provenance. Cumulative node
connection counters, dropped requests invisible to upper layers and old structure
sizes cannot establish the corresponding concurrent or resident resource bounds.
Instrumented dependencies retain tracked maintenance evidence. E022 requires the
D02-D04 whole-process derivation and passing M3b honest/hostile regressions, with
observable shedding and selected catch-up, vote/epoch-record and persistence bounds.
The original unconditional absence of a capacity warning is reconciled to these
observable, selected service guarantees. Lower constants alone do not close T5.

At the end of this batch, the ledger contained twelve model and twenty-two
external obligations. M012 is assigned to R03; E020-E022 require external
evidence in R08. No theorem witness or candidate atom is assigned here. R01 was
active after four of its five planned turns. The fifth turn closed source
disposition and claim decomposition. See [R01 source scope closure](R01-CLOSURE.md).
Full qualification remains incomplete, and later packets remain pending.
