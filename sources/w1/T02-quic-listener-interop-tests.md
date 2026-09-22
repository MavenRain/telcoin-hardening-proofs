<!-- title: ci: nothing tests the QUIC listener before establishment or against cross-version dialers -->
<!-- labels: ci, security -->

## Problem

Every swarm builds its QUIC listener at one site (`crates/network-libp2p/src/consensus.rs:563-582`), and nothing tests what it does with an incoming attempt before it is established. An *Initial*, an attempt's first packet, is taken unconditionally: `libp2p-quic` accepts every one (`libp2p-quic-0.14.0/src/transport.rs:595`) and performs no address validation. An address is *validated* only after a round trip through it completes (RFC 9000 section 8.1), and *unvalidated* until then; a *forged source*, whose sender never sees the reply, never becomes validated.

Every test under `crates/network-libp2p/src/tests/` works at or above an established connection: the peer manager, established-connection behaviour, the message codec, node-record signing; no code here names quinn's address-validation surface. The inbound handshake deadline is untested too: `libp2p-quic` applies one `handshake_timeout` (`libp2p-quic-0.14.0/src/config.rs:33`), and the deadline an inbound handshake meets is {{pending-inbound-unbounded}}'s area; a test here measures against it.

Nor is there a dialer from another release: the tree's only non-node swarm is raw (`network_tests.rs:1547-1549`), built to stand in for a peer that has not adopted the peer-exchange protocol in a goodbye fallback test (`network_tests.rs:1476`), on default configuration and, since one build resolves one `libp2p-quic`, on the listener's own version.

All 13 `runs-on` keys in the four workflow files name `ubuntu-latest` (`.github/workflows/pr.yaml:90` and twelve more), and the directory holds no `sudo`, `unshare`, `container:` or `privileged`. What a hosted runner grants if asked is unmeasured (below).

Two recent moves changed this surface. Over the `quinn-proto` span #1393 brought, a short unsupported-version packet is now ignored rather than answered, so a forged source cannot elicit a larger packet than it sent (`quinn-proto-0.11.18/src/endpoint.rs:181-187`), and an Initial arriving while the endpoint has exhausted connection identifiers or already holds `max_incoming` attempts awaiting accept is dropped silently, before Initial keys are derived rather than after (`quinn-proto-0.11.18/src/endpoint.rs:455-461`, keys at `:463`); that reordering landed in `quinn-proto` 0.11.15 (`quinn-rs/quinn#2683`). #1408 then changed the crypto provider both TLS configurations are built on (`libp2p-tls-0.7.0/src/lib.rs:48`, `:76`). Nothing failed, and nothing would have: the first signal of a regression here is a validator nobody can dial.

## Goal

- **A cross-release pairing is exercised both ways.** A dialer built from the versions resolved before #1408 (`libp2p-quic` 0.13.1, `libp2p-tls` 0.6.2) establishes against a listener configured as `consensus.rs:563-582` configures one, and today's against the older. *Observable:* per pairing, established or failed, elapsed handshake time against the inbound deadline, and the key-exchange group settled on, meaning the curve the two sides derive a shared secret with. *Baseline:* none today; **Cross-release pairings** sets the acceptable timings and failure modes the maintainers bound.
- **The listener's disposal of an attempt from a forged source is asserted on a recorded cadence.** *Observable:* a test driving the listener from a source address whose replies never reach the sender, recording the outcome and the time to it. That is the case an in-process dialer cannot produce, since a dialer on an address it owns receives what the listener sends back; presenting it over a real socket needs a link the test owns at both ends, which is why **What a hosted runner permits** decides where such a test can run. What counts as a pass is what the listener does today, which is to accept every attempt (`libp2p-quic-0.14.0/src/transport.rs:595`): the test fails when either the disposal or the time to it changes, whether or not the change was intended. *Baseline:* none today; the maintainers set the cadence from what **What a hosted runner permits** returns.
- **An honest-path baseline exists for future listener changes to be held to.** This issue changes no runtime behaviour, so the guard binds the follow-up work: an honest mass reconnect, the burst of handshakes when many peers reconnect at once after a restart, a partition heal or an epoch change, recorded here in the one shape **Honest mass reconnect on today's listener** runs, becomes what any future listener change must keep passing, with no honest handshake refused. *Observable:* a multi-swarm reconnect run reporting time to establishment and refused handshakes. *Baseline:* **Honest mass reconnect on today's listener** sets it, from which the maintainers set the tolerance.
- **Non-goals.** Measuring what this listener withstands under load. Changing what it does with any attempt. Deciding which listener change, if any, is worth making.
- The issue closes on three artefacts: a cross-release pairing test that runs both ways, on the merge path or on a schedule as **Cross-release pairings** decides; a test asserting what the listener does with an attempt from a forged source, at the cadence **What a hosted runner permits** leaves open; and a recorded honest-reconnect baseline from **Honest mass reconnect on today's listener** that future listener changes are held to.

## Background

**Threat model.** The attacker is outside the validator set and is assumed to know every validator's IP address, port, `PeerId` and BLS public key. They can forge source addresses, and they can rent a botnet of hosts with real addresses. They hold no committee key and cannot break cryptography.

**Acceptance rules.** A defence has to hold when the host firewall is absent or wrong, and has to fail open when an input it depends on (a committee list, an address list) is stale or missing, so honest peers keep connecting. Floods that saturate the link are the hosting provider's to absorb and are out of scope; the scope is what such an attacker can do to the node's CPU, memory and tasks at packet rates the NIC still delivers.

**Node shape.** Each libp2p swarm has one public QUIC listener on one UDP socket. A node runs one swarm for the primary and one per worker (`crates/node/src/manager/node.rs:1244`, `:1282`), all built by `ConsensusNetwork::new` (`crates/network-libp2p/src/consensus.rs:406`), so every per-swarm limit or cost multiplies by the number of swarms on the host.

Paths under `crates/` refer to `main` at `9b2a06b7`; a path that begins with a crate name and version, such as `libp2p-quic-0.14.0/src/transport.rs:595`, refers to the crates.io source of the version `Cargo.lock` resolves.

**Reference deployment.** The maintainers' reference deployment is a committee of ten validators, each on an Ubuntu server with 8 CPUs and 32 GB of RAM, running one node process with two swarms (the primary's and one worker's). The network between validators (link speed and round-trip times) has not been specified.

`Cargo.lock` resolves `libp2p-quic` 0.14.0 (`Cargo.lock:5605-5606`). Between 0.13.1 and 0.14.0 its accept path is unchanged; its manifest is not. `quinn`'s crypto-provider feature moved from `rustls` to `rustls-aws-lc-rs`, and `quinn-proto`'s features became explicit, `["bloom", "log", "ring"]` with `default-features = false` (`libp2p-quic-0.14.0/Cargo.toml:71-85`), `bloom` compiling in quinn's token-replay log (`quinn-proto-0.11.18/src/lib.rs:40-43`). One consequence: `libp2p-tls` 0.7.0's own test asserts the first key-exchange group offered is `X25519MLKEM768` (`libp2p-tls-0.7.0/src/lib.rs:106-108`), where the `ring` provider that 0.6.2 used lists `X25519` first (`rustls-0.23.37/src/crypto/ring/mod.rs:176-180`). Whether the cross pairing agrees at the cost of an extra round trip, or fails outright, has not been established: nothing in this repository runs it, so neither outcome has been observed here.

Upstream, `libp2p/rust-libp2p` #6182 (more QUIC transport configuration parameters) and #6435 (a crypto-provider injection seam) are both open, so what the crate lets a test set on the listener and on the TLS configurations either side builds may not stay as it is.

### Approaches surveyed so far

A devnet exercise outside CI, on real hosts. It is not a merge gate, so a regression reaches a release first.

An in-process test pointing a differently configured dialer swarm at the node's listener. One build resolves one `libp2p-quic`, so the dialer is the listener's own version, and it cannot present a source address it does not own.

A network-namespace test over a virtual interface pair with no egress filtering. It needs privileges no workflow requests, and what the hosted image grants is unmeasured.

A packet-level harness at the `quinn-proto` layer with no sockets. The tests it would sit beside are upstream's own (`quinn-proto-0.11.18/src/tests/mod.rs:90`, `:2811`, `:3696`), and a harness there exercises quinn's state machine rather than the listener this repository configures.

A privileged self-hosted or container lane. It adds a CI trust boundary and standing maintenance no workflow carries today.

A two-build lane, each release built as its own node binary, the two run as separate processes on one runner. Every run of the lane has to build and hold both releases, and what that costs the jobs `.github/workflows/pr.yaml` runs today is unmeasured.

A version matrix holding two `libp2p-quic` releases in one build under renamed dependencies. The older release drags its own `libp2p-core` tree and asks `quinn` for a different crypto provider (`libp2p-quic-0.13.1/Cargo.toml:61-62`, `:70-76`), and one unified `rustls` is linked for the whole graph, so the older half does not run against its own release's feature set.

## Implementation details to pay close attention to

If a test keys an assertion on an unvalidated source address, the value was chosen by the sender, so the test records the attacker's input, not the listener's.

If a test has to assert on what happens before `quinn::Incoming::accept()` returns, `libp2p-quic` hands out nothing between the attempt arriving and the accept call (`libp2p-quic-0.14.0/src/transport.rs:591-595`), so the assertion has nothing to observe; what an attempt costs the node before any node code decides on it is {{quic-initial-unvalidated-cost}}'s subject, and a test built against a modified transport crate inherits the upkeep {{patched-transport-crate-upkeep}} describes.

If a test asserts that an attempt is refused, and admissibility depends on an input that can go stale or missing, it pins behaviour that must fail open and keeps passing once fail-open breaks.

If a version matrix pairs only like with like, the cross case never runs, and that is where the releases differ.

If a reconnect run fixes committee size, connections per peer and burst size at the fixtures' values, it measures one shape, not the reference deployment's ten validators with two swarms on each host: the helpers build a fixture committee and wait for one expected peer at a time (`network_tests.rs:123`, `:226`, `:240`, `:313`).

If a fixture pins one committee, an epoch change that alters which `PeerId`s are admissible mid-flight goes unexercised, and the test passes while the live path diverges.

## Measurements that would affect the decision

**What a hosted runner permits.** Whether a job on the image the four workflows use can create a private network namespace and a virtual interface pair. If it can, the approaches that need a private link are open to CI; if not, they move to a privileged lane or outside CI, leaving those that need no privileges. No measurement exists of a flood carrying forged source addresses, because the test environment would not forward packets with forged sources; where such a test can run decides whether that case can be produced here at all.

**Honest mass reconnect on today's listener.** Every committee member dialling one node at once, on the reference deployment's host of 8 CPUs and 32 GB (see Background), reporting time from first dial to establishment and refused honest handshakes, which the run has to tell apart from the handshakes that went on to establish. Both outcomes reach the node's own handler for swarm events (`crates/network-libp2p/src/consensus.rs:775`, `:800-804`), which is where a run reads them from node-owned code; inbound connections whose handshake has not finished are {{pending-inbound-unbounded}}'s area, so how this run counts a refused one follows what that issue settles. On that deployment the dialling side is the nine remote validators of a committee of ten, and the node under test carries two swarms in one process, so both are reported. The network between the validators is not specified, so a distribution is read against the link the run happens to use and does not carry across to another. A distribution that crowds the inbound handshake deadline in force leaves room for a tight guard only; one well below it allows a generous one.

**Cross-release pairings.** The version pairs named in the Goal, run both ways on an ordinary runner, in whichever arrangement is chosen. Two separately built nodes put each half on the dependency tree its own release resolves; one build holding both crate versions links one `rustls` for the whole graph, so what the older half runs against is not the feature set its own release resolves. Each run reports whether it establishes, elapsed handshake time, the group settled on, and what the arrangement it used costs in wall time and cache against current `pr.yaml` jobs. A failure to establish puts the pairing on the merge path; timings like like-with-like at comparable cost make it routine; a large cost with no difference pushes it to a scheduled run.

## Open questions

- **What does a job on a GitHub-hosted `ubuntu-latest` runner get to do with the network stack: can it create a private network namespace and a virtual interface pair?** The second Goal item needs a source whose replies never reach the sender, and where a test can present one depends on the answer. The documentation for the runner image has not been read, and **What a hosted runner permits** puts the same question as a measurement.
- **Are validators ever expected to run two releases at once, as a supported deployment state rather than only during an upgrade?** The first Goal item pairs a dialer built from the versions resolved before #1408 with today's listener and the reverse; if mixed-version operation is supported, the pairing describes a running network, and if it is only an upgrade window, it describes that window, which changes what a failure to establish costs and where the test belongs. Nothing in this repository settles it: it is a decision for the maintainers.
- **Does a pairing run as a single build, both crate versions linked into one test binary, give the same result as one run as two separately built nodes?** **Cross-release pairings** can be run either way; the two differ in what each half is compiled against (`libp2p-quic-0.13.1/Cargo.toml:70-76`) and in what the lane builds and caches on every run, and whether they agree has not been established here. Running the pairing in both arrangements once would settle it.
- **What is the network between validators: link speed and round-trip times?** **Honest mass reconnect on today's listener** reports time from first dial to establishment, and that distribution is as much a property of the link as of the listener, so the baseline the third Goal item holds future listener work to only compares across runs on the same network. It is the one part of the reference deployment that has not been specified, and only the maintainers can supply it.

## Related

- #835 (closed as completed): replaced fixed real-time sleeps in `network_tests.rs` with condition polling, which is how the helpers a listener test would wait on peers are written today (`network_tests.rs:313`).
- #1010 (closed): the per-peer established-connection limit; its tests sit above an established connection.
- #1281 (open): denial-of-service bounds for the consensus and discovery RPC paths, which run above this transport and over connections a listener test would already have established.
- #1398 (open): the fatal 120 s wait for network peers, which a peerless lane on `main` burns before the process exits (`crates/node/src/manager/node/start_epoch.rs:968`, `:976`, `bin/telcoin-network/src/main.rs:23`); a listener regression that kept peers from connecting would surface there rather than as a test failure.
- #1393 brought `quinn-proto` 0.11.14 to 0.11.18, #1394 `libp2p-quic` 0.13.0 to 0.13.1, and #1408 `libp2p-quic` 0.14.0 with `libp2p-tls` 0.7.0 (all merged).
- {{quic-initial-unvalidated-cost}}: what an inbound connection attempt costs the node before any node code decides on it; a test here cannot assert below the accept call, so what this issue can cover stops where that one begins.
- {{pending-inbound-unbounded}}: how a swarm accounts for inbound connections whose handshake has not finished; the inbound deadline a test here measures against, and the refusals a reconnect run counts, are settled there.
- {{dialer-chosen-kx-group}}: the dialer chooses the key-exchange group the server computes, which is the difference between the two releases a cross-release pairing would exercise.
- {{patched-transport-crate-upkeep}}: the upkeep a test built against a modified transport crate would depend on.
