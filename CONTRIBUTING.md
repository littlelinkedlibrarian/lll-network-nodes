# Contributing a network node

Thank you for operating an independent Little Linked Librarian node. A registration pull request publishes connection and location metadata, so every field must be reviewed by the human operator before submission.

## Prerequisites

- The node continues to work with discovery disabled.
- Its public origin uses valid HTTPS and is controlled by the operator.
- The six `lll-lite` `0.1.0` reads are anonymous and read-only.
- Private scans, pending candidates, management routes, and credentials are absent from those reads.
- The operator has an LLL Central account and has copied its stable account ID from the Central profile.
- The submitted coordinates identify a public box or consented service-area centroid, not an unsuspecting person's residence.

NodeKit builders should complete Stage 06 validation and enter Stage 07 with the hybrid or connected release path selected.

## Create the manifest

Copy the template:

```bash
cp examples/node-manifest.yaml nodes/lll-your-node.yaml
```

Edit only that new manifest. Production IDs use lowercase letters, numbers, and hyphens, begin with `lll-`, and must match the filename.

The operator email is retained for credential delivery and network operations. Do not place contact information in the PR description. The manifest is public, so use an address intended for node administration.

Run the same deterministic check as CI:

```bash
python3 scripts/validate_manifests.py
```

You may also verify the live contract before opening the PR:

```bash
python3 scripts/verify_live_node.py nodes/lll-your-node.yaml
```

## Open the pull request

- Title: `Add node: <display name>`
- Add one production manifest under `nodes/`.
- Complete the node-registration pull-request template.
- Do not add credentials, screenshots containing credentials, database exports, or private photos.
- Keep unrelated application code out of the registry PR.

Passing local validation means the manifest is structurally safe; it does not guarantee approval.

## Human review

Maintainers verify:

- The operator knowingly requested publication and owns the endpoint.
- The operator's Central account ID and notification email correspond.
- The HTTPS origin is stable and the compatible reads return bounded responses.
- The node reports the pinned profile truthfully.
- Location and privacy choices are appropriate.
- The node ID is unique and the change contains no secret.
- The node remains functional when its Central adapter is disabled.

Reviewers must not approve membership merely because a schema check passed.

## After merge

Workflow automation is intentionally deferred. A maintainer currently uses a trusted admin environment to revalidate the repository, run the live contract check, and invoke `scripts/register_node.py` with `ALLOW_LOCAL_CENTRAL_REGISTRATION=true`. This creates a `pending` Central record; it does not auto-approve the node.

The registration response contains a one-time node key. The tool sends it through the configured transactional-email provider to the reviewed operator email without printing it. If delivery fails after its bounded retries, the command fails visibly and leaves the node pending for administrator-assisted credential recovery; it never activates the node.

The operator stores the received values only in the node's runtime environment:

```env
DISCOVERY_ENABLED=true
CENTRAL_BASE_URL=https://beta.littlelinkedlibrarian.com
CENTRAL_NODE_ID=lll-your-node
CENTRAL_NODE_API_KEY=<one-time-key>
CENTRAL_HEARTBEAT_INTERVAL_SECONDS=300
```

After restart, local operation continues normally and the node begins sending heartbeats. A maintainer confirms a recent heartbeat, zero health failures, and a passing live contract check, then invokes `scripts/approve_node.py` with `ALLOW_LOCAL_CENTRAL_APPROVAL=true` from the trusted environment. Only that step changes the registry status from `pending` to `active`.

## Updates and removal

- Submit endpoint, UI URL, API base URL, location, compatibility, or operator changes as a new PR.
- Node-owned display and privacy settings may use the authenticated Central node-settings API when supported.
- Removing a manifest requires human review and a separate Central suspension/removal action; deletion is never inferred silently from a Git diff.
- A lost key requires administrator-assisted recovery. A node with its current key can use Central's key-rotation endpoint.

## Maintainer environment

The trusted maintainer environment requires these secrets:

- `CENTRAL_API_URL`
- `CENTRAL_ADMIN_TOKEN`
- `SENDGRID_API_KEY`
- `KEY_DELIVERY_FROM_EMAIL`

Restrict access to this environment and require a second maintainer to confirm the reviewed manifest before registration or approval. Do not use a general user token or a node key as the Central admin token.

Central currently authenticates this boundary with an admin JWT. Keep its lifetime short, load it only for the planned operation, and replace this temporary operational bridge with a dedicated narrowly scoped automation identity when Central exposes one.
