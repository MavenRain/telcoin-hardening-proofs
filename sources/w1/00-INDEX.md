# W1 transport — issue drafts, index

## 1. State

Drafted 2026-09-19 from `plans/validator-network-hardening.md` (T1–T12), revised 2026-09-21 in pass R2. **Nothing has been posted, committed or pushed.** `w1/` and `tasks/` are git-ignored. Plan vocabulary (T1–T12, W1, W2) is allowed in this file only; the twelve drafts carry none.

Citations are pinned to `main` at `9b2a06b7`, which is where they were pinned before R2; no `path:line` moved during the pass.

R2's working files are in `tasks/w1/r2/`. `STATE.md` is the orchestrator's ledger: one row per draft per stage, the agent ids, and a dated note for every ruling taken during the run. `base/` holds the pre-revision copy of each draft and of this index (`00-INDEX.pre-r2.md`), with `SHA1SUMS`. Per-stage logs are `restore-TNN.md`, `gaps-TNN.md`, `reaudit-TNN.md`, `patch-TNN.md`, `rpatch-TNN.md`; checkpoints are `ck-<stage>-TNN.md`. The R1 working files stay in `tasks/w1/`.

## 2. What the owner decided on 2026-09-21 and how it was applied

**Disclosure.** Five drafts are filed as private security advisories (`quic-initial-unvalidated-cost`, `pending-inbound-unbounded`, `accepts-unbounded-per-poll`, `endpoint-driver-contention`, `single-inbound-socket`) and seven as public issues. Three rules bind every sentence of a public draft: no flood figure and no relative restatement of one; no path from sustained inbound arrivals to a stalled swarm task, a stalled command channel or a hung epoch start; and a line about a private sibling names the sibling's *area* in a fixed public-safe wording, never its fault, harm or figures. A fourth fable reviewer read all seven public drafts against the five private ones and found two standalone leaks and two rule-4 combinations, all patched (section 8). Section 4 lists the three drafts whose class the reviewer asked you to reconsider.

**T01 uses the long version.** The 2,154-word copy is now `w1/T01-quic-initial-unvalidated-cost.md`; the 1,599-word copy is kept at `tasks/w1/r2/base/T01-quic-initial-unvalidated-cost.short-1599.md`. Every later stage ran on the long copy, so the short one is a historical record and not a fallback.

**There is no word ceiling.** Both ceiling lines were struck from the shared brief, and no stage ran a compression pass. The restore stage put back what the ceiling had cost: 19,178 words plus the T01 swap became 26,399, with 168 added claims logged for re-audit, two items withheld for disclosure and four content removals. The gaps, patch and review-patch stages carried that to 38,674 words. Per draft the range is now 2,639 to 3,752 words, against 1,593–1,600 before. What came back is listed per draft in the R1 index's section 6 and in each `restore-TNN.md`: T01's added-round-trip measurement and two hazards, T04's honest-failure-rate measurement and committee-exemption approach, T10's third surveyed placement, T12's socket-load sentence and two approaches, T11's second Problem code block and 99th-percentile column, and the rest.

**`## Open questions` in every draft.** A new eighth heading sits between `## Measurements that would affect the decision` and `## Related`. It carries what rewriting cannot close: a fact nobody has established, a decision that belongs to the maintainers or to a different issue, a tension a measurement would resolve, and the one input still unsupplied. There are 52 entries across the twelve, 3 to 6 per draft, reproduced in full in section 5. Each entry states what is unknown and what would settle it, and states no answer; the re-auditors checked every entry for an implied answer, and the blind-test reviewer found the section had become a steering channel in its own right (section 8).

**The reference deployment.** One paragraph goes into `## Background` verbatim in all twelve drafts, directly after the citation-baseline sentence: a committee of ten validators, each on an Ubuntu server with 8 CPUs and 32 GB of RAM, running one node process with two swarms (the primary's and one worker's), with the network between them unspecified. Every "supplied by the maintainers" that referred to committee size, swarms per host or reference hardware was replaced with the value. Quantities derived from those inputs show their arithmetic, cite the source constant behind every factor, and are marked "derived, not measured" (T06's 131,072 pending attempts and 200 MiB per host; T05's 59.4 GiB worst case; the eighteen committee handshakes per host that T08, T09, T10, T11 and T12 all use; 8 CPUs read as eight tokio worker threads, only after the runtime-building code was opened). No proposed limit, budget or threshold is derived anywhere.

**The two documentation lookups stay unperformed.** What a GitHub-hosted `ubuntu-latest` runner permits (a private network namespace, a virtual interface pair) is T02's first open question; how Dependabot treats a crate replaced through `[patch]` is T03's first. Both are stated in the issues rather than settled, and no agent fetched GitHub's documentation. T12's second open question is a third of the same kind: whether the kernel on the reference hosts spreads packets arriving on one port across several sockets, which needs platform documentation the round did not allow.

**The title area prefix stays.** Ten drafts still open with `network-libp2p:` although most cited lines live in upstream crates; it names where this node builds the listener. No review finding named a title, so no title changed, and all twelve remain within fourteen words. T11's rpatch log records the prefix as still a maintainer naming call for a fault that sits in an upstream crate's configuration.

## 3. The twelve drafts

| Row | File | Title | Labels | Words | Filed as | Open questions |
|---|---|---|---|---|---|---|
| T1 | `T01-quic-initial-unvalidated-cost.md` | network-libp2p: a full QUIC handshake is paid before any node decision, forged sources included | security, enhancement | 3,695 | Private advisory | 3 |
| T2 | `T02-quic-listener-interop-tests.md` | ci: nothing tests the QUIC listener before establishment or against cross-version dialers | ci, security | 2,639 | Public issue | 4 |
| T3 | `T03-patched-transport-crate-upkeep.md` | build: no process exists for pinning, watching or rebasing a modified QUIC transport crate | dependencies, security, tech debt | 3,035 | Public issue | 4 |
| T4 | `T04-pending-inbound-unbounded.md` | network-libp2p: a swarm holds unboundedly many unfinished inbound handshakes, unattributed to any source | security, enhancement | 3,060 | Private advisory | 4 |
| T5 | `T05-per-peer-ceilings.md` | network-libp2p: ceilings on an established peer multiply, and only one has a derivation | security, enhancement | 3,348 | Public issue | 4 |
| T6 | `T06-accepts-unbounded-per-poll.md` | network-libp2p: arriving QUIC attempts can hold a swarm task, stalling its commands and timers | security, enhancement | 3,404 | Private advisory | 4 |
| T7 | `T07-endpoint-driver-contention.md` | network-libp2p: inbound handshakes and established traffic share one endpoint lock, cost unmeasured | spike, security | 3,147 | Private advisory | 5 |
| T8 | `T08-validated-address-handshake-rate.md` | network-libp2p: nothing bounds how fast one real address can start handshakes under fresh identities | security, enhancement | 3,338 | Public issue | 4 |
| T9 | `T09-redundant-cert-verification.md` | network-libp2p: full inbound handshakes parse the peer certificate three times, running seven signature verifications | enhancement, security | 3,387 | Public issue | 5 |
| T10 | `T10-late-refusal-of-strangers.md` | network-libp2p: every identity-based refusal of an inbound peer runs after the full handshake | security, enhancement | 3,029 | Public issue | 4 |
| T11 | `T11-dialer-chosen-kx-group.md` | network-libp2p: the inbound QUIC handshake computes whichever key-exchange group the dialer puts first | security, enhancement | 2,840 | Public issue | 5 |
| T12 | `T12-single-inbound-socket.md` | network-libp2p: one UDP socket per swarm carries every inbound and outbound QUIC datagram | spike, security | 3,752 | Private advisory | 6 |

Twelve drafts, 38,674 words, 52 open questions.

## 4. Decisions still yours

Every item below was raised by an agent or a reviewer and left undecided on purpose. Nothing here is a defect in a draft.

- T01, disclosure class. Reviewer D's reverse check finds Problem paragraphs 1–2 already public: public rustls and `quinn-proto` source, RFC 9000 sections 8.1 and 14.1, and `quinn-rs/quinn#2782`'s own statement that TLS session setup runs on the new-Initial path. What is private-making is paragraph 3's admission that floods were run and disagree, and the Measurements figures. The alternative is a public issue, which takes out every flood figure including the token-answering run, and most of Measurements with it.
- T01, Goal item 2. It says the node reports the reason for a refusal "wherever the node is given one" rather than asserting the node is given one; what the swarm reports for an attempt that ends without establishing sits in `pending-inbound-unbounded`'s area, so the patcher did not open that path. The alternative is asserting it, which needs that source opened and a scope check against the private sibling.
- T01, flood run. It asks for listener CPU per swarm task "where nothing on the host attributes it", falling back to one swarm at a time. Whether anything on the reference host attributes CPU per task is a property of your hosting, like the two inputs already under Open questions.
- T02, Goal item 2. It is now scoped to a flood carrying a forged source address, which the devnet, network-namespace and privileged-lane entries can meet (and arguably the packet-level harness, which has no sockets) but the in-process, two-build and version-matrix entries cannot. That is more than one surveyed approach, so it passes the rule; confirm the narrower reading is what you intended, or widen it back to any forged identifier.
- T02 and T08, the existence of the private harnesses. T02 line 74 and T08 line 70 both say no forged-source flood measurement exists, that the test environment would not forward such packets, and what the existing harnesses could not forge. No figure is carried, so no rule is broken, but a reader learns that private flood runs exist and what medium they ran on. The alternative is to drop the absence statement, which costs both drafts the limit the sentence exists to state.
- T02, the two-build entry. It states the build-and-cache cost as unmeasured. A CI wall-time figure for the current `pr.yaml` jobs would give that entry the same kind of evidence the others carry; the alternative is leaving it as the one entry with no cost.
- T03, the last Related line. Four of its seven placeholders are private siblings and all substitute to the same words, so after substitution the line reads "a related security advisory" three or four times over. Collapsing them into one mention at filing time reads better and drops four links; the drafts were left enumerating all seven because regrouping them in the text would sort the siblings into private and public in the published issue.
- T03, Goal item 4. It says the end-to-end suite runs "on a committee of ten", while the suite's local testnet is four validators on one host (`crates/e2e-tests/src/lib.rs:209-214`, `:317-323`), so ten means extending the harness or providing test hosts. The measurement carries that caveat; the alternative is to name the reference committee size conditionally in the Goal instead.
- T03, the preamble. Whether a build-process issue needs the full canonical preamble was raised in R1's adjudications and is still unanswered; it was left alone through R2 as ordered.
- T04, the dropped Goal item 4. The item said the hold time for an unfinished inbound connection is a chosen value, and it went because only one of the five surveyed entries could produce it. The facts survive in the Problem, in the shorter-deadline entry and in a new conditional hazard, but no Goal property now says the hold time is not the node's to choose. The alternative is to restore it in a form at least two entries can meet, which the patcher could not find.
- T04, the flood paragraph. The passage under **Per-pending-connection footprint** is now the longest in the draft and two reviewers disliked it. Ledger ruling 9 is what keeps both harnesses in it (both or neither). A ruling that this draft may drop both flood runs would shorten it cleanly; the patcher did not assume one.
- T07, disclosure class. Reviewer D rates this the strongest reverse-check candidate: the Problem is a source walk that arrives at what `quinn-rs/quinn#2782` (open) and `#2795` already publish about every quinn user, with the node-side placement added. Only the Measurements are private-making. The alternative is a public issue with those lines withheld, after which the sweep in **Hold time against attempt rate, on one endpoint** loses its lower bound and needs a public-safe replacement; the link-derived upper bound survives a public filing because it is RFC text and arithmetic.
- T07, the two hold times. Reading them needs a locally modified `quinn`, which the draft states conditionally. If the maintainers would rather not carry one, the two hold times have no read point at all and the decision rests on latency and drops alone.
- T07, the non-committee peer population. The draft opens a second unsupplied input, how many peers beyond the committee a node carries, which its honest reconnect rate needs and which the supplied inputs do not cover. The alternative is to drop that open question and leave the rate unscoped.
- T09, the cost split's comparator. The cold reviewer objected that the decisive measurement's comparator was a prototype of the change it decides on. The patcher took the second of the two available fixes: the run now splits server CPU per full inbound handshake by location, and the build with the repeated parses removed is kept only as optional confirmation after a decision. The alternative is the first fix, keeping the two-build comparison as the decisive run.
- T10, the `IncomingConnectionError` clause. The refused half of the count has a node-owned read point that was deliberately left out: a refusal reaches the node's event loop as `SwarmEvent::IncomingConnectionError` carrying the peer id and the denial (`libp2p-swarm-0.48.0/src/lib.rs:753-759`), taken today by the catch-all arm at `crates/network-libp2p/src/consensus.rs:853-854`. It is node code in a public repository and a public sibling already states it, but placing it next to line 14 puts two members of disclosure combination C1 in one draft. If you want the read point named, it is one clause in *how often the node refuses anyone*.
- T11, Goal item 3. It is now required for closure and depends on a per-listener count of negotiated key-exchange groups that no node-owned code can produce, because `libp2p-quic`'s TLS configuration accessor is `pub(crate)`. The alternative is to drop the item; the draft's fourth open question asks when a supported release would expose it.
- T12 and T07, the shared sweep. T12's in-scope top is now bounded by the link you have not supplied, stated as R × 9,600 bit/s at the 1,200-byte Initial minimum; T07's first measurement inherits the same sweep. Read the two side by side before filing so the arithmetic is phrased the same way.
- The network between validators is the one input still unsupplied, and it is an open question in ten of the twelve drafts (every one but T03 and T09). Link speed and round-trip times would make T01's sweep, T04's and T05's reconnect runs, T07's rate axis, T11's dial timings and T12's honest peak concrete.

T05 and T06 raise nothing that needs you. T05's one judgement call is recorded in its log: source answered the occupancy-sampling question the cold reviewer wanted asked, so it became text rather than a fourth open question.

## 5. Open questions in the drafts

All 52, copied from `tasks/w1/r2/open-questions.md`, which was extracted mechanically from the `## Open questions` section of each draft after the review-patch round.

**T01 — 3**
- What is the network between validators: link speed, and round-trip times between the places they run?
- What sits between the public internet and a validator's UDP socket, and what does it drop?
- Would `libp2p/rust-libp2p` take a decision point ahead of `accept()`?

**T02 — 4**
- What does a job on a GitHub-hosted `ubuntu-latest` runner get to do with the network stack: can it create a private network namespace and a virtual interface pair?
- Are validators ever expected to run two releases at once, as a supported deployment state rather than only during an upgrade?
- Does a pairing run as a single build, both crate versions linked into one test binary, give the same result as one run as two separately built nodes?
- What is the network between validators: link speed and round-trip times?

**T03 — 4**
- What does the bot that opened #1393 and #1394 do with a dependency that is not resolved from the registry?
- What does `cargo deny` 0.19.9 report for a package presented as a registry release, a git source, a path copy or a vendored tree?
- If no scanner matches advisories against a carried copy, is that gap accepted or does the procedure carry a step that closes it?
- Is the lag the third Goal item bounds measured to a merge in this repository or to a tagged release of it?

**T04 — 4**
- Is the Goal item about one remote's share of pending occupancy a closing condition for this issue?
- Which resource gives out first as pending inbound connections accumulate?
- What is the network between validators?
- Does the honest failure-rate window have to close before this issue does?

**T05 — 4**
- Is the peer-count gate, `max_peers()` at 39 on defaults, meant to be the standing bound on how many distinct identities can hold these ceilings at once?
- What link speed and round-trip times separate validators on the reference deployment?
- Should a remote whose `PeerId` is in no committee the node tracks and is not on the operator's allowlist be admitted to these ceilings?
- What share of the reference host's 32 GB may this transport hold at peak?

**T06 — 4**
- What is the network between validators?
- Has a validator ever stalled this way?
- What does an honest peer do when its dial passes its own deadline with no reply?
- Do the container-bridge bands hold for this node on current versions?

**T07 — 5**
- How long is the endpoint lock actually held, per Initial and per accept?
- How much added latency on established consensus traffic is too much?
- How many peers beyond the committee does a node carry?
- What is the network between validators?
- Will `quinn-rs/quinn#2782` merge, and when?

**T08 — 4**
- Is the node to refuse identities it does not recognise?
- Do the two rates overlap?
- What network sits between the validators?
- How many validators share a source address?

**T09 — 5**
- Which issue owns the presenter's choice of certificate signature scheme?
- Would `rust-libp2p` take a change to this behaviour, and on what timeline?
- What do the figures above come to on the crates `Cargo.lock` resolves?
- At what honest reconnect rate should the cost split be read?
- Where does the mixed-version handshake in the honest-peer observable run?

**T10 — 4**
- Should an identity the node has never seen be refusable at all?
- Should a placement be chosen before, alongside, or after that policy decision?
- Does a returning peer ever resume, and how often?
- What network sits between validators?

**T11 — 5**
- Does a node on this release complete a handshake with a stock dialer of the previous one?
- Do the per-group costs on the resolved provider keep the shape the superseded figures showed?
- What is the network between the validators of the reference deployment?
- Does a supported release of `libp2p-quic` let a node reach the TLS configuration its listener uses, and when?
- How many dialers outside the committee reach a node on the reference deployment, and how often?

**T12 — 6**
- What is the honest peak this socket has to carry, and what completion time counts as no worse off?
- Does the kernel on the reference hosts spread packets arriving on one port across several sockets the way the upstream issue describes?
- What run would put evidence behind a changed socket layout?
- Which way does a larger receive buffer move honest throughput?
- What receive buffer do the reference hosts actually give the socket?
- What is the network between validators?

## 6. Where source contradicted the plan — fix these in `plans/validator-network-hardening.md`

The plan file is still uncorrected. Nothing below was written back into it; R2 did not touch `plans/`, which is outside the allowed edit surface.

| Plan says | Source shows | Found by |
|---|---|---|
| T6: "one poll drains arbitrarily many Incomings"; accepts starve behaviours | One `accept()` per yielded swarm event; behaviours are polled first. What is unbounded is how long the task runs before yielding: the accept path spends no tokio cooperative budget, so under sustained arrivals the command channel, the record-refresh tick, the peer-manager heartbeat and the stream sweep stall. **Harm, verified:** an epoch start's `wait_for_network_peers` sends on that channel and awaits a reply with no timeout, so it hangs without bound (`start_epoch.rs:964-978`, `types.rs:704-708`). The plan's fix ("bounded accepts per poll") addresses a bound that already exists. The obvious approach — yielding in TN's own `run` loop — needs no fork. | T06 drafter, auditor, re-auditor |
| T10: the verifier check "reads the admitted set the established-inbound gate uses" | No such set gates admission. `handle_established_inbound_connection` refuses only self and banned peers (`peers/behavior.rs:98`, `:103`, `:107`); the repo says so at `consensus.rs:115`. Committees and the operator allowlist gate eviction and scoring only. | T10 drafter; confirmed twice |
| T4: 65 s handshake timeout | The configured 65 s never reaches quinn (`libp2p-quic-0.14.0/src/config.rs:139` destructures it to `_`); the `SwarmBuilder`'s 10 s `TransportTimeout` is the effective inbound bound. And `libp2p-core` *does* have an inbound-only constructor (`timeout.rs:76-82`); what conflates directions is `libp2p-quic`'s single field and `with_connection_timeout`. | T04 drafter, auditor |
| N1 / W0: the saturation change is in `quinn-proto` 0.11.17 | It landed in **0.11.15** (`quinn-rs/quinn#2683`). `main` resolved 0.11.18 before #1408, via dependabot #1393. | orchestrator, T01 verifier |
| T12: `SO_REUSEPORT` conflicts with QUIC connection-ID routing | Overstated (the overstatement was in my seed). With `migration(false)` a connection's 4-tuple is stable; `quinn-rs/quinn#1576` says connections move between drivers only on migration. What remains: one socket per quinn endpoint, one bind per `libp2p-quic` listener, and the attacker's control of the 4-tuple. | T12 auditor |
| T9: provider change supersedes every cost figure | The duplicated certificate verifications run on `ring` and `ed25519-dalek` directly, not on the rustls provider. But `ed25519-dalek` moved 2.2.0 → 3.0.0 with the upgrade, so those figures are superseded anyway. | T09 drafter, auditor |
| T9: two fixed primitives per parse | The **presenter chooses** the self-signature scheme (`libp2p-tls-0.7.0/src/certificate.rs:428-517`): RSA, ECDSA P-256 / P-384 and Ed25519 verify; P-521 and Ed448 fail closed. The triple parse multiplies a cost the dialer partly chooses. Candidate sibling of T11. | T09 auditor, fixer, re-auditor |
| T11: "re-check against the 0.7.0 default" | The problem holds and is sharper: rustls walks the **client's** group order (`server/hs.rs:546-569`, `:630-637`); server preference cannot protect it. Groups: X25519MLKEM768, X25519, P-256, P-384. | T11 drafter, auditor |
| T7: (research) the server's key share and signature run off the endpoint lock | They run inside `read_handshake`, under the lock (`rustls-0.23.37/src/server/tls13.rs:502`, `:787`). Upstream `quinn-rs/quinn#2782` (open) describes exactly this; two preparatory PRs merged. | T07 drafter, auditor |
| T1: "server sends no `NEW_TOKEN` frames" | `libp2p-quic` 0.14.0 enables quinn's `bloom` feature. The constraint that holds is the client token store keyed by server name while every dial uses `"l"`. The same keying means a node's client session store holds at most one TLS session across all remotes, so honest peers rarely resume. | T01 verifier, T10 auditor |
| T2: `libp2p-quic` 0.13.1 → 0.14.0 "unchanged" | The accept path is unchanged; the manifest is not: the provider feature and an explicit `quinn-proto` feature set (including `bloom`) moved inside `libp2p-quic`. | T02 auditor |
| T5 / T8: `max_peers()` = 39 is the number of identities a swarm retains | The gate registers the connection before it tests the count, so the identity that makes the count reach `max_peers()` is the one disconnected: **38 are retained per swarm, not 39** (`peers/behavior.rs:247-267`, `peers/manager.rs:611`). T05's derived ceilings moved from 2 × 39 × 8 = 624 to 2 × 38 × 8 = 608. | T08 re-auditor; orchestrator confirmed in source; patched in T05 and T08 |
| T6 / #1398: the 120 s peer wait runs once per worker | At `main` it runs for the primary and worker zero only (`crates/node/src/manager/node/start_epoch.rs:444-445`). The per-worker form is in **#1390, unmerged**; #1398 is the issue about it. | T01 re-auditor; the only draft repeating the claim was T02, patched in a second pass |
| T10: an identity-based refusal is visible where established connections are handled | Identity refusals never reach `on_connection_established`; the swarm reports them as `IncomingConnectionError` instead (`libp2p-swarm-0.48.0/src/lib.rs:741-762`), so the registration and limit check at `peers/behavior.rs:249-272` never run for them. | T10 re-auditor; the patcher disputed the exact range and the orchestrator upheld the dispute against source |
| T7 / T12: the flood sweep's top is the harness's collapse point | A sweep to 300,000 attempts per second is **2.9 Gbit/s** at RFC 9000's 1,200-byte Initial minimum (1,200 bytes = 9,600 bits), above a 1 GbE link, which the acceptance rules put out of scope. The top of the sweep has to be a function of the link speed the maintainers supply, stated as a rule until it arrives. | Reviewer B (cold, T07–T12); mirrored into T07's first measurement |

## 7. Findings outside W1 that need an owner

- **`KeyLogFile` in `libp2p-tls` 0.7.0** (`src/lib.rs:65`, `:90`), new with #1408 and now on `main`: with `SSLKEYLOGFILE` set in a validator's environment the node writes TLS session secrets to that path. In none of the twelve by ruling; needs its own issue.
- **`cargo audit` reports 11 vulnerabilities against `main`'s `Cargo.lock` today** (T03 auditor's control, advisory db of 2026-09-18). Deliberately kept out of T03. Six of the eight 2026 `quinn-proto` advisories exist only as repository advisories and are absent from RustSec, so `cargo audit` cannot see them; TN resolves 0.11.18, which has all the fixes. This is N2.
- **No stranger-refusal policy exists** (cross-draft ruling R8). T10 and T08 both lean on it conditionally. W2. T05's question — is `max_peers()` = 39, checked only after establishment and bypassed for validators and allowlisted peers, the intended standing bound on identities? — belongs with it.
- **`[workspace.dependencies]` declares `quinn-proto = "0.11.8"`** (`Cargo.toml:219`); no member uses it. Inert, and easy to mistake for a security floor.
- **No metric counts admission denials or inbound handshake starts**; established inbound connections are counted (`metrics.rs:154-160`). W7.
- **Are validators ever expected to run two releases at once?** T02 leaves it open; an answer sharpens its first Goal item.
- **Ledger gap:** the honest-throughput side of the receive-buffer trade-off has no ledger entry (`sentry-research/r8/bench-wan.md` was not among the plan's ledger sources). T12 states it in prose with no number.
- `plans/` and `sentry-research/` are untracked and unprotected on this pushed branch (reported, not changed). Your local `main` ref is stale at `2a2891db`; `origin/main` is `9b2a06b7`.
- **Ledger ruling 11, added during R2:** a ratio is not carried, both figures are. The `hs-reject-in-verifier` entry's canonical sentence in `tasks/w1/numbers.md` still reads "a 3.1× reduction", so any later stage that re-derives a sentence from the ledger will reintroduce the ratio unless the ruling is recorded against that entry.

## 8. Verification

**Restore.** All twelve drafts through the stage: 19,178 words plus the T01 long swap became 26,399, with 168 `ADDED_CLAIMS` lines logged for re-audit, two items withheld under a disclosure rule (T08), and four content removals (T03's Goal-1 clause, T09's umbrella marking, T10's intro sentence, T06's duplicate gloss). Restore agents ran 141k–192k tokens each.

**Gaps.** All twelve through review findings, deployment inputs, `## Open questions` and the disclosure pass. The ledger's twelve rows total 100 findings applied and 24 declined with reasons.

**Re-audit.** Twelve independent auditors, none of which edits a draft, checking every added or changed claim against source: **280 confirmed, 3 wrong, 1 partly unsupported**. Three drafts needed no patch (T03, T07, T11).

**Patch.** 26 defects patched across nine drafts, plus second passes on T02 (the #1398 per-worker line) and T05 (the 38-retained arithmetic). One re-audit defect was disputed by the patcher and the dispute was **upheld** after the orchestrator opened `peers/behavior.rs:265-273`: T10's `:267-272` is correct.

**Review-patch round.** One bounded round against all four reviews: **211 findings applied, 51 declined with reasons, 43 items removed with reasons**; 34,193 → 38,674 words.

**Mechanical gate** (`tasks/w1/r2/lint-final2.txt`, `cite_check.py`). Lint clean on all twelve, 0 FAIL and 0 WARN; eight headings in template order; **347 backticked `path:line` citations all resolve** (file exists, line in range); the preamble, the citation-baseline sentence and the reference-deployment paragraph are byte-identical across the twelve; every `{{slug}}` placeholder is one of the twelve and none is backticked.

**Reviews** (four fable reviewers, none of which edits a draft):

| Reviewer | Scope | Majors | Minors |
|---|---|---|---|
| A | cold maintainer, T01–T06 | 8 | 35 |
| B | cold maintainer, T07–T12 | 10 | 43 |
| C | no-solution blind test, all twelve | 15 | 10 |
| D | disclosure leak review, the seven public drafts | 3 | 7 |

Reviewer D's own totals: 2 standalone leaks (T02 line 8 with line 76; T09 line 60), 2 pivot sentences that break no rule alone (T02 line 76, T11 line 24), 2 rule-4 combinations (C1 reconstructing T04's Problem, major; C2 reconstructing T01's, minor), 5 notes for you, and 3 reverse-check candidates (T07 strong, T01 and T12 partial). No flood figure and no stall path appears in any public draft.

**Blind test, first run.** Asked to guess the approach the author privately favours, without seeing any planning document, the reviewer reached high confidence on **6 of 12** (T01, T02, T04, T06, T07, T10), against 1 of 12 at the end of R1. No draft came back "cannot tell". The rise is not in the survey entries, which stay alphabetical and even; it came from four channels the restoration and the new section opened. Open questions steer when they ask only for one entry's inputs or name one entry's fallback (T01, T02, T04, T07, T09, T12). Measurements sections name insertion points for counters and sampling, which the Goal rule keeps out one section up (T01, T02, T04, T05, T06, T08, T09). Riders group the entries by upkeep, "every entry but the last ships in a modified crate" and its variants (T06, T07, T09, T11). And figures are phrased or placed as benefits (T10's "a 3.1× reduction"; T01's and T12's token-answering run reported as a survival result; T03's one favourable experiment sitting in Background). All fifteen majors went into the review-patch round.

**Blind test, rerun** (after the review-patch round):

**Blind test, rerun after the patch round** (`tasks/w1/r2/review-nosolution-2.md`): high-confidence guesses fell from 6 of 12 to **5 of 12**; confidence held on nine drafts, fell on three (T05, T07, T09), rose on none. The four steering channels the first run named are closed where it named them (open-question fallback framings gone from every draft; "every entry but one" riders gone from T07, T09, T11; line-numbered counter sites gone from T09; T03's Background result moved to Measurements). Run 1's majors 3, 7, 8 and 12 survive as structural cues that a patch cannot remove without inventing evidence: which entries have a measurement behind them (T01 line 59 prices only the added round trip; T10 line 61 has the verifier placement as the figure's subject), which Goal item is in one entry's unit, and which entry's mechanism the Problem explains (T04, T06, T07, T09, T10, T11, T12). Two residues are cheap and specific if you want a further pass: a fallback ladder that moved into a Measurements decision rule (T02 line 72, T04 line 67), and counter sites still named by path under Measurements (T04 lines 67 and 71, T06 lines 63 and 65, T08 line 64). "A modified crate" as the only route to a reading is stated in six drafts (T01, T05, T07, T09, T11, T12); it is a fact about where the readings live. The loop is bounded here.

**Spot re-audit** of the review-patch round's new claims:

**Spot re-audit of the patch round's new claims** (`tasks/w1/r2/spot-A.md`, `spot-B.md`, `spot-C.md`): 75 confirmed, 2 wrong, 0 unsupported; all 42 content removals hold on their stated reason. Three defects, all applied (`tasks/w1/r2/fpatch.md`): T07's "pad the datagram" became "expand the payload of the datagram" (RFC 9000 section 14.1 binds the payload); T11 line 86 gave the right conclusion for the wrong reason (`FromSwarm::ConnectionEstablished` carries no duration; `established_in` exists only on the `SwarmEvent`, which the node's catch-all arm discards); T03 line 86 had two ordinals swapped. After the fixes: lint clean on all twelve, 347 citations resolve, preamble, baseline sentence and reference-deployment paragraph byte-identical across the twelve, every placeholder bare.

`git status`: no tracked file changed; nothing committed; no `gh` write; no advisory filed.

## 9. Posting mechanics

The drafts reference each other in both directions, so numbers have to exist before bodies are final:

1. Create all twelve with placeholders in place: five private security advisories (T1, T4, T6, T7, T12) and seven public issues (T2, T3, T5, T8, T9, T10, T11). Record each issue number or GHSA id in the slug map below and in `tasks/plan.md`.
2. Substitute `{{slug}}` → `#NNNN` in every body and `gh issue edit` each. A placeholder pointing **from a public issue at a private advisory** becomes the plain words "a related security advisory", because only collaborators can follow an advisory link; every public draft's sibling lines are written to read correctly after that substitution. The reverse direction, a private advisory pointing at a public issue, is an ordinary issue link. T03's last Related line carries four private placeholders that all substitute to the same words; collapse them into one mention there.
3. Strip the two HTML comment lines (title, labels) from each body; they become the `--title` and `--label` arguments.

Suggested creation order: T3, T2 (no dependencies) → T1 → T4, T6 → T8, T5 → T10, T9, T11 → T7, T12 (the two spikes share one flood run with T1 and T6; each names the others).

| Slug | Row | Filed as | Number |
|---|---|---|---|
| `quic-initial-unvalidated-cost` | T1 | Private advisory | |
| `quic-listener-interop-tests` | T2 | Public issue | |
| `patched-transport-crate-upkeep` | T3 | Public issue | |
| `pending-inbound-unbounded` | T4 | Private advisory | |
| `per-peer-ceilings` | T5 | Public issue | |
| `accepts-unbounded-per-poll` | T6 | Private advisory | |
| `endpoint-driver-contention` | T7 | Private advisory | |
| `validated-address-handshake-rate` | T8 | Public issue | |
| `redundant-cert-verification` | T9 | Public issue | |
| `late-refusal-of-strangers` | T10 | Public issue | |
| `dialer-chosen-kx-group` | T11 | Public issue | |
| `single-inbound-socket` | T12 | Private advisory | |

Two slugs are misnomers (T6's per-poll bound already exists; T10's strangers are admitted). They are placeholders only and never appear in a posted issue.

## 10. Process notes for W2

From W1's first pass:

- **Pre-split every item** (verifier → evidence file → fresh drafter). T1, the only pre-split item, had the cleanest first audit (68 / 3 / 0).
- **Do not tell drafters which approach the plan favours.** A blind reviewer named it with high confidence in 7 of 12 first drafts; every guess was right. The seeds listed it first with the richest constraint. Give it only to the no-solution reviewer, as the thing to detect.
- **The word cap cost verified content in every draft.** Compression, not content, drove token use: drafters 211–302k, fixers 240–396k against a 150k budget. Acted on in R2.
- **Freeze the brief before spawning.** Eleven drafters started before the addendum (the #1408 merge, the 0.11.15 correction) and every one carried the stale framing into its draft.
- **Seed hints are unverified leads, and should say so.** Three of mine were wrong (0.11.17; "changed by the upgrade"; the `SO_REUSEPORT` constraint); the audits caught all three.
- **The re-audit of added claims earns its cost.** It caught a mis-stated harm in T6 (fatal exit vs. unbounded hang), a missing limit on a figure in T12, a false metrics claim in T8, and six citation ranges.
- Spawns: 59 opus (1 context, 1 ledger, 13 draft, 12 audit, 12 fix, 8 patch, 12 re-audit) against about 40 expected; 5 fable (2 cold-maintainer, 1 no-solution, 1 cross-draft, 1 final).

What R2 added:

- **No brief carries a word ceiling.** The 1,600 figure was a suggestion that the previous pass enforced as a gate. With it removed the twelve drafts went from 19,178 words to 38,674, all of it verified content and none of it padding; every stage logged its removals with a content reason, and "too long" was not one. The rule is now written into the `human-writing`, `gh-issue` and `doc-writer` skills: a word count is a target, never a gate.
- **Adding content re-introduces steering cues, so the blind test has to run after every content-adding pass.** High-confidence guesses went from 1 of 12 to 6 of 12 purely from restoration and the new `## Open questions` section. The gaps and open-question writers need the steering rules stated explicitly, not inherited from the drafting brief: an open question names the unknown and what settles it and says nothing about what happens to the survey on either answer; a measurement says what a counter must distinguish and leaves the insertion point to the implementer; a figure is reported as two costs, not as a ratio or a survival result.
- **Two rate-limit interruptions cost nothing.** A weekly limit killed ten restore agents mid-section and both gaps agents at start; a second session limit later killed eight re-audits and a patch. Every agent had been rewriting its checkpoint after each section and editing its draft section by section, so every draft on disk was valid and every agent resumed from its `next` marker by message. No stage was redone.
- Spawns: 66 opus (1 project-context check, 12 restore, 12 gaps, 12 re-audit, 11 patch including second passes on T02 and T05, 12 review-patch, 3 spot re-audits, 1 final patch, 1 index, 1 plan update); 7 fable spawned, 6 completed (2 cold-maintainer, the disclosure review, the blind test — its first spawn stopped by a safeguard false positive, so once more — and the blind-test rerun). One fable reviewer was stopped by a safeguard false positive on its first attempt and was respawned on the same model.
- Agents ran 37k–256k tokens: the blind-test rerun (fable) reached 256k and the T01–T06 spot re-auditor 242k; every other agent stayed under 225k. The shape to copy is the narrow single-deliverable agent with an explicit list of paths it may open and an instruction to hand back rather than explore past them.
