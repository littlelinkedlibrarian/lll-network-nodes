# LLL Network Nodes Registry

This repository is the human-reviewed admission boundary for independently operated Little Linked Librarian nodes. A merged manifest records an operator's request to join; it never contains credentials and it never transfers ownership of the node's catalog to Central.

Compatibility is not membership. A node becomes a network member only after its manifest passes review, Central registers it as `pending`, the operator installs the one-time node credential, Central observes a healthy heartbeat, and a maintainer approves it.

## NodeKit and the ICM handoff

[Little Linked Librarian: NodeKit](https://github.com/littlelinkedlibrarian/lll-icm-node-builder) uses the Interpretable Context Methodology (ICM) to guide a learner and coding agent through discovery, specification, architecture, scaffolding, build, validation, and release. When the learner chooses the connected path, Stage 07 produces a secret-free candidate manifest for this repository.

The checked-in Happy Box application is one NodeKit reference run. Other implementations may use different languages, user interfaces, and datastores as long as they pass the same public compatibility contract. Read [the ICM onboarding contract](docs/ICM-ONBOARDING.md) for the boundary between a generated node, this registry, and LLL Central.

## Registration at a glance

1. Build and validate an LLL-compatible node. NodeKit is the supported learning path.
2. Give the node one stable HTTPS origin for its branded UI and compatible API.
3. Create an account at LLL Central. The manifest ties the node to that account without including a password or bearer token.
4. Copy [`examples/node-manifest.yaml`](examples/node-manifest.yaml) to `nodes/<node-id>.yaml` and complete the human-reviewed fields.
5. Run `python3 scripts/validate_manifests.py`.
6. Open a pull request titled `Add node: <display name>`.
7. Maintainers review identity, consent, location, privacy, endpoint ownership, and contract evidence.
8. After merge, a maintainer verifies the live node and runs the registration tool from a trusted admin environment. Central creates the node as `pending`; its one-time key is delivered to the reviewed operator and is never written to Git, logs, or the manifest.
9. The operator enables the heartbeat. After Central reports the node healthy, a maintainer runs the approval tool from the trusted environment.

External HTTPS nodes do not need to join Kubernetes or the Istio mesh. Istio remains an optional transport boundary for deployments managed by LLL; the application registry and live compatibility contract are the membership boundary.

## Public compatibility profile

The current `lll-lite` `0.1.0` profile consists of six anonymous, read-only routes:

- `GET /health`
- `GET /api/books`
- `GET /api/books/{id}`
- `GET /api/boxes`
- `GET /api/boxes/{id}`
- `GET /api/boxes/{id}/books`

Central reads current public inventory from eligible nodes; it does not replicate their canonical data. Product writes, operator identity, OpenAI credentials, source scans, pending candidates, private data, and local persistence remain under the node operator's control.

For the current Central release, `spec.connectivity.endpoint` must be the HTTPS origin that serves both the branded UI and compatible API. The manifest also records `uiUrl` and `apiBaseUrl` so the future split-origin registry contract can be introduced without changing the human review model; today they must resolve to the same origin.

## What belongs in a manifest

- A unique `lll-...` node ID and human-readable display name
- A reviewed Central account ID and notification email
- A public HTTPS origin and connectivity type
- A truthful public location or service-area centroid
- A privacy tier and explicit publication consent
- A pinned compatibility profile, version, and capabilities
- Non-sensitive implementation metadata used to explain the learning outcome

Never commit API keys, operator tokens, OpenAI credentials, passwords, private keys, tunnel credentials, database URLs, or private media.

## Status lifecycle

```text
candidate manifest -> reviewed PR -> merged -> pending in Central
                   -> healthy heartbeat -> active
                   -> suspended or removed when necessary
```

A failed heartbeat never disables the node's local application. Removing a manifest or suspending a registry record does not delete the operator's books.

## Repository layout

```text
nodes/                         reviewed registration manifests
examples/                      templates that never provision
schemas/node-manifest.schema.json
scripts/validate_manifests.py  deterministic local and CI validation
scripts/verify_live_node.py    live six-route compatibility check
scripts/register_node.py       protected Central pending-registration boundary
scripts/approve_node.py        protected heartbeat-gated approval boundary
docs/ICM-ONBOARDING.md         NodeKit Stage 07 handoff and ownership model
.github/PULL_REQUEST_TEMPLATE/ human registration-review checklist
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete operator and reviewer checklist.
