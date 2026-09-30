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

Other source units remain individually pending. `source-inventory.json` and
generated coverage report the exact remainder. R01 stays active, and later
packets remain pending until its exit criteria have audited evidence.
