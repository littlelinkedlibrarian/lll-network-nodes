# LLL Network Nodes Registry

This repository contains the registration manifests for all nodes in the Little Linked Librarian federated network.

## How to Register Your Node

1. **Set up your node** following the [lll-lite setup guide](https://github.com/littlelinkedlibrarian/lll-lite)

2. **Run the bootstrap script** which will generate your node manifest:
   ```bash
   ./bootstrap/setup.sh
   ```

3. **Submit a Pull Request** adding your manifest to `nodes/`:
   - Fork this repository
   - Add your `nodes/<your-node-id>.yaml` file
   - Create a PR with the title "Add node: <your-node-name>"

4. **Wait for approval** from network administrators

5. **Receive your API key** once approved (sent to your operator email)

## Node Manifest Format

```yaml
apiVersion: lll.network/v1
kind: NetworkNode
metadata:
  name: lll-seattle-abc123
  labels:
    region: pacific-northwest
    type: home-node
spec:
  displayName: "Seattle Downtown Library Box"

  operator:
    email: "operator@example.com"

  connectivity:
    type: cloudflare-tunnel
    endpoint: lll-seattle-abc123.lll-network.com

  location:
    description: "Seattle, WA, USA"
    coordinates:
      latitude: 47.6062
      longitude: -122.3321
```

## Approval Process

1. **Automated validation** checks manifest format and schema
2. **Admin review** verifies:
   - Operator email is valid
   - Location is legitimate
   - No duplicate nodes in the area
   - Endpoint format is correct
3. **Approval** triggers:
   - Node registered in central database
   - Istio ServiceEntry created
   - API key generated and sent to operator

## Updating Your Node

### Infrastructure changes (endpoint, connectivity type)
Submit a PR updating your manifest.

### Settings changes (privacy, allowed users)
Use the node settings API - no PR needed.

## Removing Your Node

Submit a PR removing your manifest file, or contact network admins.

## Directory Structure

```
lll-network-nodes/
├── nodes/                    # Node manifest files
│   ├── lll-seattle-abc123.yaml
│   └── ...
├── schemas/                  # JSON schemas for validation
│   └── node-manifest.schema.json
├── scripts/                  # Helper scripts
│   └── validate.sh
└── .github/workflows/        # CI/CD automation
    ├── validate-pr.yml
    └── provision-node.yml
```

## Questions?

- [LLL Documentation](https://docs.littlelinkedlibrarian.com)
- [GitHub Issues](https://github.com/littlelinkedlibrarian/lll-network-nodes/issues)
