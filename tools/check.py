#!/usr/bin/env python3
"""Check the ordered mechanism-lang proof sources and their axiom disclosure."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


MUTATIONS = [
    ("retry_bypass", "| unvalidated => retry", "| unvalidated => accept"),
    ("poll_over_budget", "| event outcome rest => next (pollWork remaining rest)",
     "| event outcome rest => next (next (pollWork remaining rest))"),
    ("release_reoccupies_slot", "| slot state rest => slot off rest)", "| slot state rest => slot on rest)"),
    ("authentication_bypass", "both authenticated (memberAllowed (effectiveProfile validPolicy requested) member)",
     "memberAllowed (effectiveProfile validPolicy requested) member"),
    ("trusted_violation_exempt", "| protocolViolation => on", "| protocolViolation => off"),
    ("batch_admitted", "| on => batchRefused", "| on => forwarded"),
    ("overload_demotes", "| http429 => failures", "| http429 => next failures"),
    ("early_endpoint_retirement", "both converged newPathPassed", "newPathPassed"),
    ("firewall_omits_current", "either current future", "future"),
    ("model_claims_implementation", "checkItem implementationLinked (checkItem numericEnvelopeSpecified",
     "checkItem on (checkItem numericEnvelopeSpecified"),
    ("stale_generation_releases", "releaseDecision generation (sameCount token generation)",
     "releaseDecision generation on"),
    ("generation_not_advanced", "| on => freeLease (next generation)", "| on => freeLease generation"),
    ("unowned_completion_refunds", "| noOwnedLease => lease", "| noOwnedLease => freeLease zero"),
    ("terminal_cleanup_skipped", "| ownedGeneration generation => releaseOwned generation lease",
     "| ownedGeneration generation => lease"),
    ("pending_pool_grows", "| reserveAt index => updateLease index reserveLease pool",
     "| reserveAt index => leaseCell (heldLease zero) (updateLease index reserveLease pool)"),
    ("handshake_credit_not_debited", "| validated => predecessor available", "| validated => available"),
    ("refill_exceeds_capacity", "| trustedClockCredit credits => boundedWork capacity (add available credits)",
     "| trustedClockCredit credits => add available credits"),
    ("eviction_mints_credit", "| sourceEvicted identity => available", "| sourceEvicted identity => capacity"),
    ("forged_clock_mints_credit", "| claimedClockCredit credits => available",
     "| claimedClockCredit credits => add available credits"),
    ("fallback_mints_credit", "| admissionPolicyChanged valid => available",
     "| admissionPolicyChanged valid => capacity"),
    ("clock_overissues_credit", "| timeTick rest => rateEvent (trustedClockCredit rate) (timedEvents rest rate)",
     "| timeTick rest => rateEvent (trustedClockCredit (next rate)) (timedEvents rest rate)"),
    ("poll_discards_backlog", "| zero => events\n    | next remaining =>",
     "| zero => noEvents\n    | next remaining =>"),
    ("poll_loses_wakeup", "| event outcome rest => on", "| event outcome rest => off"),
    ("critical_service_skipped", "| completedServiceRound => criticalTurn state",
     "| completedServiceRound => state"),
    ("pending_cost_omitted", "add (multiply queued queueCost)\n      (add (multiply pending pendingCost) (multiply established establishedCost))",
     "add (multiply queued queueCost) (multiply established establishedCost)"),
    ("record_epoch_bypassed", "recordDecision (both verified (sameCount recordEpoch currentEpoch)) index records",
     "recordDecision verified index records"),
    ("record_authentication_bypassed", "recordDecision (both verified (sameCount recordEpoch currentEpoch)) index records",
     "recordDecision (sameCount recordEpoch currentEpoch) index records"),
    ("old_epoch_resolution_retained", "| slot present rest => slot off (clearCommitteeRecords rest)",
     "| slot present rest => slot present (clearCommitteeRecords rest)"),
    ("duplicate_record_adds_member", "| slot present rest => slot on rest)",
     "| slot present rest => slot on (slot present rest))"),
    ("stale_policy_action_published", "applyPolicyDecision (sameCount observed (policyGeneration current))\n      (planPolicyUpdate action (policyView current)) current",
     "applyPolicyDecision on\n      (planPolicyUpdate action (policyView current)) current"),
    ("policy_generation_not_advanced", "| replacePolicyCore replacement => versionedPolicy (next (policyGeneration current)) replacement",
     "| replacePolicyCore replacement => versionedPolicy (policyGeneration current) replacement"),
    ("faulty_policy_remains_valid", "| faultyPolicy fault => off", "| faultyPolicy fault => on"),
    ("replacement_reuses_policy_resolution", "fun (config : PolicyConfig) => policyCore config (clearCommitteeRecords (policyRoster config))",
     "fun (config : PolicyConfig) => policyCore config (policyRoster config)"),
    ("policy_fault_keeps_resolution", "(policyCore (faultyConfig fault (coreConfig core)) (clearCommitteeRecords (policyRecords core)))",
     "(policyCore (faultyConfig fault (coreConfig core)) (policyRecords core))"),
    ("policy_record_auth_bypassed", "(both verified (sameCount recordEpoch (policyEpoch (coreConfig core)))) index core",
     "(sameCount recordEpoch (policyEpoch (coreConfig core))) index core"),
    ("policy_record_epoch_bypassed", "(both verified (sameCount recordEpoch (policyEpoch (coreConfig core)))) index core",
     "verified index core"),
    ("policy_record_dedup_bypassed", "resolutionIfNew (newPolicyResolution index (policyRecords core))\n      (both verified",
     "resolutionIfNew on\n      (both verified"),
    ("tls_policy_reader_diverges", "| tlsPrefilterConsumer => policyQuery (policyView current) authenticated identity",
     "| tlsPrefilterConsumer => authenticated"),
    ("policy_receipt_generation_bypassed", "both (sameCount capturedGeneration currentGeneration) (both (sameCount capturedEpoch currentEpoch) allowed)",
     "both on (both (sameCount capturedEpoch currentEpoch) allowed)"),
    ("policy_receipt_epoch_bypassed", "both (sameCount capturedGeneration currentGeneration) (both (sameCount capturedEpoch currentEpoch) allowed)",
     "both (sameCount capturedGeneration currentGeneration) allowed"),
    ("policy_receipt_identity_bypassed", "both (sameCount capturedIdentity identity)\n        (receiptDecision",
     "both on\n        (receiptDecision"),
    ("policy_change_refills_credit", "governedState (commitPolicyAction observed action (governedPolicy current))\n        (governedCredits current) (governedPool current)",
     "governedState (commitPolicyAction observed action (governedPolicy current))\n        capacity (governedPool current)"),
    ("policy_change_mutates_pending", "governedState (commitPolicyAction observed action (governedPolicy current))\n        (governedCredits current) (governedPool current)",
     "governedState (commitPolicyAction observed action (governedPolicy current))\n        (governedCredits current) (poolStep (reserveAt zero) (governedPool current))"),
    ("closed_policy_skips_resolution", "| closedProfile => closeIfReady on (next requiredRest) resolved",
     "| closedProfile => closedProfile"),
    ("valid_policy_record_dropped", "| on => replacePolicyCore (policyCore (coreConfig core) (markCommitteeRecord index (policyRecords core)))",
     "| on => retainPolicy"),
    ("source_table_grows", "def rec insertSource : Count -> SourceTable -> SourceTable :=\n  fun (key : Count) (table : SourceTable) =>\n    case table as self in SourceTable return SourceTable with\n    | noSourceSlots => noSourceSlots",
     "def rec insertSource : Count -> SourceTable -> SourceTable :=\n  fun (key : Count) (table : SourceTable) =>\n    case table as self in SourceTable return SourceTable with\n    | noSourceSlots => sourceSlot (trackedSource key sourceClear) noSourceSlots"),
    ("known_source_registered_again", "| off => insertSource key table\n    | on => table",
     "| off => insertSource key table\n    | on => insertSource key table"),
    ("unvalidated_source_registered", "| unvalidated => table\n    | validated => rememberKnownSource",
     "| unvalidated => insertSource key table\n    | validated => rememberKnownSource"),
    ("unvalidated_source_registration_allowed", "| unvalidated => off\n    | validated => either (sourceKnown key table) (sourceHasRoom table)",
     "| unvalidated => on\n    | validated => either (sourceKnown key table) (sourceHasRoom table)"),
    ("full_source_table_accepts_unknown", "| validated => either (sourceKnown key table) (sourceHasRoom table)",
     "| validated => on"),
    ("source_debt_evicted", "| sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef evictMatchingSource",
     "| sourceRateDebt debt => vacantSource\n      | sourceBan => trackedSource key sourceBan\n\ndef evictMatchingSource"),
    ("source_ban_evicted", "| sourceBan => trackedSource key sourceBan\n\ndef evictMatchingSource",
     "| sourceBan => vacantSource\n\ndef evictMatchingSource"),
    ("unrelated_source_evicted", "| off => cell\n    | on => evictSourceCell cell",
     "| off => evictSourceCell cell\n    | on => evictSourceCell cell"),
    ("matching_clear_source_retained", "| off => cell\n    | on => evictSourceCell cell",
     "| off => cell\n    | on => cell"),
    ("source_vacancy_unused", "| vacantSource => sourceSlot (trackedSource key sourceClear) rest",
     "| vacantSource => sourceSlot vacantSource rest"),
    ("source_churn_event_dropped", "| sourceTableThen event rest => runSourceTable rest (sourceTableStep event table)",
     "| sourceTableThen event rest => runSourceTable rest table"),
    ("resident_source_not_known", "| trackedSource resident restriction => either (sameCount key resident) (sourceKnown key rest)",
     "| trackedSource resident restriction => sourceKnown key rest"),
    ("protected_debt_forgotten", "| sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef rec protectedSources",
     "| sourceRateDebt debt => vacantSource\n      | sourceBan => trackedSource key sourceBan\n\ndef rec protectedSources"),
    ("protected_ban_forgotten", "| sourceBan => trackedSource key sourceBan\n\ndef rec protectedSources",
     "| sourceBan => vacantSource\n\ndef rec protectedSources"),
    ("source_vacancy_hidden", "| vacantSource => on", "| vacantSource => sourceHasRoom rest"),
    ("joint_source_evicted", "| sourceDebtAndBan debt => trackedSource key (sourceDebtAndBan debt)\n      | sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef evictMatchingSource",
     "| sourceDebtAndBan debt => vacantSource\n      | sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef evictMatchingSource"),
    ("protected_joint_source_erased", "| sourceDebtAndBan debt => trackedSource key (sourceDebtAndBan debt)\n      | sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef rec protectedSources",
     "| sourceDebtAndBan debt => vacantSource\n      | sourceRateDebt debt => trackedSource key (sourceRateDebt debt)\n      | sourceBan => trackedSource key sourceBan\n\ndef rec protectedSources"),
    ("zero_source_quota_allowed", "| zero => off\n      | next remaining => on)",
     "| zero => on\n      | next remaining => on)"),
    ("available_source_quota_refused", "| zero => off\n      | next remaining => on)",
     "| zero => off\n      | next remaining => off)"),
    ("source_charge_not_counted", "sourceRateDebt (boundedWork capacity (next (sourceDebt restriction)))",
     "sourceRateDebt (boundedWork capacity (sourceDebt restriction))"),
    ("source_quota_bypassed", "| sourceRateDebt debt => sourceQuotaRoom debt capacity",
     "| sourceRateDebt debt => on"),
    ("source_over_quota_allowed", "| next previous =>\n      case capacity as limit in Count return Flag with\n      | zero => off",
     "| next previous =>\n      case capacity as limit in Count return Flag with\n      | zero => on"),
    ("joint_source_ban_bypassed", "| sourceDebtAndBan debt => off\n    | sourceRateDebt debt => sourceQuotaRoom debt capacity",
     "| sourceDebtAndBan debt => sourceQuotaRoom debt capacity\n    | sourceRateDebt debt => sourceQuotaRoom debt capacity"),
    ("source_ban_bypassed", "| sourceBan => off\n\ndef sourceChargeDecision",
     "| sourceBan => sourceQuotaRoom zero capacity\n\ndef sourceChargeDecision"),
    ("unvalidated_source_cell_charged", "| unvalidated => cell\n    | validated =>\n      case cell as entry in SourceCell return SourceCell with",
     "| unvalidated =>\n      (case cell as entry in SourceCell return SourceCell with\n      | vacantSource => vacantSource\n      | trackedSource key restriction => trackedSource key (chargeSourceRestriction capacity restriction))\n    | validated =>\n      case cell as entry in SourceCell return SourceCell with"),
    ("vacant_source_cell_allowed", "| vacantSource => off\n      | trackedSource key restriction => sourceChargeAllowed capacity restriction",
     "| vacantSource => on\n      | trackedSource key restriction => sourceChargeAllowed capacity restriction"),
    ("source_ban_erases_debt", "| sourceRateDebt debt => sourceDebtAndBan debt\n    | sourceBan => sourceBan",
     "| sourceRateDebt debt => sourceBan\n    | sourceBan => sourceBan"),
    ("source_ban_not_installed", "| sourceRateDebt debt => sourceDebtAndBan debt\n    | sourceBan => sourceBan",
     "| sourceRateDebt debt => sourceRateDebt debt\n    | sourceBan => sourceBan"),
    ("claimed_source_expiry_trusted", "| claimedSourceExpiry => restriction", "| claimedSourceExpiry => sourceClear"),
    ("debt_expiry_erases_ban", "| sourceDebtAndBan debt => sourceBan\n      | sourceRateDebt debt => sourceClear",
     "| sourceDebtAndBan debt => sourceClear\n      | sourceRateDebt debt => sourceClear"),
    ("ban_expiry_erases_joint_debt", "| sourceDebtAndBan debt => sourceRateDebt debt\n      | sourceRateDebt debt => sourceRateDebt debt",
     "| sourceDebtAndBan debt => sourceClear\n      | sourceRateDebt debt => sourceRateDebt debt"),
    ("ban_expiry_erases_unbanned_debt", "| sourceDebtAndBan debt => sourceRateDebt debt\n      | sourceRateDebt debt => sourceRateDebt debt",
     "| sourceDebtAndBan debt => sourceRateDebt debt\n      | sourceRateDebt debt => sourceClear"),
    ("expired_source_debt_retained", "| sourceRateDebt debt => sourceClear\n      | sourceBan => sourceBan)",
     "| sourceRateDebt debt => sourceRateDebt debt\n      | sourceBan => sourceBan)"),
    ("expired_source_ban_retained", "| sourceBan => sourceClear\n\ndef claimedSourceExpiryIsNoOp",
     "| sourceBan => sourceBan\n\ndef claimedSourceExpiryIsNoOp"),
    ("source_trace_ban_dropped", "| sourceBanEvent => imposeSourceBan restriction", "| sourceBanEvent => restriction"),
    ("source_trace_unvalidated_charged", "| unvalidated => restriction\n      | validated => chargeSourceRestriction capacity restriction)",
     "| unvalidated => chargeSourceRestriction capacity restriction\n      | validated => chargeSourceRestriction capacity restriction)"),
    ("source_trace_expiry_dropped", "| sourceExpiryEvent expiry => expireSourceRestriction expiry restriction",
     "| sourceExpiryEvent expiry => restriction"),
    ("source_restriction_trace_event_dropped", "| sourceRestrictionThen event rest => runSourceRestrictions rest capacity (sourceRestrictionStep capacity event restriction)",
     "| sourceRestrictionThen event rest => runSourceRestrictions rest capacity restriction"),
    ("refused_source_charge_resets", "| off => restriction", "| off => sourceClear"),
    ("ban_on_clear_source_dropped", "| sourceClear => sourceBan\n    | sourceDebtAndBan debt => sourceDebtAndBan debt",
     "| sourceClear => sourceClear\n    | sourceDebtAndBan debt => sourceDebtAndBan debt"),
    ("debt_expiry_clears_lone_ban", "| sourceBan => sourceBan)", "| sourceBan => sourceClear)"),
    ("source_trace_charge_quota_shifted", "| validated => chargeSourceRestriction capacity restriction)",
     "| validated => chargeSourceRestriction (next capacity) restriction)"),
    ("source_lookup_fabricates_resident", "| noSourceSlots => vacantSource\n    | sourceSlot cell rest =>", "| noSourceSlots => trackedSource zero sourceClear\n    | sourceSlot cell rest =>"),
    ("source_lookup_stops_at_vacancy", "| vacantSource => lookupSource key rest", "| vacantSource => vacantSource"),
    ("source_lookup_ignores_key", "chooseSourceCell (sameCount key resident)", "chooseSourceCell on"),
    ("source_lookup_drops_match", "case hit as selected in Flag return SourceCell with\n    | off => missed\n    | on => matched", "case hit as selected in Flag return SourceCell with\n    | off => missed\n    | on => missed"),
    ("source_table_charge_ignores_validation", "sourceCellChargeAllowed source capacity (lookupSource key table)", "sourceCellChargeAllowed validated capacity (lookupSource key table)"),
    ("source_table_charge_quota_shifted", "sourceCellChargeAllowed source capacity (lookupSource key table)", "sourceCellChargeAllowed source (next capacity) (lookupSource key table)"),
    ("source_restriction_allocates_empty_table", "case table as self in SourceTable return SourceTable with\n    | noSourceSlots => noSourceSlots\n    | sourceSlot cell rest =>\n      case cell as entry in SourceCell return SourceTable with\n      | vacantSource => sourceSlot vacantSource (restrictSource capacity key event rest)", "case table as self in SourceTable return SourceTable with\n    | noSourceSlots => sourceSlot vacantSource noSourceSlots\n    | sourceSlot cell rest =>\n      case cell as entry in SourceCell return SourceTable with\n      | vacantSource => sourceSlot vacantSource (restrictSource capacity key event rest)"),
    ("source_restriction_allocates_vacancy", "| vacantSource => sourceSlot vacantSource (restrictSource capacity key event rest)", "| vacantSource => sourceSlot (trackedSource key sourceClear) (restrictSource capacity key event rest)"),
    ("source_restriction_stops_at_vacancy", "| vacantSource => sourceSlot vacantSource (restrictSource capacity key event rest)", "| vacantSource => sourceSlot vacantSource rest"),
    ("source_restriction_ignores_key", "| trackedSource resident restriction => chooseSourceTable (sameCount key resident)", "| trackedSource resident restriction => chooseSourceTable on"),
    ("source_restriction_drops_update", "| trackedSource resident restriction => chooseSourceTable (sameCount key resident)\n          (sourceSlot (trackedSource resident (sourceRestrictionStep capacity event restriction)) rest)", "| trackedSource resident restriction => chooseSourceTable (sameCount key resident)\n          (sourceSlot (trackedSource resident restriction) rest)"),
    ("source_restriction_updates_duplicate_tail", "| trackedSource resident restriction => chooseSourceTable (sameCount key resident)\n          (sourceSlot (trackedSource resident (sourceRestrictionStep capacity event restriction)) rest)", "| trackedSource resident restriction => chooseSourceTable (sameCount key resident)\n          (sourceSlot (trackedSource resident (sourceRestrictionStep capacity event restriction)) (restrictSource capacity key event rest))"),
    ("source_restriction_drops_tail_search", "case hit as selected in Flag return SourceTable with\n    | off => missed\n    | on => matched", "case hit as selected in Flag return SourceTable with\n    | off => matched\n    | on => matched"),
    ("source_system_drops_churn", "| sourceChurnEvent churn => sourceTableStep churn table", "| sourceChurnEvent churn => table"),
    ("source_system_drops_enforcement", "| sourceEnforceEvent key restriction => restrictSource capacity key restriction table", "| sourceEnforceEvent key restriction => table"),
    ("source_system_enforcement_quota_shifted", "| sourceEnforceEvent key restriction => restrictSource capacity key restriction table", "| sourceEnforceEvent key restriction => restrictSource (next capacity) key restriction table"),
    ("source_system_trace_drops_step", "| sourceSystemThen event rest => runSourceSystem rest capacity (sourceSystemStep capacity event table)", "| sourceSystemThen event rest => runSourceSystem rest capacity table"),
    ("source_system_trace_drops_tail", "| sourceSystemThen event rest => runSourceSystem rest capacity (sourceSystemStep capacity event table)", "| sourceSystemThen event rest => sourceSystemStep capacity event table"),
]


MUTATIONS += [
    ("admission_bypasses_source_validation", "sourceStartDecision (sourceTableChargeAllowed source quota key (admissionSources current))\n      (admissionCredits current)", "sourceStartDecision (sourceTableChargeAllowed validated quota key (admissionSources current))\n      (admissionCredits current)"),
    ("admission_shifts_source_quota", "sourceStartDecision (sourceTableChargeAllowed source quota key (admissionSources current))\n      (admissionCredits current)", "sourceStartDecision (sourceTableChargeAllowed source (next quota) key (admissionSources current))\n      (admissionCredits current)"),
    ("admission_ignores_source_refusal", "| off => refusedSourceStart\n    | on => selectSourceStart credits token", "| off => selectSourceStart credits token\n    | on => selectSourceStart credits token"),
    ("admission_starts_without_credit", "| zero => refusedSourceStart\n    | next remaining =>", "| zero => grantedSourceStart zero\n    | next remaining =>"),
    ("admission_starts_without_lease", "| noOwnedLease => refusedSourceStart", "| noOwnedLease => grantedSourceStart zero"),
    ("admission_missing_slot_fabricates_token", "| emptyLeasePool => noOwnedLease\n      | leaseCell lease rest => reservationToken (tryReserve lease)", "| emptyLeasePool => ownedGeneration zero\n      | leaseCell lease rest => reservationToken (tryReserve lease)"),
    ("admission_held_slot_fabricates_token", "| leaseCell lease rest => reservationToken (tryReserve lease)", "| leaseCell lease rest => ownedGeneration zero"),
    ("admission_slot_lookup_ignores_tail", "| leaseCell lease rest => availableLeaseToken previous rest", "| leaseCell lease rest => availableLeaseToken previous (leaseCell lease rest)"),
    ("admission_refusal_spends_credit", "| refusedSourceStart => current\n    | grantedSourceStart generation => sourceAdmission", "| refusedSourceStart => sourceAdmission (admissionSources current) (predecessor (admissionCredits current)) (admissionPool current)\n    | grantedSourceStart generation => sourceAdmission"),
    ("admission_drops_source_charge", "(restrictSource quota key (sourceChargeEvent validated) (admissionSources current))\n        (predecessor", "(admissionSources current)\n        (predecessor"),
    ("admission_charges_wrong_source", "(restrictSource quota key (sourceChargeEvent validated) (admissionSources current))\n        (predecessor", "(restrictSource quota zero (sourceChargeEvent validated) (admissionSources current))\n        (predecessor"),
    ("admission_drops_global_charge", "(predecessor (admissionCredits current))\n        (poolStep (reserveAt index)", "(admissionCredits current)\n        (poolStep (reserveAt index)"),
    ("admission_drops_pending_reservation", "(poolStep (reserveAt index) (admissionPool current))\n\ndef finishSourceAdmission", "(admissionPool current)\n\ndef finishSourceAdmission"),
    ("admission_reserves_wrong_slot", "(poolStep (reserveAt index) (admissionPool current))\n\ndef finishSourceAdmission", "(poolStep (reserveAt zero) (admissionPool current))\n\ndef finishSourceAdmission"),
    ("admission_receipt_wrong_index", "| grantedSourceStart generation => pendingAdmissionReceipt index generation", "| grantedSourceStart generation => pendingAdmissionReceipt zero generation"),
    ("admission_receipt_wrong_generation", "| grantedSourceStart generation => pendingAdmissionReceipt index generation", "| grantedSourceStart generation => pendingAdmissionReceipt index (next generation)"),
    ("admission_unowned_completion_spends_credit", "| noAdmissionReceipt => current\n    | pendingAdmissionReceipt index generation => sourceAdmission", "| noAdmissionReceipt => sourceAdmission (admissionSources current) (predecessor (admissionCredits current)) (admissionPool current)\n    | pendingAdmissionReceipt index generation => sourceAdmission"),
    ("admission_completion_refills_credit", "| pendingAdmissionReceipt index generation => sourceAdmission\n        (admissionSources current) (admissionCredits current)", "| pendingAdmissionReceipt index generation => sourceAdmission\n        (admissionSources current) (next (admissionCredits current))"),
    ("admission_completion_erases_sources", "| pendingAdmissionReceipt index generation => sourceAdmission\n        (admissionSources current) (admissionCredits current)", "| pendingAdmissionReceipt index generation => sourceAdmission\n        noSourceSlots (admissionCredits current)"),
    ("admission_completion_wrong_slot", "(poolStep (completeAt index (ownedGeneration generation) reason) (admissionPool current))", "(poolStep (completeAt zero (ownedGeneration generation) reason) (admissionPool current))"),
    ("admission_completion_wrong_generation", "(poolStep (completeAt index (ownedGeneration generation) reason) (admissionPool current))", "(poolStep (completeAt index (ownedGeneration (next generation)) reason) (admissionPool current))"),
    ("admission_maintenance_mints_credit", "(admissionCredits current) (admissionPool current)\n    | sourceAdmissionClock issued", "(next (admissionCredits current)) (admissionPool current)\n    | sourceAdmissionClock issued"),
    ("admission_maintenance_erases_pending", "(admissionCredits current) (admissionPool current)\n    | sourceAdmissionClock issued", "(admissionCredits current) emptyLeasePool\n    | sourceAdmissionClock issued"),
    ("admission_clock_ignores_capacity", "(creditsAfter capacity (admissionCredits current) (trustedClockCredit issued)) (admissionPool current)", "(add (admissionCredits current) issued) (admissionPool current)"),
    ("admission_clock_erases_sources", "| sourceAdmissionClock issued => sourceAdmission (admissionSources current)", "| sourceAdmissionClock issued => sourceAdmission noSourceSlots"),
    ("admission_drops_source_ban", "| maintainSourceBan key => sourceEnforceEvent key sourceBanEvent", "| maintainSourceBan key => sourceEnforceEvent key (sourceExpiryEvent claimedSourceExpiry)"),
    ("admission_trusts_claimed_expiry", "| maintainSourceExpiry key expiry => sourceEnforceEvent key (sourceExpiryEvent expiry)", "| maintainSourceExpiry key expiry => sourceEnforceEvent key (sourceExpiryEvent trustedDebtExpiry)"),
    ("admission_drops_source_churn", "| maintainSourceChurn churn => sourceChurnEvent churn", "| maintainSourceChurn churn => sourceEnforceEvent zero (sourceExpiryEvent claimedSourceExpiry)"),
    ("admission_trace_drops_event", "| sourceAdmissionsThen event rest => runSourceAdmissions rest quota capacity (sourceAdmissionStep quota capacity event current)", "| sourceAdmissionsThen event rest => runSourceAdmissions rest quota capacity current"),
    ("admission_refusal_emits_receipt", "| refusedSourceStart => noAdmissionReceipt", "| refusedSourceStart => pendingAdmissionReceipt index zero"),
    ("admission_distant_slot_fabricates_token", "| emptyLeasePool => noOwnedLease\n      | leaseCell lease rest => availableLeaseToken previous rest", "| emptyLeasePool => ownedGeneration zero\n      | leaseCell lease rest => availableLeaseToken previous rest"),
    ("admission_ban_wrong_key", "| maintainSourceBan key => sourceEnforceEvent key sourceBanEvent", "| maintainSourceBan key => sourceEnforceEvent zero sourceBanEvent"),
]


MUTATIONS += [
    ("admission_rate_success_not_counted", "| pendingAdmissionReceipt index generation => next zero", "| pendingAdmissionReceipt index generation => zero"),
    ("admission_rate_refusal_counted", "| noAdmissionReceipt => zero", "| noAdmissionReceipt => next zero"),
    ("admission_rate_clock_issuance_hidden", "| sourceAdmissionClock issued => issued", "| sourceAdmissionClock issued => zero"),
    ("admission_rate_issuance_tail_dropped", "add (sourceAdmissionIssuedNow event) (sourceAdmissionIssuedTotal rest)", "sourceAdmissionIssuedNow event"),
    ("admission_rate_count_tail_dropped", "(sourceAdmissionStarts rest quota capacity (sourceAdmissionStep quota capacity event current))", "zero"),
    ("admission_rate_count_uses_old_state", "(sourceAdmissionStarts rest quota capacity (sourceAdmissionStep quota capacity event current))", "(sourceAdmissionStarts rest quota capacity current)"),
    ("admission_rate_first_start_omitted", "add (admissionReceiptCount (admissionAttemptReceipt quota event current))", "add zero"),
    ("admission_rate_attempt_validation_changed", "(sourceAdmissionAttempt source swarm key index) (timedSourceAdmissions rest rate)", "(sourceAdmissionAttempt validated swarm key index) (timedSourceAdmissions rest rate)"),
    ("admission_rate_attempt_wrong_key", "(sourceAdmissionAttempt source swarm key index) (timedSourceAdmissions rest rate)", "(sourceAdmissionAttempt source swarm zero index) (timedSourceAdmissions rest rate)"),
    ("admission_rate_attempt_wrong_slot", "(sourceAdmissionAttempt source swarm key index) (timedSourceAdmissions rest rate)", "(sourceAdmissionAttempt source swarm key zero) (timedSourceAdmissions rest rate)"),
    ("admission_rate_maintenance_dropped", "sourceAdmissionsThen\n        (sourceAdmissionMaintenance maintenance) (timedSourceAdmissions rest rate)", "timedSourceAdmissions rest rate"),
    ("admission_rate_completion_dropped", "sourceAdmissionsThen\n        (sourceAdmissionFinish receipt reason) (timedSourceAdmissions rest rate)", "timedSourceAdmissions rest rate"),
    ("admission_rate_tick_overissues", "| timedAdmissionTick rest => sourceAdmissionsThen (sourceAdmissionClock rate) (timedSourceAdmissions rest rate)", "| timedAdmissionTick rest => sourceAdmissionsThen (sourceAdmissionClock (next rate)) (timedSourceAdmissions rest rate)"),
    ("admission_rate_tick_dropped", "| timedAdmissionTick rest => sourceAdmissionsThen (sourceAdmissionClock rate) (timedSourceAdmissions rest rate)", "| timedAdmissionTick rest => timedSourceAdmissions rest rate"),
    ("admission_rate_claimed_tick_issues", "| timedAdmissionClaimedTick claimed rest => timedSourceAdmissions rest rate", "| timedAdmissionClaimedTick claimed rest => sourceAdmissionsThen (sourceAdmissionClock claimed) (timedSourceAdmissions rest rate)"),
    ("admission_rate_claimed_tick_counts", "| timedAdmissionClaimedTick claimed rest => sourceAdmissionTrustedTicks rest", "| timedAdmissionClaimedTick claimed rest => next (sourceAdmissionTrustedTicks rest)"),
    ("admission_rate_trusted_tick_not_counted", "| timedAdmissionTick rest => next (sourceAdmissionTrustedTicks rest)", "| timedAdmissionTick rest => sourceAdmissionTrustedTicks rest"),
    ("admission_rate_attempt_advances_time", "| timedAdmissionAttempt source swarm key index rest => sourceAdmissionTrustedTicks rest", "| timedAdmissionAttempt source swarm key index rest => next (sourceAdmissionTrustedTicks rest)"),
    ("admission_rate_maintenance_advances_time", "| timedAdmissionMaintenance maintenance rest => sourceAdmissionTrustedTicks rest", "| timedAdmissionMaintenance maintenance rest => next (sourceAdmissionTrustedTicks rest)"),
    ("admission_rate_completion_advances_time", "| timedAdmissionFinish receipt reason rest => sourceAdmissionTrustedTicks rest", "| timedAdmissionFinish receipt reason rest => next (sourceAdmissionTrustedTicks rest)"),
    ("admission_rate_attempt_issues_credit", "| sourceAdmissionAttempt source swarm key index => zero", "| sourceAdmissionAttempt source swarm key index => next zero"),
    ("admission_rate_maintenance_issues_credit", "| sourceAdmissionMaintenance maintenance => zero", "| sourceAdmissionMaintenance maintenance => next zero"),
    ("admission_rate_completion_issues_credit", "| sourceAdmissionFinish receipt reason => zero", "| sourceAdmissionFinish receipt reason => next zero"),
    ("admission_rate_erasure_appends_refill", "| timedAdmissionsDone => sourceAdmissionsDone", "| timedAdmissionsDone => sourceAdmissionsThen (sourceAdmissionClock rate) sourceAdmissionsDone"),
    ("admission_rate_phantom_start", "| sourceAdmissionsDone => zero\n    | sourceAdmissionsThen event rest =>\n        add (admissionReceiptCount", "| sourceAdmissionsDone => next zero\n    | sourceAdmissionsThen event rest =>\n        add (admissionReceiptCount"),
]


# Arbitrary pending prefixes and failures beyond the second slot.
MUTATIONS += [
    ("indexed_prefix_loses_suffix", "| emptyLeasePool => suffix", "| emptyLeasePool => emptyLeasePool"),
    ("indexed_prefix_drops_cell", "| leaseCell lease rest => leaseCell lease (appendLeasePool rest suffix)", "| leaseCell lease rest => appendLeasePool rest suffix"),
    ("indexed_prefix_changes_head", "| leaseCell lease rest => leaseCell lease (appendLeasePool rest suffix)", "| leaseCell lease rest => leaseCell (freeLease zero) (appendLeasePool rest suffix)"),
    ("indexed_prefix_duplicates_cell", "| leaseCell lease rest => leaseCell lease (appendLeasePool rest suffix)", "| leaseCell lease rest => leaseCell lease (leaseCell lease (appendLeasePool rest suffix))"),
    ("indexed_position_aliases_head", "fun (prefix : LeasePool) => add (leaseCapacity prefix) zero", "fun (prefix : LeasePool) => zero"),
    ("indexed_position_skips_selected", "fun (prefix : LeasePool) => add (leaseCapacity prefix) zero", "fun (prefix : LeasePool) => next (add (leaseCapacity prefix) zero)"),
    ("indexed_deep_lookup_refuses", "| leaseCell lease rest => availableLeaseToken previous rest", "| leaseCell lease rest => case previous as position in Count return CompletionToken with | zero => availableLeaseToken previous rest | next earlier => noOwnedLease"),
    ("indexed_deep_lookup_aliases", "| leaseCell lease rest => availableLeaseToken previous rest", "| leaseCell lease rest => case rest as tail in LeasePool return CompletionToken with | emptyLeasePool => noOwnedLease | leaseCell selected remaining => reservationToken (tryReserve selected)"),
    ("indexed_deep_update_ignored", "| leaseCell lease rest => leaseCell lease (updateLease previous change rest)", "| leaseCell lease rest => case previous as position in Count return LeasePool with | zero => leaseCell lease (updateLease previous change rest) | next earlier => leaseCell lease rest"),
    ("indexed_deep_update_aliases", "| leaseCell lease rest => leaseCell lease (updateLease previous change rest)", "| leaseCell lease rest => leaseCell lease (case rest as tail in LeasePool return LeasePool with | emptyLeasePool => emptyLeasePool | leaseCell selected remaining => leaseCell (change selected) remaining)"),
    ("indexed_deep_receipt_aliases", "| grantedSourceStart generation => pendingAdmissionReceipt index generation", "| grantedSourceStart generation => pendingAdmissionReceipt (case index as position in Count return Count with | zero => zero | next previous => next zero) generation"),
    ("indexed_deep_completion_aliases", "(poolStep (completeAt index (ownedGeneration generation) reason) (admissionPool current))", "(poolStep (completeAt (case index as position in Count return Count with | zero => zero | next previous => next zero) (ownedGeneration generation) reason) (admissionPool current))"),
    ("indexed_deep_completion_changes_generation", "(poolStep (completeAt index (ownedGeneration generation) reason) (admissionPool current))", "(poolStep (completeAt index (ownedGeneration (case index as position in Count return Count with | zero => generation | next previous => case previous as earlier in Count return Count with | zero => generation | next rest => next generation)) reason) (admissionPool current))"),
    ("indexed_deep_reservation_aliases", "(poolStep (reserveAt index) (admissionPool current))", "(poolStep (reserveAt (case index as position in Count return Count with | zero => zero | next previous => next zero)) (admissionPool current))"),
    ("indexed_distant_missing_slot_granted", "      | emptyLeasePool => noOwnedLease\n      | leaseCell lease rest => availableLeaseToken previous rest", "      | emptyLeasePool => (case previous as depth in Count return CompletionToken with | zero => noOwnedLease | next older => ownedGeneration zero)\n      | leaseCell lease rest => availableLeaseToken previous rest"),
    ("indexed_deep_receipt_changes_generation", "| grantedSourceStart generation => pendingAdmissionReceipt index generation", "| grantedSourceStart generation => pendingAdmissionReceipt index (case index as position in Count return Count with | zero => generation | next previous => case previous as earlier in Count return Count with | zero => generation | next older => next generation)"),
]

# Policy/source composition: every control changes an executable definition.
MUTATIONS += [
    ("policy_source_gate_bypassed", "    | off => noPolicySourceWork\n    | on => sourceAdmissionAttempt source swarm key index", "    | off => sourceAdmissionAttempt source swarm key index\n    | on => sourceAdmissionAttempt source swarm key index"),
    ("policy_source_allowed_dropped", "    | on => sourceAdmissionAttempt source swarm key index", "    | on => noPolicySourceWork"),
    ("policy_source_identity_changed", "gatePolicySource (policyReceiptAllowed view identity receipt) source swarm key index", "gatePolicySource (policyReceiptAllowed view zero receipt) source swarm key index"),
    ("policy_source_validation_upgraded", "    | on => sourceAdmissionAttempt source swarm key index", "    | on => sourceAdmissionAttempt validated swarm key index"),
    ("policy_source_key_changed", "    | on => sourceAdmissionAttempt source swarm key index", "    | on => sourceAdmissionAttempt source swarm zero index"),
    ("policy_source_slot_changed", "    | on => sourceAdmissionAttempt source swarm key index", "    | on => sourceAdmissionAttempt source swarm key zero"),
    ("policy_source_publication_issues_credit", "    | policySourcePublish observed update => noPolicySourceWork", "    | policySourcePublish observed update => sourceAdmissionClock rate"),
    ("policy_source_publication_dropped", "    | policySourcePublish observed update => commitPolicyAction observed update view", "    | policySourcePublish observed update => view"),
    ("policy_source_publication_ignores_cas", "    | policySourcePublish observed update => commitPolicyAction observed update view", "    | policySourcePublish observed update => commitPolicyAction (policyGeneration view) update view"),
    ("policy_source_maintenance_dropped", "    | policySourceMaintenance maintenance => sourceAdmissionMaintenance maintenance", "    | policySourceMaintenance maintenance => noPolicySourceWork"),
    ("policy_source_completion_dropped", "    | policySourceFinish receipt reason => sourceAdmissionFinish receipt reason", "    | policySourceFinish receipt reason => noPolicySourceWork"),
    ("policy_source_tick_extra_credit", "    | policySourceTick => sourceAdmissionClock rate", "    | policySourceTick => sourceAdmissionClock (next rate)"),
    ("policy_source_claimed_tick_trusted", "    | policySourceClaimedTick claimed => noPolicySourceWork", "    | policySourceClaimedTick claimed => sourceAdmissionClock claimed"),
    ("policy_source_erasure_drops_event", "| policySourcesThen event rest => sourceAdmissionsThen\n        (policySourceResourceEvent rate event (policySourceView current))", "| policySourcesThen event rest => sourceAdmissionsThen\n        noPolicySourceWork"),
    ("policy_source_erasure_keeps_old_state", "        (erasePolicySources rest quota capacity rate (policySourceStep quota capacity rate event current))", "        (erasePolicySources rest quota capacity rate current)"),
    ("policy_source_starts_keep_old_state", "| policySourcesThen event rest => add (admissionReceiptCount (policySourceAttemptReceipt quota rate event current))\n        (policySourceStarts rest quota capacity rate (policySourceStep quota capacity rate event current))", "| policySourcesThen event rest => add (admissionReceiptCount (policySourceAttemptReceipt quota rate event current))\n        (policySourceStarts rest quota capacity rate current)"),
    ("policy_source_starts_drop_receipt", "| policySourcesThen event rest => add (admissionReceiptCount (policySourceAttemptReceipt quota rate event current))", "| policySourcesThen event rest => add zero"),
    ("policy_source_receipt_bypasses_gate", "    admissionAttemptReceipt quota (policySourceResourceEvent rate event (policySourceView current))\n      (policySourceResources current)", "    case event as action in PolicySourceEvent return AdmissionReceipt with\n    | policySourceAttempt receipt identity source swarm key index =>\n        admissionAttemptReceipt quota (sourceAdmissionAttempt source swarm key index) (policySourceResources current)\n    | policySourcePublish observed update => noAdmissionReceipt\n    | policySourceMaintenance maintenance => noAdmissionReceipt\n    | policySourceFinish receipt reason => noAdmissionReceipt\n    | policySourceTick => noAdmissionReceipt\n    | policySourceClaimedTick claimed => noAdmissionReceipt"),
    ("policy_source_tick_changes_view", "    | policySourceTick => view", "    | policySourceTick => commitPolicyAction (policyGeneration view) (policyResolution zero on zero) view"),
]

MUTATIONS += [
    ("policy_work_attempt_free", "| policySourceAttempt receipt identity source swarm key index => rateAttempt validated primarySwarm zero off", "| policySourceAttempt receipt identity source swarm key index => rateAttempt unvalidated primarySwarm zero off"),
    ("policy_work_publication_free", "| policySourcePublish observed update => rateAttempt validated primarySwarm zero off", "| policySourcePublish observed update => rateAttempt unvalidated primarySwarm zero off"),
    ("policy_work_empty_gate_bypassed", "| zero => policySourceClaimedTick zero\n    | next remaining => event", "| zero => event\n    | next remaining => event"),
    ("policy_work_funded_event_dropped", "| zero => policySourceClaimedTick zero\n    | next remaining => event", "| zero => policySourceClaimedTick zero\n    | next remaining => policySourceClaimedTick zero"),
    ("policy_work_attempt_bypasses_budget", "| policySourceAttempt receipt identity source swarm key index => creditedPolicyWorkEvent available event", "| policySourceAttempt receipt identity source swarm key index => event"),
    ("policy_work_publication_bypasses_budget", "| policySourcePublish observed update => creditedPolicyWorkEvent available event", "| policySourcePublish observed update => event"),
    ("policy_work_maintenance_dropped", "| policySourceMaintenance maintenance => event", "| policySourceMaintenance maintenance => policySourceClaimedTick zero"),
    ("policy_work_completion_dropped", "| policySourceFinish receipt reason => event", "| policySourceFinish receipt reason => policySourceClaimedTick zero"),
    ("policy_work_tick_dropped", "| policySourceTick => event", "| policySourceTick => policySourceClaimedTick zero"),
    ("policy_work_claimed_tick_forwarded", "| policySourceClaimedTick claimed => event", "| policySourceClaimedTick claimed => policySourceTick"),
    ("policy_work_maintenance_mints_credit", "| policySourceMaintenance maintenance => claimedClockCredit zero", "| policySourceMaintenance maintenance => trustedClockCredit rate"),
    ("policy_work_completion_mints_credit", "| policySourceFinish receipt reason => claimedClockCredit zero", "| policySourceFinish receipt reason => trustedClockCredit rate"),
    ("policy_work_claimed_tick_mints_credit", "| policySourceClaimedTick claimed => claimedClockCredit claimed", "| policySourceClaimedTick claimed => trustedClockCredit claimed"),
    ("policy_work_wrong_refill_rate", "creditsAfter (workCapacity config) (policyWorkCredits current) (policyWorkRateEvent (workRate config) event)", "creditsAfter (workCapacity config) (policyWorkCredits current) (policyWorkRateEvent (workHandshakeRate config) event)"),
    ("policy_work_capacity_inflated", "creditsAfter (workCapacity config) (policyWorkCredits current) (policyWorkRateEvent (workRate config) event)", "creditsAfter (next (workCapacity config)) (policyWorkCredits current) (policyWorkRateEvent (workRate config) event)"),
    ("policy_work_charge_dropped", "creditsAfter (workCapacity config) (policyWorkCredits current) (policyWorkRateEvent (workRate config) event)", "policyWorkCredits current"),
    ("policy_work_balance_aliased", "creditsAfter (workCapacity config) (policyWorkCredits current) (policyWorkRateEvent (workRate config) event)", "creditsAfter (workCapacity config) (admissionCredits (policySourceResources (policyWorkSources current))) (policyWorkRateEvent (workRate config) event)"),
    ("policy_work_empty_receipt_granted", "| zero => noPolicyWorkReceipt", "| zero => processedPolicyWork"),
    ("policy_work_processed_receipt_dropped", "| next remaining => processedPolicyWork", "| next remaining => noPolicyWorkReceipt"),
    ("policy_work_completion_counted", "| policySourceFinish receipt reason => noPolicyWorkReceipt", "| policySourceFinish receipt reason => processedPolicyWork"),
    ("policy_work_trace_reuses_initial_credit", "| policySourcesThen event rest => add (policyWorkReceiptCount (policyWorkReceipt event (policyWorkCredits current)))\n        (policyWorkProcessed rest config (policyWorkStep config event current))", "| policySourcesThen event rest => add (policyWorkReceiptCount (policyWorkReceipt event (policyWorkCredits current)))\n        (policyWorkProcessed rest config current)"),
    ("policy_work_receipt_count_doubled", "| processedPolicyWork => next zero", "| processedPolicyWork => next (next zero)"),
    ("policy_work_source_uses_post_charge", "(policyWorkSourceEvent (policyWorkCredits current) event) (policyWorkSources current))", "(policyWorkSourceEvent (predecessor (policyWorkCredits current)) event) (policyWorkSources current))"),
    ("policy_work_admission_receipt_bypasses_budget", "policySourceAttemptReceipt (workSourceQuota config) (workHandshakeRate config)\n      (policyWorkSourceEvent (policyWorkCredits current) event) (policyWorkSources current)", "policySourceAttemptReceipt (workSourceQuota config) (workHandshakeRate config)\n      event (policyWorkSources current)"),
    ("policy_work_unfunded_event_ticks_clock", "| zero => policySourceClaimedTick zero\n    | next remaining => event", "| zero => policySourceTick\n    | next remaining => event"),
    ("policy_work_tick_skips_refill", "| policySourceTick => trustedClockCredit rate", "| policySourceTick => claimedClockCredit zero"),
    ("policy_work_gate_reads_handshake_credit", "(policyWorkSourceEvent (policyWorkCredits current) event) (policyWorkSources current))", "(policyWorkSourceEvent (admissionCredits (policySourceResources (policyWorkSources current))) event) (policyWorkSources current))"),
]


MUTATIONS += [
    ("policy_ingress_empty_query_bypassed", "| zero => noPolicyQuery\n    | next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated identity)", "| zero => queriedPolicy (readPolicy admissionConsumer view authenticated identity)\n    | next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated identity)"),
    ("policy_ingress_funded_query_dropped", "| next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated identity)", "| next remaining => noPolicyQuery"),
    ("policy_ingress_query_authentication_bypassed", "| next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated identity)", "| next remaining => queriedPolicy (readPolicy admissionConsumer view on identity)"),
    ("policy_ingress_query_identity_changed", "| next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated identity)", "| next remaining => queriedPolicy (readPolicy admissionConsumer view authenticated (next identity))"),
    ("policy_ingress_empty_query_mints_tick", "| noPolicyQuery => policySourceClaimedTick zero", "| noPolicyQuery => policySourceTick"),
    ("policy_ingress_query_result_dropped", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key index", "| queriedPolicy receipt => policySourceClaimedTick zero"),
    ("policy_ingress_attempt_identity_changed", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key index", "| queriedPolicy receipt => policySourceAttempt receipt (next identity) source swarm key index"),
    ("policy_ingress_attempt_source_changed", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key index", "| queriedPolicy receipt => policySourceAttempt receipt identity validated swarm key index"),
    ("policy_ingress_attempt_key_changed", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key index", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm (next key) index"),
    ("policy_ingress_attempt_slot_changed", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key index", "| queriedPolicy receipt => policySourceAttempt receipt identity source swarm key (next index)"),
    ("policy_ingress_publication_generation_changed", "| policyIngressPublish observed update => policySourcePublish observed update", "| policyIngressPublish observed update => policySourcePublish (next observed) update"),
    ("policy_ingress_maintenance_dropped", "| policyIngressMaintenance maintenance => policySourceMaintenance maintenance", "| policyIngressMaintenance maintenance => policySourceClaimedTick zero"),
    ("policy_ingress_completion_dropped", "| policyIngressFinish receipt reason => policySourceFinish receipt reason", "| policyIngressFinish receipt reason => policySourceClaimedTick zero"),
    ("policy_ingress_tick_dropped", "| policyIngressTick => policySourceTick", "| policyIngressTick => policySourceClaimedTick zero"),
    ("policy_ingress_claimed_tick_trusted", "| policyIngressClaimedTick claimed => policySourceClaimedTick claimed", "| policyIngressClaimedTick claimed => policySourceTick"),
    ("policy_ingress_run_ignores_event", "| policyIngressThen event rest => runPolicyIngress rest config (policyIngressStep config event current)", "| policyIngressThen event rest => runPolicyIngress rest config current"),
    ("policy_ingress_projection_reuses_old_state", "| policyIngressThen event rest => policySourcesThen (policyIngressEvent event current)\n        (erasePolicyIngress rest config (policyIngressStep config event current))", "| policyIngressThen event rest => policySourcesThen (policyIngressEvent event current)\n        (erasePolicyIngress rest config current)"),
    ("policy_ingress_query_reads_handshake_credit", "queriedPolicyAttempt\n          (budgetedPolicyQuery (policyWorkCredits current)", "queriedPolicyAttempt\n          (budgetedPolicyQuery (admissionCredits (policySourceResources (policyWorkSources current)))"),
    ("policy_ingress_trusted_tick_uncounted", "| policyIngressTick => next ticks", "| policyIngressTick => ticks"),
    ("policy_ingress_claimed_tick_counted", "| policyIngressClaimedTick claimed => ticks", "| policyIngressClaimedTick claimed => next ticks"),
    ("policy_poll_prefix_drops_event", "| policyIngressThen event rest => policyIngressThen event (policyIngressPollPrefix remaining rest)", "| policyIngressThen event rest => policyIngressPollPrefix remaining rest"),
    ("policy_poll_prefix_changes_event", "| policyIngressThen event rest => policyIngressThen event (policyIngressPollPrefix remaining rest)", "| policyIngressThen event rest => policyIngressThen policyIngressTick (policyIngressPollPrefix remaining rest)"),
    ("policy_poll_zero_fuel_loses_backlog", "case fuel as self in Count return PolicyIngressTrace with\n    | zero => trace", "case fuel as self in Count return PolicyIngressTrace with\n    | zero => policyIngressDone"),
    ("policy_poll_remainder_replays_event", "| policyIngressThen event rest => policyIngressPollRemainder remaining rest", "| policyIngressThen event rest => policyIngressThen event (policyIngressPollRemainder remaining rest)"),
    ("policy_poll_work_undercounts", "| policyIngressThen event rest => next (policyIngressPollWork remaining rest)", "| policyIngressThen event rest => policyIngressPollWork remaining rest"),
    ("policy_poll_work_exceeds_fuel", "| policyIngressThen event rest => next (policyIngressPollWork remaining rest)", "| policyIngressThen event rest => next (next (policyIngressPollWork remaining rest))"),
    ("policy_poll_attempt_guard_is_free", "| policyIngressThen event rest => next (policyIngressPollWork remaining rest)", "| policyIngressThen event rest =>\n        case event as action in PolicyIngressEvent return Count with\n        | policyIngressAttempt authenticated identity source swarm key index => policyIngressPollWork remaining rest\n        | policyIngressPublish observed update => next (policyIngressPollWork remaining rest)\n        | policyIngressMaintenance maintenance => next (policyIngressPollWork remaining rest)\n        | policyIngressFinish receipt reason => next (policyIngressPollWork remaining rest)\n        | policyIngressTick => next (policyIngressPollWork remaining rest)\n        | policyIngressClaimedTick claimed => next (policyIngressPollWork remaining rest)"),
    ("policy_poll_cleanup_is_free", "| policyIngressThen event rest => next (policyIngressPollWork remaining rest)", "| policyIngressThen event rest =>\n        case event as action in PolicyIngressEvent return Count with\n        | policyIngressAttempt authenticated identity source swarm key index => next (policyIngressPollWork remaining rest)\n        | policyIngressPublish observed update => next (policyIngressPollWork remaining rest)\n        | policyIngressMaintenance maintenance => policyIngressPollWork remaining rest\n        | policyIngressFinish receipt reason => policyIngressPollWork remaining rest\n        | policyIngressTick => next (policyIngressPollWork remaining rest)\n        | policyIngressClaimedTick claimed => next (policyIngressPollWork remaining rest)"),
    ("policy_poll_zero_fuel_runs_queue", "case fuel as self in Count return PolicyWorkState with\n    | zero => current", "case fuel as self in Count return PolicyWorkState with\n    | zero => runPolicyIngress trace config current"),
    ("policy_poll_skips_transition", "| policyIngressThen event rest => runPolicyIngressPoll remaining rest config (policyIngressStep config event current)", "| policyIngressThen event rest => runPolicyIngressPoll remaining rest config current"),
    ("policy_poll_replays_transition", "| policyIngressThen event rest => runPolicyIngressPoll remaining rest config (policyIngressStep config event current)", "| policyIngressThen event rest => runPolicyIngressPoll remaining rest config (policyIngressStep config event (policyIngressStep config event current))"),
    ("policy_poll_backlog_loses_wake", "case trace as self in PolicyIngressTrace return Flag with\n    | policyIngressDone => off\n    | policyIngressThen event rest => on", "case trace as self in PolicyIngressTrace return Flag with\n    | policyIngressDone => off\n    | policyIngressThen event rest => off"),
    ("policy_poll_empty_queue_spins", "case trace as self in PolicyIngressTrace return Flag with\n    | policyIngressDone => off\n    | policyIngressThen event rest => on", "case trace as self in PolicyIngressTrace return Flag with\n    | policyIngressDone => on\n    | policyIngressThen event rest => on"),
    ("policy_poll_wakes_for_consumed_prefix", "policyIngressBacklogWake (policyIngressPollRemainder fuel trace)", "policyIngressBacklogWake (policyIngressPollPrefix fuel trace)"),
    ("policy_poll_cost_drops_overhead", "add (multiply (policyIngressPollWork fuel trace) eventCost)\n      (add (multiply (policyIngressProcessed", "add zero\n      (add (multiply (policyIngressProcessed"),
    ("policy_poll_cost_charges_unprocessed_backlog", "add (multiply (policyIngressPollWork fuel trace) eventCost)\n      (add (multiply (policyIngressProcessed", "add (multiply (policyIngressLength trace) eventCost)\n      (add (multiply (policyIngressProcessed"),
    ("policy_poll_idle_queue_burns_fuel", "| policyIngressDone => zero\n      | policyIngressThen event rest => next (policyIngressPollWork remaining rest)", "| policyIngressDone => next remaining\n      | policyIngressThen event rest => next (policyIngressPollWork remaining rest)"),
    ("policy_poll_wake_ignores_deep_backlog", "policyIngressBacklogWake (policyIngressPollRemainder fuel trace)", "case fuel as self in Count return Flag with\n    | zero => policyIngressBacklogWake trace\n    | next remaining =>\n      case remaining as later in Count return Flag with\n      | zero => policyIngressBacklogWake (policyIngressPollRemainder (next zero) trace)\n      | next spare => off"),
]


def invoke(compiler: Path, command: str, bundle: Path):
    return subprocess.run([str(compiler), command, str(bundle)], capture_output=True, text=True, timeout=120)


def negative_checks(compiler: Path, source: str, build: Path) -> list[str]:
    cases = [(name, source.replace(before, after)) for name, before, after in MUTATIONS]
    if any(source.count(before) != 1 for _, before, _ in MUTATIONS):
        raise ValueError("a mutation target is absent or ambiguous")
    cases.extend([
        ("false_equality", source + "\ndef impossible : Equal Flag off on := same\n"),
        ("false_bound", source + "\ndef impossible : AtMost (next zero) zero := least zero\n"),
        ("nonterminating_proof", source + "\ndef rec loop : Count -> Count := fun (n : Count) => loop n\n"),
    ])
    rejected = []
    negative_dir = build / "negative"
    negative_dir.mkdir(exist_ok=True)
    for name, candidate in cases:
        path = negative_dir / f"{name}.mech"
        path.write_text(candidate)
        result = invoke(compiler, "check", path)
        diagnostic = result.stdout + result.stderr
        (negative_dir / f"{name}.log").write_text(diagnostic)
        # Parser failures, crashes, timeouts and tool usage errors are not proof rejection.
        expected = "termination:" if name == "nonterminating_proof" else "mismatch:"
        if result.returncode != 1 or not diagnostic.strip().startswith(expected):
            raise ValueError(f"negative check {name} did not produce a type/termination rejection: {diagnostic}")
        rejected.append(name)
    return rejected


def validate_compiler(compiler: Path, catalog: dict) -> dict:
    lock = catalog["load"](ROOT / "toolchain.lock.json")["compiler"]
    receipt = catalog["load"](ROOT / ".cache" / "compiler-build.json")
    for field in ("revision", "vendor_veil_revision"):
        if receipt[field] != lock[field]:
            raise ValueError("compiler provenance differs from toolchain lock")
    if receipt["compiler_sha256"] != hashlib.sha256(compiler.read_bytes()).hexdigest():
        raise ValueError("checker binary does not match the pinned build receipt")
    return receipt


def implementation_links(path: Path | None, catalog: dict) -> dict:
    mapping = catalog["load"](ROOT / "implementation-map.json")
    lock = catalog["load"](ROOT / "toolchain.lock.json")["implementation"]
    if mapping["revision"] != lock["revision"]:
        raise ValueError("implementation mapping has a different target revision")
    if path is None:
        return {"status": "not_checked_this_run", "refinement_proved": False}
    revision = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    if revision != lock["revision"]:
        raise ValueError("implementation checkout is not at the pinned revision")
    for entry in mapping["entries"]:
        file = path / entry["path"]
        if not file.resolve().is_relative_to(path.resolve()) or file.is_symlink():
            raise ValueError("unsafe implementation path")
        if hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"implementation source changed: {entry['path']}")
    return {"status": "source_links_checked", "revision": revision,
            "entries": len(mapping["entries"]), "refinement_proved": False}


def input_hashes() -> dict[str, str]:
    paths = ["claims.json", "atomic-claims.json", "source-inventory.json",
             "sources/manifest.json", "implementation-map.json", "toolchain.lock.json",
             "README.md", "docs/COVERAGE.md", "docs/MODELS.md", "docs/TRUST.md",
             "docs/ROADMAP.md", "Makefile", ".github/workflows/model-checks.yml"]
    paths.extend(str(path.relative_to(ROOT)) for path in (ROOT / "proofs").glob("*.mech"))
    paths.extend(str(path.relative_to(ROOT)) for path in (ROOT / "tools").glob("*.py"))
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in sorted(paths)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mech", default=os.environ.get("MECH", str(ROOT / ".cache/mechanism-lang/_build/default/bin/mech.exe")))
    parser.add_argument("--implementation", type=Path)
    parser.add_argument("--require-complete", action="store_true",
                        help="also require every implementation and deployment claim to be proved")
    args = parser.parse_args()
    build = ROOT / ".build"
    build.mkdir(exist_ok=True)
    (build / "report.json").unlink(missing_ok=True)
    checked_inputs = input_hashes()
    compiler = Path(args.mech).resolve(strict=True)
    catalog = runpy.run_path(str(ROOT / "tools" / "catalog.py"))
    provenance = validate_compiler(compiler, catalog)
    inventory = catalog["inventory"]()
    if inventory != catalog["load"](ROOT / "source-inventory.json"):
        raise ValueError("source inventory is stale; run tools/catalog.py and review the change")
    if catalog["coverage_markdown"](inventory) != (ROOT / "docs" / "COVERAGE.md").read_text():
        raise ValueError("coverage document is stale")
    linked = implementation_links(args.implementation, catalog)
    files = sorted((ROOT / "proofs").glob("*.mech"))
    if not files:
        raise ValueError("no proof sources")
    source = "\n".join(path.read_text() for path in files)
    if re.search(r"\b(axiom|sorry|admit|unsafe|primitive)\b", re.sub(r"--[^\n]*", "", source)):
        raise ValueError("proof source contains a prohibited escape hatch")
    bundle = build / "all.mech"
    bundle.write_text(source)
    for command in ("check", "axioms"):
        result = invoke(compiler, command, bundle)
        (build / f"{command}.log").write_text(result.stdout + result.stderr)
        if result.returncode != 0:
            print(result.stdout + result.stderr, file=sys.stderr)
            return 1
        if command == "axioms" and (result.stdout.strip() or result.stderr.strip()):
            print("nonempty axiom disclosure", file=sys.stderr)
            return 1
    rejected = negative_checks(compiler, source, build)
    claims = catalog["load"](ROOT / "claims.json")["claims"]
    atoms = catalog["atomic_claims"](catalog["theorem_names"](source), {row["id"] for row in claims})
    if checked_inputs != input_hashes():
        raise ValueError("proof inputs or validation tooling changed during this run")
    report = {"model_checked": True, "axioms": [], "modules": len(files),
              "inputs_sha256": checked_inputs,
              "checked_proof_declarations": len(catalog["theorem_names"](source)),
              "negative_checks_rejected": rejected,
              "claim_groups": len(claims), "source_units": len(inventory["units"]),
              "atomic_model_obligations": len(atoms),
              "claim_decomposition_complete": False,
              "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "compiler": provenance, "implementation_links": linked,
              "implementation_proved": False, "deployment_qualified": False,
              "blockers": ["Complete atomic claim decomposition and model coverage",
                           "Machine-checked refinement from pinned Rust and transport dependencies",
                           "Resolve D01-D12 and record the accepted numerical envelope",
                           "Supply required M1-M6, topology, storage and operator evidence"]}
    (build / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: report[key] for key in ("model_checked", "checked_proof_declarations",
          "claim_groups", "atomic_model_obligations", "source_units", "implementation_proved", "deployment_qualified")} |
          {"negative_checks_rejected": len(rejected), "report": ".build/report.json"}))
    if args.require_complete:
        print("Full qualification blocked: " + "; ".join(report["blockers"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        sys.exit(1)
