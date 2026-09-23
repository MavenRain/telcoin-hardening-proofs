# Evidence still required

No runtime or deployment result has been supplied or synthesized. The `.build`
report records local model checking only. The current complete-qualification
command rejects all implementation and deployment certification.

`initial-model-check.json` preserves the first model-checking receipt.
`trace-model-check.json` records the expanded transition proofs, atomic ledger,
semantic mutation checks and validation of the pinned implementation file hashes.
`portable-bootstrap-model-check.json` repeats that validation after fixing fresh
GitHub bootstrapping to fetch only the compiler's required Veil submodule.
`policy-model-check.json` records versioned policy and receipt proofs, mixed
resource traces, their negative controls and the pinned implementation source links.
`source-table-model-check.json` records bounded source-table churn, preservation
of existing security state, four additional atomic obligations and 15 additional
semantic mutation checks. It was produced without `--implementation`, so its
`implementation_links` status is `not_checked_this_run`: that run did not compare
the pinned implementation file hashes. It is the only receipt without that check.
The earlier receipts carry `source_links_checked`, most recently
`policy-model-check.json` (revision 579aa551fe39593e32a48e1dbcfeccbccab64e3e,
6 entries). To restore the check, run `python3 -I tools/check.py --implementation
/path/to/telcoin-network` against a checkout at that revision and copy
`.build/report.json` over this receipt.
These are reproducible local receipts within the trust boundary described in
[TRUST.md](../docs/TRUST.md), not deployment measurements or external attestations.

The authoritative run requirements are in
[the acceptance specification](../sources/w1-modified/04-DECISIONS-AND-ACCEPTANCE.md).
Each future run needs exact implementation/dependency/configuration identities,
accepted thresholds, hardware and host settings, topology, offered and accepted
load, traffic generation details, raw metrics, instrumentation overhead, test
duration, failures and uncertainty. Include the firewall state and all swarms.

Gate 1 covers the maintained Retry feature. Gates 2 through 6 additionally cover
resource/timeout settings, resilience, topology/transaction paths, operations
and storage. A feature-level result does not satisfy the remaining gates.

Operational evidence remains an explicit environmental assumption even when a
formal model proves that its recorded values satisfy an acceptance predicate.
