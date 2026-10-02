#!/usr/bin/env python3
"""Check the ordered mechanism-lang proof sources and their axiom disclosure."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
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
    ('policy_resume_drops_old_head', '        (scannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))\n        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))', '        (scannedPolicyIngress scanFuel arrivals)\n        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))'),
    ('policy_resume_fresh_overtakes_old', '        (scannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))\n        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))', '        (scannedPolicyIngress scanFuel (appendPolicyIngress arrivals deferred))\n        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))'),
    ('policy_resume_loses_continuation', '        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))\n', '        (resumedPolicyIngressSchedule scanFuel rest policyIngressDone)\n'),
    ('policy_resume_replays_examined', '        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))\n', '        (resumedPolicyIngressSchedule scanFuel rest (appendPolicyIngress deferred arrivals))\n'),
    ('policy_resume_retains_wrong_half', '        (resumedPolicyIngressSchedule scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))\n', '        (resumedPolicyIngressSchedule scanFuel rest (scannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals)))\n'),
    ('policy_resume_erases_service_fuel', '    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (scannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))', '    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero\n        (scannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))'),
    ('policy_resume_erases_final_suffix', "def rec resumedPolicyIngressDeferred : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred", "def rec resumedPolicyIngressDeferred : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone"),
    ('policy_resume_suffix_omits_arrivals', '        resumedPolicyIngressDeferred scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))\n', '        resumedPolicyIngressDeferred scanFuel rest (unscannedPolicyIngress scanFuel deferred)\n'),
    ('policy_resume_suffix_keeps_examined', '        resumedPolicyIngressDeferred scanFuel rest (unscannedPolicyIngress scanFuel (appendPolicyIngress deferred arrivals))\n', '        resumedPolicyIngressDeferred scanFuel rest (appendPolicyIngress deferred arrivals)\n'),
    ('policy_resume_scan_uses_service_fuel', 'policyIngressTurn scanFuel arrivals (policyIngressResumptionScanSchedule scanFuel rest)', 'policyIngressTurn fuel arrivals (policyIngressResumptionScanSchedule scanFuel rest)'),
    ('policy_resume_scan_omits_fresh', 'policyIngressTurn scanFuel arrivals (policyIngressResumptionScanSchedule scanFuel rest)', 'policyIngressTurn scanFuel policyIngressDone (policyIngressResumptionScanSchedule scanFuel rest)'),
    ('policy_resume_scan_budget_loses_turns', 'policyIngressScheduleFuel (policyIngressResumptionScanSchedule scanFuel schedule)', 'scanFuel'),
    ('policy_resume_getter_loses_suffix', '| policyIngressResumeState deferred queued => deferred', '| policyIngressResumeState deferred queued => policyIngressDone'),
    ('policy_resume_runner_replays_suffix', 'policyIngressResumeState (resumedPolicyIngressDeferred scanFuel schedule (deferredPolicyIngress state))', 'policyIngressResumeState (deferredPolicyIngress state)'),
    ('policy_resume_runner_loses_queue_work', '(runPayloadIngress weight slots payloadLimit\n        (resumedPolicyIngressSchedule scanFuel schedule (deferredPolicyIngress state)) config (resumedPolicyIngressQueue state))', '(resumedPolicyIngressQueue state)'),
    ('policy_resume_runner_bypasses_admission', '      (runPayloadIngress weight slots payloadLimit\n        (resumedPolicyIngressSchedule scanFuel schedule (deferredPolicyIngress state)) config (resumedPolicyIngressQueue state))', '      (runPolicyIngressSchedule\n        (resumedPolicyIngressSchedule scanFuel schedule (deferredPolicyIngress state)) config (resumedPolicyIngressQueue state))'),
    ('policy_resume_trace_bypasses_admission', '    payloadIngressTrace weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events', '    policyIngressScheduleTrace (resumedPolicyIngressSchedule scanFuel schedule deferred) events'),
    ('policy_resume_scan_cost_erased', '    multiply (policyIngressLength (resumedPolicyIngressExamined scanFuel schedule deferred)) scanCost\n', '    zero\n'),
    ('policy_resume_cost_omits_scan', 'add (resumedPolicyIngressScanCost scanFuel schedule deferred scanCost)', 'add zero'),
    ('policy_resume_cost_omits_dispatch', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current eventCost policyCost handshakeCost)\n\n', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current zero policyCost handshakeCost)\n\n'),
    ('policy_resume_cost_omits_policy', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current eventCost policyCost handshakeCost)\n\n', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current eventCost zero handshakeCost)\n\n'),
    ('policy_resume_cost_omits_handshake', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current eventCost policyCost handshakeCost)\n\n', '      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config current eventCost policyCost zero)\n\n'),
    ('policy_resume_limit_erases_scan', 'add (multiply (resumedPolicyIngressScanFuel scanFuel schedule) scanCost)', 'add zero'),
    ('policy_resume_limit_erases_dispatch', '      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config eventCost policyCost handshakeCost)\n\n', '      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit (resumedPolicyIngressSchedule scanFuel schedule deferred) events)\n        events config zero policyCost handshakeCost)\n\n'),

    ("policy_scan_bypasses_fuel", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollPrefix scanFuel arrivals", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => arrivals"),
    ("policy_scan_discards_prefix", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollPrefix scanFuel arrivals", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressDone"),
    ("policy_scan_inflates_fuel", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollPrefix scanFuel arrivals", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollPrefix (next scanFuel) arrivals"),
    ("policy_scan_loses_unexamined", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollRemainder scanFuel arrivals", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressDone"),
    ("policy_scan_replays_examined", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => policyIngressPollRemainder scanFuel arrivals", "fun (scanFuel : Count) (arrivals : PolicyIngressTrace) => arrivals"),
    ("policy_scan_accepts_unexamined", "    admittedPayloadIngress weight slots payloadLimit events (scannedPolicyIngress scanFuel arrivals)", "    admittedPayloadIngress weight slots payloadLimit events arrivals"),
    ("policy_scan_rejects_unexamined", "    rejectedPayloadIngress weight slots payloadLimit events (scannedPolicyIngress scanFuel arrivals)", "    rejectedPayloadIngress weight slots payloadLimit events arrivals"),
    ("policy_scan_hides_rejections", "    rejectedPayloadIngress weight slots payloadLimit events (scannedPolicyIngress scanFuel arrivals)", "    policyIngressDone"),
    ("policy_scan_ready_bypasses_fuel", "    payloadIngressReady weight slots payloadLimit events (scannedPolicyIngress scanFuel arrivals)", "    payloadIngressReady weight slots payloadLimit events arrivals"),
    ("policy_scan_ready_loses_backlog", "    payloadIngressReady weight slots payloadLimit events (scannedPolicyIngress scanFuel arrivals)", "    payloadIngressReady weight slots payloadLimit policyIngressDone (scannedPolicyIngress scanFuel arrivals)"),
    ("policy_scan_schedule_bypasses_fuel", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (scannedPolicyIngress scanFuel arrivals)", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel arrivals"),
    ("policy_scan_schedule_erases_service", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (scannedPolicyIngress scanFuel arrivals)", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero (scannedPolicyIngress scanFuel arrivals)"),
    ("policy_scan_schedule_loses_tail", "        (scannedPolicyIngressSchedule scanFuel rest)", "        policyIngressScheduleDone"),
    ("policy_scan_runner_bypasses_fuel", "    runPayloadIngress weight slots payloadLimit (scannedPolicyIngressSchedule scanFuel schedule) config queued", "    runPayloadIngress weight slots payloadLimit schedule config queued"),
    ("policy_scan_trace_bypasses_fuel", "    payloadIngressTrace weight slots payloadLimit (scannedPolicyIngressSchedule scanFuel schedule) events", "    payloadIngressTrace weight slots payloadLimit schedule events"),
    ("policy_scan_cost_unbounded", "    multiply (policyIngressLength (scannedPolicyIngress scanFuel arrivals)) scanCost", "    multiply (policyIngressLength arrivals) scanCost"),
    ("policy_scan_cost_free", "    multiply (policyIngressLength (scannedPolicyIngress scanFuel arrivals)) scanCost", "    zero"),
    ("policy_scan_total_erases_admission", "    add (policyIngressScanCost scanFuel arrivals scanCost)\n      (policyIngressPollCost fuel", "    add zero\n      (policyIngressPollCost fuel"),
    ("policy_scan_limit_erases_admission", "    add (multiply scanFuel scanCost)\n      (policyIngressPollCostLimit fuel", "    add zero\n      (policyIngressPollCostLimit fuel"),
    ("policy_payload_erases_head_charge", "    | policyIngressThen event rest => add (weight event) (policyIngressPayload weight rest)", "    | policyIngressThen event rest => policyIngressPayload weight rest"),
    ("policy_payload_erases_tail_charge", "    | policyIngressThen event rest => add (weight event) (policyIngressPayload weight rest)", "    | policyIngressThen event rest => weight event"),
    ("policy_payload_doubles_charge", "    | policyIngressThen event rest => add (weight event) (policyIngressPayload weight rest)", "    | policyIngressThen event rest => add (weight event) (add (weight event) (policyIngressPayload weight rest))"),
    ("policy_payload_remaining_grows", "    | policyPayloadRoom room equation => room", "    | policyPayloadRoom room equation => next room"),
    ("policy_payload_space_resets", "  fun (amount : Count) (capacity : Count) => policyPayloadRemaining amount capacity (reservePolicyPayload amount capacity)", "  fun (amount : Count) (capacity : Count) => capacity"),
    ("policy_payload_candidates_reset", "    selectedPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit)\n      (selectPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit))", "    selectedPayloadIngress weight arrivals payloadLimit\n      (selectPayloadIngress weight arrivals payloadLimit)"),
    ("policy_payload_candidates_empty", "    selectedPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit)\n      (selectPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit))", "    policyIngressDone"),
    ("policy_payload_excess_empty", "    deferredPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit)\n      (selectPayloadIngress weight arrivals (policyPayloadSpace (policyIngressPayload weight events) payloadLimit))", "    policyIngressDone"),
    ("policy_payload_selector_denies_all", "    | policyIngressThen event rest => fun (capacity : Count) => selectPayloadIngressHead weight event rest capacity\n        (fun (room : Count) => selectPayloadIngress weight rest room) (reservePolicyPayload (weight event) capacity)", "    | policyIngressThen event rest => fun (capacity : Count) => payloadIngressSelection policyIngressDone (policyIngressThen event rest) same (least capacity)"),
    ("policy_payload_prepend_loses_head", "        payloadIngressSelection (policyIngressThen event accepted) rejected\n          (congruent PolicyIngressTrace PolicyIngressTrace (fun (tail : PolicyIngressTrace) => policyIngressThen event tail)\n            (appendPolicyIngress accepted rejected) rest partition)\n          (equalTransport Count (fun (cap : Count) => AtMost (add (weight event) (policyIngressPayload weight accepted)) cap)\n            (add (weight event) room) capacity equation\n            (addBounds (weight event) (weight event) (policyIngressPayload weight accepted) room (reflexiveBound (weight event)) fits))", "        payloadIngressSelection policyIngressDone (policyIngressThen event rest) same (least capacity)"),
    ("policy_payload_admission_ignores_slots", "    admittedPolicyIngress slots events (payloadIngressCandidates weight payloadLimit events arrivals)", "    payloadIngressCandidates weight payloadLimit events arrivals"),
    ("policy_payload_rejection_reorders", "    appendPolicyIngress (rejectedPolicyIngress slots events (payloadIngressCandidates weight payloadLimit events arrivals))\n      (payloadIngressExcess weight payloadLimit events arrivals)", "    appendPolicyIngress (payloadIngressExcess weight payloadLimit events arrivals)\n      (rejectedPolicyIngress slots events (payloadIngressCandidates weight payloadLimit events arrivals))"),
    ("policy_payload_ready_forgets_backlog", "    boundedPolicyIngressReady slots events (payloadIngressCandidates weight payloadLimit events arrivals)", "    admittedPayloadIngress weight slots payloadLimit events arrivals"),
    ("policy_payload_schedule_keeps_old_queue", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          events)"),
    ("policy_payload_schedule_accepts_offered", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel arrivals\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))"),
    ("policy_payload_schedule_erases_fuel", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))"),
    ("policy_payload_runtime_unfiltered", "    runPolicyIngressSchedule (payloadIngressSchedule weight slots payloadLimit schedule (queuedPolicyIngress queued)) config queued", "    runPolicyIngressSchedule schedule config queued"),
    ("policy_payload_trace_unfiltered", "    policyIngressScheduleTrace (payloadIngressSchedule weight slots payloadLimit schedule events) events", "    policyIngressScheduleTrace schedule events"),
    ("policy_payload_schedule_retains_dispatched", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollRemainder fuel (payloadIngressReady weight slots payloadLimit events arrivals)))", "    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPayloadIngress weight slots payloadLimit events arrivals)\n        (payloadIngressSchedule weight slots payloadLimit rest\n          (policyIngressPollPrefix fuel (payloadIngressReady weight slots payloadLimit events arrivals)))"),
    ("policy_payload_runtime_skips_dispatch", "    runPolicyIngressSchedule (payloadIngressSchedule weight slots payloadLimit schedule (queuedPolicyIngress queued)) config queued", "    queued"),
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
    ('policy_overload_uses_total_capacity', 'def admittedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollPrefix (policyIngressFuelAfter limit events) arrivals', 'def admittedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollPrefix limit arrivals'),
    ('policy_overload_admits_tail', 'def admittedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollPrefix (policyIngressFuelAfter limit events) arrivals', 'def admittedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollRemainder (policyIngressFuelAfter limit events) arrivals'),
    ('policy_overload_forgets_rejections', 'def rejectedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollRemainder (policyIngressFuelAfter limit events) arrivals', 'def rejectedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDone'),
    ('policy_overload_reports_admitted_as_rejected', 'def rejectedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollRemainder (policyIngressFuelAfter limit events) arrivals', 'def rejectedPolicyIngress : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollPrefix (policyIngressFuelAfter limit events) arrivals'),
    ('policy_overload_drops_backlog', 'def boundedPolicyIngressReady : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress events (admittedPolicyIngress limit events arrivals)', 'def boundedPolicyIngressReady : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    admittedPolicyIngress limit events arrivals'),
    ('policy_overload_prepends_arrivals', 'def boundedPolicyIngressReady : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress events (admittedPolicyIngress limit events arrivals)', 'def boundedPolicyIngressReady : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (events : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress (admittedPolicyIngress limit events arrivals) events'),
    ('policy_overload_drops_fuel', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))'),
    ('policy_overload_creates_fuel', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn (next fuel) (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))'),
    ('policy_overload_bypasses_admission', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel arrivals\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))'),
    ('policy_overload_drops_admitted', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel policyIngressDone\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))'),
    ('policy_overload_stale_queue', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          events)'),
    ('policy_overload_ignores_dispatch', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (boundedPolicyIngressReady limit events arrivals))'),
    ('policy_overload_resets_queue', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          (policyIngressPollRemainder fuel (boundedPolicyIngressReady limit events arrivals)))', 'def rec boundedPolicyIngressSchedule : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel (admittedPolicyIngress limit events arrivals)\n        (boundedPolicyIngressSchedule limit rest\n          policyIngressDone)'),
    ('policy_overload_runner_unbounded', 'def runBoundedPolicyIngress : Count -> PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    runPolicyIngressSchedule (boundedPolicyIngressSchedule limit schedule (queuedPolicyIngress queued)) config queued', 'def runBoundedPolicyIngress : Count -> PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    runPolicyIngressSchedule schedule config queued'),
    ('policy_overload_trace_unbounded', 'def boundedPolicyIngressTrace : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    policyIngressScheduleTrace (boundedPolicyIngressSchedule limit schedule events) events', 'def boundedPolicyIngressTrace : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    policyIngressScheduleTrace schedule events'),
    ('policy_overload_cost_erases_work', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost (boundedPolicyIngressSchedule limit schedule events) events config current eventCost policyCost handshakeCost', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost (boundedPolicyIngressSchedule limit schedule events) events config current eventCost zero handshakeCost'),
    ('policy_overload_cost_erases_handshakes', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost (boundedPolicyIngressSchedule limit schedule events) events config current eventCost policyCost handshakeCost', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost (boundedPolicyIngressSchedule limit schedule events) events config current eventCost policyCost zero'),
    ('policy_overload_limit_erases_dispatch', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config eventCost policyCost handshakeCost', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config zero policyCost handshakeCost'),
    ('policy_overload_limit_erases_policy', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config eventCost policyCost handshakeCost', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config eventCost zero handshakeCost'),
    ('policy_overload_limit_erases_handshakes', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config eventCost policyCost handshakeCost', 'def boundedPolicyIngressCostLimit : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCostLimit (boundedPolicyIngressSchedule limit schedule events) events config eventCost policyCost zero'),
    ('policy_overload_cost_unbounded', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost (boundedPolicyIngressSchedule limit schedule events) events config current eventCost policyCost handshakeCost', 'def boundedPolicyIngressCost : Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (limit : Count) (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    policyIngressScheduleCost schedule events config current eventCost policyCost handshakeCost'),
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
    ("admission_unowned_completion_refunds_live_slot", "| noAdmissionReceipt => current\n    | pendingAdmissionReceipt index generation => sourceAdmission", "| noAdmissionReceipt => sourceAdmission (admissionSources current) (admissionCredits current) (poolStep (completeAt zero (ownedGeneration zero) reason) (admissionPool current))\n    | pendingAdmissionReceipt index generation => sourceAdmission"),
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


MUTATIONS += [
    ("policy_queue_drops_backlog", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress events arrivals) current", "| policyIngressQueueState events current => policyIngressQueueState arrivals current"),
    ("policy_queue_arrivals_overtake_backlog", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress events arrivals) current", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress arrivals events) current"),
    ("policy_queue_drops_arrivals", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress events arrivals) current", "| policyIngressQueueState events current => policyIngressQueueState events current"),
    ("policy_queue_enqueue_regrants_work", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress events arrivals) current", "| policyIngressQueueState events current => policyIngressQueueState (appendPolicyIngress events arrivals) (policyWorkState (next (policyWorkCredits current)) (policyWorkSources current))"),
    ("policy_queue_poll_loses_remainder", "(policyIngressPollRemainder fuel events) (runPolicyIngressPoll fuel events config current)", "policyIngressDone (runPolicyIngressPoll fuel events config current)"),
    ("policy_queue_poll_replays_backlog", "(policyIngressPollRemainder fuel events) (runPolicyIngressPoll fuel events config current)", "events (runPolicyIngressPoll fuel events config current)"),
    ("policy_queue_poll_reuses_old_state", "(policyIngressPollRemainder fuel events) (runPolicyIngressPoll fuel events config current)", "(policyIngressPollRemainder fuel events) current"),
    ("policy_queue_poll_executes_extra_event", "(policyIngressPollRemainder fuel events) (runPolicyIngressPoll fuel events config current)", "(policyIngressPollRemainder fuel events) (runPolicyIngressPoll (next fuel) events config current)"),
    ("policy_queue_suppresses_wake", "fun (queued : PolicyIngressQueueState) => policyIngressBacklogWake (queuedPolicyIngress queued)", "fun (queued : PolicyIngressQueueState) => off"),
    ("policy_queue_wakes_empty_queue", "fun (queued : PolicyIngressQueueState) => policyIngressBacklogWake (queuedPolicyIngress queued)", "fun (queued : PolicyIngressQueueState) => on"),
    ("policy_queue_round_has_zero_fuel", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        (pollPolicyIngressQueue (next zero) config (enqueuePolicyIngress (arrivals zero) queued))", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        (pollPolicyIngressQueue zero config (enqueuePolicyIngress (arrivals zero) queued))"),
    ("policy_queue_round_ignores_arrivals", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        (pollPolicyIngressQueue (next zero) config (enqueuePolicyIngress (arrivals zero) queued))", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        (pollPolicyIngressQueue (next zero) config queued)"),
    ("policy_queue_round_keeps_old_snapshot", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        (pollPolicyIngressQueue (next zero) config (enqueuePolicyIngress (arrivals zero) queued))", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config\n        queued"),
    ("policy_queue_reuses_arrival_batch", "| next remaining => runPolicyIngressQueueRounds remaining (policyIngressLaterArrivals arrivals) config", "| next remaining => runPolicyIngressQueueRounds remaining arrivals config"),
    ("policy_queue_arrival_index_does_not_advance", "fun (arrivals : Count -> PolicyIngressTrace) (round : Count) => arrivals (next round)", "fun (arrivals : Count -> PolicyIngressTrace) (round : Count) => arrivals round"),
    ("policy_queue_arrival_history_drops_batch", "| next remaining => appendPolicyIngress (arrivals zero) (policyIngressArrivalsThrough remaining (policyIngressLaterArrivals arrivals))", "| next remaining => policyIngressArrivalsThrough remaining (policyIngressLaterArrivals arrivals)"),
    ("policy_queue_arrival_history_reorders_batches", "| next remaining => appendPolicyIngress (arrivals zero) (policyIngressArrivalsThrough remaining (policyIngressLaterArrivals arrivals))", "| next remaining => appendPolicyIngress (policyIngressArrivalsThrough remaining (policyIngressLaterArrivals arrivals)) (arrivals zero)"),
    ("policy_queue_trace_drops_dispatch", "| next remaining => appendPolicyIngress (policyIngressPollPrefix (next zero) (appendPolicyIngress events (arrivals zero)))", "| next remaining => appendPolicyIngress policyIngressDone"),
    ("policy_queue_cost_omits_dispatch", "add (multiply (policyIngressLength (policyIngressQueueTrace rounds arrivals events)) eventCost)\n      (add", "add zero\n      (add"),
    ("policy_queue_cost_limit_drops_dispatch", "add (multiply rounds eventCost)\n      (add (multiply (add (workCapacity config)", "add zero\n      (add (multiply (add (workCapacity config)"),
    # Arbitrary delivered fuel schedules and conditional FIFO prefix service.
    ('policy_schedule_counts_turns_as_fuel', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add fuel (policyIngressScheduleFuel rest)', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => next (policyIngressScheduleFuel rest)'),
    ('policy_schedule_drops_later_fuel', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add fuel (policyIngressScheduleFuel rest)', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => fuel'),
    ('policy_schedule_inflates_fuel', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add fuel (policyIngressScheduleFuel rest)', 'def rec policyIngressScheduleFuel : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add (next fuel) (policyIngressScheduleFuel rest)'),
    ('policy_schedule_drops_arrival_batch', 'def rec policyIngressScheduleArrivals : PolicyIngressSchedule -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress arrivals (policyIngressScheduleArrivals rest)', 'def rec policyIngressScheduleArrivals : PolicyIngressSchedule -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => policyIngressScheduleArrivals rest'),
    ('policy_schedule_reverses_arrival_batches', 'def rec policyIngressScheduleArrivals : PolicyIngressSchedule -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress arrivals (policyIngressScheduleArrivals rest)', 'def rec policyIngressScheduleArrivals : PolicyIngressSchedule -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress (policyIngressScheduleArrivals rest) arrivals'),
    ('policy_schedule_drops_terminal_queue', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => policyIngressQueueState policyIngressDone (queuedPolicyWork queued)\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))'),
    ('policy_schedule_skips_turn', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        queued'),
    ('policy_schedule_fixes_fuel_at_one', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue (next zero) config (enqueuePolicyIngress arrivals queued))'),
    ('policy_schedule_duplicates_arrivals', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress (appendPolicyIngress arrivals arrivals) queued))'),
    ('policy_schedule_keeps_old_resource_state', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', 'def rec runPolicyIngressSchedule : PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressQueueState -> PolicyIngressQueueState :=\n  fun (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (queued : PolicyIngressQueueState) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressQueueState with\n    | policyIngressScheduleDone => queued\n    | policyIngressTurn fuel arrivals rest => runPolicyIngressSchedule rest config\n        (policyIngressQueueState (policyIngressPollRemainder fuel (appendPolicyIngress (queuedPolicyIngress queued) arrivals)) (queuedPolicyWork queued))'),
    ('policy_schedule_trace_drops_later_dispatch', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        policyIngressDone\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events'),
    ('policy_schedule_trace_drops_continuation', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressDone))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events'),
    ('policy_schedule_trace_takes_unfueled_events', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (appendPolicyIngress events arrivals)\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events'),
    ('policy_schedule_trace_replays_prefix', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events', 'def rec policyIngressScheduleTrace : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (appendPolicyIngress events arrivals))\n\n-- A prefix witness contains the exact ordered suffix, not just a length bound.\nmu PolicyIngressPrefix (0 prefix : PolicyIngressTrace) (0 events : PolicyIngressTrace) : Type 0 with\n| policyIngressPrefixWitness : (suffix : PolicyIngressTrace) ->\n    Equal PolicyIngressTrace (appendPolicyIngress prefix suffix) events -> PolicyIngressPrefix prefix events'),
    ('policy_schedule_service_suffix_is_initial_suffix', 'def policyIngressScheduleServiceSuffix : (schedule : PolicyIngressSchedule) -> (prefix : PolicyIngressTrace) ->\n    (suffix : PolicyIngressTrace) -> (slack : Count) ->\n    Equal Count (policyIngressScheduleFuel schedule) (add (policyIngressLength prefix) slack) -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (prefix : PolicyIngressTrace) (suffix : PolicyIngressTrace) (slack : Count)\n      (enough : Equal Count (policyIngressScheduleFuel schedule) (add (policyIngressLength prefix) slack)) =>\n    policyIngressPrefixSuffix prefix (policyIngressScheduleTrace schedule (appendPolicyIngress prefix suffix))\n      (policyIngressScheduleServesPrefix schedule prefix suffix slack enough)', 'def policyIngressScheduleServiceSuffix : (schedule : PolicyIngressSchedule) -> (prefix : PolicyIngressTrace) ->\n    (suffix : PolicyIngressTrace) -> (slack : Count) ->\n    Equal Count (policyIngressScheduleFuel schedule) (add (policyIngressLength prefix) slack) -> PolicyIngressTrace :=\n  fun (schedule : PolicyIngressSchedule) (prefix : PolicyIngressTrace) (suffix : PolicyIngressTrace) (slack : Count)\n      (enough : Equal Count (policyIngressScheduleFuel schedule) (add (policyIngressLength prefix) slack)) =>\n    suffix'),
    ('policy_schedule_unit_arrivals_repeat_first_batch', 'def rec policyIngressUnitSchedule : Count -> (Count -> PolicyIngressTrace) -> PolicyIngressSchedule :=\n  fun (rounds : Count) (arrivals : Count -> PolicyIngressTrace) =>\n    case rounds as self in Count return PolicyIngressSchedule with\n    | zero => policyIngressScheduleDone\n    | next remaining => policyIngressTurn (next zero) (arrivals zero) (policyIngressUnitSchedule remaining (policyIngressLaterArrivals arrivals))', 'def rec policyIngressUnitSchedule : Count -> (Count -> PolicyIngressTrace) -> PolicyIngressSchedule :=\n  fun (rounds : Count) (arrivals : Count -> PolicyIngressTrace) =>\n    case rounds as self in Count return PolicyIngressSchedule with\n    | zero => policyIngressScheduleDone\n    | next remaining => policyIngressTurn (next zero) (arrivals zero) (policyIngressUnitSchedule remaining (arrivals))'),
    ('policy_schedule_guard_dispatch_is_free', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressLength (policyIngressScheduleTrace schedule events)) eventCost)\n      (add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) policyCost)\n        (multiply (policyIngressStarts (policyIngressScheduleTrace schedule events) config current) handshakeCost))', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) eventCost)\n      (add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) policyCost)\n        (multiply (policyIngressStarts (policyIngressScheduleTrace schedule events) config current) handshakeCost))'),
    ('policy_schedule_drops_policy_cost', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressLength (policyIngressScheduleTrace schedule events)) eventCost)\n      (add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) policyCost)\n        (multiply (policyIngressStarts (policyIngressScheduleTrace schedule events) config current) handshakeCost))', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressLength (policyIngressScheduleTrace schedule events)) eventCost)\n      (add (zero)\n        (multiply (policyIngressStarts (policyIngressScheduleTrace schedule events) config current) handshakeCost))'),
    ('policy_schedule_drops_handshake_cost', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressLength (policyIngressScheduleTrace schedule events)) eventCost)\n      (add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) policyCost)\n        (multiply (policyIngressStarts (policyIngressScheduleTrace schedule events) config current) handshakeCost))', 'def policyIngressScheduleCost : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig) (current : PolicyWorkState)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressLength (policyIngressScheduleTrace schedule events)) eventCost)\n      (add (multiply (policyIngressProcessed (policyIngressScheduleTrace schedule events) config current) policyCost)\n        (zero))'),
    ('policy_schedule_limit_drops_dispatch', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressScheduleFuel schedule) eventCost)\n      (add (multiply (add (workCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config))) policyCost)\n        (multiply (add (workHandshakeCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config))) handshakeCost))', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (zero)\n      (add (multiply (add (workCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config))) policyCost)\n        (multiply (add (workHandshakeCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config))) handshakeCost))'),
    ('policy_schedule_limit_drops_work_burst', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressScheduleFuel schedule) eventCost)\n      (add (multiply (add (workCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config))) policyCost)\n        (multiply (add (workHandshakeCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config))) handshakeCost))', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressScheduleFuel schedule) eventCost)\n      (add (multiply (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config)) policyCost)\n        (multiply (add (workHandshakeCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config))) handshakeCost))'),
    ('policy_schedule_limit_drops_handshake_burst', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressScheduleFuel schedule) eventCost)\n      (add (multiply (add (workCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config))) policyCost)\n        (multiply (add (workHandshakeCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config))) handshakeCost))', 'def policyIngressScheduleCostLimit : PolicyIngressSchedule -> PolicyIngressTrace -> PolicyWorkConfig -> Count -> Count -> Count -> Count :=\n  fun (schedule : PolicyIngressSchedule) (events : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (multiply (policyIngressScheduleFuel schedule) eventCost)\n      (add (multiply (add (workCapacity config) (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workRate config))) policyCost)\n        (multiply (multiply (policyIngressTrustedTicks (policyIngressScheduleTrace schedule events)) (workHandshakeRate config)) handshakeCost))'),
    ('policy_schedule_polls_before_enqueue', '(pollPolicyIngressQueue fuel config (enqueuePolicyIngress arrivals queued))', '(enqueuePolicyIngress arrivals (pollPolicyIngressQueue fuel config queued))'),
    ('policy_schedule_trace_ignores_arrivals', '| policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel (appendPolicyIngress events arrivals))\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel (appendPolicyIngress events arrivals)))', '| policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (policyIngressPollPrefix fuel events)\n        (policyIngressScheduleTrace rest (policyIngressPollRemainder fuel events))'),
    ('policy_schedule_unit_turn_has_zero_fuel', '| next remaining => policyIngressTurn (next zero) (arrivals zero) (policyIngressUnitSchedule remaining (policyIngressLaterArrivals arrivals))', '| next remaining => policyIngressTurn zero (arrivals zero) (policyIngressUnitSchedule remaining (policyIngressLaterArrivals arrivals))'),
]

# Bounded deferred handoff: every control changes an executable definition.
MUTATIONS += [
    ("policy_deferred_prefix_replays_overflow", "def policyIngressDeferredPrefix : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollPrefix capacity events", "def policyIngressDeferredPrefix : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollRemainder capacity events"),
    ("policy_deferred_overflow_replays_prefix", "def policyIngressDeferredOverflow : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollRemainder capacity events", "def policyIngressDeferredOverflow : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollPrefix capacity events"),
    ("policy_deferred_capacity_inflated", "def policyIngressDeferredPrefix : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollPrefix capacity events", "def policyIngressDeferredPrefix : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollPrefix (next capacity) events"),
    ("policy_deferred_overflow_erased", "def policyIngressDeferredOverflow : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressPollRemainder capacity events", "def policyIngressDeferredOverflow : Count -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (events : PolicyIngressTrace) =>\n    policyIngressDone"),
    ("policy_resumed_offered_drops_deferred", "def boundedResumedPolicyIngressOffered : PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress deferred arrivals", "def boundedResumedPolicyIngressOffered : PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    arrivals"),
    ("policy_resumed_examined_bypasses_scan", "def boundedResumedPolicyIngressExamined : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    scannedPolicyIngress scanFuel (boundedResumedPolicyIngressOffered deferred arrivals)", "def boundedResumedPolicyIngressExamined : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    boundedResumedPolicyIngressOffered deferred arrivals"),
    ("policy_resumed_unexamined_erases_suffix", "def boundedResumedPolicyIngressUnexamined : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    unscannedPolicyIngress scanFuel (boundedResumedPolicyIngressOffered deferred arrivals)", "def boundedResumedPolicyIngressUnexamined : Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDone"),
    ("policy_resumed_deferred_uses_examined", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals)", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)"),
    ("policy_resumed_overflow_replays_deferred", "def boundedResumedPolicyIngressOverflow : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredOverflow capacity (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals)", "def boundedResumedPolicyIngressOverflow : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals)"),
    ("policy_resumed_fresh_overtakes_deferred", "def boundedResumedPolicyIngressOffered : PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress deferred arrivals", "def boundedResumedPolicyIngressOffered : PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    appendPolicyIngress arrivals deferred"),
    ("policy_resumed_deferred_always_empty", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals)", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDone"),
    ("policy_resumed_ready_drops_deferred", "    scannedPayloadIngressReady weight slots payloadLimit scanFuel events\n      (boundedResumedPolicyIngressOffered deferred arrivals)", "    scannedPayloadIngressReady weight slots payloadLimit scanFuel events arrivals"),
    ("policy_resumed_trace_skips_service_poll", "def boundedResumedPayloadIngressTrace : (weight : PolicyIngressEvent -> Count) -> (slots : Count) ->\n    (payloadLimit : Count) -> (scanFuel : Count) -> (fuel : Count) -> (events : PolicyIngressTrace) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> PolicyIngressTrace :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (scanFuel : Count)\n      (fuel : Count) (events : PolicyIngressTrace) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressPollPrefix fuel\n      (boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel events deferred arrivals)", "def boundedResumedPayloadIngressTrace : (weight : PolicyIngressEvent -> Count) -> (slots : Count) ->\n    (payloadLimit : Count) -> (scanFuel : Count) -> (fuel : Count) -> (events : PolicyIngressTrace) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> PolicyIngressTrace :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (scanFuel : Count)\n      (fuel : Count) (events : PolicyIngressTrace) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel events deferred arrivals"),
    ("policy_resumed_runner_drops_deferred", "        policyIngressResumeState\n          (boundedResumedPolicyIngressDeferred deferredCapacity scanFuel deferred arrivals)", "        policyIngressResumeState\n          policyIngressDone"),
    ("policy_resumed_runner_drops_queue_suffix", "          (policyIngressQueueState\n            (policyIngressPollRemainder fuel\n              (boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel\n                (queuedPolicyIngress queued) deferred arrivals))", "          (policyIngressQueueState\n            policyIngressDone"),
    ("policy_resumed_runner_skips_dispatch", "            (runPolicyIngressPoll fuel\n              (boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel\n                (queuedPolicyIngress queued) deferred arrivals)\n              config (queuedPolicyWork queued)))", "            (queuedPolicyWork queued))"),
    ("policy_resumed_runner_uses_scan_fuel", "            (runPolicyIngressPoll fuel\n              (boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel", "            (runPolicyIngressPoll scanFuel\n              (boundedResumedPayloadIngressReady weight slots payloadLimit scanFuel"),
    ("policy_resumed_ready_bypasses_scan", "    scannedPayloadIngressReady weight slots payloadLimit scanFuel events\n      (boundedResumedPolicyIngressOffered deferred arrivals)", "    payloadIngressReady weight slots payloadLimit events\n      (boundedResumedPolicyIngressOffered deferred arrivals)"),
    ("policy_resumed_cost_omits_overflow", "def boundedResumedPolicyIngressDispositionCost : (capacity : Count) -> (scanFuel : Count) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> (scanCost : Count) ->\n    (overflowCost : Count) -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace)\n      (scanCost : Count) (overflowCost : Count) =>\n    add\n      (multiply (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)) scanCost)\n      (multiply (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)) overflowCost)", "def boundedResumedPolicyIngressDispositionCost : (capacity : Count) -> (scanFuel : Count) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> (scanCost : Count) ->\n    (overflowCost : Count) -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace)\n      (scanCost : Count) (overflowCost : Count) =>\n    add\n      (multiply (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)) scanCost)\n      zero"),
    ("policy_resumed_cost_omits_scan", "def boundedResumedPolicyIngressDispositionCost : (capacity : Count) -> (scanFuel : Count) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> (scanCost : Count) ->\n    (overflowCost : Count) -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace)\n      (scanCost : Count) (overflowCost : Count) =>\n    add\n      (multiply (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)) scanCost)\n      (multiply (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)) overflowCost)", "def boundedResumedPolicyIngressDispositionCost : (capacity : Count) -> (scanFuel : Count) ->\n    (deferred : PolicyIngressTrace) -> (arrivals : PolicyIngressTrace) -> (scanCost : Count) ->\n    (overflowCost : Count) -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace)\n      (scanCost : Count) (overflowCost : Count) =>\n    add\n      zero\n      (multiply (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)) overflowCost)"),
    ("policy_deferred_handoff_loses_overflow", "    boundedPolicyIngressHandoff\n      (boundedResumedPolicyIngressOverflow deferredCapacity scanFuel (deferredPolicyIngress state) arrivals)", "    boundedPolicyIngressHandoff\n      policyIngressDone"),
    ("policy_deferred_handoff_keeps_old_state", "def handoffBoundedPayloadIngress : (weight : PolicyIngressEvent -> Count) -> (slots : Count) ->\n    (payloadLimit : Count) -> (deferredCapacity : Count) -> (scanFuel : Count) -> (fuel : Count) ->\n    (arrivals : PolicyIngressTrace) -> (config : PolicyWorkConfig) -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (deferredCapacity : Count)\n      (scanFuel : Count) (fuel : Count) (arrivals : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedResumedPolicyIngressOverflow deferredCapacity scanFuel (deferredPolicyIngress state) arrivals)\n      (runBoundedResumedPayloadIngress weight slots payloadLimit deferredCapacity scanFuel fuel arrivals config state)", "def handoffBoundedPayloadIngress : (weight : PolicyIngressEvent -> Count) -> (slots : Count) ->\n    (payloadLimit : Count) -> (deferredCapacity : Count) -> (scanFuel : Count) -> (fuel : Count) ->\n    (arrivals : PolicyIngressTrace) -> (config : PolicyWorkConfig) -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (deferredCapacity : Count)\n      (scanFuel : Count) (fuel : Count) (arrivals : PolicyIngressTrace) (config : PolicyWorkConfig)\n      (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedResumedPolicyIngressOverflow deferredCapacity scanFuel (deferredPolicyIngress state) arrivals)\n      state\n"),
    ("policy_deferred_handoff_reports_retained", "| boundedPolicyIngressHandoff overflow state => overflow", "| boundedPolicyIngressHandoff overflow state => deferredPolicyIngress state"),
    ("policy_deferred_handoff_drops_retained", "| boundedPolicyIngressHandoff overflow state => state", "| boundedPolicyIngressHandoff overflow state => policyIngressResumeState policyIngressDone (resumedPolicyIngressQueue state)"),
    ("policy_resumed_capacity_before_scan", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals)", "def boundedResumedPolicyIngressDeferred : Count -> Count -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (deferred : PolicyIngressTrace) (arrivals : PolicyIngressTrace) =>\n    policyIngressDeferredPrefix capacity (boundedResumedPolicyIngressOffered deferred arrivals)"),
]



MUTATIONS += [
    ('policy_handoff_schedule_scan_bypassed', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressOffered deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_fuel_erased', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_retained_input_erased', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          policyIngressDone)'),
    ('policy_handoff_schedule_overflow_replayed', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressUnexamined scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_stale_input_replayed', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          deferred)'),
    ('policy_handoff_schedule_terminal_deferred_resubmitted', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressSchedule : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressSchedule with\n    | policyIngressScheduleDone => policyIngressTurn zero deferred policyIngressScheduleDone\n    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scanFuel deferred arrivals)\n        (boundedDeferredIngressSchedule capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_empty_remainder_erased', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals)', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals)'),
    ('policy_handoff_schedule_capacity_inflated', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals)', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        (boundedResumedPolicyIngressDeferred (next capacity) scanFuel deferred arrivals)'),
    ('policy_handoff_schedule_remainder_stale', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals)', 'def rec boundedDeferredIngressRemainder : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => boundedDeferredIngressRemainder capacity scanFuel rest\n        deferred'),
    ('policy_handoff_schedule_empty_overflow_replays_deferred', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => deferred\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_first_overflow_erased', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        policyIngressDone\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_later_overflow_erased', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        policyIngressDone'),
    ('policy_handoff_schedule_overflow_order_reversed', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)'),
    ('policy_handoff_schedule_overflow_uses_stale_input', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressOverflow : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return PolicyIngressTrace with\n    | policyIngressScheduleDone => policyIngressDone\n    | policyIngressTurn fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)\n        (boundedDeferredIngressOverflow capacity scanFuel rest\n          deferred)'),
    ('policy_handoff_schedule_handoff_overflow_erased', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      policyIngressDone\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))'),
    ('policy_handoff_schedule_handoff_remainder_erased', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        policyIngressDone\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))'),
    ('policy_handoff_schedule_queue_slots_inflated', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight (next slots) payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))'),
    ('policy_handoff_schedule_payload_limit_inflated', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots (next payloadLimit)\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))'),
    ('policy_handoff_schedule_queue_execution_skipped', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', 'def runBoundedDeferredIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->\n    PolicyIngressSchedule -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=\n  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (scanFuel : Count) (schedule : PolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>\n    boundedPolicyIngressHandoff\n      (boundedDeferredIngressOverflow capacity scanFuel schedule (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (boundedDeferredIngressRemainder capacity scanFuel schedule (deferredPolicyIngress state))\n        (runPayloadIngress weight slots payloadLimit\n          policyIngressScheduleDone\n          config (resumedPolicyIngressQueue state)))'),
    ('policy_handoff_schedule_initial_deferred_skipped', '          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))', '          (boundedDeferredIngressSchedule capacity scanFuel schedule policyIngressDone)'),
    ('policy_handoff_schedule_queue_state_erased', '          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))', '          (boundedDeferredIngressSchedule capacity scanFuel schedule (deferredPolicyIngress state))\n          config (policyIngressQueueState policyIngressDone (queuedPolicyWork (resumedPolicyIngressQueue state)))))'),
    ('policy_handoff_schedule_accounting_terminal_erased', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_accounting_examined_erased', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add zero\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_accounting_overflow_erased', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          zero)\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))'),
    ('policy_handoff_schedule_accounting_stale_input', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          (boundedResumedPolicyIngressDeferred capacity scanFuel deferred arrivals))', 'def rec boundedDeferredIngressAccounted : Count -> Count -> PolicyIngressSchedule -> PolicyIngressTrace -> Count :=\n  fun (capacity : Count) (scanFuel : Count) (schedule : PolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => policyIngressLength deferred\n    | policyIngressTurn fuel arrivals rest => add\n        (add (policyIngressLength (boundedResumedPolicyIngressExamined scanFuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity scanFuel deferred arrivals)))\n        (boundedDeferredIngressAccounted capacity scanFuel rest\n          deferred)'),
    ('policy_handoff_schedule_arrivals_erased', 'def rec policyIngressScheduledArrivalCount : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add (policyIngressLength arrivals) (policyIngressScheduledArrivalCount rest)', 'def rec policyIngressScheduledArrivalCount : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add zero (policyIngressScheduledArrivalCount rest)'),
    ('policy_handoff_schedule_arrivals_duplicated', 'def rec policyIngressScheduledArrivalCount : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add (policyIngressLength arrivals) (policyIngressScheduledArrivalCount rest)', 'def rec policyIngressScheduledArrivalCount : PolicyIngressSchedule -> Count :=\n  fun (schedule : PolicyIngressSchedule) =>\n    case schedule as self in PolicyIngressSchedule return Count with\n    | policyIngressScheduleDone => zero\n    | policyIngressTurn fuel arrivals rest => add (add (policyIngressLength arrivals) (policyIngressLength arrivals)) (policyIngressScheduledArrivalCount rest)'),
    ('policy_handoff_service_omits_initial_deferred', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule policyIngressDone)'),
    ('policy_handoff_service_drops_scan_allowance', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity zero schedule deferred)'),
    ('policy_handoff_service_drops_capacity', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule zero scanFuel schedule deferred)'),
    ('policy_handoff_service_inflates_capacity', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule (next capacity) scanFuel schedule deferred)'),
    ('policy_handoff_service_inflates_scan_allowance', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity (next scanFuel) schedule deferred)'),
    ('policy_handoff_service_swaps_capacity_and_scan', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule scanFuel capacity schedule deferred)'),
    ('policy_handoff_service_replays_initial_deferred', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    appendPolicyIngress deferred (policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred))'),
    ('policy_handoff_service_reports_overflow_as_examined', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    boundedDeferredIngressOverflow capacity scanFuel schedule deferred'),
    ('policy_handoff_service_drops_first_examined', '    policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred)', '    policyIngressPollRemainder (next zero) (policyIngressScheduleArrivals (boundedDeferredIngressSchedule capacity scanFuel schedule deferred))'),
    ('policy_handoff_service_turn_count_missing', '    | policyIngressTurn fuel arrivals rest => next (policyIngressScheduleTurns rest)', '    | policyIngressTurn fuel arrivals rest => policyIngressScheduleTurns rest'),
    ('policy_handoff_service_turn_count_uses_dispatch_fuel', '    | policyIngressTurn fuel arrivals rest => next (policyIngressScheduleTurns rest)', '    | policyIngressTurn fuel arrivals rest => add fuel (policyIngressScheduleTurns rest)'),
    ('policy_handoff_service_turn_count_doubled', '    | policyIngressTurn fuel arrivals rest => next (policyIngressScheduleTurns rest)', '    | policyIngressTurn fuel arrivals rest => next (next (policyIngressScheduleTurns rest))'),
    ('policy_handoff_service_retained_suffix_uncapped', '    policyIngressPollPrefix (policyIngressFuelAfter capacity prefix) suffix', '    suffix'),
    ('policy_handoff_service_retained_suffix_ignores_prefix', '    policyIngressPollPrefix (policyIngressFuelAfter capacity prefix) suffix', '    policyIngressPollPrefix capacity suffix'),
    ('policy_handoff_service_retained_suffix_erased', '    policyIngressPollPrefix (policyIngressFuelAfter capacity prefix) suffix', '    policyIngressDone'),
    ('policy_handoff_service_service_suffix_erased', '    policyIngressPrefixSuffix prefix (boundedDeferredIngressExamined capacity (next zero) schedule (appendPolicyIngress prefix suffix))\n      (boundedDeferredIngressServesPrefix capacity schedule prefix suffix capacitySlack turnSlack fits enough)', '    policyIngressDone'),
    ('policy_handoff_service_unit_suffix_erased', '    policyIngressPrefixSuffix (policyIngressPollPrefix (policyIngressScheduleTurns schedule) prefix)\n      (boundedDeferredIngressExamined capacity (next zero) schedule (appendPolicyIngress prefix suffix))\n      (boundedDeferredIngressUnitPrefix capacity schedule prefix suffix slack fits)', '    policyIngressDone'),
    ('policy_handoff_service_example_drops_second_turn', '    policyIngressTurn zero (policyIngressThen fresh (policyIngressThen overflowA (policyIngressThen overflowB policyIngressDone)))\n      (policyIngressTurn zero policyIngressDone policyIngressScheduleDone)', '    policyIngressTurn zero (policyIngressThen fresh (policyIngressThen overflowA (policyIngressThen overflowB policyIngressDone)))\n      policyIngressScheduleDone'),
    ('policy_handoff_service_example_reorders_overflow', '    policyIngressTurn zero (policyIngressThen fresh (policyIngressThen overflowA (policyIngressThen overflowB policyIngressDone)))\n      (policyIngressTurn zero policyIngressDone policyIngressScheduleDone)', '    policyIngressTurn zero (policyIngressThen fresh (policyIngressThen overflowB (policyIngressThen overflowA policyIngressDone)))\n      (policyIngressTurn zero policyIngressDone policyIngressScheduleDone)'),
]


MUTATIONS += [
    ('policy_handoff_pauses_off_scans', 'def policyIngressScanAllowance : Flag -> Count :=\n  fun (scan : Flag) => case scan as self in Flag return Count with\n  | off => zero', 'def policyIngressScanAllowance : Flag -> Count :=\n  fun (scan : Flag) => case scan as self in Flag return Count with\n  | off => next zero'),
    ('policy_handoff_pauses_on_skips', '  | on => next zero\n\ndef rec pacedPolicyIngressScans', '  | on => zero\n\ndef rec pacedPolicyIngressScans'),
    ('policy_handoff_pauses_counts_paused_turns', '    | pacedPolicyIngressTurn scan fuel arrivals rest => add (policyIngressScanAllowance scan) (pacedPolicyIngressScans rest)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => next (pacedPolicyIngressScans rest)'),
    ('policy_handoff_pauses_omits_later_scans', '    | pacedPolicyIngressTurn scan fuel arrivals rest => add (policyIngressScanAllowance scan) (pacedPolicyIngressScans rest)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressScanAllowance scan'),
    ('policy_handoff_pauses_counts_dispatch_as_scan', '    | pacedPolicyIngressTurn scan fuel arrivals rest => add (policyIngressScanAllowance scan) (pacedPolicyIngressScans rest)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => add fuel (pacedPolicyIngressScans rest)'),
    ('policy_handoff_pauses_erases_dispatch', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn zero\n        (boundedResumedPolicyIngressExamined'),
    ('policy_handoff_pauses_input_erases_dispatch', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel arrivals (pacedPolicyIngressInput rest)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn zero arrivals (pacedPolicyIngressInput rest)'),
    ('policy_handoff_pauses_fresh_arrivals_first', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) arrivals deferred)'),
    ('policy_handoff_pauses_omits_initial_deferred', '    policyIngressScheduleArrivals (pacedDeferredIngressSchedule capacity schedule deferred)', '    policyIngressScheduleArrivals (pacedDeferredIngressSchedule capacity schedule policyIngressDone)'),
    ('policy_handoff_pauses_omits_fresh_arrivals', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred policyIngressDone)'),
    ('policy_handoff_pauses_replays_scanned', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity zero deferred arrivals))'),
    ('policy_handoff_pauses_drops_capacity', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred zero (policyIngressScanAllowance scan) deferred arrivals))'),
    ('policy_handoff_pauses_inflates_capacity', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))', '        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred (next capacity) (policyIngressScanAllowance scan) deferred arrivals))'),
    ('policy_handoff_pauses_terminal_remainder_erased', 'def rec pacedDeferredIngressRemainder : Count -> PacedPolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return PolicyIngressTrace with\n    | pacedPolicyIngressDone => deferred', 'def rec pacedDeferredIngressRemainder : Count -> PacedPolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace :=\n  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return PolicyIngressTrace with\n    | pacedPolicyIngressDone => policyIngressDone'),
    ('policy_handoff_pauses_remainder_replays_overflow', '    | pacedPolicyIngressTurn scan fuel arrivals rest => pacedDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => pacedDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)'),
    ('policy_handoff_pauses_overflow_erased', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        policyIngressDone'),
    ('policy_handoff_pauses_overflow_repeats_examined', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals)'),
    ('policy_handoff_pauses_overflow_reversed', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)\n        (pacedDeferredIngressOverflow capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))', '    | pacedPolicyIngressTurn scan fuel arrivals rest => appendPolicyIngress\n        (pacedDeferredIngressOverflow capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))\n        (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)'),
    ('policy_handoff_pauses_prefix_suffix_erased', '    policyIngressPrefixSuffix (policyIngressPollPrefix (pacedPolicyIngressScans schedule) prefix)\n      (pacedDeferredIngressExamined capacity schedule (appendPolicyIngress prefix suffix))\n      (pacedDeferredIngressPrefix capacity schedule prefix suffix slack fits)', '    policyIngressDone'),
    ('policy_handoff_pauses_service_suffix_erased', '    policyIngressPrefixSuffix prefix (pacedDeferredIngressExamined capacity schedule (appendPolicyIngress prefix suffix))\n      (pacedDeferredIngressServesPrefix capacity schedule prefix suffix capacitySlack scanSlack fits enough)', '    policyIngressDone'),
    ('policy_handoff_pauses_example_scans_during_pause', '    pacedPolicyIngressTurn off fuel (policyIngressThen earlyA (policyIngressThen earlyB policyIngressDone))', '    pacedPolicyIngressTurn on fuel (policyIngressThen earlyA (policyIngressThen earlyB policyIngressDone))'),
    ('policy_handoff_pauses_example_loses_last_scan', '          (pacedPolicyIngressTurn on fuel policyIngressDone pacedPolicyIngressDone)))', '          pacedPolicyIngressDone))'),
    ('policy_handoff_pauses_example_overflow_reordered', '    pacedPolicyIngressTurn off fuel (policyIngressThen earlyA (policyIngressThen earlyB policyIngressDone))', '    pacedPolicyIngressTurn off fuel (policyIngressThen earlyB (policyIngressThen earlyA policyIngressDone))'),
    ('policy_handoff_pauses_scan_bound_overclaims', 'AtMost (policyIngressLength (pacedDeferredIngressExamined capacity schedule deferred)) (pacedPolicyIngressScans schedule) :=', 'AtMost (policyIngressLength (pacedDeferredIngressExamined capacity schedule deferred)) zero :='),
    ('policy_handoff_pauses_remainder_inflates_capacity', '    | pacedPolicyIngressTurn scan fuel arrivals rest => pacedDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals)', '    | pacedPolicyIngressTurn scan fuel arrivals rest => pacedDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressDeferred (next capacity) (policyIngressScanAllowance scan) deferred arrivals)'),
]


MUTATIONS += [
    ("policy_paced_execution_drops_overflow",
     "    boundedPolicyIngressHandoff\n      (pacedDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      policyIngressDone"),
    ("policy_paced_execution_reports_retained",
     "    boundedPolicyIngressHandoff\n      (pacedDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      (pacedDeferredIngressRemainder capacity schedule (deferredPolicyIngress state))"),
    ("policy_paced_execution_keeps_old_deferred",
     "        (pacedDeferredIngressRemainder capacity schedule (deferredPolicyIngress state))",
     "        (deferredPolicyIngress state)"),
    ("policy_paced_execution_drops_queue_work",
     "        (runPayloadIngress weight slots payloadLimit\n          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state))",
     "        (resumedPolicyIngressQueue state)"),
    ("policy_paced_execution_bypasses_scan",
     "          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "          (pacedPolicyIngressInput schedule)"),
    ("policy_paced_execution_erases_queue",
     "          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n          config (resumedPolicyIngressQueue state)))",
     "          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n          config (policyIngressQueueState policyIngressDone (queuedPolicyWork (resumedPolicyIngressQueue state)))))"),
    ("policy_paced_execution_changes_capacity",
     "          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "          (pacedDeferredIngressSchedule (next capacity) schedule (deferredPolicyIngress state))"),
    ("policy_paced_execution_ignores_deferred",
     "          (pacedDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "          (pacedDeferredIngressSchedule capacity schedule policyIngressDone)"),
    ("policy_paced_execution_grows_slots",
     "        (runPayloadIngress weight slots payloadLimit\n          (pacedDeferredIngressSchedule",
     "        (runPayloadIngress weight (next slots) payloadLimit\n          (pacedDeferredIngressSchedule"),
    ("policy_paced_execution_grows_payload",
     "        (runPayloadIngress weight slots payloadLimit\n          (pacedDeferredIngressSchedule",
     "        (runPayloadIngress weight slots (next payloadLimit)\n          (pacedDeferredIngressSchedule"),
    ("policy_paced_execution_erases_empty_accounting",
     "    | pacedPolicyIngressDone => policyIngressLength deferred",
     "    | pacedPolicyIngressDone => zero"),
    ("policy_paced_execution_drops_examined_count",
     "        (add (policyIngressLength (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)))",
     "        (policyIngressLength (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals))"),
    ("policy_paced_execution_drops_overflow_count",
     "        (add (policyIngressLength (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)))",
     "        (policyIngressLength (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals))"),
    ("policy_paced_execution_recounts_old_deferred",
     "        (pacedDeferredIngressAccounted capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "        (pacedDeferredIngressAccounted capacity rest deferred)"),
    ("policy_paced_execution_drops_accounting_tail",
     "        (pacedDeferredIngressAccounted capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "        zero"),
    ("policy_paced_execution_overclaims_cost",
     "      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost) :=",
     "      zero :="),
    ("policy_paced_execution_overflow_ignores_deferred",
     "    boundedPolicyIngressHandoff\n      (pacedDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      (pacedDeferredIngressOverflow capacity schedule policyIngressDone)"),
    ("policy_paced_execution_accounts_examined_with_fuel",
     "        (add (policyIngressLength (boundedResumedPolicyIngressExamined (policyIngressScanAllowance scan) deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)))",
     "        (add (policyIngressLength (boundedResumedPolicyIngressExamined fuel deferred arrivals))\n          (policyIngressLength (boundedResumedPolicyIngressOverflow capacity (policyIngressScanAllowance scan) deferred arrivals)))"),
    ("policy_paced_cost_turn_not_counted",
     "  fun (schedule : PacedPolicyIngressSchedule) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => next (pacedPolicyIngressTurns rest)",
     "  fun (schedule : PacedPolicyIngressSchedule) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => pacedPolicyIngressTurns rest"),
    ("policy_paced_cost_visits_omit_deferred",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (policyIngressLength arrivals)\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))"),
    ("policy_paced_cost_visits_omit_arrivals",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (policyIngressLength deferred)\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))"),
    ("policy_paced_cost_visits_stop_early",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        zero"),
    ("policy_paced_cost_visits_reuse_initial",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          deferred)"),
    ("policy_paced_cost_visits_force_scan",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (next zero) deferred arrivals))"),
    ("policy_paced_cost_visits_inflate_capacity",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred (next capacity) (policyIngressScanAllowance scan) deferred arrivals))"),
    ("policy_paced_cost_limit_ignores_initial",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add initial (policyIngressLength arrivals))\n        (pacedDeferredIngressVisitLimit capacity rest capacity)",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (policyIngressLength arrivals)\n        (pacedDeferredIngressVisitLimit capacity rest capacity)"),
    ("policy_paced_cost_limit_ignores_arrivals",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add initial (policyIngressLength arrivals))\n        (pacedDeferredIngressVisitLimit capacity rest capacity)",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        initial\n        (pacedDeferredIngressVisitLimit capacity rest capacity)"),
    ("policy_paced_cost_limit_ignores_retention",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add initial (policyIngressLength arrivals))\n        (pacedDeferredIngressVisitLimit capacity rest capacity)",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (initial : Count) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add initial (policyIngressLength arrivals))\n        (pacedDeferredIngressVisitLimit capacity rest zero)"),
    ("policy_paced_cost_scan_weight_erased",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (scanCost : Count) =>\n    multiply (policyIngressLength (pacedDeferredIngressExamined capacity schedule deferred)) scanCost",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (scanCost : Count) =>\n    multiply (policyIngressLength (pacedDeferredIngressExamined capacity schedule deferred)) zero"),
    ("policy_paced_cost_scan_counts_allowance",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (scanCost : Count) =>\n    multiply (policyIngressLength (pacedDeferredIngressExamined capacity schedule deferred)) scanCost",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (scanCost : Count) =>\n    multiply (pacedPolicyIngressScans schedule) scanCost"),
    ("policy_paced_cost_admin_omits_scan",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (pacedDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (pacedDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add zero\n      (add (multiply (pacedDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))"),
    ("policy_paced_cost_admin_omits_handoff",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (pacedDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (pacedDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (pacedDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add zero\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))"),
    ("policy_paced_cost_admin_omits_turn",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (pacedDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (pacedDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (pacedDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (pacedDeferredIngressVisits capacity schedule deferred) handoffCost)\n        zero)"),
    ("policy_paced_cost_admin_limit_omits_scan",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (multiply (pacedPolicyIngressScans schedule) scanCost)\n      (add (multiply (pacedDeferredIngressVisitLimit capacity schedule (policyIngressLength deferred)) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add zero\n      (add (multiply (pacedDeferredIngressVisitLimit capacity schedule (policyIngressLength deferred)) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))"),
    ("policy_paced_cost_admin_limit_omits_handoff",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (multiply (pacedPolicyIngressScans schedule) scanCost)\n      (add (multiply (pacedDeferredIngressVisitLimit capacity schedule (policyIngressLength deferred)) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (multiply (pacedPolicyIngressScans schedule) scanCost)\n      (add zero\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))"),
    ("policy_paced_cost_admin_limit_omits_turn",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (multiply (pacedPolicyIngressScans schedule) scanCost)\n      (add (multiply (pacedDeferredIngressVisitLimit capacity schedule (policyIngressLength deferred)) handoffCost)\n        (multiply (pacedPolicyIngressTurns schedule) turnCost))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace)\n      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>\n    add (multiply (pacedPolicyIngressScans schedule) scanCost)\n      (add (multiply (pacedDeferredIngressVisitLimit capacity schedule (policyIngressLength deferred)) handoffCost)\n        zero)"),
    ("policy_paced_cost_total_omits_admin",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)\n      (turnCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminCost capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config current eventCost policyCost handshakeCost)",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)\n      (turnCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add zero\n      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config current eventCost policyCost handshakeCost)"),
    ("policy_paced_cost_total_omits_execution",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)\n      (turnCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminCost capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config current eventCost policyCost handshakeCost)",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)\n      (turnCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminCost capacity schedule deferred scanCost handoffCost turnCost)\n      zero"),
    ("policy_paced_cost_total_limit_omits_admin",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count) (turnCost : Count)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count) (turnCost : Count)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add zero\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)"),
    ("policy_paced_cost_total_limit_omits_execution",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count) (turnCost : Count)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (pacedDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)",
     "  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)\n      (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) (events : PolicyIngressTrace)\n      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count) (turnCost : Count)\n      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>\n    add (pacedDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      zero"),
    ("policy_paced_cost_turn_charges_done",
     "  fun (schedule : PacedPolicyIngressSchedule) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => next (pacedPolicyIngressTurns rest)",
     "  fun (schedule : PacedPolicyIngressSchedule) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => next zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => next (pacedPolicyIngressTurns rest)"),
    ("policy_paced_cost_visits_charge_leftover",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => zero\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))",
     "  fun (capacity : Count) (schedule : PacedPolicyIngressSchedule) (deferred : PolicyIngressTrace) =>\n    case schedule as self in PacedPolicyIngressSchedule return Count with\n    | pacedPolicyIngressDone => policyIngressLength deferred\n    | pacedPolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (pacedDeferredIngressVisits capacity rest\n          (boundedResumedPolicyIngressDeferred capacity (policyIngressScanAllowance scan) deferred arrivals))"),
]



# Natural scan allowances, FIFO handoffs, execution and administrative work.
MUTATIONS += [
    ("policy_variable_scans_count_uses_dispatch_fuel",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add scan (variablePolicyIngressScans rest)\n",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add fuel (variablePolicyIngressScans rest)\n"),
    ("policy_variable_scans_count_clamps_to_one",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add scan (variablePolicyIngressScans rest)\n",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => next (variablePolicyIngressScans rest)\n"),
    ("policy_variable_scans_count_inflates_allowance",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add scan (variablePolicyIngressScans rest)\n",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add (next scan) (variablePolicyIngressScans rest)\n"),
    ("policy_variable_scans_input_rewrites_fuel",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel arrivals (variablePolicyIngressInput rest)",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => policyIngressTurn scan arrivals (variablePolicyIngressInput rest)"),
    ("policy_variable_scans_dispatch_uses_scans",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => policyIngressTurn fuel\n        (boundedResumedPolicyIngressExamined scan deferred arrivals)",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => policyIngressTurn scan\n        (boundedResumedPolicyIngressExamined scan deferred arrivals)"),
    ("policy_variable_scans_examination_clamps_to_one",
     "        (boundedResumedPolicyIngressExamined scan deferred arrivals)",
     "        (boundedResumedPolicyIngressExamined (next zero) deferred arrivals)"),
    ("policy_variable_scans_examination_exceeds_allowance",
     "        (boundedResumedPolicyIngressExamined scan deferred arrivals)",
     "        (boundedResumedPolicyIngressExamined (next scan) deferred arrivals)"),
    ("policy_variable_scans_fresh_arrivals_overtake_fifo",
     "        (boundedResumedPolicyIngressExamined scan deferred arrivals)",
     "        (boundedResumedPolicyIngressExamined scan arrivals deferred)"),
    ("policy_variable_scans_examination_loses_deferred",
     "        (boundedResumedPolicyIngressExamined scan deferred arrivals)",
     "        (boundedResumedPolicyIngressExamined scan policyIngressDone arrivals)"),
    ("policy_variable_scans_handoff_inflates_capacity",
     "        (variableDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals))\n",
     "        (variableDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred (next capacity) scan deferred arrivals))\n"),
    ("policy_variable_scans_handoff_replays_examined",
     "        (variableDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals))\n",
     "        (variableDeferredIngressSchedule capacity rest\n          (boundedResumedPolicyIngressDeferred capacity zero deferred arrivals))\n"),
    ("policy_variable_scans_stopped_drops_deferred",
     "| variablePolicyIngressDone => deferred",
     "| variablePolicyIngressDone => policyIngressDone"),
    ("policy_variable_scans_remainder_inflates_capacity",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => variableDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals)\n",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => variableDeferredIngressRemainder capacity rest\n        (boundedResumedPolicyIngressDeferred (next capacity) scan deferred arrivals)\n"),
    ("policy_variable_scans_overflow_erases_arrivals",
     "        (boundedResumedPolicyIngressOverflow capacity scan deferred arrivals)",
     "        (boundedResumedPolicyIngressOverflow capacity scan deferred policyIngressDone)"),
    ("policy_variable_scans_overflow_replays_examined",
     "        (boundedResumedPolicyIngressOverflow capacity scan deferred arrivals)",
     "        (boundedResumedPolicyIngressOverflow capacity zero deferred arrivals)"),
    ("policy_variable_scans_execution_drops_deferred",
     "          (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "          (variableDeferredIngressSchedule capacity schedule policyIngressDone)"),
    ("policy_variable_scans_execution_grows_slots",
     "        (runPayloadIngress weight slots payloadLimit\n          (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "        (runPayloadIngress weight (next slots) payloadLimit\n          (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))"),
    ("policy_variable_scans_execution_grows_payload",
     "        (runPayloadIngress weight slots payloadLimit\n          (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))",
     "        (runPayloadIngress weight slots (next payloadLimit)\n          (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))"),
    ("policy_variable_scans_visits_drop_initial_fifo",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (variableDeferredIngressVisits capacity rest",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (policyIngressLength arrivals)\n        (variableDeferredIngressVisits capacity rest"),
    ("policy_variable_scans_visits_drop_arrivals",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (add (policyIngressLength deferred) (policyIngressLength arrivals))\n        (variableDeferredIngressVisits capacity rest",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (policyIngressLength deferred)\n        (variableDeferredIngressVisits capacity rest"),
    ("policy_variable_scans_visit_limit_ignores_initial",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (add initial (policyIngressLength arrivals))\n        (variableDeferredIngressVisitLimit capacity rest capacity)",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => add\n        (add capacity (policyIngressLength arrivals))\n        (variableDeferredIngressVisitLimit capacity rest capacity)"),
    ("policy_variable_scans_visit_limit_omits_retention",
     "        (add initial (policyIngressLength arrivals))\n        (variableDeferredIngressVisitLimit capacity rest capacity)\n",
     "        (add initial (policyIngressLength arrivals))\n        (variableDeferredIngressVisitLimit capacity rest zero)\n"),
    ("policy_variable_scans_admin_omits_scan_work",
     "    add (variableDeferredIngressScanCost capacity schedule deferred scanCost)",
     "    add (zero)"),
    ("policy_variable_scans_admin_omits_handoff_work",
     "    add (variableDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (variableDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (variablePolicyIngressTurns schedule) turnCost))",
     "    add (variableDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (zero)\n        (multiply (variablePolicyIngressTurns schedule) turnCost))"),
    ("policy_variable_scans_admin_omits_turn_work",
     "    add (variableDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (variableDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (multiply (variablePolicyIngressTurns schedule) turnCost))\n\n",
     "    add (variableDeferredIngressScanCost capacity schedule deferred scanCost)\n      (add (multiply (variableDeferredIngressVisits capacity schedule deferred) handoffCost)\n        (zero))\n\n"),
    ("policy_variable_scans_scan_limit_understates_weight",
     "    add (multiply (variablePolicyIngressScans schedule) scanCost)",
     "    add (variablePolicyIngressScans schedule)"),
    ("policy_variable_scans_cost_omits_execution",
     "    add (variableDeferredIngressAdminCost capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit\n        (variableDeferredIngressSchedule capacity schedule deferred) events) events config current eventCost policyCost handshakeCost)\n",
     "    add (variableDeferredIngressAdminCost capacity schedule deferred scanCost handoffCost turnCost)\n      (zero)\n"),
    ("policy_variable_scans_turn_not_counted",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => next (variablePolicyIngressTurns rest)",
     "    | variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurns rest"),
    ("policy_variable_scans_execution_drops_overflow",
     "    boundedPolicyIngressHandoff\n      (variableDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      policyIngressDone"),
    ("policy_variable_scans_execution_reports_retained",
     "    boundedPolicyIngressHandoff\n      (variableDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      (variableDeferredIngressRemainder capacity schedule (deferredPolicyIngress state))"),
    ("policy_variable_scans_execution_overflow_ignores_deferred",
     "    boundedPolicyIngressHandoff\n      (variableDeferredIngressOverflow capacity schedule (deferredPolicyIngress state))",
     "    boundedPolicyIngressHandoff\n      (variableDeferredIngressOverflow capacity schedule policyIngressDone)"),
    ("policy_variable_scans_cost_limit_omits_execution",
     "    add (variableDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (variableDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)\n",
     "    add (variableDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      (zero)\n"),
    ("policy_variable_scans_cost_limit_omits_admin",
     "    add (variableDeferredIngressAdminLimit capacity schedule deferred scanCost handoffCost turnCost)\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (variableDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)\n",
     "    add (zero)\n      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit\n        (variableDeferredIngressSchedule capacity schedule deferred) events) events config eventCost policyCost handshakeCost)\n"),
]

_VARIABLE_ACCOUNTING_LEDGER = """def rec variableDeferredIngressLedger : Count -> VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressLedger :=
  fun (capacity : Count) (schedule : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) =>
    case schedule as self in VariablePolicyIngressSchedule return PolicyIngressLedger with
    | variablePolicyIngressDone => policyIngressLedgerDone waiting
    | variablePolicyIngressTurn scan fuel arrivals rest => policyIngressLedgerTurn
        (boundedResumedPolicyIngressExamined scan waiting arrivals)
        (policyIngressLength (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))
        (boundedResumedPolicyIngressOverflow capacity scan waiting arrivals)
        (variableDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))"""

MUTATIONS += [
    ('policy_accounting_splice_drops_overflow',
     '    | zero => appendPolicyIngress overflow continuation',
     '    | zero => continuation'),
    ('policy_accounting_splice_drops_continuation',
     '    | zero => appendPolicyIngress overflow continuation',
     '    | zero => overflow'),
    ('policy_accounting_splice_reverses_boundary',
     '    | zero => appendPolicyIngress overflow continuation',
     '    | zero => appendPolicyIngress continuation overflow'),
    ('policy_accounting_splice_drops_prefix_head',
     '        | policyIngressThen event rest => policyIngressThen event (insertPolicyIngressOverflow remaining overflow rest)',
     '        | policyIngressThen event rest => insertPolicyIngressOverflow remaining overflow rest'),
    ('policy_accounting_splice_loses_deep_overflow',
     '        | policyIngressThen event rest => policyIngressThen event (insertPolicyIngressOverflow remaining overflow rest)',
     '        | policyIngressThen event rest => policyIngressThen event (insertPolicyIngressOverflow remaining policyIngressDone rest)'),
    ('policy_accounting_splice_loses_deep_continuation',
     '        | policyIngressThen event rest => policyIngressThen event (insertPolicyIngressOverflow remaining overflow rest)',
     '        | policyIngressThen event rest => policyIngressThen event (insertPolicyIngressOverflow remaining overflow policyIngressDone)'),
    ('policy_accounting_examined_replays_terminal',
     '    | policyIngressLedgerDone waiting => policyIngressDone\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined (policyIngressLedgerExamined rest)',
     '    | policyIngressLedgerDone waiting => waiting\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined (policyIngressLedgerExamined rest)'),
    ('policy_accounting_examined_reverses_turns',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined (policyIngressLedgerExamined rest)',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress (policyIngressLedgerExamined rest) examined'),
    ('policy_accounting_examined_drops_current',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined (policyIngressLedgerExamined rest)',
     '    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerExamined rest'),
    ('policy_accounting_deferred_drops_terminal',
     '    | policyIngressLedgerDone waiting => waiting\n    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerDeferred rest',
     '    | policyIngressLedgerDone waiting => policyIngressDone\n    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerDeferred rest'),
    ('policy_accounting_deferred_reports_overflow',
     '    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerDeferred rest',
     '    | policyIngressLedgerTurn examined retained overflow rest => overflow'),
    ('policy_accounting_overflow_replays_terminal',
     '    | policyIngressLedgerDone waiting => policyIngressDone\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress overflow (policyIngressLedgerOverflow rest)',
     '    | policyIngressLedgerDone waiting => waiting\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress overflow (policyIngressLedgerOverflow rest)'),
    ('policy_accounting_overflow_reverses_turns',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress overflow (policyIngressLedgerOverflow rest)',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress (policyIngressLedgerOverflow rest) overflow'),
    ('policy_accounting_overflow_drops_current',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress overflow (policyIngressLedgerOverflow rest)',
     '    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerOverflow rest'),
    ('policy_accounting_chronology_drops_terminal',
     '    | policyIngressLedgerDone waiting => waiting\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined',
     '    | policyIngressLedgerDone waiting => policyIngressDone\n    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined'),
    ('policy_accounting_chronology_replays_overflow',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress examined\n        (insertPolicyIngressOverflow retained overflow (policyIngressLedgerChronological rest))',
     '    | policyIngressLedgerTurn examined retained overflow rest => appendPolicyIngress overflow\n        (insertPolicyIngressOverflow retained overflow (policyIngressLedgerChronological rest))'),
    ('policy_accounting_chronology_moves_boundary',
     '        (insertPolicyIngressOverflow retained overflow (policyIngressLedgerChronological rest))',
     '        (insertPolicyIngressOverflow zero overflow (policyIngressLedgerChronological rest))'),
    ('policy_accounting_chronology_erases_overflow',
     '        (insertPolicyIngressOverflow retained overflow (policyIngressLedgerChronological rest))',
     '        (insertPolicyIngressOverflow retained policyIngressDone (policyIngressLedgerChronological rest))'),
    ('policy_accounting_ledger_drops_terminal',
     '    | variablePolicyIngressDone => policyIngressLedgerDone waiting',
     '    | variablePolicyIngressDone => policyIngressLedgerDone policyIngressDone'),
    ('policy_accounting_ledger_uses_dispatch_fuel', _VARIABLE_ACCOUNTING_LEDGER, _VARIABLE_ACCOUNTING_LEDGER.replace('        (boundedResumedPolicyIngressExamined scan waiting arrivals)', '        (boundedResumedPolicyIngressExamined fuel waiting arrivals)')),
    ('policy_accounting_ledger_boundary_uses_capacity', _VARIABLE_ACCOUNTING_LEDGER, _VARIABLE_ACCOUNTING_LEDGER.replace('        (policyIngressLength (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '        capacity')),
    ('policy_accounting_ledger_erases_overflow',
     '        (boundedResumedPolicyIngressOverflow capacity scan waiting arrivals)\n        (variableDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))',
     '        policyIngressDone\n        (variableDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))'),
    ('policy_accounting_ledger_loses_carried_suffix', _VARIABLE_ACCOUNTING_LEDGER, _VARIABLE_ACCOUNTING_LEDGER.replace('        (variableDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '        (variableDeferredIngressLedger capacity rest policyIngressDone)')),
    ('policy_accounting_ledger_changes_capacity', _VARIABLE_ACCOUNTING_LEDGER, _VARIABLE_ACCOUNTING_LEDGER.replace('        (variableDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '        (variableDeferredIngressLedger zero rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))')),
    ('policy_accounting_splice_drops_short_overflow',
     '        | policyIngressDone => overflow',
     '        | policyIngressDone => policyIngressDone'),
]


MUTATIONS += [
    ('policy_composition_schedule_drops_second',
     '| variablePolicyIngressDone => second\n    | variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals',
     '| variablePolicyIngressDone => variablePolicyIngressDone\n    | variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals'),
    ('policy_composition_schedule_swaps_budgets',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn fuel scan arrivals\n        (appendVariablePolicyIngressSchedule rest second)'),
    ('policy_composition_schedule_erases_scan',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn zero fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)'),
    ('policy_composition_schedule_erases_fuel',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan zero arrivals\n        (appendVariablePolicyIngressSchedule rest second)'),
    ('policy_composition_schedule_erases_arrivals',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     '| variablePolicyIngressTurn scan fuel arrivals rest => variablePolicyIngressTurn scan fuel policyIngressDone\n        (appendVariablePolicyIngressSchedule rest second)'),
    ('policy_composition_schedule_drops_deep_second',
     'variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     'variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest variablePolicyIngressDone)'),
    ('policy_composition_schedule_drops_rest',
     'variablePolicyIngressTurn scan fuel arrivals\n        (appendVariablePolicyIngressSchedule rest second)',
     'variablePolicyIngressTurn scan fuel arrivals second'),
    ('policy_composition_ledger_keeps_old_terminal',
     '| policyIngressLedgerDone waiting => second\n    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained overflow',
     '| policyIngressLedgerDone waiting => policyIngressLedgerDone waiting\n    | policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained overflow'),
    ('policy_composition_ledger_erases_examined',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest second)',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn policyIngressDone retained overflow\n        (appendPolicyIngressLedger rest second)'),
    ('policy_composition_ledger_moves_boundary',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest second)',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined zero overflow\n        (appendPolicyIngressLedger rest second)'),
    ('policy_composition_ledger_erases_overflow',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest second)',
     '| policyIngressLedgerTurn examined retained overflow rest => policyIngressLedgerTurn examined retained policyIngressDone\n        (appendPolicyIngressLedger rest second)'),
    ('policy_composition_ledger_drops_rest',
     'policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest second)',
     'policyIngressLedgerTurn examined retained overflow second'),
    ('policy_composition_ledger_drops_deep_second',
     'policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest second)',
     'policyIngressLedgerTurn examined retained overflow\n        (appendPolicyIngressLedger rest (policyIngressLedgerDone (policyIngressLedgerDeferred rest)))'),
    ('policy_composition_first_erases_waiting',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first policyIngressDone)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))'),
    ('policy_composition_first_changes_capacity',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger (next capacity) first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))'),
    ('policy_composition_second_erases_waiting',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second policyIngressDone)'),
    ('policy_composition_second_replays_initial',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second waiting)'),
    ('policy_composition_second_uses_wrong_remainder',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity second waiting))'),
    ('policy_composition_second_changes_capacity',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger (next capacity) second (variableDeferredIngressRemainder capacity first waiting))'),
    ('policy_composition_second_drops_schedule',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity variablePolicyIngressDone (variableDeferredIngressRemainder capacity first waiting))'),
    ('policy_composition_second_replays_first',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity first (variableDeferredIngressRemainder capacity first waiting))'),
    ('policy_composition_remainder_changes_capacity',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder capacity first waiting))',
     'appendPolicyIngressLedger (variableDeferredIngressLedger capacity first waiting)\n      (variableDeferredIngressLedger capacity second (variableDeferredIngressRemainder (next capacity) first waiting))'),
]


# Complete execution and dispatch composition across schedule boundaries.
MUTATIONS += [
    ('policy_execution_empty_drops_second',
     '    | policyIngressScheduleDone => second',
     '    | policyIngressScheduleDone => policyIngressScheduleDone'),
    ('policy_execution_append_erases_fuel',
     '    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel arrivals',
     '    | policyIngressTurn fuel arrivals rest => policyIngressTurn zero arrivals'),
    ('policy_execution_append_erases_arrivals',
     '    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel arrivals',
     '    | policyIngressTurn fuel arrivals rest => policyIngressTurn fuel policyIngressDone'),
    ('policy_execution_append_drops_tail',
     '        (appendPolicyIngressSchedule rest second)',
     '        second'),
    ('policy_execution_overflow_reversed',
     '      (appendPolicyIngress (policyIngressHandoffOverflow first) (policyIngressHandoffOverflow second))',
     '      (appendPolicyIngress (policyIngressHandoffOverflow second) (policyIngressHandoffOverflow first))'),
    ('policy_execution_overflow_loses_first',
     '      (appendPolicyIngress (policyIngressHandoffOverflow first) (policyIngressHandoffOverflow second))',
     '      (policyIngressHandoffOverflow second)'),
    ('policy_execution_overflow_loses_second',
     '      (appendPolicyIngress (policyIngressHandoffOverflow first) (policyIngressHandoffOverflow second))',
     '      (policyIngressHandoffOverflow first)'),
    ('policy_execution_overflow_replays_first',
     '      (appendPolicyIngress (policyIngressHandoffOverflow first) (policyIngressHandoffOverflow second))',
     '      (appendPolicyIngress (policyIngressHandoffOverflow first) (appendPolicyIngress (policyIngressHandoffOverflow first) (policyIngressHandoffOverflow second)))'),
    ('policy_execution_returns_first_state',
     '      (policyIngressHandoffState second)',
     '      (policyIngressHandoffState first)'),
    ('policy_execution_restarts_initial_state',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        state)'),
    ('policy_execution_drops_deferred_boundary',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressResumeState policyIngressDone (resumedPolicyIngressQueue (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))))'),
    ('policy_execution_drops_queue_boundary',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressResumeState (deferredPolicyIngress (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state))) (policyIngressQueueState policyIngressDone (queuedPolicyWork (resumedPolicyIngressQueue (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))))))'),
    ('policy_execution_resets_work_boundary',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressResumeState (deferredPolicyIngress (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state))) (policyIngressQueueState (queuedPolicyIngress (resumedPolicyIngressQueue (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))) (queuedPolicyWork (resumedPolicyIngressQueue state)))))'),
    ('policy_execution_replays_first_schedule',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity first config'),
    ('policy_execution_first_changes_capacity',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity first config state)\n      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight slots payloadLimit zero first config state)\n      (runVariableDeferredIngress weight slots payloadLimit capacity second config'),
    ('policy_execution_second_changes_capacity',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight slots payloadLimit zero second config'),
    ('policy_execution_second_changes_slots',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight zero payloadLimit capacity second config'),
    ('policy_execution_second_changes_payload',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight slots zero capacity second config'),
    ('policy_execution_second_changes_weight',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress (fun (event : PolicyIngressEvent) => zero) slots payloadLimit capacity second config'),
    ('policy_execution_dispatch_drops_backlog',
     '      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n      (queuedPolicyIngress (resumedPolicyIngressQueue state))',
     '      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n      policyIngressDone'),
    ('policy_execution_dispatch_changes_capacity',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule zero schedule (deferredPolicyIngress state))'),
    ('policy_execution_dispatch_drops_schedule',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity variablePolicyIngressDone (deferredPolicyIngress state))'),
    ('policy_execution_dispatch_erased',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n      (queuedPolicyIngress (resumedPolicyIngressQueue state))',
     '    policyIngressDone'),
    ('policy_execution_dispatch_uses_examined',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))\n      (queuedPolicyIngress (resumedPolicyIngressQueue state))',
     '    variableDeferredIngressExamined capacity schedule (deferredPolicyIngress state)'),
    ('policy_execution_second_changes_config',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second (policyWorkConfig zero zero zero zero zero)'),
    ('policy_execution_boundary_changes_capacity',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity first config state)))',
     '      (runVariableDeferredIngress weight slots payloadLimit capacity second config\n        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit zero first config state)))'),
    ('policy_execution_dispatch_changes_slots',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))',
     '    payloadIngressTrace weight zero payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))'),
    ('policy_execution_dispatch_changes_payload',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))',
     '    payloadIngressTrace weight slots zero\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))'),
    ('policy_execution_dispatch_changes_weight',
     '    payloadIngressTrace weight slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))',
     '    payloadIngressTrace (fun (event : PolicyIngressEvent) => zero) slots payloadLimit\n      (variableDeferredIngressSchedule capacity schedule (deferredPolicyIngress state))'),
]


# Cost composition controls retain the universal theorem statements.
MUTATIONS += [
    ('policy_cost_composition_turns_forgets_tail',
     '(variablePolicyIngressTurnsAppend rest second)',
     '(variablePolicyIngressTurnsAppend rest rest)'),
    ('policy_cost_composition_visits_resets_deferred',
     '(variableDeferredIngressVisitsAppend capacity rest second (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals))',
     '(variableDeferredIngressVisitsAppend capacity rest second deferred)'),
    ('policy_cost_composition_visits_changes_capacity',
     '(variableDeferredIngressVisitsAppend capacity rest second (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals))',
     '(variableDeferredIngressVisitsAppend zero rest second (boundedResumedPolicyIngressDeferred capacity scan deferred arrivals))'),
    ('policy_cost_composition_examined_omits_second',
     '(variableDeferredIngressScheduleAppend capacity first second deferred)',
     '(variableDeferredIngressScheduleAppend capacity first variablePolicyIngressDone deferred)'),
    ('policy_cost_composition_examined_length_omits_second',
     '(variableDeferredIngressExaminedAppend capacity first second deferred)',
     '(variableDeferredIngressExaminedAppend capacity first first deferred)'),
    ('policy_cost_composition_admin_swaps_scan_handoff',
     '(variablePolicyIngressTurns first) (variablePolicyIngressTurns second) scanCost handoffCost turnCost)',
     '(variablePolicyIngressTurns first) (variablePolicyIngressTurns second) handoffCost scanCost turnCost)'),
    ('policy_cost_composition_processed_reuses_initial_state',
     '(policyIngressProcessedAppend rest second config (policyIngressStep config event current))',
     '(policyIngressProcessedAppend rest second config current)'),
    ('policy_cost_composition_starts_reuses_initial_state',
     '(policyIngressStartsAppend rest second config (policyIngressStep config event current))',
     '(policyIngressStartsAppend rest second config current)'),
    ('policy_cost_composition_boundary_reuses_initial_state',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config state)',
     'state'),
    ('policy_cost_composition_boundary_zero_capacity',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config state)',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit zero schedule config state)'),
    ('policy_cost_composition_boundary_zero_slots',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config state)',
     'policyIngressHandoffState (runVariableDeferredIngress weight zero payloadLimit capacity schedule config state)'),
    ('policy_cost_composition_boundary_zero_payload_limit',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config state)',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots zero capacity schedule config state)'),
    ('policy_cost_composition_boundary_omits_first',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config state)',
     'policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity variablePolicyIngressDone config state)'),
    ('policy_cost_composition_dispatch_erases_trace',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost policyCost handshakeCost',
     'policyIngressTraceCost policyIngressDone config (ingressCostWork state) eventCost policyCost handshakeCost'),
    ('policy_cost_composition_dispatch_erases_event_charge',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost policyCost handshakeCost',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) zero policyCost handshakeCost'),
    ('policy_cost_composition_dispatch_erases_policy_charge',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost policyCost handshakeCost',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost zero handshakeCost'),
    ('policy_cost_composition_dispatch_erases_handshake_charge',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost policyCost handshakeCost',
     'policyIngressTraceCost (variableDeferredIngressDispatched weight slots payloadLimit capacity schedule state)\n      config (ingressCostWork state) eventCost policyCost zero'),
    ('policy_cost_composition_execution_erases_deferred',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      policyIngressDone (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_queue',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) policyIngressDone config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_scanCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      zero handoffCost turnCost eventCost policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_handoffCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost zero turnCost eventCost policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_turnCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost zero eventCost policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_eventCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost zero policyCost handshakeCost'),
    ('policy_cost_composition_execution_erases_policyCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost zero handshakeCost'),
    ('policy_cost_composition_execution_erases_handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost handshakeCost',
     'variableDeferredIngressCost weight slots payloadLimit capacity schedule\n      (deferredPolicyIngress state) (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state)\n      scanCost handoffCost turnCost eventCost policyCost zero'),
    ('policy_cost_composition_execution_admin_omits_second',
     '(variableDeferredIngressAdminCostAppend capacity first second (deferredPolicyIngress state) scanCost handoffCost turnCost)',
     '(variableDeferredIngressAdminCostAppend capacity first variablePolicyIngressDone (deferredPolicyIngress state) scanCost handoffCost turnCost)'),
    ('policy_cost_composition_execution_dispatch_omits_second',
     '(variableDeferredIngressDispatchCostAppend weight slots payloadLimit capacity first second config state eventCost policyCost handshakeCost)',
     '(variableDeferredIngressDispatchCostAppend weight slots payloadLimit capacity first variablePolicyIngressDone config state eventCost policyCost handshakeCost)'),
    ('policy_cost_composition_envelope_omits_second',
     '(variableDeferredIngressCostEnvelope weight slots payloadLimit capacity (appendVariablePolicyIngressSchedule first second)',
     '(variableDeferredIngressCostEnvelope weight slots payloadLimit capacity first'),
    ('policy_cost_composition_envelope_erases_handoff_charge',
     'scanCost handoffCost turnCost eventCost policyCost handshakeCost workInitial handshakeInitial)',
     'scanCost zero turnCost eventCost policyCost handshakeCost workInitial handshakeInitial)'),
    ('policy_cost_composition_envelope_erases_policy_charge',
     'scanCost handoffCost turnCost eventCost policyCost handshakeCost workInitial handshakeInitial)',
     'scanCost handoffCost turnCost eventCost zero handshakeCost workInitial handshakeInitial)'),
    ('policy_cost_composition_dispatch_second_changes_weight',
     '        (variableDeferredIngressDispatchCost weight slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state) eventCost policyCost handshakeCost)) :=',
     '        (variableDeferredIngressDispatchCost (fun (event : PolicyIngressEvent) => zero) slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state) eventCost policyCost handshakeCost)) :='),
    ('policy_cost_composition_dispatch_second_changes_config',
     '        (variableDeferredIngressDispatchCost weight slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state) eventCost policyCost handshakeCost)) :=',
     '        (variableDeferredIngressDispatchCost weight slots payloadLimit capacity second (policyWorkConfig zero zero zero zero zero)\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state) eventCost policyCost handshakeCost)) :='),
    ('policy_cost_composition_execution_second_changes_weight',
     '        (variableDeferredIngressExecutionCost weight slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state)\n          scanCost handoffCost turnCost eventCost policyCost handshakeCost)) :=',
     '        (variableDeferredIngressExecutionCost (fun (event : PolicyIngressEvent) => zero) slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state)\n          scanCost handoffCost turnCost eventCost policyCost handshakeCost)) :='),
    ('policy_cost_composition_execution_second_changes_config',
     '        (variableDeferredIngressExecutionCost weight slots payloadLimit capacity second config\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state)\n          scanCost handoffCost turnCost eventCost policyCost handshakeCost)) :=',
     '        (variableDeferredIngressExecutionCost weight slots payloadLimit capacity second (policyWorkConfig zero zero zero zero zero)\n          (variableDeferredIngressCostBoundary weight slots payloadLimit capacity first config state)\n          scanCost handoffCost turnCost eventCost policyCost handshakeCost)) :='),
]

MUTATIONS += [
    ("policy_capacity_handoff_erases_boundary_overflow",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      policyIngressDone\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_reports_retained_as_overflow",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_skips_first_rejected",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow (next capacity) (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_reports_all_as_overflow",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (deferredPolicyIngress state)\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_retains_overflow",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_retains_above_capacity",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix (next capacity) (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_keeps_unbounded_input",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (deferredPolicyIngress state)\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_erases_retained",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        policyIngressDone\n        (resumedPolicyIngressQueue state))"),
    ("policy_capacity_handoff_erases_admitted_queue",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (resumedPolicyIngressQueue state))",
     "    boundedPolicyIngressHandoff\n      (policyIngressDeferredOverflow capacity (deferredPolicyIngress state))\n      (policyIngressResumeState\n        (policyIngressDeferredPrefix capacity (deferredPolicyIngress state))\n        (policyIngressQueueState policyIngressDone (queuedPolicyWork (resumedPolicyIngressQueue state))))"),
    ("policy_capacity_handoff_drops_boundary_when_resuming",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))",
     "      (appendPolicyIngress\n        policyIngressDone\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))"),
    ("policy_capacity_handoff_drops_later_overflow",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))",
     "      (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))"),
    ("policy_capacity_handoff_reverses_overflow_chronology",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state)))"),
    ("policy_capacity_handoff_overflows_from_original_input",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          state)))"),
    ("policy_capacity_handoff_overflow_uses_old_limit",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))",
     "      (appendPolicyIngress\n        (policyIngressHandoffOverflow (resizeDeferredPolicyIngress capacity state))\n        (policyIngressHandoffOverflow (runVariableDeferredIngress weight slots payloadLimit (next capacity) schedule config\n          (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state)))))"),
    ("policy_capacity_handoff_executes_original_input",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        state))\n\n"),
    ("policy_capacity_handoff_execution_changes_capacity",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit (next capacity) schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
    ("policy_capacity_handoff_execution_erases_schedule",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity variablePolicyIngressDone config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
    ("policy_capacity_handoff_execution_changes_slots",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight zero payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
    ("policy_capacity_handoff_execution_changes_payload_limit",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots zero capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
    ("policy_capacity_handoff_execution_changes_weight",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress (fun (event : PolicyIngressEvent) => zero) slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
    ("policy_capacity_handoff_execution_changes_config",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule config\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n",
     "      (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit capacity schedule (policyWorkConfig zero zero zero zero zero)\n        (policyIngressHandoffState (resizeDeferredPolicyIngress capacity state))))\n\n"),
]


_CAPACITY_ACCOUNTING_LEDGER = """def resizedDeferredIngressLedger : Count -> VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressLedger :=
  fun (capacity : Count) (schedule : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) =>
    policyIngressLedgerTurn policyIngressDone
      (policyIngressLength (policyIngressDeferredPrefix capacity waiting))
      (policyIngressDeferredOverflow capacity waiting)
      (variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))"""

MUTATIONS += [
    (f"policy_capacity_accounting_{name}", _CAPACITY_ACCOUNTING_LEDGER,
     _CAPACITY_ACCOUNTING_LEDGER.replace(before, after))
    for name, before, after in [
        ("examines_retained_at_boundary", "policyIngressLedgerTurn policyIngressDone",
         "policyIngressLedgerTurn (policyIngressDeferredPrefix capacity waiting)"),
        ("examines_original_at_boundary", "policyIngressLedgerTurn policyIngressDone",
         "policyIngressLedgerTurn waiting"),
        ("boundary_uses_capacity", "(policyIngressLength (policyIngressDeferredPrefix capacity waiting))", "capacity"),
        ("boundary_uses_zero", "(policyIngressLength (policyIngressDeferredPrefix capacity waiting))", "zero"),
        ("boundary_counts_original", "(policyIngressLength (policyIngressDeferredPrefix capacity waiting))", "(policyIngressLength waiting)"),
        ("erases_boundary_overflow", "(policyIngressDeferredOverflow capacity waiting)", "policyIngressDone"),
        ("reports_retained_as_overflow", "(policyIngressDeferredOverflow capacity waiting)", "(policyIngressDeferredPrefix capacity waiting)"),
        ("skips_first_rejected", "(policyIngressDeferredOverflow capacity waiting)", "(policyIngressDeferredOverflow (next capacity) waiting)"),
        ("reports_original_as_overflow", "(policyIngressDeferredOverflow capacity waiting)", "waiting"),
        ("continuation_replays_original", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger capacity schedule waiting)"),
        ("continuation_replays_overflow", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredOverflow capacity waiting))"),
        ("continuation_erases_retained", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger capacity schedule policyIngressDone)"),
        ("continuation_changes_limit", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger (next capacity) schedule (policyIngressDeferredPrefix capacity waiting))"),
        ("continuation_zero_limit", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger zero schedule (policyIngressDeferredPrefix capacity waiting))"),
        ("continuation_erases_schedule", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger capacity variablePolicyIngressDone (policyIngressDeferredPrefix capacity waiting))"),
        ("continuation_retains_extra", "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix capacity waiting))",
         "(variableDeferredIngressLedger capacity schedule (policyIngressDeferredPrefix (next capacity) waiting))"),
    ]
]


_CAPACITY_COMPOSITION_LEDGER = """def capacityComposedDeferredIngressLedger : Count -> Count -> VariablePolicyIngressSchedule ->
    VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressLedger :=
  fun (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) =>
    appendPolicyIngressLedger (variableDeferredIngressLedger oldCapacity first waiting)
      (resizedDeferredIngressLedger newCapacity second (variableDeferredIngressRemainder oldCapacity first waiting))"""

MUTATIONS += [
    (f"policy_capacity_composition_{name}", _CAPACITY_COMPOSITION_LEDGER,
     _CAPACITY_COMPOSITION_LEDGER.replace(before, after))
    for name, before, after in [
        ("drops_first_history", "(variableDeferredIngressLedger oldCapacity first waiting)", "(policyIngressLedgerDone waiting)"),
        ("first_uses_new_capacity", "(variableDeferredIngressLedger oldCapacity first waiting)", "(variableDeferredIngressLedger newCapacity first waiting)"),
        ("first_erases_schedule", "(variableDeferredIngressLedger oldCapacity first waiting)\n      (resizedDeferredIngressLedger newCapacity second (variableDeferredIngressRemainder oldCapacity first waiting))", "(variableDeferredIngressLedger oldCapacity variablePolicyIngressDone waiting)\n      (resizedDeferredIngressLedger newCapacity second (variableDeferredIngressRemainder oldCapacity variablePolicyIngressDone waiting))"),
        ("first_erases_waiting", "(variableDeferredIngressLedger oldCapacity first waiting)", "(variableDeferredIngressLedger oldCapacity first policyIngressDone)"),
        ("boundary_uses_old_capacity", "resizedDeferredIngressLedger newCapacity second", "resizedDeferredIngressLedger oldCapacity second"),
        ("boundary_uses_zero_capacity", "resizedDeferredIngressLedger newCapacity second", "resizedDeferredIngressLedger zero second"),
        ("boundary_erases_schedule", "resizedDeferredIngressLedger newCapacity second", "resizedDeferredIngressLedger newCapacity variablePolicyIngressDone"),
        ("boundary_replays_first_schedule", "resizedDeferredIngressLedger newCapacity second", "resizedDeferredIngressLedger newCapacity first"),
        ("boundary_replays_original", "(variableDeferredIngressRemainder oldCapacity first waiting)", "waiting"),
        ("boundary_drops_carried_suffix", "(variableDeferredIngressRemainder oldCapacity first waiting)", "policyIngressDone"),
        ("handoff_uses_new_capacity", "variableDeferredIngressRemainder oldCapacity first waiting", "variableDeferredIngressRemainder newCapacity first waiting"),
        ("boundary_omits_resize", "resizedDeferredIngressLedger newCapacity second", "variableDeferredIngressLedger newCapacity second"),
    ]
]



_CAPACITY_EXECUTION_SCHEDULE = """def capacityComposedIngressSchedule : Count -> Count -> VariablePolicyIngressSchedule ->
    VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressSchedule :=
  fun (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) =>
    appendPolicyIngressSchedule (variableDeferredIngressSchedule oldCapacity first waiting)
      (variableDeferredIngressSchedule newCapacity second
        (policyIngressDeferredPrefix newCapacity (variableDeferredIngressRemainder oldCapacity first waiting)))"""

_CAPACITY_EXECUTION_RUN = """def runCapacityComposedIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->
    VariablePolicyIngressSchedule -> VariablePolicyIngressSchedule -> PolicyWorkConfig ->
    PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count)
      (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>
    appendBoundedPolicyIngressHandoff
      (runVariableDeferredIngress weight slots payloadLimit oldCapacity first config state)
      (runResizedDeferredIngress weight slots payloadLimit newCapacity second config
        (policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit oldCapacity first config state)))"""

_CAPACITY_EXECUTION_DISPATCHED = """def capacityComposedIngressDispatched : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->
    VariablePolicyIngressSchedule -> VariablePolicyIngressSchedule -> PolicyIngressResumeState -> PolicyIngressTrace :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count)
      (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (state : PolicyIngressResumeState) =>
    payloadIngressTrace weight slots payloadLimit
      (capacityComposedIngressSchedule oldCapacity newCapacity first second (deferredPolicyIngress state))
      (queuedPolicyIngress (resumedPolicyIngressQueue state))"""

_CAPACITY_EXECUTION_MIDDLE = "(policyIngressHandoffState (runVariableDeferredIngress weight slots payloadLimit oldCapacity first config state))"
_CAPACITY_EXECUTION_RESET_QUEUE = "(policyIngressResumeState (deferredPolicyIngress " + _CAPACITY_EXECUTION_MIDDLE + ") (policyIngressQueueState policyIngressDone (ingressCostWork " + _CAPACITY_EXECUTION_MIDDLE + ")))"
_CAPACITY_EXECUTION_RESET_WORK = "(policyIngressResumeState (deferredPolicyIngress " + _CAPACITY_EXECUTION_MIDDLE + ") (policyIngressQueueState (queuedPolicyIngress (resumedPolicyIngressQueue " + _CAPACITY_EXECUTION_MIDDLE + ")) (ingressCostWork state)))"

MUTATIONS += [
    (f"policy_capacity_execution_{name}", _CAPACITY_EXECUTION_RUN,
     _CAPACITY_EXECUTION_RUN.replace(before, after))
    for name, before, after in [
        ("first_uses_new_capacity", "oldCapacity first config state", "newCapacity first config state"),
        ("first_erases_schedule", "oldCapacity first config state", "oldCapacity variablePolicyIngressDone config state"),
        ("first_erases_waiting", "first config state", "first config (policyIngressResumeState policyIngressDone (resumedPolicyIngressQueue state))"),
        ("boundary_uses_old_capacity", "newCapacity second config", "oldCapacity second config"),
        ("boundary_uses_zero_capacity", "newCapacity second config", "zero second config"),
        ("second_replays_first", "newCapacity second config", "newCapacity first config"),
        ("second_erases_schedule", "newCapacity second config", "newCapacity variablePolicyIngressDone config"),
        ("boundary_omits_resize", "runResizedDeferredIngress", "runVariableDeferredIngress"),
        ("boundary_restarts_original_state", _CAPACITY_EXECUTION_MIDDLE, "state"),
        ("boundary_discards_queue", _CAPACITY_EXECUTION_MIDDLE, _CAPACITY_EXECUTION_RESET_QUEUE),
        ("boundary_resets_resources", _CAPACITY_EXECUTION_MIDDLE, _CAPACITY_EXECUTION_RESET_WORK),
        ("drops_first_overflow", "appendBoundedPolicyIngressHandoff\n      (runVariableDeferredIngress weight slots payloadLimit oldCapacity first config state)", "appendBoundedPolicyIngressHandoff\n      (boundedPolicyIngressHandoff policyIngressDone state)"),
        ("second_changes_slots", "runResizedDeferredIngress weight slots payloadLimit newCapacity", "runResizedDeferredIngress weight zero payloadLimit newCapacity"),
        ("second_changes_payload", "runResizedDeferredIngress weight slots payloadLimit newCapacity", "runResizedDeferredIngress weight slots zero newCapacity"),
        ("second_changes_weight", "runResizedDeferredIngress weight slots payloadLimit newCapacity", "runResizedDeferredIngress (fun (event : PolicyIngressEvent) => zero) slots payloadLimit newCapacity"),
        ("second_changes_config", "newCapacity second config", "newCapacity second (policyWorkConfig zero zero zero zero zero)"),
    ]
]

MUTATIONS += [
    (f"policy_capacity_execution_{name}", _CAPACITY_EXECUTION_SCHEDULE,
     _CAPACITY_EXECUTION_SCHEDULE.replace(before, after))
    for name, before, after in [
        ("schedule_first_uses_new_capacity", "variableDeferredIngressSchedule oldCapacity first", "variableDeferredIngressSchedule newCapacity first"),
        ("schedule_second_uses_old_capacity", "variableDeferredIngressSchedule newCapacity second", "variableDeferredIngressSchedule oldCapacity second"),
        ("schedule_prefix_uses_old_capacity", "policyIngressDeferredPrefix newCapacity", "policyIngressDeferredPrefix oldCapacity"),
        ("schedule_restarts_waiting", "(variableDeferredIngressRemainder oldCapacity first waiting)", "waiting"),
        ("schedule_drops_first", "appendPolicyIngressSchedule (variableDeferredIngressSchedule oldCapacity first waiting)", "appendPolicyIngressSchedule policyIngressScheduleDone"),
    ]
]

MUTATIONS += [
    (f"policy_capacity_execution_{name}", _CAPACITY_EXECUTION_DISPATCHED,
     _CAPACITY_EXECUTION_DISPATCHED.replace(before, after))
    for name, before, after in [
        ("dispatch_drops_initial_queue", "(queuedPolicyIngress (resumedPolicyIngressQueue state))", "policyIngressDone"),
        ("dispatch_uses_zero_slots", "payloadIngressTrace weight slots payloadLimit", "payloadIngressTrace weight zero payloadLimit"),
        ("dispatch_uses_zero_payload", "payloadIngressTrace weight slots payloadLimit", "payloadIngressTrace weight slots zero"),
        ("dispatch_changes_weight", "payloadIngressTrace weight slots payloadLimit", "payloadIngressTrace (fun (event : PolicyIngressEvent) => zero) slots payloadLimit"),
        ("dispatch_swaps_capacities", "capacityComposedIngressSchedule oldCapacity newCapacity first", "capacityComposedIngressSchedule newCapacity oldCapacity first"),
        ("dispatch_drops_waiting", "first second (deferredPolicyIngress state)", "first second policyIngressDone"),
    ]
]



# Costs across one deferred-capacity boundary, including resize work.
_CAPACITY_COST_VISITS = """def deferredIngressResizeVisits : Count -> PolicyIngressTrace -> Count :=
  fun (capacity : Count) (waiting : PolicyIngressTrace) =>
    add (policyIngressLength (policyIngressDeferredPrefix capacity waiting))
      (policyIngressLength (policyIngressDeferredOverflow capacity waiting))"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_VISITS, _CAPACITY_COST_VISITS.replace(before, after))
    for name, before, after in [
        ("drops_retained", "(policyIngressLength (policyIngressDeferredPrefix capacity waiting))", "zero"),
        ("drops_overflow", "(policyIngressLength (policyIngressDeferredOverflow capacity waiting))", "zero"),
        ("counts_retained_twice", "policyIngressDeferredOverflow capacity waiting", "policyIngressDeferredPrefix capacity waiting"),
    ]
]

_CAPACITY_COST_RESIZE = """def deferredIngressResizeCost : Count -> PolicyIngressTrace -> Count -> Count -> Count :=
  fun (capacity : Count) (waiting : PolicyIngressTrace) (resizeCost : Count) (boundaryCost : Count) =>
    add (multiply (deferredIngressResizeVisits capacity waiting) resizeCost) boundaryCost"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_RESIZE, _CAPACITY_COST_RESIZE.replace(before, after))
    for name, before, after in [
        ("drops_visit_charge", "(multiply (deferredIngressResizeVisits capacity waiting) resizeCost)", "zero"),
        ("drops_boundary_charge", "resizeCost) boundaryCost", "resizeCost) zero"),
        ("uses_boundary_weight_for_visits", "waiting) resizeCost", "waiting) boundaryCost"),
    ]
]

_CAPACITY_COST_ADMIN = """def capacityComposedIngressAdminCost : Count -> Count -> VariablePolicyIngressSchedule ->
    VariablePolicyIngressSchedule -> PolicyIngressTrace -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) =>
    add (variableDeferredIngressAdminCost oldCapacity first waiting scanCost handoffCost turnCost)
      (add (deferredIngressResizeCost newCapacity (variableDeferredIngressRemainder oldCapacity first waiting)
          resizeCost boundaryCost)
        (variableDeferredIngressAdminCost newCapacity second
          (policyIngressDeferredPrefix newCapacity (variableDeferredIngressRemainder oldCapacity first waiting))
          scanCost handoffCost turnCost))"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_ADMIN, _CAPACITY_COST_ADMIN.replace(before, after))
    for name, before, after in [
        ("first_uses_new_capacity", "variableDeferredIngressAdminCost oldCapacity first", "variableDeferredIngressAdminCost newCapacity first"),
        ("drops_first_segment", "(variableDeferredIngressAdminCost oldCapacity first waiting scanCost handoffCost turnCost)", "zero"),
        ("resizes_initial_waiting", "deferredIngressResizeCost newCapacity (variableDeferredIngressRemainder oldCapacity first waiting)", "deferredIngressResizeCost newCapacity waiting"),
        ("drops_resize_visits", "resizeCost boundaryCost)", "zero boundaryCost)"),
        ("drops_second_segment", "variableDeferredIngressAdminCost newCapacity second", "variableDeferredIngressAdminCost newCapacity variablePolicyIngressDone"),
        ("second_uses_old_capacity", "variableDeferredIngressAdminCost newCapacity second", "variableDeferredIngressAdminCost oldCapacity second"),
        ("second_uses_untrimmed_input", "(policyIngressDeferredPrefix newCapacity (variableDeferredIngressRemainder oldCapacity first waiting))", "(variableDeferredIngressRemainder oldCapacity first waiting)"),
        ("second_replays_first", "variableDeferredIngressAdminCost newCapacity second", "variableDeferredIngressAdminCost newCapacity first"),
    ]
]

_CAPACITY_COST_ADMIN_LIMIT = """def capacityComposedIngressAdminLimit : Count -> Count -> VariablePolicyIngressSchedule ->
    VariablePolicyIngressSchedule -> PolicyIngressTrace -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) =>
    add (variableDeferredIngressAdminLimit oldCapacity first waiting scanCost handoffCost turnCost)
      (add (deferredIngressResizeCost newCapacity (variableDeferredIngressRemainder oldCapacity first waiting)
          resizeCost boundaryCost)
        (variableDeferredIngressAdminLimit newCapacity second
          (policyIngressDeferredPrefix newCapacity (variableDeferredIngressRemainder oldCapacity first waiting))
          scanCost handoffCost turnCost))"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_ADMIN_LIMIT, _CAPACITY_COST_ADMIN_LIMIT.replace(before, after))
    for name, before, after in [
        ("limit_drops_first_scan", "variableDeferredIngressAdminLimit oldCapacity first waiting scanCost", "variableDeferredIngressAdminLimit oldCapacity first waiting zero"),
        ("limit_drops_boundary_charge", "resizeCost boundaryCost)", "resizeCost zero)"),
        ("limit_drops_second_weights", "scanCost handoffCost turnCost))", "zero zero zero))"),
    ]
]

_CAPACITY_COST_EXECUTION = """def capacityComposedIngressCost : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->
    VariablePolicyIngressSchedule -> VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace ->
    PolicyWorkConfig -> PolicyWorkState -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count)
      (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) (events : PolicyIngressTrace)
      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)
      (turnCost : Count) (resizeCost : Count) (boundaryCost : Count)
      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    add (capacityComposedIngressAdminCost oldCapacity newCapacity first second waiting
        scanCost handoffCost turnCost resizeCost boundaryCost)
      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit
        (capacityComposedIngressSchedule oldCapacity newCapacity first second waiting) events)
        events config current eventCost policyCost handshakeCost)"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_EXECUTION, _CAPACITY_COST_EXECUTION.replace(before, after))
    for name, before, after in [
        ("execution_drops_admin", "scanCost handoffCost turnCost resizeCost boundaryCost)", "zero zero zero zero zero)"),
        ("execution_drops_dispatch", "events config current eventCost policyCost handshakeCost)", "events config current zero zero zero)"),
        ("execution_swaps_capacities", "capacityComposedIngressSchedule oldCapacity newCapacity", "capacityComposedIngressSchedule newCapacity oldCapacity"),
        ("execution_uses_zero_slots", "payloadIngressSchedule weight slots payloadLimit", "payloadIngressSchedule weight zero payloadLimit"),
        ("execution_uses_zero_payload", "payloadIngressSchedule weight slots payloadLimit", "payloadIngressSchedule weight slots zero"),
        ("execution_changes_weight", "payloadIngressSchedule weight slots payloadLimit", "payloadIngressSchedule (fun (event : PolicyIngressEvent) => zero) slots payloadLimit"),
        ("execution_drops_waiting", "first second waiting) events)", "first second policyIngressDone) events)"),
    ]
]

_CAPACITY_COST_LIMIT = """def capacityComposedIngressCostLimit : (PolicyIngressEvent -> Count) -> Count -> Count -> Count -> Count ->
    VariablePolicyIngressSchedule -> VariablePolicyIngressSchedule -> PolicyIngressTrace -> PolicyIngressTrace ->
    PolicyWorkConfig -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count)
      (oldCapacity : Count) (newCapacity : Count) (first : VariablePolicyIngressSchedule)
      (second : VariablePolicyIngressSchedule) (waiting : PolicyIngressTrace) (events : PolicyIngressTrace)
      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count)
      (turnCost : Count) (resizeCost : Count) (boundaryCost : Count)
      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    add (capacityComposedIngressAdminLimit oldCapacity newCapacity first second waiting
        scanCost handoffCost turnCost resizeCost boundaryCost)
      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit
        (capacityComposedIngressSchedule oldCapacity newCapacity first second waiting) events)
        events config eventCost policyCost handshakeCost)"""

MUTATIONS += [
    (f"policy_capacity_cost_{name}", _CAPACITY_COST_LIMIT, _CAPACITY_COST_LIMIT.replace(before, after))
    for name, before, after in [
        ("limit_drops_dispatch", "events config eventCost policyCost handshakeCost)", "events config zero zero zero)"),
        ("limit_drops_admin", "scanCost handoffCost turnCost resizeCost boundaryCost)", "zero zero zero zero zero)"),
    ]
]

_CAPACITY_SCHEDULE_LEDGER = """def rec capacityDeferredIngressLedger : Count -> PolicyIngressCapacitySchedule -> PolicyIngressTrace -> PolicyIngressLedger :=
  fun (capacity : Count) (schedule : PolicyIngressCapacitySchedule) (waiting : PolicyIngressTrace) =>
    case schedule as self in PolicyIngressCapacitySchedule return PolicyIngressLedger with
    | policyIngressCapacityDone => policyIngressLedgerDone waiting
    | policyIngressCapacityResize resized rest => policyIngressLedgerTurn policyIngressDone
        (policyIngressLength (policyIngressDeferredPrefix resized waiting))
        (policyIngressDeferredOverflow resized waiting)
        (capacityDeferredIngressLedger resized rest (policyIngressDeferredPrefix resized waiting))
    | policyIngressCapacityTurn scan arrivals rest => policyIngressLedgerTurn
        (boundedResumedPolicyIngressExamined scan waiting arrivals)
        (policyIngressLength (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))
        (boundedResumedPolicyIngressOverflow capacity scan waiting arrivals)
        (capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))"""
MUTATIONS += [
    (f"policy_capacity_schedule_{name}", _CAPACITY_SCHEDULE_LEDGER, _CAPACITY_SCHEDULE_LEDGER.replace(before, after))
    for name, before, after in [
        ('terminal_drops_waiting', 'policyIngressLedgerDone waiting', 'policyIngressLedgerDone policyIngressDone'),
        ('resize_examines_waiting', 'policyIngressLedgerTurn policyIngressDone', 'policyIngressLedgerTurn waiting'),
        ('resize_records_old_length', '(policyIngressLength (policyIngressDeferredPrefix resized waiting))', '(policyIngressLength waiting)'),
        ('resize_records_zero_length', '(policyIngressLength (policyIngressDeferredPrefix resized waiting))', 'zero'),
        ('resize_drops_overflow', '(policyIngressDeferredOverflow resized waiting)', 'policyIngressDone'),
        ('resize_reports_prefix', '(policyIngressDeferredOverflow resized waiting)', '(policyIngressDeferredPrefix resized waiting)'),
        ('resize_keeps_old_capacity', 'capacityDeferredIngressLedger resized rest', 'capacityDeferredIngressLedger capacity rest'),
        ('resize_truncates_at_old_capacity', 'resized waiting', 'capacity waiting'),
        ('resize_retains_rejected', '(capacityDeferredIngressLedger resized rest (policyIngressDeferredPrefix resized waiting))', '(capacityDeferredIngressLedger resized rest waiting)'),
        ('resize_replays_overflow', '(capacityDeferredIngressLedger resized rest (policyIngressDeferredPrefix resized waiting))', '(capacityDeferredIngressLedger resized rest (policyIngressDeferredOverflow resized waiting))'),
        ('resize_drops_continuation', '(capacityDeferredIngressLedger resized rest (policyIngressDeferredPrefix resized waiting))', '(policyIngressLedgerDone (policyIngressDeferredPrefix resized waiting))'),
        ('turn_skips_examination', '(boundedResumedPolicyIngressExamined scan waiting arrivals)', 'policyIngressDone'),
        ('turn_reverses_offered', '(boundedResumedPolicyIngressExamined scan waiting arrivals)', '(boundedResumedPolicyIngressExamined scan arrivals waiting)'),
        ('turn_records_capacity', '(policyIngressLength (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', 'capacity'),
        ('turn_drops_overflow', '(boundedResumedPolicyIngressOverflow capacity scan waiting arrivals)', 'policyIngressDone'),
        ('turn_drops_retained', '(capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '(capacityDeferredIngressLedger capacity rest policyIngressDone)'),
        ('turn_replays_overflow', '(capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '(capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressOverflow capacity scan waiting arrivals))'),
        ('turn_forgets_capacity', '(capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '(capacityDeferredIngressLedger zero rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))'),
        ('turn_polls_with_scan_capacity', 'capacity scan waiting arrivals', 'scan scan waiting arrivals'),
        ('turn_drops_continuation', '(capacityDeferredIngressLedger capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', '(policyIngressLedgerDone (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))'),
    ]
]

_CAPACITY_SCHEDULE_ARRIVALS = """def rec capacityScheduleArrivals : PolicyIngressCapacitySchedule -> PolicyIngressTrace :=
  fun (schedule : PolicyIngressCapacitySchedule) =>
    case schedule as self in PolicyIngressCapacitySchedule return PolicyIngressTrace with
    | policyIngressCapacityDone => policyIngressDone
    | policyIngressCapacityResize capacity rest => capacityScheduleArrivals rest
    | policyIngressCapacityTurn scan arrivals rest => appendPolicyIngress arrivals (capacityScheduleArrivals rest)"""
MUTATIONS += [
    (f"policy_capacity_schedule_{name}", _CAPACITY_SCHEDULE_ARRIVALS, _CAPACITY_SCHEDULE_ARRIVALS.replace(before, after))
    for name, before, after in [
        ('arrivals_drop_resize_tail', 'policyIngressCapacityResize capacity rest => capacityScheduleArrivals rest', 'policyIngressCapacityResize capacity rest => policyIngressDone'),
        ('arrivals_reverse_turns', 'appendPolicyIngress arrivals (capacityScheduleArrivals rest)', 'appendPolicyIngress (capacityScheduleArrivals rest) arrivals'),
        ('arrivals_drop_turn_batch', 'appendPolicyIngress arrivals (capacityScheduleArrivals rest)', 'capacityScheduleArrivals rest'),
    ]
]

_CAPACITY_SCHEDULE_LIMIT = """def rec capacityScheduleLimit : Count -> PolicyIngressCapacitySchedule -> Count :=
  fun (capacity : Count) (schedule : PolicyIngressCapacitySchedule) =>
    case schedule as self in PolicyIngressCapacitySchedule return Count with
    | policyIngressCapacityDone => capacity
    | policyIngressCapacityResize resized rest => capacityScheduleLimit resized rest
    | policyIngressCapacityTurn scan arrivals rest => capacityScheduleLimit capacity rest"""
MUTATIONS += [
    (f"policy_capacity_schedule_{name}", _CAPACITY_SCHEDULE_LIMIT, _CAPACITY_SCHEDULE_LIMIT.replace(before, after))
    for name, before, after in [
        ('limit_ignores_resize', 'policyIngressCapacityResize resized rest => capacityScheduleLimit resized rest', 'policyIngressCapacityResize resized rest => capacityScheduleLimit capacity rest'),
        ('limit_stops_at_first_resize', 'policyIngressCapacityResize resized rest => capacityScheduleLimit resized rest', 'policyIngressCapacityResize resized rest => resized'),
        ('limit_turn_uses_scan', 'policyIngressCapacityTurn scan arrivals rest => capacityScheduleLimit capacity rest', 'policyIngressCapacityTurn scan arrivals rest => capacityScheduleLimit scan rest'),
        ('limit_done_returns_zero', '| policyIngressCapacityDone => capacity', '| policyIngressCapacityDone => zero'),
    ]
]

_CAPACITY_SCHEDULE_EMBED = """def rec embedVariableCapacitySchedule : VariablePolicyIngressSchedule -> PolicyIngressCapacitySchedule :=
  fun (schedule : VariablePolicyIngressSchedule) =>
    case schedule as self in VariablePolicyIngressSchedule return PolicyIngressCapacitySchedule with
    | variablePolicyIngressDone => policyIngressCapacityDone
    | variablePolicyIngressTurn scan fuel arrivals rest =>
        policyIngressCapacityTurn scan arrivals (embedVariableCapacitySchedule rest)"""
MUTATIONS += [
    (f"policy_capacity_schedule_{name}", _CAPACITY_SCHEDULE_EMBED, _CAPACITY_SCHEDULE_EMBED.replace(before, after))
    for name, before, after in [
        ('embed_skips_scan', 'policyIngressCapacityTurn scan arrivals', 'policyIngressCapacityTurn zero arrivals'),
        ('embed_drops_arrivals', 'policyIngressCapacityTurn scan arrivals', 'policyIngressCapacityTurn scan policyIngressDone'),
        ('embed_drops_continuation', '(embedVariableCapacitySchedule rest)', 'policyIngressCapacityDone'),
    ]
]


_CAPACITY_EXECUTION_ACCOUNTING = """def rec capacityExecutionAccounting : PolicyIngressCapacityExecution -> PolicyIngressCapacitySchedule :=
  fun (schedule : PolicyIngressCapacityExecution) =>
    case schedule as self in PolicyIngressCapacityExecution return PolicyIngressCapacitySchedule with
    | policyIngressCapacityExecutionDone => policyIngressCapacityDone
    | policyIngressCapacityExecutionResize resized rest => policyIngressCapacityResize resized (capacityExecutionAccounting rest)
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest => policyIngressCapacityTurn scan arrivals (capacityExecutionAccounting rest)"""
MUTATIONS += [
    (f"policy_capacity_scheduled_{name}", _CAPACITY_EXECUTION_ACCOUNTING, _CAPACITY_EXECUTION_ACCOUNTING.replace(before, after))
    for name, before, after in [
        ('accounting_ignores_resize', 'policyIngressCapacityResize resized (capacityExecutionAccounting rest)', 'capacityExecutionAccounting rest'),
        ('accounting_scans_dispatch_fuel', 'policyIngressCapacityTurn scan arrivals', 'policyIngressCapacityTurn fuel arrivals'),
        ('accounting_drops_arrivals', 'policyIngressCapacityTurn scan arrivals', 'policyIngressCapacityTurn scan policyIngressDone'),
        ('accounting_drops_resize_continuation', 'policyIngressCapacityResize resized (capacityExecutionAccounting rest)', 'policyIngressCapacityResize resized policyIngressCapacityDone'),
        ('accounting_drops_turn_continuation', 'policyIngressCapacityTurn scan arrivals (capacityExecutionAccounting rest)', 'policyIngressCapacityTurn scan arrivals policyIngressCapacityDone'),
    ]
]

_CAPACITY_EXECUTION_SCHEDULE = """def rec capacityExecutionSchedule : Count -> PolicyIngressCapacityExecution -> PolicyIngressTrace -> PolicyIngressSchedule :=
  fun (capacity : Count) (schedule : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace) =>
    case schedule as self in PolicyIngressCapacityExecution return PolicyIngressSchedule with
    | policyIngressCapacityExecutionDone => policyIngressScheduleDone
    | policyIngressCapacityExecutionResize resized rest =>
        capacityExecutionSchedule resized rest (policyIngressDeferredPrefix resized waiting)
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest => policyIngressTurn fuel
        (boundedResumedPolicyIngressExamined scan waiting arrivals)
        (capacityExecutionSchedule capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))"""
MUTATIONS += [
    (f"policy_capacity_scheduled_{name}", _CAPACITY_EXECUTION_SCHEDULE, _CAPACITY_EXECUTION_SCHEDULE.replace(before, after))
    for name, before, after in [
        ('resize_keeps_old_capacity', 'capacityExecutionSchedule resized rest', 'capacityExecutionSchedule capacity rest'),
        ('resize_keeps_rejected_suffix', '(policyIngressDeferredPrefix resized waiting)', 'waiting'),
        ('resize_replays_overflow', '(policyIngressDeferredPrefix resized waiting)', '(policyIngressDeferredOverflow resized waiting)'),
        ('resize_drops_execution_continuation', 'capacityExecutionSchedule resized rest (policyIngressDeferredPrefix resized waiting)', 'policyIngressScheduleDone'),
        ('turn_zeros_dispatch_fuel', 'policyIngressTurn fuel', 'policyIngressTurn zero'),
        ('turn_dispatches_scan_fuel', 'policyIngressTurn fuel', 'policyIngressTurn scan'),
        ('turn_scans_dispatch_fuel', '(boundedResumedPolicyIngressExamined scan waiting arrivals)', '(boundedResumedPolicyIngressExamined fuel waiting arrivals)'),
        ('turn_reverses_offered', '(boundedResumedPolicyIngressExamined scan waiting arrivals)', '(boundedResumedPolicyIngressExamined scan arrivals waiting)'),
        ('turn_replays_waiting', '(boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)', 'waiting'),
        ('turn_uses_scan_as_capacity', '(boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)', '(boundedResumedPolicyIngressDeferred scan scan waiting arrivals)'),
        ('turn_drops_execution_continuation', '(capacityExecutionSchedule capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals))', 'policyIngressScheduleDone'),
        ('turn_carry_drops_arrivals', '(boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)', '(boundedResumedPolicyIngressDeferred capacity scan waiting policyIngressDone)'),
    ]
]

_CAPACITY_EXECUTION_RUN = """def runCapacityScheduledIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>
    boundedPolicyIngressHandoff
      (policyIngressLedgerOverflow (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))
      (policyIngressResumeState
        (policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))
        (runPayloadIngress weight slots payloadLimit
          (capacityExecutionSchedule capacity schedule (deferredPolicyIngress state)) config (resumedPolicyIngressQueue state)))"""
MUTATIONS += [
    (f"policy_capacity_scheduled_{name}", _CAPACITY_EXECUTION_RUN, _CAPACITY_EXECUTION_RUN.replace(before, after))
    for name, before, after in [
        ('handoff_drops_overflow', '(policyIngressLedgerOverflow (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))', 'policyIngressDone'),
        ('handoff_reports_deferred_as_overflow', '(policyIngressLedgerOverflow (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))', '(policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))'),
        ('handoff_restores_initial_waiting', '(policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))', '(deferredPolicyIngress state)'),
        ('handoff_drops_deferred', '(policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule (deferredPolicyIngress state)))', 'policyIngressDone'),
        ('handoff_skips_queue_execution', '(runPayloadIngress weight slots payloadLimit\n          (capacityExecutionSchedule capacity schedule (deferredPolicyIngress state)) config (resumedPolicyIngressQueue state))', '(resumedPolicyIngressQueue state)'),
        ('handoff_clears_carried_queue', 'config (resumedPolicyIngressQueue state)', 'config (policyIngressQueueState policyIngressDone (queuedPolicyWork (resumedPolicyIngressQueue state)))'),
        ('handoff_swaps_queue_limits', 'runPayloadIngress weight slots payloadLimit', 'runPayloadIngress weight payloadLimit slots'),
        ('handoff_drops_initial_waiting', '(capacityExecutionSchedule capacity schedule (deferredPolicyIngress state))', '(capacityExecutionSchedule capacity schedule policyIngressDone)'),
    ]
]

_CAPACITY_EXECUTION_EMBED = """def rec capacityExecutionFromVariable : VariablePolicyIngressSchedule -> PolicyIngressCapacityExecution :=
  fun (schedule : VariablePolicyIngressSchedule) =>
    case schedule as self in VariablePolicyIngressSchedule return PolicyIngressCapacityExecution with
    | variablePolicyIngressDone => policyIngressCapacityExecutionDone
    | variablePolicyIngressTurn scan fuel arrivals rest =>
        policyIngressCapacityExecutionTurn scan fuel arrivals (capacityExecutionFromVariable rest)"""
MUTATIONS += [
    (f"policy_capacity_scheduled_{name}", _CAPACITY_EXECUTION_EMBED, _CAPACITY_EXECUTION_EMBED.replace(before, after))
    for name, before, after in [
        ('embedding_swaps_fuels', 'policyIngressCapacityExecutionTurn scan fuel arrivals', 'policyIngressCapacityExecutionTurn fuel scan arrivals'),
        ('embedding_drops_continuation', '(capacityExecutionFromVariable rest)', 'policyIngressCapacityExecutionDone'),
        ('embedding_drops_arrivals', 'policyIngressCapacityExecutionTurn scan fuel arrivals', 'policyIngressCapacityExecutionTurn scan fuel policyIngressDone'),
    ]
]


_CAPACITY_EXECUTION_FUEL = """def rec capacityExecutionFuel : PolicyIngressCapacityExecution -> Count :=
  fun (schedule : PolicyIngressCapacityExecution) =>
    case schedule as self in PolicyIngressCapacityExecution return Count with
    | policyIngressCapacityExecutionDone => zero
    | policyIngressCapacityExecutionResize resized rest => capacityExecutionFuel rest
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest => add fuel (capacityExecutionFuel rest)"""
MUTATIONS += [
    (f"policy_capacity_scheduled_fuel_{name}", _CAPACITY_EXECUTION_FUEL, _CAPACITY_EXECUTION_FUEL.replace(before, after))
    for name, before, after in [
        ('terminal_invents_fuel', 'policyIngressCapacityExecutionDone => zero', 'policyIngressCapacityExecutionDone => next zero'),
        ('resize_invents_fuel', 'policyIngressCapacityExecutionResize resized rest => capacityExecutionFuel rest', 'policyIngressCapacityExecutionResize resized rest => add (next zero) (capacityExecutionFuel rest)'),
        ('turn_counts_scan', 'add fuel (capacityExecutionFuel rest)', 'add scan (capacityExecutionFuel rest)'),
        ('turn_drops_later_fuel', 'add fuel (capacityExecutionFuel rest)', 'fuel'),
    ]
]


_CAPACITY_SCHEDULE_COST_POLL_COST = """def capacityIngressPollAdminCost : Count -> PolicyIngressTrace -> PolicyIngressTrace -> Count -> Count -> Count -> Count :=
  fun (scan : Count) (waiting : PolicyIngressTrace) (arrivals : PolicyIngressTrace)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>
    add (multiply (policyIngressLength (boundedResumedPolicyIngressExamined scan waiting arrivals)) scanCost)
      (add (multiply (add (policyIngressLength waiting) (policyIngressLength arrivals)) handoffCost) turnCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_POLL_COST, _CAPACITY_SCHEDULE_COST_POLL_COST.replace(before, after))
    for name, before, after in [
        ('poll_omits_scan', 'multiply (policyIngressLength (boundedResumedPolicyIngressExamined scan waiting arrivals)) scanCost', 'multiply zero scanCost'),
        ('poll_omits_waiting_visits', 'add (policyIngressLength waiting) (policyIngressLength arrivals)', 'add zero (policyIngressLength arrivals)'),
        ('poll_omits_arrival_visits', 'add (policyIngressLength waiting) (policyIngressLength arrivals)', 'add (policyIngressLength waiting) zero'),
        ('poll_omits_turn_charge', 'handoffCost) turnCost)', 'handoffCost) zero)'),
        ('poll_uses_handoff_scan_weight', 'arrivals)) scanCost)', 'arrivals)) handoffCost)'),
    ]
]

_CAPACITY_SCHEDULE_COST_POLL_LIMIT = """def capacityIngressPollAdminLimit : Count -> Count -> PolicyIngressTrace -> Count -> Count -> Count -> Count :=
  fun (scan : Count) (initial : Count) (arrivals : PolicyIngressTrace)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) =>
    add (multiply scan scanCost)
      (add (multiply (add initial (policyIngressLength arrivals)) handoffCost) turnCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_POLL_LIMIT, _CAPACITY_SCHEDULE_COST_POLL_LIMIT.replace(before, after))
    for name, before, after in [
        ('poll_admin_limit_omits_scan', 'add (multiply scan scanCost)', 'add (multiply zero scanCost)'),
        ('poll_admin_limit_omits_initial', 'add initial (policyIngressLength arrivals)', 'add zero (policyIngressLength arrivals)'),
        ('poll_admin_limit_omits_arrivals', 'add initial (policyIngressLength arrivals)', 'add initial zero'),
        ('poll_admin_limit_omits_turn', 'handoffCost) turnCost)', 'handoffCost) zero)'),
    ]
]

_CAPACITY_SCHEDULE_COST_ADMIN_COST = """def rec capacityScheduledIngressAdminCost : Count -> PolicyIngressCapacityExecution -> PolicyIngressTrace ->
    Count -> Count -> Count -> Count -> Count -> Count :=
  fun (capacity : Count) (schedule : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) =>
    case schedule as self in PolicyIngressCapacityExecution return Count with
    | policyIngressCapacityExecutionDone => zero
    | policyIngressCapacityExecutionResize resized rest =>
        add (deferredIngressResizeCost resized waiting resizeCost boundaryCost)
          (capacityScheduledIngressAdminCost resized rest (policyIngressDeferredPrefix resized waiting)
            scanCost handoffCost turnCost resizeCost boundaryCost)
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest =>
        add (capacityIngressPollAdminCost scan waiting arrivals scanCost handoffCost turnCost)
          (capacityScheduledIngressAdminCost capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)
            scanCost handoffCost turnCost resizeCost boundaryCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_ADMIN_COST, _CAPACITY_SCHEDULE_COST_ADMIN_COST.replace(before, after))
    for name, before, after in [
        ('done_charges_boundary', '| policyIngressCapacityExecutionDone => zero', '| policyIngressCapacityExecutionDone => boundaryCost'),
        ('resize_omits_input_visits', 'deferredIngressResizeCost resized waiting resizeCost boundaryCost', 'deferredIngressResizeCost resized policyIngressDone resizeCost boundaryCost'),
        ('resize_omits_boundary', 'deferredIngressResizeCost resized waiting resizeCost boundaryCost', 'deferredIngressResizeCost resized waiting resizeCost zero'),
        ('resize_keeps_old_capacity', 'capacityScheduledIngressAdminCost resized rest', 'capacityScheduledIngressAdminCost capacity rest'),
        ('resize_restores_overflow', '(policyIngressDeferredPrefix resized waiting)', 'waiting'),
        ('resize_drops_tail', 'capacityScheduledIngressAdminCost resized rest (policyIngressDeferredPrefix resized waiting)\n            scanCost handoffCost turnCost resizeCost boundaryCost', 'zero'),
        ('poll_scans_dispatch_fuel', 'capacityIngressPollAdminCost scan waiting arrivals', 'capacityIngressPollAdminCost fuel waiting arrivals'),
        ('poll_drops_tail', 'capacityScheduledIngressAdminCost capacity rest (boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)\n            scanCost handoffCost turnCost resizeCost boundaryCost', 'zero'),
        ('poll_replays_waiting', '(boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)', 'waiting'),
        ('poll_retains_by_dispatch_fuel', '(boundedResumedPolicyIngressDeferred capacity scan waiting arrivals)', '(boundedResumedPolicyIngressDeferred capacity fuel waiting arrivals)'),
    ]
]

_CAPACITY_SCHEDULE_COST_ADMIN_LIMIT = """def rec capacityScheduledIngressAdminLimit : Count -> PolicyIngressCapacityExecution -> Count ->
    Count -> Count -> Count -> Count -> Count -> Count :=
  fun (capacity : Count) (schedule : PolicyIngressCapacityExecution) (initial : Count)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) =>
    case schedule as self in PolicyIngressCapacityExecution return Count with
    | policyIngressCapacityExecutionDone => zero
    | policyIngressCapacityExecutionResize resized rest =>
        add (add (multiply initial resizeCost) boundaryCost)
          (capacityScheduledIngressAdminLimit resized rest resized scanCost handoffCost turnCost resizeCost boundaryCost)
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest =>
        add (capacityIngressPollAdminLimit scan initial arrivals scanCost handoffCost turnCost)
          (capacityScheduledIngressAdminLimit capacity rest capacity scanCost handoffCost turnCost resizeCost boundaryCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_ADMIN_LIMIT, _CAPACITY_SCHEDULE_COST_ADMIN_LIMIT.replace(before, after))
    for name, before, after in [
        ('resize_limit_uses_new_size', 'multiply initial resizeCost', 'multiply resized resizeCost'),
        ('resize_limit_omits_boundary', 'multiply initial resizeCost) boundaryCost', 'multiply initial resizeCost) zero'),
        ('resize_limit_keeps_old_capacity', 'capacityScheduledIngressAdminLimit resized rest resized', 'capacityScheduledIngressAdminLimit capacity rest resized'),
        ('resize_limit_drops_retained_bound', 'capacityScheduledIngressAdminLimit resized rest resized', 'capacityScheduledIngressAdminLimit resized rest zero'),
        ('poll_limit_uses_dispatch_fuel', 'capacityIngressPollAdminLimit scan initial arrivals', 'capacityIngressPollAdminLimit fuel initial arrivals'),
        ('poll_limit_caps_initial_suffix', 'capacityIngressPollAdminLimit scan initial arrivals', 'capacityIngressPollAdminLimit scan capacity arrivals'),
        ('poll_limit_drops_retained_bound', 'capacityScheduledIngressAdminLimit capacity rest capacity', 'capacityScheduledIngressAdminLimit capacity rest zero'),
        ('limit_done_charges_boundary', '| policyIngressCapacityExecutionDone => zero', '| policyIngressCapacityExecutionDone => boundaryCost'),
        ('poll_limit_omits_offered_arrivals', 'capacityIngressPollAdminLimit scan initial arrivals', 'capacityIngressPollAdminLimit scan initial policyIngressDone'),
    ]
]

_CAPACITY_SCHEDULE_COST_TOTAL_COST = """def capacityScheduledIngressCost : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyWorkConfig -> PolicyWorkState ->
    Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace) (events : PolicyIngressTrace)
      (config : PolicyWorkConfig) (current : PolicyWorkState) (scanCost : Count) (handoffCost : Count)
      (turnCost : Count) (resizeCost : Count) (boundaryCost : Count)
      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    add (capacityScheduledIngressAdminCost capacity schedule waiting scanCost handoffCost turnCost resizeCost boundaryCost)
      (policyIngressScheduleCost (payloadIngressSchedule weight slots payloadLimit
        (capacityExecutionSchedule capacity schedule waiting) events) events config current eventCost policyCost handshakeCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_TOTAL_COST, _CAPACITY_SCHEDULE_COST_TOTAL_COST.replace(before, after))
    for name, before, after in [
        ('total_omits_admin', 'capacityScheduledIngressAdminCost capacity schedule waiting', 'capacityScheduledIngressAdminCost capacity policyIngressCapacityExecutionDone waiting'),
        ('total_omits_dispatch', 'capacityExecutionSchedule capacity schedule waiting', 'capacityExecutionSchedule capacity policyIngressCapacityExecutionDone waiting'),
        ('total_confuses_backlogs', ') events) events config current', ') waiting) waiting config current'),
    ]
]

_CAPACITY_SCHEDULE_COST_TOTAL_LIMIT = """def capacityScheduledIngressCostLimit : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyIngressTrace -> PolicyIngressTrace -> PolicyWorkConfig ->
    Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace) (events : PolicyIngressTrace)
      (config : PolicyWorkConfig) (scanCost : Count) (handoffCost : Count)
      (turnCost : Count) (resizeCost : Count) (boundaryCost : Count)
      (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    add (capacityScheduledIngressAdminLimit capacity schedule (policyIngressLength waiting)
        scanCost handoffCost turnCost resizeCost boundaryCost)
      (policyIngressScheduleCostLimit (payloadIngressSchedule weight slots payloadLimit
        (capacityExecutionSchedule capacity schedule waiting) events) events config eventCost policyCost handshakeCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_{name}", _CAPACITY_SCHEDULE_COST_TOTAL_LIMIT, _CAPACITY_SCHEDULE_COST_TOTAL_LIMIT.replace(before, after))
    for name, before, after in [
        ('total_limit_caps_initial_suffix', 'capacityScheduledIngressAdminLimit capacity schedule (policyIngressLength waiting)', 'capacityScheduledIngressAdminLimit capacity schedule capacity'),
        ('total_limit_omits_dispatch', 'capacityExecutionSchedule capacity schedule waiting', 'capacityExecutionSchedule capacity policyIngressCapacityExecutionDone waiting'),
    ]
]

_CAPACITY_SCHEDULE_COMPOSITION_APPEND = """def rec appendCapacityExecution : PolicyIngressCapacityExecution -> PolicyIngressCapacityExecution -> PolicyIngressCapacityExecution :=
  fun (first : PolicyIngressCapacityExecution) (second : PolicyIngressCapacityExecution) =>
    case first as self in PolicyIngressCapacityExecution return PolicyIngressCapacityExecution with
    | policyIngressCapacityExecutionDone => second
    | policyIngressCapacityExecutionResize resized rest => policyIngressCapacityExecutionResize resized (appendCapacityExecution rest second)
    | policyIngressCapacityExecutionTurn scan fuel arrivals rest => policyIngressCapacityExecutionTurn scan fuel arrivals (appendCapacityExecution rest second)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_composition_{name}", _CAPACITY_SCHEDULE_COMPOSITION_APPEND, _CAPACITY_SCHEDULE_COMPOSITION_APPEND.replace(before, after))
    for name, before, after in [
        ('done_drops_second', 'policyIngressCapacityExecutionDone => second', 'policyIngressCapacityExecutionDone => policyIngressCapacityExecutionDone'),
        ('resize_drops_boundary', 'policyIngressCapacityExecutionResize resized (appendCapacityExecution rest second)', 'appendCapacityExecution rest second'),
        ('resize_uses_zero', 'policyIngressCapacityExecutionResize resized (appendCapacityExecution rest second)', 'policyIngressCapacityExecutionResize zero (appendCapacityExecution rest second)'),
        ('resize_drops_tail', 'policyIngressCapacityExecutionResize resized (appendCapacityExecution rest second)', 'policyIngressCapacityExecutionResize resized second'),
        ('turn_drops_tail', 'policyIngressCapacityExecutionTurn scan fuel arrivals (appendCapacityExecution rest second)', 'policyIngressCapacityExecutionTurn scan fuel arrivals second'),
        ('turn_swaps_fuel', 'policyIngressCapacityExecutionTurn scan fuel arrivals (appendCapacityExecution rest second)', 'policyIngressCapacityExecutionTurn fuel scan arrivals (appendCapacityExecution rest second)'),
        ('turn_drops_arrivals', 'policyIngressCapacityExecutionTurn scan fuel arrivals (appendCapacityExecution rest second)', 'policyIngressCapacityExecutionTurn scan fuel policyIngressDone (appendCapacityExecution rest second)'),
    ]
]

_CAPACITY_SCHEDULE_COMPOSITION_LIMIT = """def capacityExecutionLimit : Count -> PolicyIngressCapacityExecution -> Count :=
  fun (capacity : Count) (schedule : PolicyIngressCapacityExecution) =>
    capacityScheduleLimit capacity (capacityExecutionAccounting schedule)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_composition_{name}", _CAPACITY_SCHEDULE_COMPOSITION_LIMIT, _CAPACITY_SCHEDULE_COMPOSITION_LIMIT.replace(before, after))
    for name, before, after in [
        ('limit_forgets_schedule', 'capacityScheduleLimit capacity (capacityExecutionAccounting schedule)', 'capacityScheduleLimit capacity policyIngressCapacityDone'),
    ]
]

_CAPACITY_SCHEDULE_COMPOSITION_REMAINDER = """def capacityExecutionRemainder : Count -> PolicyIngressCapacityExecution -> PolicyIngressTrace -> PolicyIngressTrace :=
  fun (capacity : Count) (schedule : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace) =>
    policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule waiting)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_composition_{name}", _CAPACITY_SCHEDULE_COMPOSITION_REMAINDER, _CAPACITY_SCHEDULE_COMPOSITION_REMAINDER.replace(before, after))
    for name, before, after in [
        ('remainder_restarts_input', 'policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule waiting)', 'waiting'),
        ('remainder_discards_input', 'policyIngressLedgerDeferred (capacityExecutionLedger capacity schedule waiting)', 'policyIngressDone'),
    ]
]

_CAPACITY_SCHEDULE_COMPOSITION_LEDGER = """def composedCapacityExecutionLedger : Count -> PolicyIngressCapacityExecution -> PolicyIngressCapacityExecution -> PolicyIngressTrace -> PolicyIngressLedger :=
  fun (capacity : Count) (first : PolicyIngressCapacityExecution) (second : PolicyIngressCapacityExecution) (waiting : PolicyIngressTrace) =>
    appendPolicyIngressLedger (capacityExecutionLedger capacity first waiting)
      (capacityExecutionLedger (capacityExecutionLimit capacity first) second (capacityExecutionRemainder capacity first waiting))
"""
MUTATIONS += [
    (f"policy_capacity_schedule_composition_{name}", _CAPACITY_SCHEDULE_COMPOSITION_LEDGER, _CAPACITY_SCHEDULE_COMPOSITION_LEDGER.replace(before, after))
    for name, before, after in [
        ('ledger_stale_capacity', '(capacityExecutionLimit capacity first)', 'capacity'),
        ('ledger_restarts_input', '(capacityExecutionRemainder capacity first waiting)', 'waiting'),
        ('ledger_drops_prefix', 'appendPolicyIngressLedger (capacityExecutionLedger capacity first waiting)', 'appendPolicyIngressLedger (policyIngressLedgerDone waiting)'),
    ]
]

_CAPACITY_SCHEDULE_COMPOSITION_HANDOFF = """def runComposedCapacityScheduledIngress : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState -> BoundedPolicyIngressHandoff :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (first : PolicyIngressCapacityExecution) (second : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>
    appendBoundedPolicyIngressHandoff (runCapacityScheduledIngress weight slots payloadLimit capacity first config state)
      (runCapacityScheduledIngress weight slots payloadLimit (capacityExecutionLimit capacity first) second config
        (policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state)))
"""
MUTATIONS += [
    (f"policy_capacity_schedule_composition_{name}", _CAPACITY_SCHEDULE_COMPOSITION_HANDOFF, _CAPACITY_SCHEDULE_COMPOSITION_HANDOFF.replace(before, after))
    for name, before, after in [
        ('handoff_stale_capacity', '(capacityExecutionLimit capacity first)', 'capacity'),
        ('handoff_restarts_queue', '(policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state))', '(policyIngressResumeState (deferredPolicyIngress (policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state))) (resumedPolicyIngressQueue state))'),
        ('handoff_discards_deferred', '(policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state))', '(policyIngressResumeState policyIngressDone (resumedPolicyIngressQueue (policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state))))'),
        ('handoff_drops_overflow', 'appendBoundedPolicyIngressHandoff (runCapacityScheduledIngress weight slots payloadLimit capacity first config state)', 'appendBoundedPolicyIngressHandoff (boundedPolicyIngressHandoff policyIngressDone (policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity first config state)))'),
        ('handoff_skips_second', '(capacityExecutionLimit capacity first) second config', '(capacityExecutionLimit capacity first) policyIngressCapacityExecutionDone config'),
    ]
]


_CAPACITY_SCHEDULE_COST_COMPOSITION_BOUNDARY = """def capacityScheduledIngressCostBoundary : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState -> PolicyIngressResumeState :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) =>
    policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity schedule config state)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_composition_{name}", _CAPACITY_SCHEDULE_COST_COMPOSITION_BOUNDARY, _CAPACITY_SCHEDULE_COST_COMPOSITION_BOUNDARY.replace(before, after))
    for name, before, after in [
        ("boundary_skips_execution", "policyIngressHandoffState (runCapacityScheduledIngress weight slots payloadLimit capacity schedule config state)", "state"),
        ("boundary_uses_zero_capacity", "runCapacityScheduledIngress weight slots payloadLimit capacity schedule", "runCapacityScheduledIngress weight slots payloadLimit zero schedule"),
        ("boundary_drops_queue", "runCapacityScheduledIngress weight slots payloadLimit capacity schedule config state", "runCapacityScheduledIngress weight slots payloadLimit capacity schedule config (policyIngressResumeState (deferredPolicyIngress state) (policyIngressQueueState policyIngressDone (ingressCostWork state)))"),
    ]
]

_CAPACITY_SCHEDULE_COST_COMPOSITION_TRACE = """def capacityScheduledIngressDispatched : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyIngressResumeState -> PolicyIngressTrace :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (state : PolicyIngressResumeState) =>
    payloadIngressTrace weight slots payloadLimit (capacityExecutionSchedule capacity schedule (deferredPolicyIngress state))
      (queuedPolicyIngress (resumedPolicyIngressQueue state))
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_composition_{name}", _CAPACITY_SCHEDULE_COST_COMPOSITION_TRACE, _CAPACITY_SCHEDULE_COST_COMPOSITION_TRACE.replace(before, after))
    for name, before, after in [
        ("trace_skips_schedule", "capacityExecutionSchedule capacity schedule (deferredPolicyIngress state)", "capacityExecutionSchedule capacity policyIngressCapacityExecutionDone (deferredPolicyIngress state)"),
        ("trace_drops_deferred", "(deferredPolicyIngress state)", "policyIngressDone"),
        ("trace_drops_queue", "(queuedPolicyIngress (resumedPolicyIngressQueue state))", "policyIngressDone"),
    ]
]

_CAPACITY_SCHEDULE_COST_COMPOSITION_DISPATCH = """def capacityScheduledIngressDispatchCost : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    policyIngressTraceCost (capacityScheduledIngressDispatched weight slots payloadLimit capacity schedule state) config (ingressCostWork state) eventCost policyCost handshakeCost
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_composition_{name}", _CAPACITY_SCHEDULE_COST_COMPOSITION_DISPATCH, _CAPACITY_SCHEDULE_COST_COMPOSITION_DISPATCH.replace(before, after))
    for name, before, after in [
        ("dispatch_omits_events", "config (ingressCostWork state) eventCost policyCost handshakeCost", "config (ingressCostWork state) zero policyCost handshakeCost"),
        ("dispatch_omits_policy", "config (ingressCostWork state) eventCost policyCost handshakeCost", "config (ingressCostWork state) eventCost zero handshakeCost"),
        ("dispatch_omits_handshakes", "config (ingressCostWork state) eventCost policyCost handshakeCost", "config (ingressCostWork state) eventCost policyCost zero"),
    ]
]

_CAPACITY_SCHEDULE_COST_COMPOSITION_TOTAL = """def capacityScheduledIngressExecutionCost : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState ->
    Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (schedule : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    capacityScheduledIngressCost weight slots payloadLimit capacity schedule (deferredPolicyIngress state)
      (queuedPolicyIngress (resumedPolicyIngressQueue state)) config (ingressCostWork state) scanCost handoffCost turnCost resizeCost boundaryCost eventCost policyCost handshakeCost
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_composition_{name}", _CAPACITY_SCHEDULE_COST_COMPOSITION_TOTAL, _CAPACITY_SCHEDULE_COST_COMPOSITION_TOTAL.replace(before, after))
    for name, before, after in [
        ("total_skips_schedule", "capacityScheduledIngressCost weight slots payloadLimit capacity schedule", "capacityScheduledIngressCost weight slots payloadLimit capacity policyIngressCapacityExecutionDone"),
        ("total_drops_deferred", "(deferredPolicyIngress state)", "policyIngressDone"),
        ("total_drops_queue", "(queuedPolicyIngress (resumedPolicyIngressQueue state))", "policyIngressDone"),
        ("total_omits_resize", "config (ingressCostWork state) scanCost handoffCost turnCost resizeCost boundaryCost eventCost policyCost handshakeCost", "config (ingressCostWork state) scanCost handoffCost turnCost zero boundaryCost eventCost policyCost handshakeCost"),
        ("total_omits_boundary", "config (ingressCostWork state) scanCost handoffCost turnCost resizeCost boundaryCost eventCost policyCost handshakeCost", "config (ingressCostWork state) scanCost handoffCost turnCost resizeCost zero eventCost policyCost handshakeCost"),
    ]
]

_CAPACITY_SCHEDULE_COST_COMPOSITION_COMPOSED = """def composedCapacityScheduledIngressCost : (PolicyIngressEvent -> Count) -> Count -> Count -> Count ->
    PolicyIngressCapacityExecution -> PolicyIngressCapacityExecution -> PolicyWorkConfig -> PolicyIngressResumeState ->
    Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count -> Count :=
  fun (weight : PolicyIngressEvent -> Count) (slots : Count) (payloadLimit : Count) (capacity : Count)
      (first : PolicyIngressCapacityExecution) (second : PolicyIngressCapacityExecution) (config : PolicyWorkConfig) (state : PolicyIngressResumeState)
      (scanCost : Count) (handoffCost : Count) (turnCost : Count) (resizeCost : Count) (boundaryCost : Count) (eventCost : Count) (policyCost : Count) (handshakeCost : Count) =>
    add (capacityScheduledIngressExecutionCost weight slots payloadLimit capacity first config state scanCost handoffCost turnCost resizeCost boundaryCost eventCost policyCost handshakeCost)
      (capacityScheduledIngressExecutionCost weight slots payloadLimit (capacityExecutionLimit capacity first) second config (capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state) scanCost handoffCost turnCost resizeCost boundaryCost eventCost policyCost handshakeCost)
"""
MUTATIONS += [
    (f"policy_capacity_schedule_cost_composition_{name}", _CAPACITY_SCHEDULE_COST_COMPOSITION_COMPOSED, _CAPACITY_SCHEDULE_COST_COMPOSITION_COMPOSED.replace(before, after))
    for name, before, after in [
        ("composed_stale_capacity", "(capacityExecutionLimit capacity first)", "capacity"),
        ("composed_restarts_state", "(capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state)", "state"),
        ("composed_drops_prefix", "capacityScheduledIngressExecutionCost weight slots payloadLimit capacity first config state", "capacityScheduledIngressExecutionCost weight slots payloadLimit capacity policyIngressCapacityExecutionDone config state"),
        ("composed_drops_suffix", "(capacityExecutionLimit capacity first) second config", "(capacityExecutionLimit capacity first) policyIngressCapacityExecutionDone config"),
        ("composed_restarts_deferred", "(capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state)", "(policyIngressResumeState (deferredPolicyIngress state) (resumedPolicyIngressQueue (capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state)))"),
        ("composed_restarts_work", "(capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state)", "(policyIngressResumeState (deferredPolicyIngress (capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state)) (policyIngressQueueState (queuedPolicyIngress (resumedPolicyIngressQueue (capacityScheduledIngressCostBoundary weight slots payloadLimit capacity first config state))) (ingressCostWork state)))"),
    ]
]


_CAPACITY_COMPATIBILITY_BOUNDARY = """def capacityExecutionSingleBoundary : VariablePolicyIngressSchedule -> Count ->
    VariablePolicyIngressSchedule -> PolicyIngressCapacityExecution :=
  fun (first : VariablePolicyIngressSchedule) (resized : Count) (second : VariablePolicyIngressSchedule) =>
    appendCapacityExecution (capacityExecutionFromVariable first)
      (policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))"""
MUTATIONS += [
    (f"policy_capacity_compatibility_{name}", _CAPACITY_COMPATIBILITY_BOUNDARY,
     _CAPACITY_COMPATIBILITY_BOUNDARY.replace(before, after))
    for name, before, after in [
        ("drops_prefix", "(capacityExecutionFromVariable first)", "policyIngressCapacityExecutionDone"),
        ("drops_suffix", "(capacityExecutionFromVariable second)", "policyIngressCapacityExecutionDone"),
        ("drops_resize", "(policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))",
         "(capacityExecutionFromVariable second)"),
        ("zero_resize", "policyIngressCapacityExecutionResize resized", "policyIngressCapacityExecutionResize zero"),
        ("increments_resize", "policyIngressCapacityExecutionResize resized", "policyIngressCapacityExecutionResize (next resized)"),
        ("swaps_segments", "appendCapacityExecution (capacityExecutionFromVariable first)\n      (policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))",
         "appendCapacityExecution (capacityExecutionFromVariable second)\n      (policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable first))"),
        ("early_resize", "appendCapacityExecution (capacityExecutionFromVariable first)\n      (policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))",
         "policyIngressCapacityExecutionResize resized\n      (appendCapacityExecution (capacityExecutionFromVariable first) (capacityExecutionFromVariable second))"),
        ("late_resize", "(policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))",
         "(appendCapacityExecution (capacityExecutionFromVariable second)\n        (policyIngressCapacityExecutionResize resized policyIngressCapacityExecutionDone))"),
        ("replays_prefix", "appendCapacityExecution (capacityExecutionFromVariable first)",
         "appendCapacityExecution (appendCapacityExecution (capacityExecutionFromVariable first) (capacityExecutionFromVariable first))"),
        ("replays_suffix", "(capacityExecutionFromVariable second)",
         "(appendCapacityExecution (capacityExecutionFromVariable second) (capacityExecutionFromVariable second))"),
        ("replays_boundary", "(policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second))",
         "(policyIngressCapacityExecutionResize resized\n        (policyIngressCapacityExecutionResize resized (capacityExecutionFromVariable second)))"),
    ]
]
_CAPACITY_COMPATIBILITY_VARIABLE_TURN = """| variablePolicyIngressTurn scan fuel arrivals rest =>
        policyIngressCapacityExecutionTurn scan fuel arrivals (capacityExecutionFromVariable rest)"""
MUTATIONS += [
    (f"policy_capacity_compatibility_{name}", _CAPACITY_COMPATIBILITY_VARIABLE_TURN,
     _CAPACITY_COMPATIBILITY_VARIABLE_TURN.replace(before, after))
    for name, before, after in [
        ("changes_scan", "ExecutionTurn scan fuel", "ExecutionTurn (next scan) fuel"),
        ("drops_dispatch_fuel", "ExecutionTurn scan fuel", "ExecutionTurn scan zero"),
        ("drops_scan", "ExecutionTurn scan fuel", "ExecutionTurn zero fuel"),
        ("increments_fuel", "ExecutionTurn scan fuel", "ExecutionTurn scan (next fuel)"),
    ]
]


# Cost compatibility controls mutate operational charges, not proof statements.
MUTATIONS += [
    (f"policy_capacity_cost_compatibility_{name}", target, target.replace(before, after))
    for name, target, before, after in [
        ("drops_scan_charge", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "arrivals)) scanCost", "arrivals)) zero"),
        ("drops_handoff_charge", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "arrivals)) handoffCost", "arrivals)) zero"),
        ("changes_turn_weight", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "handoffCost) turnCost", "handoffCost) scanCost"),
        ("replays_turn_charge", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "handoffCost) turnCost", "handoffCost) (add turnCost turnCost)"),
        ("replays_scan_charge", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "arrivals)) scanCost", "arrivals)) (add scanCost scanCost)"),
        ("omits_retained_visits", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "add (policyIngressLength waiting) (policyIngressLength arrivals)", "policyIngressLength arrivals"),
        ("omits_arrival_visits", _CAPACITY_SCHEDULE_COST_POLL_COST,
         "add (policyIngressLength waiting) (policyIngressLength arrivals)", "policyIngressLength waiting"),
        ("drops_resize_charge", _CAPACITY_SCHEDULE_COST_ADMIN_COST,
         "deferredIngressResizeCost resized waiting resizeCost boundaryCost", "zero"),
        ("replays_resize_charge", _CAPACITY_SCHEDULE_COST_ADMIN_COST,
         "deferredIngressResizeCost resized waiting resizeCost boundaryCost",
         "add (deferredIngressResizeCost resized waiting resizeCost boundaryCost)\n            (deferredIngressResizeCost resized waiting resizeCost boundaryCost)"),
        ("trims_prefix_cost_input", _CAPACITY_COST_ADMIN,
         "variableDeferredIngressAdminCost oldCapacity first waiting",
         "variableDeferredIngressAdminCost oldCapacity first (policyIngressDeferredPrefix newCapacity waiting)"),
        ("charges_only_retained_resize_input", _CAPACITY_COST_ADMIN,
         "deferredIngressResizeCost newCapacity (variableDeferredIngressRemainder oldCapacity first waiting)",
         "deferredIngressResizeCost newCapacity (policyIngressDeferredPrefix newCapacity\n          (variableDeferredIngressRemainder oldCapacity first waiting))"),
        ("drops_dispatch_charge", _CAPACITY_SCHEDULE_COST_TOTAL_COST,
         "events config current eventCost policyCost handshakeCost", "events config current zero zero zero"),
    ]
]


MUTATIONS += [
    ("saturated_pool_omits_exhaustion",
     "def rec exhaustedPoolHasNoToken : (pool : LeasePool) -> (index : Count) ->\n"
     "    Equal Count (leaseAvailability pool) zero ->",
     "def rec exhaustedPoolHasNoToken : (pool : LeasePool) -> (index : Count) ->"),
    ("saturated_pool_one_available_still_refused",
     "def rec exhaustedPoolHasNoToken : (pool : LeasePool) -> (index : Count) ->\n"
     "    Equal Count (leaseAvailability pool) zero ->",
     "def rec exhaustedPoolHasNoToken : (pool : LeasePool) -> (index : Count) ->\n"
     "    Equal Count (leaseAvailability pool) (next zero) ->"),
    ("saturated_admission_one_available_is_noop",
     "    (index : Count) -> (current : SourceAdmission) ->\n"
     "    Equal Count (leaseAvailability (admissionPool current)) zero ->\n"
     "    Equal SourceAdmission",
     "    (index : Count) -> (current : SourceAdmission) ->\n"
     "    Equal Count (leaseAvailability (admissionPool current)) (next zero) ->\n"
     "    Equal SourceAdmission"),
    ("saturated_admission_one_available_has_no_receipt",
     "    (swarm : SwarmClass) -> (key : Count) -> (index : Count) -> (current : SourceAdmission) ->\n"
     "    Equal Count (leaseAvailability (admissionPool current)) zero ->\n"
     "    Equal AdmissionReceipt",
     "    (swarm : SwarmClass) -> (key : Count) -> (index : Count) -> (current : SourceAdmission) ->\n"
     "    Equal Count (leaseAvailability (admissionPool current)) (next zero) ->\n"
     "    Equal AdmissionReceipt"),
]


_INVALID_EVIDENCE_BRANCH = (
    "    | invalidReachabilityEvidence => current\n"
    "    | validReachabilityEvidence => admissionAuthority validated (authorityIdentity current) (authorityPrivilege current)"
)
_VALID_EVIDENCE_BRANCH = (
    "    | validReachabilityEvidence => admissionAuthority validated (authorityIdentity current) (authorityPrivilege current)"
)
MUTATIONS += [
    ("reachability_invalid_grants_validation", _INVALID_EVIDENCE_BRANCH,
     _INVALID_EVIDENCE_BRANCH.replace("=> current\n", "=> admissionAuthority validated (authorityIdentity current) (authorityPrivilege current)\n")),
    ("reachability_invalid_grants_identity", _INVALID_EVIDENCE_BRANCH,
     _INVALID_EVIDENCE_BRANCH.replace("=> current\n", "=> admissionAuthority (authorityReachability current) on (authorityPrivilege current)\n")),
    ("reachability_invalid_grants_privilege", _INVALID_EVIDENCE_BRANCH,
     _INVALID_EVIDENCE_BRANCH.replace("=> current\n", "=> admissionAuthority (authorityReachability current) (authorityIdentity current) on\n")),
    ("reachability_valid_grants_identity", _VALID_EVIDENCE_BRANCH,
     _VALID_EVIDENCE_BRANCH.replace("(authorityIdentity current)", "on")),
    ("reachability_valid_grants_privilege", _VALID_EVIDENCE_BRANCH,
     _VALID_EVIDENCE_BRANCH.replace("(authorityPrivilege current)", "on")),
    ("reachability_valid_fails_to_validate", _VALID_EVIDENCE_BRANCH,
     _VALID_EVIDENCE_BRANCH.replace("validated", "unvalidated")),
    ("reachability_trace_discards_authority",
     "    | reachabilityEvidenceDone => current\n"
     "    | reachabilityEvidenceThen evidence rest => runReachabilityEvidence rest (applyReachabilityEvidence evidence current)",
     "    | reachabilityEvidenceDone => admissionAuthority (authorityReachability current) off off\n"
     "    | reachabilityEvidenceThen evidence rest => runReachabilityEvidence rest (applyReachabilityEvidence evidence current)"),
]


_AUTHENTICATION_STATE = (
    "    admissionAuthority (authorityReachability current) verified (privileged verified listed)"
)
_AUTHORITY_DISPATCH = (
    "    | authorityReachabilityEvent evidence => applyReachabilityEvidence evidence current\n"
    "    | authorityAuthenticationEvent verified listed => applyAuthentication verified listed current"
)
_AUTHENTICATION_ONLY_DISPATCH = (
    "    | authorityReachabilityEvent evidence => current\n"
    "    | authorityAuthenticationEvent verified listed => applyAuthentication verified listed current"
)
_AUTHORITY_ERASURE = (
    "    admissionAuthority unvalidated (authorityIdentity current) (authorityPrivilege current)"
)
MUTATIONS += [
    ("authentication_unverified_grants_identity", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace(") verified (", ") on (")),
    ("authentication_verified_never_grants_identity", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace(") verified (", ") off (")),
    ("authentication_privilege_ignores_verification", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace("privileged verified listed", "privileged on listed")),
    ("authentication_privilege_ignores_listing", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace("privileged verified listed", "privileged verified on")),
    ("authentication_never_grants_privilege", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace("(privileged verified listed)", "off")),
    ("authentication_grants_reachability", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace("(authorityReachability current)", "validated")),
    ("authentication_retains_old_identity", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace(") verified (", ") (authorityIdentity current) (")),
    ("authentication_retains_old_privilege", _AUTHENTICATION_STATE,
     _AUTHENTICATION_STATE.replace("(privileged verified listed)", "(authorityPrivilege current)")),
    ("mixed_reachability_grants_authentication", _AUTHORITY_DISPATCH,
     _AUTHORITY_DISPATCH.replace("applyReachabilityEvidence evidence current", "applyAuthentication on on current")),
    ("mixed_authentication_swaps_verification_and_listing", _AUTHORITY_DISPATCH,
     _AUTHORITY_DISPATCH.replace("applyAuthentication verified listed current", "applyAuthentication listed verified current")),
    ("mixed_authentication_is_skipped", _AUTHORITY_DISPATCH,
     _AUTHORITY_DISPATCH.replace("applyAuthentication verified listed current", "current")),
    ("mixed_authentication_grants_reachability", _AUTHORITY_DISPATCH,
     _AUTHORITY_DISPATCH.replace("applyAuthentication verified listed current",
                               "applyReachabilityEvidence validReachabilityEvidence (applyAuthentication verified listed current)")),
    ("mixed_trace_skips_head_event",
     "    | authorityThen event rest => runAuthorityTrace rest (authorityStep event current)",
     "    | authorityThen event rest => runAuthorityTrace rest current"),
    ("authentication_projection_accepts_reachability", _AUTHENTICATION_ONLY_DISPATCH,
     _AUTHENTICATION_ONLY_DISPATCH.replace("evidence => current", "evidence => applyReachabilityEvidence evidence current")),
    ("authentication_projection_skips_authentication", _AUTHENTICATION_ONLY_DISPATCH,
     _AUTHENTICATION_ONLY_DISPATCH.replace("applyAuthentication verified listed current", "current")),
    ("authority_erasure_discards_identity", _AUTHORITY_ERASURE,
     _AUTHORITY_ERASURE.replace("(authorityIdentity current)", "off")),
    ("authority_erasure_discards_privilege", _AUTHORITY_ERASURE,
     _AUTHORITY_ERASURE.replace("(authorityPrivilege current)", "off")),
    ("mixed_trace_claims_no_authentication_changes",
     "def rec mixedAuthorityTraceErasesToAuthenticationTrace : (trace : AuthorityTrace) ->\n"
     "    (current : AdmissionAuthority) ->\n"
     "    Equal AdmissionAuthority (eraseAuthorityReachability (runAuthorityTrace trace current))\n"
     "      (runAuthenticationOnlyTrace trace (eraseAuthorityReachability current)) :=",
     "def rec mixedAuthorityTraceErasesToAuthenticationTrace : (trace : AuthorityTrace) ->\n"
     "    (current : AdmissionAuthority) ->\n"
     "    Equal AdmissionAuthority (eraseAuthorityReachability (runAuthorityTrace trace current))\n"
     "      (eraseAuthorityReachability current) :="),
]




# Pre-validation queue, allocation and charge weakening controls.
MUTATIONS += [
    ('prevalidation_overflow_allocates_slot', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationVacant cap (prevalidationEnd cap)\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)'),
    ('prevalidation_vacancy_drops_packet', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationVacant cap rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)'),
    ('prevalidation_packet_storage_uncapped', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap demand (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)'),
    ('prevalidation_arrival_overwrites_held', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest'),
    ('prevalidation_arrival_skips_deep_vacancy', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound (prevalidationPush cap demand rest)', 'def rec prevalidationPush : (byteCap : Count) -> Count -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (demand : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest =>\n      prevalidationHeld cap (boundedWork cap demand) (workBound cap demand) rest\n    | prevalidationHeld cap bytes bound rest =>\n      prevalidationHeld cap bytes bound rest'),
    ('prevalidation_pop_skips_deep_packet', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap (prevalidationPop cap rest)\n    | prevalidationHeld cap bytes bound rest => prevalidationVacant cap rest', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap rest\n    | prevalidationHeld cap bytes bound rest => prevalidationVacant cap rest'),
    ('prevalidation_decision_retains_packet', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap (prevalidationPop cap rest)\n    | prevalidationHeld cap bytes bound rest => prevalidationVacant cap rest', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap (prevalidationPop cap rest)\n    | prevalidationHeld cap bytes bound rest => prevalidationHeld cap bytes bound rest'),
    ('prevalidation_decision_drops_capacity', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap (prevalidationPop cap rest)\n    | prevalidationHeld cap bytes bound rest => prevalidationVacant cap rest', 'def rec prevalidationPop : (byteCap : Count) -> PrevalidationQueue byteCap ->\n    PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return PrevalidationQueue cap with\n    | prevalidationEnd cap => prevalidationEnd cap\n    | prevalidationVacant cap rest => prevalidationVacant cap (prevalidationPop cap rest)\n    | prevalidationHeld cap bytes bound rest => rest'),
    ('prevalidation_worker_bypasses_shared_queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand =>\n      (case swarm as origin in PrevalidationSwarm return PrevalidationQueue byteCap with\n      | prevalidationPrimary => prevalidationPush byteCap demand queue\n      | prevalidationWorker => queue)\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue'),
    ('prevalidation_retry_leaks_packet', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case outcome as result in Outcome return PrevalidationQueue byteCap with\n      | accept => prevalidationPop byteCap queue\n      | retry => queue\n      | refuse => prevalidationPop byteCap queue\n      | ignore => prevalidationPop byteCap queue'),
    ('prevalidation_refuse_leaks_packet', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case outcome as result in Outcome return PrevalidationQueue byteCap with\n      | accept => prevalidationPop byteCap queue\n      | retry => prevalidationPop byteCap queue\n      | refuse => queue\n      | ignore => prevalidationPop byteCap queue'),
    ('prevalidation_ignore_leaks_packet', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case outcome as result in Outcome return PrevalidationQueue byteCap with\n      | accept => prevalidationPop byteCap queue\n      | retry => prevalidationPop byteCap queue\n      | refuse => prevalidationPop byteCap queue\n      | ignore => queue'),
    ('prevalidation_accept_leaks_packet', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case outcome as result in Outcome return PrevalidationQueue byteCap with\n      | accept => queue\n      | retry => prevalidationPop byteCap queue\n      | refuse => prevalidationPop byteCap queue\n      | ignore => prevalidationPop byteCap queue'),
    ('prevalidation_silent_decision_leaks_packet', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand => prevalidationPop byteCap queue', 'def prevalidationStep : (byteCap : Count) -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (event : PrevalidationEvent) (queue : PrevalidationQueue byteCap) =>\n    case event as self in PrevalidationEvent return PrevalidationQueue byteCap with\n    | prevalidationArrival swarm demand => prevalidationPush byteCap demand queue\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case emits as flag in Flag return PrevalidationQueue byteCap with\n      | off => queue\n      | on => prevalidationPop byteCap queue'),
    ('prevalidation_retained_payload_not_counted', 'def rec prevalidationRetainedBytes : (0 byteCap : Count) -> PrevalidationQueue byteCap -> Count :=\n  fun (0 byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return Count with\n    | prevalidationEnd cap => zero\n    | prevalidationVacant cap rest => prevalidationRetainedBytes cap rest\n    | prevalidationHeld cap bytes bound rest => add bytes (prevalidationRetainedBytes cap rest)', 'def rec prevalidationRetainedBytes : (0 byteCap : Count) -> PrevalidationQueue byteCap -> Count :=\n  fun (0 byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return Count with\n    | prevalidationEnd cap => zero\n    | prevalidationVacant cap rest => prevalidationRetainedBytes cap rest\n    | prevalidationHeld cap bytes bound rest => prevalidationRetainedBytes cap rest'),
    ('prevalidation_held_occupancy_exceeds_slots', 'def rec prevalidationOccupancy : (0 byteCap : Count) -> PrevalidationQueue byteCap -> Count :=\n  fun (0 byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return Count with\n    | prevalidationEnd cap => zero\n    | prevalidationVacant cap rest => prevalidationOccupancy cap rest\n    | prevalidationHeld cap bytes bound rest => next (prevalidationOccupancy cap rest)', 'def rec prevalidationOccupancy : (0 byteCap : Count) -> PrevalidationQueue byteCap -> Count :=\n  fun (0 byteCap : Count) (queue : PrevalidationQueue byteCap) =>\n    case queue as self in PrevalidationQueue cap return Count with\n    | prevalidationEnd cap => zero\n    | prevalidationVacant cap rest => prevalidationOccupancy cap rest\n    | prevalidationHeld cap bytes bound rest => next (next (prevalidationOccupancy cap rest))'),
    ('prevalidation_metadata_allocation_not_counted', 'def prevalidationTransientBytes : (byteCap : Count) -> Count -> PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (entryBytes : Count) (queue : PrevalidationQueue byteCap) =>\n    add (add (multiply (prevalidationSlots byteCap queue) entryBytes)\n      (prevalidationRetainedBytes byteCap queue)) byteCap', 'def prevalidationTransientBytes : (byteCap : Count) -> Count -> PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (entryBytes : Count) (queue : PrevalidationQueue byteCap) =>\n    add (add zero\n      (prevalidationRetainedBytes byteCap queue)) byteCap'),
    ('prevalidation_workspace_allocation_not_counted', 'def prevalidationTransientBytes : (byteCap : Count) -> Count -> PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (entryBytes : Count) (queue : PrevalidationQueue byteCap) =>\n    add (add (multiply (prevalidationSlots byteCap queue) entryBytes)\n      (prevalidationRetainedBytes byteCap queue)) byteCap', 'def prevalidationTransientBytes : (byteCap : Count) -> Count -> PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (entryBytes : Count) (queue : PrevalidationQueue byteCap) =>\n    add (add (multiply (prevalidationSlots byteCap queue) entryBytes)\n      (prevalidationRetainedBytes byteCap queue)) zero'),
    ('prevalidation_arrival_packet_demand_not_charged', 'def prevalidationPacketDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => demand\n    | prevalidationDecision outcome emits parseDemand tokenDemand => zero', 'def prevalidationPacketDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => zero'),
    ('prevalidation_decision_parse_demand_not_charged', 'def prevalidationParseDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => parseDemand', 'def prevalidationParseDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => zero'),
    ('prevalidation_decision_token_demand_not_charged', 'def prevalidationTokenDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => tokenDemand', 'def prevalidationTokenDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => zero'),
    ('prevalidation_silent_parse_demand_not_charged', 'def prevalidationParseDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand => parseDemand', 'def prevalidationParseDemand : PrevalidationEvent -> Count :=\n  fun (event : PrevalidationEvent) =>\n    case event as self in PrevalidationEvent return Count with\n    | prevalidationArrival swarm demand => zero\n    | prevalidationDecision outcome emits parseDemand tokenDemand =>\n      case emits as flag in Flag return Count with\n      | off => zero\n      | on => parseDemand'),
    ('prevalidation_packet_work_omitted', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add zero\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))'),
    ('prevalidation_queue_scan_work_omitted', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add zero\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))'),
    ('prevalidation_parse_work_omitted', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add zero\n          (boundedWork tokenCap (prevalidationTokenDemand event))))'),
    ('prevalidation_token_work_omitted', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          zero))'),
    ('prevalidation_parse_work_exceeds_cap', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork (next parseCap) (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))'),
    ('prevalidation_token_work_exceeds_cap', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork tokenCap (prevalidationTokenDemand event))))', 'def prevalidationStepWork : (byteCap : Count) -> Count -> Count -> PrevalidationEvent ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (event : PrevalidationEvent)\n      (queue : PrevalidationQueue byteCap) =>\n    add (boundedWork byteCap (prevalidationPacketDemand event))\n      (add (prevalidationSlots byteCap queue)\n        (add (boundedWork parseCap (prevalidationParseDemand event))\n          (boundedWork (next tokenCap) (prevalidationTokenDemand event))))'),
    ('prevalidation_bytecap_budget_omitted', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add parseCap tokenCap))', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add zero (add slotCap (add parseCap tokenCap))'),
    ('prevalidation_slotcap_budget_omitted', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add parseCap tokenCap))', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add zero (add parseCap tokenCap))'),
    ('prevalidation_parsecap_budget_omitted', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add parseCap tokenCap))', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add zero tokenCap))'),
    ('prevalidation_tokencap_budget_omitted', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add parseCap tokenCap))', 'def prevalidationUnitBudget : Count -> Count -> Count -> Count -> Count :=\n  fun (byteCap : Count) (slotCap : Count) (parseCap : Count) (tokenCap : Count) =>\n    add byteCap (add slotCap (add parseCap zero))'),
    ('prevalidation_trace_skips_transition', 'def rec runPrevalidationTrace : (byteCap : Count) -> PrevalidationTrace ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (trace : PrevalidationTrace) (queue : PrevalidationQueue byteCap) =>\n    case trace as self in PrevalidationTrace return PrevalidationQueue byteCap with\n    | prevalidationDone => queue\n    | prevalidationThen event rest =>\n      runPrevalidationTrace byteCap rest (prevalidationStep byteCap event queue)', 'def rec runPrevalidationTrace : (byteCap : Count) -> PrevalidationTrace ->\n    PrevalidationQueue byteCap -> PrevalidationQueue byteCap :=\n  fun (byteCap : Count) (trace : PrevalidationTrace) (queue : PrevalidationQueue byteCap) =>\n    case trace as self in PrevalidationTrace return PrevalidationQueue byteCap with\n    | prevalidationDone => queue\n    | prevalidationThen event rest =>\n      runPrevalidationTrace byteCap rest queue'),
    ('prevalidation_trace_skips_head_charge', 'def rec prevalidationTraceWork : (byteCap : Count) -> Count -> Count -> PrevalidationTrace ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (trace : PrevalidationTrace)\n      (queue : PrevalidationQueue byteCap) =>\n    case trace as self in PrevalidationTrace return Count with\n    | prevalidationDone => zero\n    | prevalidationThen event rest =>\n      add (prevalidationStepWork byteCap parseCap tokenCap event queue)\n        (prevalidationTraceWork byteCap parseCap tokenCap rest (prevalidationStep byteCap event queue))', 'def rec prevalidationTraceWork : (byteCap : Count) -> Count -> Count -> PrevalidationTrace ->\n    PrevalidationQueue byteCap -> Count :=\n  fun (byteCap : Count) (parseCap : Count) (tokenCap : Count) (trace : PrevalidationTrace)\n      (queue : PrevalidationQueue byteCap) =>\n    case trace as self in PrevalidationTrace return Count with\n    | prevalidationDone => zero\n    | prevalidationThen event rest =>\n      prevalidationTraceWork byteCap parseCap tokenCap rest (prevalidationStep byteCap event queue)'),
    ('prevalidation_trace_length_omits_head', 'def rec prevalidationTraceLength : PrevalidationTrace -> Count :=\n  fun (trace : PrevalidationTrace) =>\n    case trace as self in PrevalidationTrace return Count with\n    | prevalidationDone => zero\n    | prevalidationThen event rest => next (prevalidationTraceLength rest)', 'def rec prevalidationTraceLength : PrevalidationTrace -> Count :=\n  fun (trace : PrevalidationTrace) =>\n    case trace as self in PrevalidationTrace return Count with\n    | prevalidationDone => zero\n    | prevalidationThen event rest => prevalidationTraceLength rest'),
    ('prevalidation_zero_fuel_runs_trace', 'def rec prevalidationTake : Count -> PrevalidationTrace -> PrevalidationTrace :=\n  fun (fuel : Count) (trace : PrevalidationTrace) =>\n    case fuel as self in Count return PrevalidationTrace with\n    | zero => prevalidationDone\n    | next remaining =>\n      case trace as pending in PrevalidationTrace return PrevalidationTrace with\n      | prevalidationDone => prevalidationDone\n      | prevalidationThen event rest => prevalidationThen event (prevalidationTake remaining rest)', 'def rec prevalidationTake : Count -> PrevalidationTrace -> PrevalidationTrace :=\n  fun (fuel : Count) (trace : PrevalidationTrace) =>\n    case fuel as self in Count return PrevalidationTrace with\n    | zero => trace\n    | next remaining =>\n      case trace as pending in PrevalidationTrace return PrevalidationTrace with\n      | prevalidationDone => prevalidationDone\n      | prevalidationThen event rest => prevalidationThen event (prevalidationTake remaining rest)'),
    ('prevalidation_fuel_prefix_skips_head', 'def rec prevalidationTake : Count -> PrevalidationTrace -> PrevalidationTrace :=\n  fun (fuel : Count) (trace : PrevalidationTrace) =>\n    case fuel as self in Count return PrevalidationTrace with\n    | zero => prevalidationDone\n    | next remaining =>\n      case trace as pending in PrevalidationTrace return PrevalidationTrace with\n      | prevalidationDone => prevalidationDone\n      | prevalidationThen event rest => prevalidationThen event (prevalidationTake remaining rest)', 'def rec prevalidationTake : Count -> PrevalidationTrace -> PrevalidationTrace :=\n  fun (fuel : Count) (trace : PrevalidationTrace) =>\n    case fuel as self in Count return PrevalidationTrace with\n    | zero => prevalidationDone\n    | next remaining =>\n      case trace as pending in PrevalidationTrace return PrevalidationTrace with\n      | prevalidationDone => prevalidationDone\n      | prevalidationThen event rest => prevalidationTake remaining rest'),
]

# R03 unlocked handshake executor controls. Targets retain their reviewed source.
MUTATIONS += [
    ('executor_unowned_waiting_dispatches', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => on\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n'),
    ('executor_stale_waiting_dispatches', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => on))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n'),
    ('executor_deep_waiting_checks_head', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation pool\n'),
    ('executor_missing_waiting_dispatches', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n', 'def rec executorOwnedAt : Count -> Count -> LeasePool -> Flag :=\n  fun (index : Count) (generation : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => on\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease current => off\n        | heldLease current => sameCount generation current))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => on\n      | leaseCell lease rest => executorOwnedAt previous generation rest\n'),
    ('executor_occupied_active_accepts', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => off))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorVacantAt previous rest\n', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => on))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorVacantAt previous rest\n'),
    ('executor_missing_active_accepts', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => off))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorVacantAt previous rest\n', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => on\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => off))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => on\n      | leaseCell lease rest => executorVacantAt previous rest\n'),
    ('executor_deep_active_checks_head', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => off))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorVacantAt previous rest\n', 'def rec executorVacantAt : Count -> LeasePool -> Flag :=\n  fun (index : Count) (pool : LeasePool) =>\n    case index as selected in Count return Flag with\n    | zero =>\n      (case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest =>\n        (case lease as cell in Lease return Flag with\n        | freeLease generation => on\n        | heldLease generation => off))\n    | next previous =>\n      case pool as self in LeasePool return Flag with\n      | emptyLeasePool => off\n      | leaseCell lease rest => executorVacantAt previous pool\n'),
    ('executor_refused_dispatch_starts', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => reserveAt activeIndex\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n'),
    ('executor_dispatch_retains_waiting', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex noOwnedLease connectionEstablished\n      | on => reserveAt activeIndex\n'),
    ('executor_dispatch_skips_active_owner', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => executorIdle\n'),
    ('executor_dispatch_releases_wrong_waiting', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt zero (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n'),
    ('executor_dispatch_reserves_wrong_active', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt activeIndex\n', 'def executorDispatchAction : Flag -> Flag -> Count -> Count -> Count -> PoolAction :=\n  fun (allowed : Flag) (active : Flag) (waitingIndex : Count) (generation : Count) (activeIndex : Count) =>\n    case allowed as decision in Flag return PoolAction with\n    | off => executorIdle\n    | on =>\n      case active as lane in Flag return PoolAction with\n      | off => completeAt waitingIndex (ownedGeneration generation) connectionEstablished\n      | on => reserveAt zero\n'),
    ('executor_arrival_loses_waiting_owner', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n'),
    ('executor_waiting_terminal_retains_owner', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index noOwnedLease reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n'),
    ('executor_active_terminal_retains_owner', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index noOwnedLease reason)\n    | executorWork swarm endpoint demand => executorIdle\n'),
    ('executor_waiting_terminal_releases_wrong_slot', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt zero token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n'),
    ('executor_active_terminal_releases_wrong_slot', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt index token reason)\n    | executorWork swarm endpoint demand => executorIdle\n', 'def executorLaneAction : Flag -> ExecutorEvent -> ExecutorBank -> PoolAction :=\n  fun (active : Flag) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    case event as self in ExecutorEvent return PoolAction with\n    | executorArrival swarm endpoint index demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => reserveAt index\n      | on => executorIdle)\n    | executorDispatch swarm endpoint waitingIndex generation activeIndex demand =>\n      executorDispatchAction (executorTransferAllowed waitingIndex generation activeIndex bank)\n        active waitingIndex generation activeIndex\n    | executorWaitingEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => completeAt index token reason\n      | on => executorIdle)\n    | executorActiveEnd swarm endpoint index token reason demand =>\n      (case active as lane in Flag return PoolAction with\n      | off => executorIdle\n      | on => completeAt zero token reason)\n    | executorWork swarm endpoint demand => executorIdle\n'),
    ('executor_active_resource_exceeds_allocation', 'def executorResource : Count -> Count -> ExecutorBank -> Count :=\n  fun (waitingWeight : Count) (activeWeight : Count) (bank : ExecutorBank) =>\n    add (multiply (leaseOccupancy (executorLane off bank)) waitingWeight)\n      (multiply (leaseOccupancy (executorLane on bank)) activeWeight)\n', 'def executorResource : Count -> Count -> ExecutorBank -> Count :=\n  fun (waitingWeight : Count) (activeWeight : Count) (bank : ExecutorBank) =>\n    add (multiply (leaseOccupancy (executorLane off bank)) waitingWeight)\n      (multiply (next (leaseCapacity (executorLane on bank))) activeWeight)\n'),
    ('executor_waiting_resource_exceeds_allocation', 'def executorResource : Count -> Count -> ExecutorBank -> Count :=\n  fun (waitingWeight : Count) (activeWeight : Count) (bank : ExecutorBank) =>\n    add (multiply (leaseOccupancy (executorLane off bank)) waitingWeight)\n      (multiply (leaseOccupancy (executorLane on bank)) activeWeight)\n', 'def executorResource : Count -> Count -> ExecutorBank -> Count :=\n  fun (waitingWeight : Count) (activeWeight : Count) (bank : ExecutorBank) =>\n    add (multiply (next (leaseCapacity (executorLane off bank))) waitingWeight)\n      (multiply (leaseOccupancy (executorLane on bank)) activeWeight)\n'),
    ('executor_work_uncapped', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (add base (executorScanEnvelope bank)) (boundedWork workCap (executorDemand event))\n', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (add base (executorScanEnvelope bank)) (executorDemand event)\n'),
    ('executor_work_omits_fixed_charge', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (add base (executorScanEnvelope bank)) (boundedWork workCap (executorDemand event))\n', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (executorScanEnvelope bank) (boundedWork workCap (executorDemand event))\n'),
    ('executor_work_omits_scan_charge', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (add base (executorScanEnvelope bank)) (boundedWork workCap (executorDemand event))\n', 'def executorEventWork : Count -> Count -> ExecutorEvent -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (event : ExecutorEvent) (bank : ExecutorBank) =>\n    add (base) (boundedWork workCap (executorDemand event))\n'),
    ('executor_trace_omits_event_charge', 'def rec executorTraceWork : Count -> Count -> ExecutorTrace -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (trace : ExecutorTrace) (bank : ExecutorBank) =>\n    case trace as self in ExecutorTrace return Count with\n    | executorDone => zero\n    | executorThen event rest =>\n      add (executorEventWork base workCap event bank) (executorTraceWork base workCap rest (executorStep event bank))\n', 'def rec executorTraceWork : Count -> Count -> ExecutorTrace -> ExecutorBank -> Count :=\n  fun (base : Count) (workCap : Count) (trace : ExecutorTrace) (bank : ExecutorBank) =>\n    case trace as self in ExecutorTrace return Count with\n    | executorDone => zero\n    | executorThen event rest =>\n      executorTraceWork base workCap rest (executorStep event bank)\n'),
    ('executor_trace_length_omits_event', 'def rec executorTraceLength : ExecutorTrace -> Count :=\n  fun (trace : ExecutorTrace) =>\n    case trace as self in ExecutorTrace return Count with\n    | executorDone => zero\n    | executorThen event rest => next (executorTraceLength rest)\n', 'def rec executorTraceLength : ExecutorTrace -> Count :=\n  fun (trace : ExecutorTrace) =>\n    case trace as self in ExecutorTrace return Count with\n    | executorDone => zero\n    | executorThen event rest => executorTraceLength rest\n'),
]


def invoke(compiler: Path, command: str, bundle: Path):
    return subprocess.run([str(compiler), command, str(bundle)], capture_output=True, text=True, timeout=120)



# R03 arbitrary shared host composition and identity-churn controls.
MUTATIONS += [
    ('host_use_drops_weight', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankUse previous rest\n', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => leaseOccupancy pool)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankUse previous rest\n'),
    ('host_use_charges_capacity', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankUse previous rest\n', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankUse previous rest\n'),
    ('host_allocation_drops_weight', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankAllocation previous rest\n', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => leaseCapacity pool)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankAllocation previous rest\n'),
    ('host_allocation_charges_occupancy', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankAllocation previous rest\n', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankAllocation previous rest\n'),
    ('host_bank_use_wrong_dimension', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankUse previous rest\n', 'def rec hostBankUse : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseOccupancy pool) weight\n'),
    ('host_bank_allocation_wrong_dimension', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => hostBankAllocation previous rest\n', 'def rec hostBankAllocation : Count -> HostBanks -> Count :=\n  fun (axis : Count) (banks : HostBanks) =>\n    case axis as selected in Count return Count with\n    | zero =>\n      (case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight)\n    | next previous =>\n      case banks as self in HostBanks return Count with\n      | noHostBanks => zero\n      | hostBank weight pool rest => multiply (leaseCapacity pool) weight\n'),
    ('host_bank_step_ignores_action', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) rest)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool (hostBankStep previous action rest)\n', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool rest)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool (hostBankStep previous action rest)\n'),
    ('host_bank_step_drops_tail', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) rest)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool (hostBankStep previous action rest)\n', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) noHostBanks)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool (hostBankStep previous action rest)\n'),
    ('host_bank_step_updates_wrong_dimension', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) rest)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight pool (hostBankStep previous action rest)\n', 'def rec hostBankStep : Count -> PoolAction -> HostBanks -> HostBanks :=\n  fun (axis : Count) (action : PoolAction) (banks : HostBanks) =>\n    case axis as selected in Count return HostBanks with\n    | zero =>\n      (case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) rest)\n    | next previous =>\n      case banks as self in HostBanks return HostBanks with\n      | noHostBanks => noHostBanks\n      | hostBank weight pool rest => hostBank weight (poolStep action pool) rest\n'),
    ('host_use_omits_swarm', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (hostBankUse axis banks) (hostFleetUse axis rest)\n', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      hostFleetUse axis rest\n'),
    ('host_use_omits_population_tail', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (hostBankUse axis banks) (hostFleetUse axis rest)\n', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      hostBankUse axis banks\n'),
    ('host_use_duplicates_allocation', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (hostBankUse axis banks) (hostFleetUse axis rest)\n', 'def rec hostFleetUse : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (add (hostBankUse axis banks) (hostBankUse axis banks)) (hostFleetUse axis rest)\n'),
    ('host_allocation_omits_swarm', 'def rec hostFleetAllocation : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (hostBankAllocation axis banks) (hostFleetAllocation axis rest)\n', 'def rec hostFleetAllocation : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      hostFleetAllocation axis rest\n'),
    ('host_allocation_omits_population_tail', 'def rec hostFleetAllocation : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (hostBankAllocation axis banks) (hostFleetAllocation axis rest)\n', 'def rec hostFleetAllocation : Count -> HostFleet -> Count :=\n  fun (axis : Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      hostBankAllocation axis banks\n'),
    ('host_step_ignores_action', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks (hostFleetStep previous axis action rest)\n', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks (hostFleetStep previous axis action rest)\n'),
    ('host_step_drops_swarm_tail', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks (hostFleetStep previous axis action rest)\n', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) noHostFleet)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks (hostFleetStep previous axis action rest)\n'),
    ('host_step_updates_wrong_identity', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity banks (hostFleetStep previous axis action rest)\n', 'def rec hostFleetStep : Count -> Count -> PoolAction -> HostFleet -> HostFleet :=\n  fun (member : Count) (axis : Count) (action : PoolAction) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember role swarm source identity banks rest =>\n        hostMember role swarm source identity (hostBankStep axis action banks) rest\n'),
    ('host_churn_resets_banks', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity noHostBanks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n'),
    ('host_churn_duplicates_slice', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks (hostMember role swarm source identity banks rest))\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n'),
    ('host_churn_drops_population_tail', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks noHostFleet)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n'),
    ('host_churn_ignores_new_identity', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n'),
    ('host_churn_skips_deep_member', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          (hostFleetRelabel previous role swarm source identity rest)\n', 'def rec hostFleetRelabel : Count -> HostRole -> Count -> Count -> Count -> HostFleet -> HostFleet :=\n  fun (member : Count) (role : HostRole) (swarm : Count) (source : Count) (identity : Count) (fleet : HostFleet) =>\n    case member as selected in Count return HostFleet with\n    | zero =>\n      (case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember role swarm source identity banks rest)\n    | next previous =>\n      case fleet as self in HostFleet return HostFleet with\n      | noHostFleet => noHostFleet\n      | hostMember oldRole oldSwarm oldSource oldIdentity banks rest =>\n        hostMember oldRole oldSwarm oldSource oldIdentity banks\n          rest\n'),
    ('host_trace_skips_action', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => runHostFleet rest (hostFleetStep member axis action fleet)\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest (hostFleetRelabel member role swarm source identity fleet)\n', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => runHostFleet rest fleet\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest (hostFleetRelabel member role swarm source identity fleet)\n'),
    ('host_trace_skips_tail', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => runHostFleet rest (hostFleetStep member axis action fleet)\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest (hostFleetRelabel member role swarm source identity fleet)\n', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => hostFleetStep member axis action fleet\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest (hostFleetRelabel member role swarm source identity fleet)\n'),
    ('host_trace_skips_churn', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => runHostFleet rest (hostFleetStep member axis action fleet)\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest (hostFleetRelabel member role swarm source identity fleet)\n', 'def rec runHostFleet : HostTrace -> HostFleet -> HostFleet :=\n  fun (trace : HostTrace) (fleet : HostFleet) =>\n    case trace as self in HostTrace return HostFleet with\n    | hostDone => fleet\n    | hostEvent member axis action rest => runHostFleet rest (hostFleetStep member axis action fleet)\n    | hostChurn member role swarm source identity rest =>\n      runHostFleet rest fleet\n'),
    ('host_work_bypasses_slice', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (demand zero)\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n'),
    ('host_work_omits_member', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (zero)\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n'),
    ('host_work_omits_population_tail', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        zero\n'),
    ('host_work_reuses_first_demand', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand index) rest)\n'),
    ('host_work_duplicates_slice', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (hostBankAllocation axis banks) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n', 'def rec hostFleetWork : Count -> (Count -> Count) -> HostFleet -> Count :=\n  fun (axis : Count) (demand : Count -> Count) (fleet : HostFleet) =>\n    case fleet as self in HostFleet return Count with\n    | noHostFleet => zero\n    | hostMember role swarm source identity banks rest =>\n      add (boundedWork (add (hostBankAllocation axis banks) (hostBankAllocation axis banks)) (demand zero))\n        (hostFleetWork axis (fun (index : Count) => demand (next index)) rest)\n'),
]

# R03 endpoint routing, migration and discarded-state controls.
MUTATIONS += [
    ('route_occupied_loses_charge', '| occupiedRoute generation owner endpoint phase => heldLease generation', '| occupiedRoute generation owner endpoint phase => freeLease generation'),
    ('route_vacant_retains_charge', '| vacantRoute generation => freeLease generation\n    | occupiedRoute generation owner endpoint phase => heldLease generation', '| vacantRoute generation => heldLease generation\n    | occupiedRoute generation owner endpoint phase => heldLease generation'),
    ('route_reservation_steals_owner', '| vacantRoute generation => occupiedRoute generation endpoint endpoint pendingRoutePhase\n    | occupiedRoute generation owner current phase => occupiedRoute generation owner current phase', '| vacantRoute generation => occupiedRoute generation endpoint endpoint pendingRoutePhase\n    | occupiedRoute generation owner current phase => occupiedRoute generation endpoint endpoint pendingRoutePhase'),
    ('route_reservation_loses_endpoint', '| vacantRoute generation => occupiedRoute generation endpoint endpoint pendingRoutePhase', '| vacantRoute generation => vacantRoute generation'),
    ('route_migration_steals_owner', '| on => occupiedRoute generation owner destination phase', '| on => occupiedRoute generation destination destination phase'),
    ('route_migration_ignores_destination', '| on => occupiedRoute generation owner destination phase', '| on => occupiedRoute generation owner current phase'),
    ('route_migration_ignores_validation', 'migrationRouteDecision generation owner current phase destination\n        (both validated (sameCount token generation))', 'migrationRouteDecision generation owner current phase destination\n        (sameCount token generation)'),
    ('route_migration_ignores_generation', 'migrationRouteDecision generation owner current phase destination\n        (both validated (sameCount token generation))', 'migrationRouteDecision generation owner current phase destination\n        validated'),
    ('route_handshake_loses_routing', '| on => occupiedRoute generation owner current establishedRoutePhase', '| on => vacantRoute (next generation)'),
    ('route_handshake_ignores_generation', 'establishRouteDecision generation owner current phase (sameCount token generation)', 'establishRouteDecision generation owner current phase on'),
    ('route_establish_revives_vacant', '| vacantRoute generation => vacantRoute generation\n    | occupiedRoute generation owner current phase =>\n      establishRouteDecision', '| vacantRoute generation => occupiedRoute generation (listenerRouteEndpoint zero zero) (listenerRouteEndpoint zero zero) establishedRoutePhase\n    | occupiedRoute generation owner current phase =>\n      establishRouteDecision'),
    ('route_terminal_skips_release', '| on => vacantRoute (next generation)', '| on => occupiedRoute generation owner current phase'),
    ('route_terminal_reuses_generation', '| on => vacantRoute (next generation)', '| on => vacantRoute generation'),
    ('route_terminal_ignores_generation', 'finishRouteDecision generation owner current phase (sameCount token generation)', 'finishRouteDecision generation owner current phase on'),
    ('route_lookup_returns_owner', '| occupiedRoute generation owner current phase => routeLookupDecision current (sameCount token generation)', '| occupiedRoute generation owner current phase => routeLookupDecision owner (sameCount token generation)'),
    ('route_lookup_ignores_generation', '| occupiedRoute generation owner current phase => routeLookupDecision current (sameCount token generation)', '| occupiedRoute generation owner current phase => routeLookupDecision current on'),
    ('route_lookup_erases_live_route', '| on => atRouteEndpoint endpoint', '| on => noRouteLocation'),
    ('route_update_skips_selected_cell', '| routePoolCell cell rest => routePoolCell (change cell) rest', '| routePoolCell cell rest => routePoolCell cell rest'),
    ('route_update_changes_other_cell', '| routePoolCell cell rest => routePoolCell cell (updateRoute previous change rest)', '| routePoolCell cell rest => routePoolCell (change cell) (updateRoute previous change rest)'),
    ('route_update_drops_slot', '| routePoolCell cell rest => routePoolCell (change cell) rest', '| routePoolCell cell rest => rest'),
    ('route_read_ignores_deep_index', '| routePoolCell cell rest => routeAt previous rest', '| routePoolCell cell rest => cell'),
    ('route_schedule_skips_event', '| routeScheduleNext action rest => runRouteSchedule rest (routeStep action pool)', '| routeScheduleNext action rest => runRouteSchedule rest pool'),
]


# R03 normalized address attribution and authority controls.

_ATTRIBUTION_KEY = 'def rec ipv4PrefixKey : Count -> Count :=\n  fun (prefix : Count) =>\n    case prefix as self in Count return Count with\n    | zero => zero\n    | next rest => next (next (ipv4PrefixKey rest))\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_KEY, _ATTRIBUTION_KEY.replace(before, after))
    for name, before, after in [('key_drops_namespace_stride', 'next (next (ipv4PrefixKey rest))', 'next (ipv4PrefixKey rest)'), ('key_collapses_prefixes', 'next (next (ipv4PrefixKey rest))', 'zero')]]

_ATTRIBUTION_NORMALIZE = 'def normalizedSourceKey : SourceAddress -> Count :=\n  fun (address : SourceAddress) =>\n    case address as self in SourceAddress return Count with\n    | ipv4SourceAddress prefix host => ipv4PrefixKey prefix\n    | mappedIpv4SourceAddress prefix host => ipv4PrefixKey prefix\n    | ipv6SourceAddress prefix host => ipv6PrefixKey prefix\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_NORMALIZE, _ATTRIBUTION_NORMALIZE.replace(before, after))
    for name, before, after in [('ipv4_uses_host', '| ipv4SourceAddress prefix host => ipv4PrefixKey prefix', '| ipv4SourceAddress prefix host => ipv4PrefixKey host'), ('ipv6_uses_host', '| ipv6SourceAddress prefix host => ipv6PrefixKey prefix', '| ipv6SourceAddress prefix host => ipv6PrefixKey host'), ('mapped_uses_host', '| mappedIpv4SourceAddress prefix host => ipv4PrefixKey prefix', '| mappedIpv4SourceAddress prefix host => ipv4PrefixKey host'), ('mapped_uses_ipv6_namespace', '| mappedIpv4SourceAddress prefix host => ipv4PrefixKey prefix', '| mappedIpv4SourceAddress prefix host => ipv6PrefixKey prefix'), ('ipv6_aliases_ipv4', '| ipv6SourceAddress prefix host => ipv6PrefixKey prefix', '| ipv6SourceAddress prefix host => ipv4PrefixKey prefix')]]

_ATTRIBUTION_EVENT = 'def attributedSourceEvent : AttributedSourceEvent -> SourceAdmissionEvent :=\n  fun (event : AttributedSourceEvent) =>\n    case event as action in AttributedSourceEvent return SourceAdmissionEvent with\n    | attributedSourceAttempt source address swarm identity claimedKey index =>\n        sourceAdmissionAttempt source swarm (normalizedSourceKey address) index\n    | attributedSourceRegistration source address claimedKey =>\n        sourceAdmissionMaintenance (maintainSourceChurn (sourceRegistration source (normalizedSourceKey address)))\n    | attributedSourcePenalty source address claimedKey =>\n        (case source as evidence in Reachability return SourceAdmissionEvent with\n        | unvalidated => sourceAdmissionFinish noAdmissionReceipt handshakeFailed\n        | validated => sourceAdmissionMaintenance (maintainSourceBan (normalizedSourceKey address)))\n    | attributedSourceEviction address =>\n        sourceAdmissionMaintenance (maintainSourceChurn (sourceEviction (normalizedSourceKey address)))\n    | attributedSourceExpiry address expiry =>\n        sourceAdmissionMaintenance (maintainSourceExpiry (normalizedSourceKey address) expiry)\n    | attributedSourceClock issued => sourceAdmissionClock issued\n    | attributedSourceFinish receipt reason => sourceAdmissionFinish receipt reason\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_EVENT, _ATTRIBUTION_EVENT.replace(before, after))
    for name, before, after in [('attempt_uses_claim', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) index', 'sourceAdmissionAttempt source swarm claimedKey index'), ('attempt_uses_identity', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) index', 'sourceAdmissionAttempt source swarm identity index'), ('attempt_changes_slot', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) index', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) zero'), ('attempt_forces_validation', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) index', 'sourceAdmissionAttempt validated swarm (normalizedSourceKey address) index'), ('attempt_changes_swarm', 'sourceAdmissionAttempt source swarm (normalizedSourceKey address) index', 'sourceAdmissionAttempt source primarySwarm (normalizedSourceKey address) index'), ('registration_uses_claim', 'sourceRegistration source (normalizedSourceKey address)', 'sourceRegistration source claimedKey'), ('registration_forces_validation', 'sourceRegistration source (normalizedSourceKey address)', 'sourceRegistration validated (normalizedSourceKey address)'), ('penalty_uses_claim', '| validated => sourceAdmissionMaintenance (maintainSourceBan (normalizedSourceKey address))', '| validated => sourceAdmissionMaintenance (maintainSourceBan claimedKey)'), ('penalty_bypasses_validation', '| unvalidated => sourceAdmissionFinish noAdmissionReceipt handshakeFailed', '| unvalidated => sourceAdmissionMaintenance (maintainSourceBan (normalizedSourceKey address))'), ('eviction_uses_zero_key', 'sourceEviction (normalizedSourceKey address)', 'sourceEviction zero'), ('expiry_uses_zero_key', 'maintainSourceExpiry (normalizedSourceKey address) expiry', 'maintainSourceExpiry zero expiry'), ('clock_drops_issue', '| attributedSourceClock issued => sourceAdmissionClock issued', '| attributedSourceClock issued => sourceAdmissionClock zero'), ('finish_drops_receipt', '| attributedSourceFinish receipt reason => sourceAdmissionFinish receipt reason', '| attributedSourceFinish receipt reason => sourceAdmissionFinish noAdmissionReceipt reason'), ('finish_changes_reason', '| attributedSourceFinish receipt reason => sourceAdmissionFinish receipt reason', '| attributedSourceFinish receipt reason => sourceAdmissionFinish receipt handshakeFailed')]]

_ATTRIBUTION_PROJECT = 'def rec attributedSourceAdmissions : AttributedSourceTrace -> SourceAdmissionTrace :=\n  fun (trace : AttributedSourceTrace) =>\n    case trace as self in AttributedSourceTrace return SourceAdmissionTrace with\n    | attributedSourcesDone => sourceAdmissionsDone\n    | attributedSourcesThen event rest =>\n        sourceAdmissionsThen (attributedSourceEvent event) (attributedSourceAdmissions rest)\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_PROJECT, _ATTRIBUTION_PROJECT.replace(before, after))
    for name, before, after in [('projection_drops_head', 'sourceAdmissionsThen (attributedSourceEvent event) (attributedSourceAdmissions rest)', 'attributedSourceAdmissions rest'), ('projection_drops_tail', 'sourceAdmissionsThen (attributedSourceEvent event) (attributedSourceAdmissions rest)', 'sourceAdmissionsThen (attributedSourceEvent event) sourceAdmissionsDone')]]

_ATTRIBUTION_RUN = 'def rec runAttributedSources : AttributedSourceTrace -> Count -> Count -> SourceAdmission -> SourceAdmission :=\n  fun (trace : AttributedSourceTrace) (quota : Count) (capacity : Count) (current : SourceAdmission) =>\n    case trace as self in AttributedSourceTrace return SourceAdmission with\n    | attributedSourcesDone => current\n    | attributedSourcesThen event rest =>\n        runAttributedSources rest quota capacity (attributedSourceStep quota capacity event current)\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_RUN, _ATTRIBUTION_RUN.replace(before, after))
    for name, before, after in [('execution_drops_head', 'runAttributedSources rest quota capacity (attributedSourceStep quota capacity event current)', 'runAttributedSources rest quota capacity current'), ('execution_drops_tail', 'runAttributedSources rest quota capacity (attributedSourceStep quota capacity event current)', 'attributedSourceStep quota capacity event current'), ('execution_duplicates_head', 'runAttributedSources rest quota capacity (attributedSourceStep quota capacity event current)', 'runAttributedSources rest quota capacity (attributedSourceStep quota capacity event (attributedSourceStep quota capacity event current))')]]

_ATTRIBUTION_RECEIPT = 'def attributedAttemptReceipt : Count -> AttributedSourceEvent -> SourceAdmission -> AdmissionReceipt :=\n  fun (quota : Count) (event : AttributedSourceEvent) (current : SourceAdmission) =>\n    admissionAttemptReceipt quota (attributedSourceEvent event) current\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_RECEIPT, _ATTRIBUTION_RECEIPT.replace(before, after))
    for name, before, after in [('receipt_uses_zero_key', 'admissionAttemptReceipt quota (attributedSourceEvent event) current', 'sourceStartReceipt zero (planSourceStart quota validated zero zero current)')]]

_ATTRIBUTION_STEP = 'def attributedSourceStep : Count -> Count -> AttributedSourceEvent -> SourceAdmission -> SourceAdmission :=\n  fun (quota : Count) (capacity : Count) (event : AttributedSourceEvent) (current : SourceAdmission) =>\n    sourceAdmissionStep quota capacity (attributedSourceEvent event) current\n'

MUTATIONS += [("attribution_" + name, _ATTRIBUTION_STEP, _ATTRIBUTION_STEP.replace(before, after))
    for name, before, after in [('step_inflates_capacity', 'sourceAdmissionStep quota capacity (attributedSourceEvent event) current', 'sourceAdmissionStep quota (next capacity) (attributedSourceEvent event) current'), ('step_inflates_quota', 'sourceAdmissionStep quota capacity (attributedSourceEvent event) current', 'sourceAdmissionStep (next quota) capacity (attributedSourceEvent event) current')]]


def negative_checks(compiler: Path, source: str, build: Path, jobs: int = 1) -> list[str]:
    if jobs not in range(1, 9):
        raise ValueError("negative-check jobs must be between 1 and 8")
    cases = [(name, source.replace(before, after)) for name, before, after in MUTATIONS]
    if any(source.count(before) != 1 for _, before, _ in MUTATIONS):
        raise ValueError("a mutation target is absent or ambiguous")
    cases.extend([
        ("false_equality", source + "\ndef impossible : Equal Flag off on := same\n"),
        ("false_bound", source + "\ndef impossible : AtMost (next zero) zero := least zero\n"),
        ("nonterminating_proof", source + "\ndef rec loop : Count -> Count := fun (n : Count) => loop n\n"),
    ])
    if len({name for name, _ in cases}) != len(cases):
        raise ValueError("duplicate negative check names")
    negative_dir = build / "negative"
    negative_dir.mkdir(exist_ok=True)

    def reject_case(case: tuple[str, str]) -> str:
        name, candidate = case
        path = negative_dir / f"{name}.mech"
        path.write_text(candidate)
        result = invoke(compiler, "check", path)
        diagnostic = result.stdout + result.stderr
        (negative_dir / f"{name}.log").write_text(diagnostic)
        # Parser failures, crashes, timeouts and tool usage errors are not proof rejection.
        expected = "termination:" if name == "nonterminating_proof" else "mismatch:"
        if result.returncode != 1 or not diagnostic.strip().startswith(expected):
            raise ValueError(f"negative check {name} did not produce a type/termination rejection: {diagnostic}")
        return name

    if jobs == 1:
        return [reject_case(case) for case in cases]
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        # map preserves report order while each checker writes distinct files.
        return list(executor.map(reject_case, cases))


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
    paths = ["claims.json", "atomic-claims.json", "source-inventory.json", "source-ledger.json",
             "proof-roadmap.json", "proof-scope.json", "proof-audit.json", "docs/R01-CLOSURE.md", "docs/R02-AUDIT.md", "docs/R03-ADMISSION.md",
             "docs/FULL-QUALIFICATION-ROADMAP.md", "docs/SOURCE-LEDGER.md",
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
    parser.add_argument("--jobs", type=int, choices=range(1, 9), default=1,
                        help="independent negative-check workers (default: 1)")
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
    rejected = negative_checks(compiler, source, build, args.jobs)
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
              "source_dispositions": inventory["dispositions"],
              "proof_witness_audit": inventory["witness_audit"],
              "claim_decomposition_complete": inventory["semantically_complete"],
              "model_coverage_complete": catalog["load"](ROOT / "atomic-claims.json")["coverage_complete"],
              "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "compiler": provenance, "implementation_links": linked,
              "implementation_proved": False, "deployment_qualified": False,
              "blockers": ["Complete model proof coverage of the sealed source obligations" if inventory["semantically_complete"]
                           else "Complete atomic claim decomposition and model coverage",
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
