# Proof meaning and trust boundary

The checked terms inhabit dependent types in mechanism-lang. `Count`, `Flag`,
equality and the indexed `AtMost` relation are defined in source. `AtMost` lives
in `Type 0` and carries constructive witnesses. This avoids assuming a numeric
axiom or a proposition erasure feature that the checker does not provide.
The equality family lives in `Prop`.

Some results follow by reduction of a pure decision function. Arithmetic
composition, finite transition traces, generation-safe cleanup, committee
deduplication and service-round bounds use structural induction. The checker
rejects nontermination, unequal boolean endpoints and an impossible bound.
Forty-five further semantic mutations must
invalidate the corresponding proofs. These controls provide evidence that the
intended definitions matter; they are not a soundness proof of the checker.

## Trusted components

The trust base includes the pinned mechanism-lang frontend, kernel and vendored
Veil code, the OCaml compiler and dependencies, the host OS and hardware, and the
small repository scripts. The driver starts with its normal initial globals;
the proof source never references their numeric axiom or primitives. The
dependency disclosure for the complete proof bundle must be empty. No claim of
an independently verified empty-global checker run is made.

The bootstrap builds exact commits and records the resulting executable hash.
The verification command refuses an executable that differs from that build
receipt. This is reproducibility within the stated trust base, not a signed
third-party attestation. File hashes detect drift, not semantic correctness.

## Open boundaries

- `Reachability.validated` must be connected to correct QUIC token semantics,
  return reachability and restart/key behavior. The model does not verify tokens.
- Authentication, policy freshness, committee membership and source attribution
  are inputs. The committee model rejects unverified or old-epoch records,
  deduplicates a fixed roster and clears resolution on epoch reset. Correct
  signature/epoch binding, stable member indices and freshness still need
  refinement. The positive recovery threshold is supplied as a model input;
  deriving committee size minus f remains open.
- The policy model orders complete views with nonwrapping generations. Real
  publication must be atomic. Receipt validation and authorization must linearize
  with publication, or retain equivalent protection through use. A separate
  version check followed by unprotected use is insufficient. Peer identifiers,
  receipt provenance, fault detection and external governance ordering need
  refinement; the local generation alone does not establish input freshness.
- Work units are symbolic. Weighted resource and handshake-cost bounds require
  runtime cost dominance and complete accounting of retained allocations.
  The shared token-bucket trace proves a discrete burst-plus-rate envelope;
  trusted ticks must correspond to the real clock. Per-source security-state
  eviction and restart persistence remain open.
- Poll fuel bounds processed events and conserves the retained backlog. A model
  wakeup flag does not establish correct waker registration, executor fairness,
  traffic admission opportunities or wall-clock progress.
- Pending slots carry generations. Arbitrary serialized traces preserve capacity,
  and stale completions cannot release a later generation. The Rust mapping must
  establish atomic transitions, owned callback tokens, complete terminal-path
  handling and safe machine-counter wrap behavior.
- Critical service progresses within a bound on completed service rounds.
  The implementation must preserve the modeled FIFO rank and perform the promised
  critical service each round. Consensus progress, catch-up performance, permit
  hold times and wall-clock scheduler fairness are separate obligations.
- RPC constructors represent already parsed requests and responses. Actual JSON
  parsing, proxy identity verification, HTTP status mapping, retry timing and
  origin isolation require implementation evidence.
- Firewall flags describe per-identity inclusion. Address expansion, ports,
  rule order, notrack behavior and mitigation products require their own checks.
- Gate booleans express a necessary evidence policy. No model term creates the
  measurements or establishes that an operator report is truthful.

The compiler proves the model statements actually written. It does not prove
that the statements fully capture prose, that Rust executes the model, or that
the network satisfies the environment assumptions. `--require-complete`
therefore remains blocked. Simply adding a JSON status or a theorem name cannot
promote a claim to implementation-proved or deployment-qualified.
