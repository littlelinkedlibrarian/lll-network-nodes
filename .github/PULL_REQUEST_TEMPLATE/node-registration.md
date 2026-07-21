## Node registration

- Node ID:
- Display name:
- Manifest path:

## Operator attestations

- [ ] I operate this node or am authorized to register it.
- [ ] I reviewed every manifest field and consent to publishing the manifest.
- [ ] The operator email is appropriate for network administration and credential delivery.
- [ ] The Central account ID belongs to the reviewed operator email.
- [ ] The submitted coordinates identify a public box or a deliberately chosen service-area centroid.
- [ ] No API key, token, password, private key, database URL, private scan, or other secret is included.

## Compatibility evidence

- [ ] The node remains usable with Central discovery disabled.
- [ ] The production endpoint uses HTTPS and serves the branded UI and compatible API from the declared origin.
- [ ] `python3 scripts/validate_manifests.py` passes.
- [ ] `python3 scripts/verify_live_node.py nodes/<node-id>.yaml` passes.
- [ ] The six public compatibility routes expose only anonymous, read-only, operator-approved data.

## Maintainer review

- [ ] Identifier and endpoint are unique.
- [ ] Operator/account binding has been verified without placing private contact details in this PR.
- [ ] Location, privacy, and capability claims are truthful.
- [ ] The merge may register this node as `pending`; it does not authorize activation before a healthy heartbeat.
