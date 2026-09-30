# Source disposition ledger

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
The ledger now contains ten model and sixteen external obligations. No theorem
has been credited or model obligation closed: exact witness/assumption auditing
remains R02 work, and external evidence remains outstanding.

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

Other source units remain individually pending. `source-inventory.json` and
generated coverage report the exact remainder. R01 remains active after two of
its five planned turns, with no exit criterion closed. Later packets remain
pending until its exit criteria have audited evidence.
