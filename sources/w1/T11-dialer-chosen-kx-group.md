<!-- title: network-libp2p: the inbound QUIC handshake computes whichever key-exchange group the dialer puts first -->
<!-- labels: security, enhancement -->

## Problem

In TLS 1.3 the dialer's ClientHello lists the key-exchange groups it supports, and the server computes its half in one of them. The QUIC listener accepts four and lets the remote pick. `libp2p-tls-0.7.0/src/lib.rs:76-77` builds the server config from the `aws_lc_rs` provider's defaults, replacing only the cipher suites:

```rust
let mut provider = rustls::crypto::aws_lc_rs::default_provider();
provider.cipher_suites = verifier::CIPHERSUITES.to_vec();
```

`kx_groups` is never touched, so the list is the provider default at `rustls-0.23.37/src/crypto/aws_lc_rs/mod.rs:247-255`: `X25519MLKEM768`, `X25519`, `SECP256R1` (P-256), `SECP384R1` (P-384). The first is a hybrid, for which the server runs an X25519 exchange and an ML-KEM-768 encapsulation (`aws_lc_rs/pq/mod.rs:14-19`, `pq/hybrid.rs:42-47`); `prefer-post-quantum`, which puts it first, is required by `libp2p-tls-0.7.0/Cargo.toml:60-66`.

Selection runs in the dialer's order, not the server's. `rustls-0.23.37/src/server/hs.rs:548-556` walks the ClientHello's `supported_groups` and looks each one up in the server's list:

```rust
for offered_group in client_groups {
    let supported = self.config.provider.kx_groups.iter().find(|skxg| {
        skxg.usable_for_version(selected_version) && skxg.name() == *offered_group
    });
```

`hs.rs:629-641` then takes the first hit, so the server's ordering decides membership only: a dialer offering one group gets that group or `NoKxGroupsInCommon` and a fatal alert (`hs.rs:586-588`). The server's half runs at `rustls-0.23.37/src/server/tls13.rs:502` (call site `:342`) while it reads the ClientHello, before the dialer's certificate and `PeerId` are seen.

The list is fixed inside `libp2p-tls` and unreachable from here: `libp2p-quic-0.14.0/src/config.rs:66`, `:68` hold both TLS configs as private fields, `Config::new` (`:79-102`) always builds them from `libp2p_tls`, and `Config`'s only other public methods are `mtu_upper_bound` (`:105`) and `disable_path_mtu_discovery` (`:113`); nothing in `crates/` or `bin/` names `rustls`, `CryptoProvider` or `kx_group`.

What that choice costs is unmeasured on this provider: the four are different algorithms, but the only per-group figures were taken on the previous release's provider and sit under Measurements with their limits. A remote, not the node, decides which group the server computes on each inbound handshake, so a remote decides how much of the node's CPU that handshake spends on the key exchange, and the work finishes before the node knows who is dialling.

## Goal

- **What a remote can cost the server by choosing the key-exchange group on one inbound handshake is known, and bounded if the maintainers decide a bound is needed.** *Observable:* the per-group figures from **Per-group first-flight cost on the resolved provider** below (a first flight is the ClientHello read through Finished written); the maintainers read the spread from them and decide whether to set a bound at all. *Baseline:* none on this provider.
- **Honest peers unaffected.** With every member of the reference deployment's committee reconnecting at once (see Background), no honest handshake fails on group selection for stock dialers of either release, and the honest path's server CPU and time to an established connection do not regress. *Observable:* **What stock dialers negotiate, and what the honest path pays** below. *Baseline:* that measurement sets it, and it states which of the readings it needs the resolved crates already allow.
- **The negotiated group is visible from a running node**, whichever way the cost figures come out: it is what tells an operator which groups honest peers use. *Observable:* a per-listener count of inbound handshakes by negotiated group. *Baseline:* none. No node-owned code can read the negotiated group on the resolved crates, so the count depends on a modified transport crate ({{patched-transport-crate-upkeep}}) or on an accessor upstream adds; **What stock dialers negotiate, and what the honest path pays** below states what is readable today and what is not.
- **Non-goals.** Prescribing the list's contents, or whether post-quantum key exchange is worth its server cost. The certificate work that follows ({{redundant-cert-verification}}). Bounding how many handshakes start ({{validated-address-handshake-rate}}).
- The issue closes on the per-group figures, the interoperability result and a per-listener count of inbound handshakes by negotiated group, plus either a decision that the spread justifies no change or a bound set from the figures.

## Background

**Threat model.** The attacker is outside the validator set and is assumed to know every validator's IP address, port, `PeerId` and BLS public key. They can forge source addresses, and they can rent a botnet of hosts with real addresses. They hold no committee key and cannot break cryptography.

**Acceptance rules.** A defence has to hold when the host firewall is absent or wrong, and has to fail open when an input it depends on (a committee list, an address list) is stale or missing, so honest peers keep connecting. Floods that saturate the link are the hosting provider's to absorb and are out of scope; the scope is what such an attacker can do to the node's CPU, memory and tasks at packet rates the NIC still delivers.

**Node shape.** Each libp2p swarm has one public QUIC listener on one UDP socket. A node runs one swarm for the primary and one per worker (`crates/node/src/manager/node.rs:1244`, `:1282`), all built by `ConsensusNetwork::new` (`crates/network-libp2p/src/consensus.rs:406`), so every per-swarm limit or cost multiplies by the number of swarms on the host.

Paths under `crates/` refer to `main` at `9b2a06b7`; a path that begins with a crate name and version, such as `libp2p-quic-0.14.0/src/transport.rs:595`, refers to the crates.io source of the version `Cargo.lock` resolves.

**Reference deployment.** The maintainers' reference deployment is a committee of ten validators, each on an Ubuntu server with 8 CPUs and 32 GB of RAM, running one node process with two swarms (the primary's and one worker's). The network between validators (link speed and round-trip times) has not been specified.

`libp2p-tls` restricts the handshake to TLS 1.3 and three cipher suites (`libp2p-tls-0.7.0/src/verifier.rs:48`, `:52-57`), so every inbound connection reaches that selection; a dialer that names a group without a key share gets a HelloRetryRequest, moving the agreement to a second ClientHello (`rustls-0.23.37/src/server/tls13.rs:204-226`) — a different cost shape.

`main` resolves `libp2p-tls` 0.7.0 on the `aws_lc_rs` provider (`libp2p-tls-0.7.0/src/lib.rs:48`, `:76`); 0.6.2, the previous release, built both configs on ring (`libp2p-tls-0.6.2/src/lib.rs:48`, `:75`). `libp2p/rust-libp2p#6568` (merged) made that move and added the hybrid, part of `libp2p/rust-libp2p#6236` (open), which asks for post-quantum key exchange. The classical groups are compiled against `aws-lc-rs` too (`aws_lc_rs/mod.rs:7`, `:31-32`), so ring timings do not carry over. A stock 0.6.2 dialer offers ring's three groups, `X25519`, `SECP256R1` and `SECP384R1` (`libp2p-tls-0.6.2/src/lib.rs:48-49`, `rustls-0.23.37/src/crypto/ring/mod.rs:176-180`); a stock 0.7.0 dialer offers those three and the hybrid; the server's list holds all four.

### Approaches surveyed so far

Leaving the list as it is and bounding handshake starts instead. It runs into the bound acting on how many handshakes start rather than on what one of them costs: a handshake that clears such a bound still runs whichever group the dialer named first, so each one that clears it carries the per-group spread, whatever that spread turns out to be. How many handshakes start is {{validated-address-handshake-rate}}'s subject, and what one inbound attempt costs the node before any node code decides on it is {{quic-initial-unvalidated-cost}}'s.

Narrowing the server's accepted list. It runs into two equally fixed dialer lists: a group absent from the server's list is a fatal alert for a dialer offering only it (`hs.rs:586-588`), and the hybrid is what `libp2p/rust-libp2p#6568` added and this release's dialers name first.

Reordering the server's preference without removing a group. It runs into selection being made in the dialer's order: `hs.rs:548-556` collects the candidates in the ClientHello's order and `:629-641` takes the first of them the server also has, so a change to the server's order changes which groups a dialer can reach, not which of them it gets; `ignore_client_order` (`rustls-0.23.37/src/server/server_conn.rs:301-304`) covers cipher suites, not groups.

Supplying the transport's crypto provider from outside the crate. It runs into `libp2p-quic` 0.14.0 having no constructor that takes one: `Config::new` builds both TLS configs from `libp2p_tls` (`libp2p-quic-0.14.0/src/config.rs:79-102`), and `libp2p/rust-libp2p#6435`, the upstream issue asking for that seam, is open.

Narrowing, reordering and supplying a provider each reach the TLS configuration this repository never constructs (`libp2p-quic-0.14.0/src/config.rs:66`, `:68`), so on the resolved crates each of the three would be delivered as a modified transport crate, and each would depend on the upkeep {{patched-transport-crate-upkeep}} covers.

## Implementation details to pay close attention to

If a restriction on the accepted list is derived from a runtime input, then a stale or missing value fails closed rather than open: group selection has no fallback, and a dialer left with no group in common gets a fatal alert instead of a slower handshake.

If the hybrid stops being negotiated, then the honest path moves too, in a direction nobody has measured: this release's dialers name it first, so an honest mass reconnect — a restart, a partition heal, an epoch change — pays for it.

If the server's TLS configuration is built anywhere other than `libp2p_tls::make_server_config` (`libp2p-tls-0.7.0/src/lib.rs:71-93`), then the restriction to TLS 1.3 and three cipher suites that function applies travels no further than the crate: `PROTOCOL_VERSIONS` and `CIPHERSUITES` are `pub(crate)` in `libp2p-tls` (`libp2p-tls-0.7.0/src/verifier.rs:48`, `:52-57`), so a second construction site decides what else the handshake accepts, not only which groups it offers.

If a bound is meant to apply only to remotes outside every committee the node tracks, then the group is computed before the certificate is parsed (`transport.rs:595`), so nothing keyed on identity can condition it ({{late-refusal-of-strangers}}).

If a per-group figure or a per-group count does not separate handshakes that took a second ClientHello from single-flight ones, then a group carries cost that is not its own: when the dialer names the selected group without a key share, the server hands the connection back to `hs::ExpectClientHello` (`rustls-0.23.37/src/server/tls13.rs:204-226`, `:231`), so it reads and selects twice for one connection.

If a bound on the key-exchange CPU one inbound handshake may cost is set from the per-group figures, then three inputs this issue does not carry stand between those figures and any value: how many honest dialers arrive at once, which on the reference deployment is nine remote committee members for each of a node's two swarms, so eighteen inbound handshakes reaching one node process when the whole committee reconnects together (derived from the reference deployment's ten validators and two swarms per node, not measured), before any peer outside the committee; how many connections each dialer holds; and how much of the reference host's 8 CPUs is left to handshakes once both swarms and the rest of the node process have taken their share.

## Measurements that would affect the decision

**Per-group first-flight cost on the resolved provider.** It has not been run, and the issue turns on it. Drive the server `libp2p_tls::make_server_config` builds (`libp2p-tls-0.7.0/src/lib.rs:71-93`) with client configs restricted to one group each, on a host of the reference deployment's class (see Background), reporting server CPU per first flight at the median and the 99th percentile for each group and for the no-key-share case. The first flight also carries the server's certificate signature (`tls13.rs:787`), which is constant across groups and narrows the ratio. The hybrid's column read against X25519's is what the honest path pays for the hybrid, which stock dialers of this release name first: `make_client_config` takes the same provider defaults the server does (`libp2p-tls-0.7.0/src/lib.rs:48-49`). Within run-to-run noise, the dialer's choice is not a lever and the decision the closing line asks for is that the spread justifies no change; if one group costs several times another, that spread is what a bound has to cover.

**The existing figures, on the superseded provider.** When the dialer offered only P-384, the server's first flight cost 616.4 µs of CPU at the median — 6.7× the 91.9 µs it cost when the dialer offered X25519 — measured by an in-process benchmark on one desktop-class Intel CPU with `libp2p-tls` 0.6.2 and `rustls` 0.23.37 on the ring provider; the dialer chooses the group and the server honours its order, and this is not reproduced on current versions. P-256 in the same run cost 87.9 µs, essentially the same as X25519. They are first flights, not whole handshakes, on one host whose CPU frequency could not be pinned; the hybrid has no figure at all.

**What stock dialers negotiate, and what the honest path pays.** Two runs. A listener check against stock dialers on `libp2p-tls` 0.6.2 and 0.7.0 reports whether either pairing is refused and which group each negotiates. Refusal is visible to the dialer as a failed connection. Which group was agreed is not visible on either side of a QUIC connection: `libp2p-quic-0.14.0/src/connection.rs:37-49` keeps its `quinn::Connection` private and the type's only inherent method is a private constructor (`:52-65`), and quinn's own handshake data carries the negotiated protocol and the server name, not the group (`quinn-proto-0.11.18/src/crypto/rustls.rs:259-267`). `rustls` exposes the agreed group on the connection itself (`rustls-0.23.37/src/common_state.rs:168`), so a run that drives the TLS configurations `libp2p-tls` builds (`libp2p-tls-0.7.0/src/lib.rs:41-67`, `:71-93`) without the QUIC transport can read it there, and reading it from a running node, as the Goal's per-listener count does, depends on a modified transport crate ({{patched-transport-crate-upkeep}}) or on an accessor upstream adds. If both pairings complete, the groups a supported release's dialer actually reaches are known and the decision rests on the cost figures alone; if either is refused, the cross-release pairing is broken today, whatever the costs turn out to be. An honest mass reconnect across the reference deployment's committee of ten, each node running both of its swarms in the one process as it does in production and reporting, per swarm, the negotiated group and the time to an established connection, gives the floor the honest-peer Goal is read against: a change that leaves the distribution and the negotiated groups where this run puts them has not touched the honest path, and one that moves either has. Of the two values that run reports, the time to an established connection is readable from node-owned code today, since the swarm attaches `established_in` to every `SwarmEvent::ConnectionEstablished` the node's own loop receives (`libp2p-swarm-0.48.0/src/lib.rs:176-177`, `libp2p-swarm-0.48.0/src/connection/pool.rs:771`), and the node discards it today; the per-swarm negotiated group carries the same dependency as the Goal's count.

## Open questions

- **Does a node on this release complete a handshake with a stock dialer of the previous one?** Goal item 2's honest-peer baseline turns on it; source settles which groups each release's dialer offers, not whether the pairing completes, and the pairing has never been run. The first run of **What stock dialers negotiate, and what the honest path pays** would settle it, and {{quic-listener-interop-tests}} covers the CI lane it would run in.
- **Do the per-group costs on the resolved provider keep the shape the superseded figures showed?** Goal item 1's bound, and whether the maintainers set one at all, come from the answer. **Per-group first-flight cost on the resolved provider** would settle it, and nobody has run it.
- **What is the network between the validators of the reference deployment?** The honest mass reconnect in **What stock dialers negotiate, and what the honest path pays** reports time to an established connection, which moves with link speed and round-trip times, so the floor it sets holds only for the network it was run on. It is an input the maintainers supply.
- **Does a supported release of `libp2p-quic` let a node reach the TLS configuration its listener uses, and when?** The configuration is private to the crate today (`libp2p-quic-0.14.0/src/config.rs:66`, `:68`), which is what makes three of the surveyed approaches and the Goal's per-listener count depend on a modified transport crate; if a release exposes it, none of them does. `libp2p/rust-libp2p#6435` is the upstream issue asking for the provider seam, and an upstream release is what settles it.
- **How many dialers outside the committee reach a node on the reference deployment, and how often?** The hazard about setting a bound from the per-group figures names the honest arrival count as one of its inputs, and the reference deployment fixes only the committee's nine remote members per swarm; the honest mass reconnect in **What stock dialers negotiate, and what the honest path pays** measures committee members alone, so neither the hazard's input nor that measurement's coverage is complete without it. It is an input the maintainers supply from their deployment.

## Related

- {{quic-initial-unvalidated-cost}}: what an inbound connection attempt costs the node before any node code decides on it; this key exchange is part of that cost, run inside `accept()` (`transport.rs:595`).
- {{redundant-cert-verification}}: the certificate work that follows in the same handshake.
- {{late-refusal-of-strangers}}: identity-keyed refusal runs after the key exchange, so a refused peer's choice is paid for.
- {{validated-address-handshake-rate}}: bounds how many handshakes start; this is what one costs.
- {{patched-transport-crate-upkeep}}: the upkeep an approach here needing a modified crate depends on.
- {{quic-listener-interop-tests}}: no lane exercises a listener against stock dialers of other versions, so this issue's interoperability result waits on it.
- #1010 (closed): a single unbanned peer could hold unboundedly many inbound connections, closed by the per-peer established-connection limit (`crates/network-libp2p/src/consensus.rs:117`); that limit counts connections once they are established, so it bounds how many of these key exchanges one peer ends up holding, not what any of them cost before that point.
- #1281 (open): denial-of-service bounds for consensus and discovery requests, which run on connections this key exchange has already paid for, so a bound set there starts after the cost this issue measures.
- #1408 (merged): the upgrade to `aws-lc-rs` that added the hybrid, and why the per-group figures are on a provider no longer used.
