# M012 two-turn closure requirement

Recorded 2026-10-03 from the user's instruction: M012 must be fully closed
within the next two development turns. The R03 execution count was 13 at recording,
so the deadline is the end of R03 turn 15. This document records the requirement;
it does not advance the execution count or claim additional proof coverage.

The four M012 acceptance criteria in [the frozen source ledger](../source-ledger.json)
remain unchanged. At recording, criteria 0 and 3 were witnessed. Criteria 1 and
2 were open in [the proof audit](../proof-audit.json). The turn result sections
below record the later state.

## Turn 14: close stage accounting

Close criterion 1 using the existing coupled process in
[module 88](../proofs/88-coupled-stage-process.mech).

- Prove successful promotion for arbitrary pending, peer, bank and slot
  prefixes and suffixes, without assuming the promotion guard is already true.
- Prove that promotion releases exactly the selected pending generation,
  acquires exactly the selected established slot, preserves the executor,
  and preserves every unselected prefix and suffix.
- Prove complete-state refusal for absent pending, member, bank and slot
  indices, free or stale pending ownership, and occupied destinations at
  arbitrary positions.
- Retain generation consumption, replay refusal, release isolation and
  mixed-trace stage allocation bounds. Add mutation controls for the new
  general operational witnesses.
- Review the evidence against criterion 1 and mark it witnessed only when
  its remaining work is discharged. Keep criterion 2 open for turn 15.

## Turn 15: close critical service and finish M012

Close criterion 2 by proving critical-class service within the finite
whole-process resource allocation, across the required peer and swarm scope.

- State concrete workload, eligibility, scheduling and cost assumptions.
  Derive the service guarantee from those assumptions and modeled transitions;
  do not use the desired service guarantee itself as a premise.
- Connect the guarantee to the established-resource vector and its composed
  finite allocation. Include critical and bulk work and make runtime scheduler
  conformance a separate external obligation.
- Reject weakening controls that remove a necessary workload or scheduling
  premise, permit bulk work to consume protected critical allocation, or omit
  required process participants from composition.
- Review all four frozen criteria together, refresh catalogue and evidence,
  and run the required integrated validation before marking M012 covered.

## Completion gate

M012 is closed only when all of the following hold:

- Every criterion is witnessed with concrete general proof evidence and no
  remaining model work; the audit is reviewed and scope-complete, and the
  generated inventory reports M012 as covered.
- Positive proofs check with an empty axiom set, all required negative controls
  reject, audit/scope/disposition regressions pass, and catalogue evidence and
  receipts match the checked inputs.
- The original resource dimensions, peer/swarm scope, ownership requirements
  and explicit resident-memory domination boundary remain intact.
- Runtime routing, atomicity, authority, cost domination and scheduler
  conformance remain explicit external obligations. Closing M012 does not
  claim that the repository as a whole is deployment-qualified.
- All changes are staged, as requested by the user.

Additional intermediate models or supporting proof counts do not extend this
deadline. If a required claim cannot be proved, report the exact unresolved
claim and evidence; do not weaken the acceptance criteria or mark M012 closed.

## Turn 14 result

Module 89 discharges criterion 1 using the existing coupled process. Successful
promotion and complete-state refusal now cover arbitrary positions and all
absent indices without assuming the promotion guard. Exact prefix/suffix and
generation effects have mutation controls. Criteria 0, 1 and 3 are witnessed;
criterion 2 remains open. The turn-15 deadline and completion gate are unchanged.
