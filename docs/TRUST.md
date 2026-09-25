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
The 367 additional semantic mutations must
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
  trusted ticks must correspond to the real clock.
- Module 42 charges processed attempts and publications from an
  independent shared balance before the delegated policy/source event. Its cost
  envelope includes denied operations but receives already constructed policy
  receipts. Receipt creation, authentication, pre-budget work, exhausted guards,
  maintenance, completion and established resources need separate cost bounds.
  Runtime evidence must justify fixed rates, capacities and per-operation weights,
  including payload and roster bounds, and the atomic pre-state ordering. Policy
  recovery and honest traffic can be delayed; no scheduling fairness is proved.
- Module 43 produces policy receipts internally after the work-credit guard,
  from the current policy view and attempted identity. Every processed query
  spends work credit, including denials. Mixed traces preserve the work and
  handshake cost envelopes if the operation weight also covers bounded query
  and receipt construction. Authentication flags, peer identity bindings,
  runtime entry-point discipline and atomic query/charge/admission still require
  refinement. Pre-guard authentication, exhausted guards, dispatch, cleanup and
  established-resource costs remain outside this envelope.
- Module 44 adds a finite poll fuel that charges every dispatched ingress event,
  including exhausted-credit guards, maintenance and completion. Exact queue
  reconstruction, prefix execution and resumption preserve the existing state
  semantics and pending bound. Its combined cost envelope assumes an event
  weight covering all per-dispatch work outside policy and handshake costs.
  Queue construction, pre-dispatch authentication, empty-poll costs, runtime
  wakers and executor overhead still need separate bounds. Cleanup bypasses
  exhausted policy work credit but requires poll fuel and actual scheduling.
  Positive fuel, executor fairness and cleanup priority are open refinements;
  the model does not supply a wall-clock latency or global polling-rate bound.

- Module 45 couples a persistent FIFO queue to the carried resource state.
  Under the explicit scheduler with one unit of fuel per delivered turn, any
  original prefix finishes after its length of turns despite finite arrivals
  before every turn. The exact suffix and arrival history remain queued.
  Repeated service preserves the dispatched-trace semantics, pending capacity
  and a combined cost envelope with each initial burst counted once. Runtime
  queue retention, concurrent producers, actual wakes, enough service turns and
  runtime simulation remain open. This supplies no wall-clock
  cleanup bound, queue-memory bound or bound on enqueue, empty-turn or executor
  overhead.

- Module 46 permits arbitrary finite varying-fuel turns, including zero. It
  preserves exact queue and dispatched-state semantics. An original prefix
  is serviced when cumulative delivered fuel equals its length plus natural
  slack; later dispatched events can further change the resource state.
  Dispatch count is bounded by summed fuel, pending capacity is preserved,
  and the cost envelope counts each initial burst once. Runtime fuel delivery,
  actual wakeups, queue growth, enqueue and empty-turn costs, and wall-clock
  latency remain separate obligations. The theorem does not guarantee enough
  fuel will be delivered or certify an infinite schedule.

- Module 47 admits only the arrival prefix that fits a fixed queue-entry cap
  before each poll, retains old backlog and reports an explicit rejected suffix.
  An initially fitting queue stays within its cap across finite schedules.
  Filtering preserves delivered fuel, conditional service of original queued
  prefixes, exact dispatched-state semantics and the combined dispatch-cost
  envelope. Entry count is not a byte bound. Offered-batch construction,
  admission, rejection and storage costs remain outside that envelope.
  Newly offered cleanup, maintenance, clock and publication events may be
  rejected; safe delivery or loss/retry semantics require runtime refinement.
  No service guarantee applies to rejected arrivals. Real fuel delivery,
  wall-clock latency, cap changes and restart remain open.

- Module 48 additionally bounds a fixed sum of immutable per-event payload
  charges, alongside the entry cap, before dispatch and across finite schedules
  when the corresponding initial bound holds. Exact overflow accounting,
  conditional original-prefix service and the execution envelope are preserved.
  Concrete storage dominance and non-forgeable charges remain assumptions.
  Offered and rejected batches, temporary selections, proof certificates,
  allocator overhead and charge/admission work are outside the retained-payload
  bound. Both limits can reject mandatory events. Safe delivery, runtime fuel,
  wall-clock progress, mutable payloads, cap changes and restart remain open.
- Module 49 bounds the number of arrivals selected for admission inspection
  before payload and entry filtering. Accepted, rejected and unexamined arrivals
  reconstruct each offered batch exactly. Unexamined arrivals are caller-owned
  and excluded from the retained-queue bound. Queue bounds and conditional
  service of existing backlog survive scanning; this gives no progress or
  resubmission guarantee for unexamined arrivals. The per-turn cost theorem adds
  a symbolic charge for each examined event, including rejected and zero-payload
  events, to the existing dispatch envelope. Concrete scan-cost dominance,
  backlog summation, offered-batch construction, external storage, rejection
  disposal and executor work remain open. Mandatory events need a delivery
  argument under both admission exhaustion and queue overload.

- Source-table churn preserves supplied rate debt and bans in a fixed slot vector.
  Runtime refinement must establish canonical validated keys, unique initial
  bindings and complete security-state classification, including simultaneous
  restrictions. Selected-cell charging refuses missing and unvalidated sources,
  its tracked restriction refuses banned and exhausted sources, and a validated
  cell charge is the restriction-trace charge step; restriction traces preserve
  a fixed per-source debt bound. Trusted debt and ban expiry assume a validated
  source, current restriction generation and deadline; the model does not check
  timer provenance or stale callbacks itself. Keyed source-system traces now
  compose lookup, churn and restriction updates, preserving initial slot width
  and a debt bound for every resident supplied by the initial quota witness.
  Lookup and update select the first matching key; runtime canonical extraction,
  unique bindings and atomic enforcement before work still require refinement.
  Source-admission traces couple source charging, shared credits and pending
  reservation in one atomic step. Refusal leaves the state unchanged; completion
  preserves source restrictions and global credits. Internal receipts bind a
  slot index and generation to the successful attempt's pre-state. The raw plan
  and commit helpers are not separate runtime APIs. State bounds require fixed
  configuration and initial credit/debt bounds where stated. Cumulative starts
  counted from emitted receipts cannot exceed initial shared credit plus trusted
  issuance. The closed timed trace language issues exactly rate credits per
  trusted tick before clamping, giving a burst-plus-rate bound when initial
  credit is within burst. A supplied cost weight bounds accepted-start work;
  it does not account for rejected attempts or other resource classes.
  Arbitrary pending prefixes and suffixes now have enabled admission, exact
  receipt, counting, completion and refusal proofs. They preserve unselected
  leases and reject mismatched generations, including stale receipts after reuse.
  Fixed runtime slot identities, internal receipt provenance and atomic callback
  behavior still require refinement; the prefix representation is a model of
  indexing, not a proof about Rust storage or ConnectionId mapping.
  Policy/source traces now validate current policy receipts before that same
  admission step. They preserve the indexed admission equations, resource bounds
  and receipt-counted rate and cost envelopes across policy changes. Policy
  receipts and completion receipts have distinct internal provenance obligations;
  the composed model does not authenticate their raw constructors. Policy
  validation and resource enforcement must linearize together in the runtime.
  Live per-source pending attribution, established resources, real clock
  correspondence, bounded retention and restart persistence remain open.
  Overflow refusal does not prove honest-source admission or reconnect fairness.
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
