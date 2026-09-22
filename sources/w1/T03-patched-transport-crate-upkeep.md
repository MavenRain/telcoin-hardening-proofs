<!-- title: build: no process exists for pinning, watching or rebasing a modified QUIC transport crate -->
<!-- labels: dependencies, security, tech debt -->

## Problem

Remedies for several sibling issues about this listener (see Related) may need internals `libp2p-quic` and `libp2p-tls` do not expose: the TLS configurations handed to quinn are private fields (`libp2p-quic-0.14.0/src/config.rs:66-68`) built in `libp2p-tls` (`libp2p-tls-0.7.0/src/lib.rs:42-93`), and this repository's reach from outside is a six-value closure over timeouts and stream limits (`crates/network-libp2p/src/consensus.rs:565-573`).

```rust
client_tls_config: Arc<QuicClientConfig>,
server_tls_config: Arc<QuicServerConfig>,
```

If a change to either crate has to ship before upstream releases it, the node runs a carried copy — a modified build in place of the published release — of a crate that terminates every inbound connection, and nothing in the repository says how it is pinned, where the modified source lives, how advisories reach it, who rebases it, or how it gets upstream. Nothing is carried today, so none of it has been exercised.

Neither crate is named in any workspace manifest and there is no `[patch]` table: the workspace reaches both through the `libp2p` umbrella crate (`Cargo.toml:273`) with the `quic` feature (`crates/network-libp2p/Cargo.toml:12-19`). The one manifest line naming a transport crate is inert: `Cargo.toml:219` declares `quinn-proto = "0.11.8"` and no member references it, so the built 0.11.18 arrives transitively.

## Goal

- **A carried transport crate is identifiable from the repository alone.** For `libp2p-quic` and `libp2p-tls`, a reviewer holding only the tracked manifests and lockfile can say whether each is built from its published release and, where one is not, name the upstream revision the copy is based on. *Observable:* the dry run named in the last line takes a no-op change through the procedure, and a reviewer who has nothing but the repository at that commit either answers both questions from it or cannot. *Baseline:* nothing is carried, so there is nothing to name today; the one dependency family here not resolved from the registry, reth, is pinned by tag (`Cargo.toml:117`) with the commit that tag resolves recorded only in `Cargo.lock:7820`, and changing that is a non-goal.
- **An upstream advisory can be matched to a carried copy without new tooling.** A written procedure exists for checking advisories against the version a copy is based on, and has been run once against a published advisory. *Threshold:* **Advisory matching across source kinds** sets how much of it a scanner could do. *Baseline:* neither exists.
- **The lag from an upstream security release to the commit carrying it is bounded by a stated number.** *Baseline:* GHSA-5hq8-qhww-jm7q was published 2026-07-10 and the bump to the patched `libp2p-quic` 0.13.1 merged ten weeks later, nothing carried. *Threshold:* **Release-to-commit lag**; the maintainers set the bound and name who holds it.
- **Honest peers unaffected.** A carried build resolves the same dependency set outside that crate and connects to committee peers as a registry build does. *Observable:* **A carried build against a registry build**, which runs the end-to-end suite against both builds on a committee of ten.
- **Non-goals.** Whether anything is carried at all, and what a modification would contain. Adding a dependency-audit job to CI: whether this repository gets one is decided elsewhere, and the second item is written as a check a person can run. Changing how reth is pinned.
- **What closes this.** That procedure — what a copy is pinned to, where its source lives, how advisories reach it, who rebases it and how it goes upstream, in whichever form a copy takes — and one recorded dry run against a no-op change. Neither waits on a modification existing.

## Background

**Threat model.** The attacker is outside the validator set and is assumed to know every validator's IP address, port, `PeerId` and BLS public key. They can forge source addresses, and they can rent a botnet of hosts with real addresses. They hold no committee key and cannot break cryptography.

**Acceptance rules.** A defence has to hold when the host firewall is absent or wrong, and has to fail open when an input it depends on (a committee list, an address list) is stale or missing, so honest peers keep connecting. Floods that saturate the link are the hosting provider's to absorb and are out of scope; the scope is what such an attacker can do to the node's CPU, memory and tasks at packet rates the NIC still delivers.

**Node shape.** Each libp2p swarm has one public QUIC listener on one UDP socket. A node runs one swarm for the primary and one per worker (`crates/node/src/manager/node.rs:1244`, `:1282`), all built by `ConsensusNetwork::new` (`crates/network-libp2p/src/consensus.rs:406`), so every per-swarm limit or cost multiplies by the number of swarms on the host.

Paths under `crates/` refer to `main` at `9b2a06b7`; a path that begins with a crate name and version, such as `libp2p-quic-0.14.0/src/transport.rs:595`, refers to the crates.io source of the version `Cargo.lock` resolves.

**Reference deployment.** The maintainers' reference deployment is a committee of ten validators, each on an Ubuntu server with 8 CPUs and 32 GB of RAM, running one node process with two swarms (the primary's and one worker's). The network between validators (link speed and round-trip times) has not been specified.

A carried copy serves every swarm on the host, two on the reference deployment, so a bad rebase lands on the whole node. The two crates that would be carried, `libp2p-quic` and `libp2p-tls`, publish from one `libp2p/rust-libp2p` commit: 0.14.0 and 0.7.0 both record `7171dce2f90c05ba7892d4ba926abb1881db27c7` in their `.cargo_vcs_info.json`, from `transports/quic` and `transports/tls` of that tree, so a rebase picks one upstream revision for both. In that tree the siblings are workspace dependencies (`libp2p-quic-0.14.0/Cargo.toml.orig:15-16` declares `libp2p-core` and `libp2p-tls` as `{ workspace = true }`), while the published manifest names them by registry version, `libp2p-core` 0.44.0 at `libp2p-quic-0.14.0/Cargo.toml:62-63` and `libp2p-tls` 0.7.0 at `:68-69`, which the generated header at `:1-10` says is what Cargo substitutes for a `path` dependency on publish. `quinn-proto` is not a candidate — `libp2p-quic-0.14.0/Cargo.toml.orig:19` declares it as `"0.11"`, a range — so its releases arrive transitively whatever is carried.

### How an advisory would reach a dependency here

`cargo audit` matches advisories on the `source` field in `Cargo.lock`, not on name and version, so how a copy is recorded decides whether a scanner matches it at all; what each way of recording one reports is **Advisory matching across source kinds**, under Measurements.

Nothing here would notice a miss: no `deny.toml`, no `.cargo/audit.toml`, no advisory job in any of the four workflows under `.github/workflows/`, and no `.github/dependabot.yml` on `main`. The two bot bumps before #1408, from `app/dependabot`, changed `Cargo.lock` only; #1408 itself was human-authored. How that bot is configured is unknown.

### Upstream cadence

`libp2p-quic` had one security release in the last year, a handshake panic. The tree under it moves faster: `quinn-proto` had eight advisories published in 2026, between 2026-03-09 and 2026-09-14, across four release points. A copy rebases over that cadence and over an uneven surface: the release to 0.14.0 changed eight of `libp2p-quic`'s nine source files.

### Approaches surveyed so far

Replacing `libp2p-quic` with direct use of `quinn`. Nobody has scoped what the glue between quinn and the swarm would contain, so its size is unknown.

Running a modified copy from a source this repository controls: a `[patch.crates-io]` entry at a git repository, or at a mirror of one. The lockfile then records that source instead of a registry release, one of the kinds **Advisory matching across source kinds** covers, and the source needs an owner.

Upstreaming the configuration surface, at once or in pieces. The two upstream pull requests opening configuration in these crates, `libp2p/rust-libp2p` #6435 and #6182, have been open since 2026-05-11 and 2025-10-15, searches of that repository found no inbound-admission work to join, and in pieces a copy is carried until the last lands.

Vendoring the crate into the workspace. How the vendored tree is recorded decides whether a scanner still matches it, the same measurement's question, and the copy is then carried as a tree inside this repository: in-tree diff surface and a licence review.

## Implementation details to pay close attention to

If a copy is recorded so that a scanner keyed on the lockfile's `source` field no longer matches it, then advisories against the release it is based on stop reaching it, and an audit job added later passes while the copy sits behind them.

If a replacement points at a monorepo member, then its siblings leave the registry with it, because upstream they are workspace dependencies and carry registry versions only in the published manifest (see Background), so the replaced set is wider than intended.

If the change reaches TLS behaviour, then two crates are carried rather than one: `Config::new` builds both TLS configurations through `libp2p-tls` and keeps them in private fields (`libp2p-quic-0.14.0/src/config.rs:66-68`, built at `:79-86`), so every rebase and every advisory check is two crates wide.

If nobody is named to rebase, then a security release lands upstream with nothing scheduled to follow it, at the cadence above.

If an upstream `libp2p` bump and a change to the carried crate land in one pull request, then neither can be reviewed or reverted without the other.

If a carried crate changes what the listener does on the wire, then peers running stock crates of this release and the previous meet a listener matching no upstream version; that coverage is {{quic-listener-interop-tests}}, not this item.

If a copy is pinned by a reference that can be repointed at its source, such as a branch or a tag, then the revision built is whichever one the lockfile holds, and a move upstream arrives here as a single lockfile line with no manifest diff behind it.

If a copy lives in this repository's tree, then each upstream release arrives as a diff a reviewer here reads rather than as a version bump, and nothing outside this repository records which upstream revision that tree still corresponds to.

If a copy is fetched from outside this repository at build time and that source is unreachable, then the build fails closed: a release hazard, not a runtime one.

## Measurements that would affect the decision

**Advisory matching across source kinds.** What `cargo deny` 0.19.9 and `cargo audit` report for `quinn-proto` 0.11.14 and `RUSTSEC-2026-0185` — the pair the existing partial run used, so the four results stay comparable with it — presented as a registry release, a git source, a path copy and a vendored tree. That partial run: against `cargo-audit` 0.22.2 with a local database and no network, one-package lockfiles for that package differing only in `source` report the advisory for a registry source and nothing for a `git+` source or for an entry with no `source` line, as a path copy has; a vendored tree with source replacement is the registry line again, because `cargo vendor` does not rewrite `Cargo.lock`, so what is matched there is the release the lockfile still names rather than the tree that is built. Read as a cost, that is one published advisory unreported per copy for the kinds that report nothing, and, for the kinds that do report, nothing at all about the crates this issue is about: the database behind the run, an `advisory-db` checkout at its 2026-09-18 state, carries advisory directories for `quinn` and `quinn-proto` and none for `libp2p-quic`, although GHSA-5hq8-qhww-jm7q was patched in `libp2p-quic` 0.13.1. Limits: one tool, one advisory, one database snapshot. `cargo deny`, which reads `cargo metadata` rather than a bare lockfile, has not been run against any of the four kinds, so half of what this measurement asks for is unmeasured. Whichever kinds both tools match, the procedure the second Goal item asks for can lean on a scanner for those and needs a named watch per copy for the rest; if the missing `libp2p-quic` directory holds under `cargo deny` as well, the watch is needed for every kind, a registry release included, and how a copy is recorded stops separating the routes at all.

**Where bump notifications come from.** Whether anything proposes a version bump for a dependency that is not a registry release. No configuration for such a bot is tracked here (see Background), so what produced #1393 and #1394 has to be read from the repository's settings, and the record to read beside it is what that bot has opened over the last year for reth, the one dependency here already resolved from a git source. Proposals arriving for a non-registry source let the procedure the second Goal item asks for point at something already running; none arriving, or a configuration that cannot be read at all, puts a named watch per copy inside that procedure and leaves the rebase-ownership hazard above with nothing automatic behind it. Whether the two bumps that did arrive came from a security alert or from a version schedule is part of the same reading, because an alert route reaches only what the advisory database names.

**Rebase cost across one upstream release.** Where conflicts fall when a change to `libp2p-quic` is replayed across the 0.13.1 to 0.14.0 boundary: in the lines it touches, or only in the churn around them. Which change is replayed is an input this issue does not pick: nothing is carried today and the no-op change of the dry run has no lines to conflict, so the run needs either a modification one of the sibling issues produces or one the maintainers name. Churn-only conflicts argue a copy is mechanical to hold between bumps; conflicts in the changed lines make every release a re-review, pushing toward replacing the crate or toward upstreaming. One release is one sample, and neither of those two routes has a measurement of its own here: what would size the first is glue nobody has scoped, and what would settle the second is how long an upstream review takes, which the open dates under Approaches bound from below and nothing here measures.

**Release-to-commit lag.** Elapsed time from each upstream release of these crates, and of the tree under them, to the commit here that resolves it, over the last year. A short and even lag makes the third Goal item a policy statement; a long or uneven one makes it a bound somebody has to hold. Whether to measure to a merge or a tagged release is an input the maintainers supply.

**A carried build against a registry build.** Whether a build with the transport crate replaced resolves the same dependency set outside that crate, and whether a committee of such builds forms and stays connected: read from a lockfile diff between the two builds and from the end-to-end suite run against both. That suite's local testnet starts four validators on one host today (`crates/e2e-tests/src/lib.rs:209-214`, started at `:317-323`), so running it at the reference committee size of ten means either extending that harness or test hosts the maintainers provide; the committee size is what this borrows from the reference deployment, and the reference deployment is not where it runs. A resolution difference outside the replaced crate, or a failure the registry build does not show, makes a carried copy a wider change than one crate, whatever form the copy takes; no difference in either makes this a check to repeat at each rebase rather than a gate on the first carry. Nothing is carried today, so what it would first run against is the no-op change in the last Goal line.

## Open questions

- **What does the bot that opened #1393 and #1394 do with a dependency that is not resolved from the registry?** The second Goal item's procedure either points at a notification route that already covers a carried copy or has to name a watcher for each copy, and in the second case the hazard "If nobody is named to rebase" has nothing automatic behind it. **Where bump notifications come from** is the reading that would settle it; the bot's own documentation on how it treats a non-registry source has not been consulted.
- **What does `cargo deny` 0.19.9 report for a package presented as a registry release, a git source, a path copy or a vendored tree?** Only `cargo audit` has been run, on one advisory and one database snapshot, and `cargo deny` reads `cargo metadata` rather than a bare lockfile, so how much of the second Goal item's procedure a scanner could carry is unknown for every one of the four kinds, and with it the constraint each carrying route runs into in Approaches. **Advisory matching across source kinds** runs both tools over the four kinds and would settle it.
- **If no scanner matches advisories against a carried copy, is that gap accepted or does the procedure carry a step that closes it?** The run already recorded under **Advisory matching across source kinds** leaves some of those kinds unmatched and the transport crate itself unmatched from any of them, so the second Goal item's procedure is either a written note that this is understood or a standing task somebody performs per copy, and the third Goal item's lag bound assumes somebody learns of the upstream release at all. The maintainers decide that; the measurement tells them how much a tool would cover, not whether what is left over is acceptable.
- **Is the lag the third Goal item bounds measured to a merge in this repository or to a tagged release of it?** The baseline under that item is an elapsed time to a merge, so a bound stated against a different endpoint is not comparable with it, and **Release-to-commit lag** produces a different series under each convention. The maintainers supply that choice.

## Related

- #1408: the merged pull request that last moved `libp2p-quic` (to 0.14.0) and `libp2p-tls` (to 0.7.0); the bot bumps before it are #1393 (`quinn-proto` to 0.11.18) and #1394 (`libp2p-quic` to 0.13.1).
- #1281: the open issue for this repository's gateway limits and its consensus and discovery denial-of-service bounds; it weighs the dependency moves its own work would need and names neither transport crate, so nothing there carries the upkeep this item asks for.
- {{quic-listener-interop-tests}}: the listener coverage a carried crate would need before it ships.
- {{quic-initial-unvalidated-cost}}, {{pending-inbound-unbounded}}, {{accepts-unbounded-per-poll}}, {{redundant-cert-verification}}, {{late-refusal-of-strangers}}, {{dialer-chosen-kx-group}}, {{single-inbound-socket}}: each may need an internal these crates do not expose; where one does, this is the upkeep it depends on and cannot be acted on until that exists.
