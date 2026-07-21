# ICM release handoff to the LLL network

This document is the registry-side context for NodeKit Stage 07. It makes the ownership and approval boundary interpretable to a learner, a coding agent, a node operator, and a Central maintainer.

## Purpose

NodeKit can produce an independent application, a compatible standalone node, a hybrid own-domain node, or an LLL-hosted learning deployment. Only a human-approved hybrid or connected release enters this registry flow.

The onboarding model deliberately separates three systems:

| System | Owns | Never receives |
|---|---|---|
| Independent node | Product UX, canonical boxes and books, writes, operator identity, media, OpenAI use, vectors, database, backups | A dependency on Central for local operation |
| This registry | Secret-free application manifest, review evidence, history of approved metadata changes | Node keys, operator tokens, OpenAI keys, private scans, database credentials |
| LLL Central | Membership status, node-key hash, operator account binding, privacy, location, health and heartbeat state, live aggregation | Ownership of the remote catalog or authority to mutate it |

## Context supplied by NodeKit

Before creating the candidate manifest, Stage 07 must read the approved discovery brief, specification, architecture, validation report, connection-path rules, and release policy. It may not infer operator consent or publish secrets.

The Stage 07 agent presents these decisions to the human:

1. **Release identity** — requested node ID and display name.
2. **Ownership** — operator email and the existing Central account ID to bind.
3. **Connection** — HTTPS origin, branded UI URL, API base URL, and connectivity type.
4. **Visibility** — privacy tier, public catalog consent, and location consent.
5. **Location** — public box coordinates or a deliberately chosen service-area centroid.
6. **Compatibility** — pinned profile/version and capabilities proven by Stage 06.
7. **Implementation metadata** — optional language/datastore labels used for learning and presentation, never for admission eligibility.

The agent writes `stages/07-release/output/node-manifest.yaml` only after the human approves those values. The operator then copies that artifact to `nodes/<metadata.name>.yaml` in a fork of this repository.

[`examples/happy-box-nodekit.yaml`](../examples/happy-box-nodekit.yaml) shows the resulting shape for the deployed NodeKit reference run. It is deliberately kept under `examples/`, uses operator placeholders, and can never trigger provisioning.

## Manifest invariants

- The manifest contains no credential or private key.
- Its filename equals its node ID.
- A production node has one stable HTTPS origin in the current Central release.
- `endpoint`, `uiUrl`, and `apiBaseUrl` share an origin until Central stores split origins explicitly.
- The six compatible reads are anonymous and contain public data only.
- The node remains usable when discovery and heartbeat are disabled.
- Coordinates are optional, paired, and knowingly published.
- Capability claims are backed by validation evidence.
- Compatibility is not described as membership before approval.

## Human checkpoint

The pull request is the human checkpoint, not a formality. The operator attests that the submitted endpoint and data may be published. A maintainer confirms the endpoint, Central account binding, privacy choice, contract evidence, and lack of secrets.

Automated validation rejects malformed identifiers, duplicate origins, private production URLs, mismatched filenames, unknown fields, unpaired coordinates, incomplete capability claims, and common credential signatures. It cannot establish ownership or informed consent; reviewers do that.

## Post-merge state machine

```text
merged manifest
  -> maintainer live verification
  -> Central record + one-time node key
  -> pending
  -> operator installs key and starts heartbeat
  -> maintainer health check and approval
  -> active and eligible for discovery
```

Automation is intentionally not enabled in this repository yet. Maintainers run the guarded registration and approval tools from a trusted environment. Registration never auto-approves, and the approval tool refuses a stale heartbeat, nonzero health failures, a missing manifest, or an endpoint that differs from the reviewed manifest. Maintainers also rerun the live compatibility check before approval.

## Central behavior

Central filters active nodes by status, privacy, authentication context, heartbeat freshness, health failures, and optional proximity. Aggregation reads current node responses with bounded timeouts and partial-failure behavior. Remote records keep a source label and link back to their independently branded node.

Istio may provide transport controls for LLL-managed workloads, but an external node does not become a mesh workload merely by joining the application registry.

## Credential boundary

Central generates a single-purpose node credential during pending registration and stores only its hash. The registration tool never prints the raw value and delivers it to the reviewed operator address. The operator stores it outside Git and uses it only for its own heartbeat and settings endpoints.

The node key is not:

- a Central user token;
- a NodeKit operator token;
- an OpenAI key;
- an aggregator credential; or
- permission for Central to call node management routes.

Key delivery failure leaves the node pending and requires an administrator-assisted recovery or rotation. It never justifies exposing the key in command output, a pull-request comment, an issue, or a manifest.

## Exit and recovery

Suspension or removal stops network discovery without deleting the independent node. The operator retains its domain, database, media, backups, and local application. A hosted learner must additionally receive export and graduation instructions before release.
