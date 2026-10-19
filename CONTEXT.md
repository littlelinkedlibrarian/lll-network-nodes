# Registry context router

This repository admits independently operated nodes. It is not the builder, a catalog database, or an automatic deployment service.

| Task | Read first | Then |
|---|---|---|
| Learn to build an app | [NodeKit START-HERE](https://github.com/littlelinkedlibrarian/lll-icm-node-builder/blob/main/START-HERE.md) | Follow its staged ICM workflow |
| Understand admission | `README.md`, `docs/ICM-ONBOARDING.md` | Keep compatibility, membership and hosting separate |
| Prepare a manifest | `CONTRIBUTING.md`, `schemas/node-manifest.schema.json`, `examples/node-manifest.yaml` | Validate with `scripts/validate_manifests.py`; human reviews publication |
| Verify public reads | `scripts/verify_live_node.py`, NodeKit's pinned reference OpenAPI | Check six routes; skipped empty-list details are not full conformance proof |
| Register or approve | `docs/ICM-ONBOARDING.md`, `scripts/register_node.py`, `scripts/approve_node.py` | Protected maintainer operation; never put credentials in Git |
| Consume hosted Central | [Central integration guide](https://beta.littlelinkedlibrarian.com/integrations) | Use that deployment's OpenAPI; Central source is private |

LLL Lite compatibility uses `/api/boxes`; Central's local catalog uses `/api/library-boxes`. They are separate API surfaces. A richer Central contract does not increase the minimum beginner node's requirements.

Do not run registration, approval, email delivery or membership changes merely to inspect this repository. Validation and documentation review do not require those side effects.
