# Contributing to LLL Network Nodes

Thank you for your interest in joining the Little Linked Librarian network!

## Adding Your Node

### Prerequisites

Before submitting a node registration:

1. **Set up your node** - Follow the [lll-lite setup guide](https://github.com/littlelinkedlibrarian/lll-lite)
2. **Configure networking** - Ensure your node is accessible via Cloudflare Tunnel, Tailscale, or manual port forwarding
3. **Test locally** - Verify your node works at `http://localhost:18080`

### Submission Process

1. **Fork this repository**

2. **Create your node manifest** in `nodes/<your-node-id>.yaml`:

   ```yaml
   apiVersion: lll.network/v1
   kind: NetworkNode
   metadata:
     name: lll-yourname-abc12345  # Use the ID from your bootstrap script
     labels:
       region: your-region
       type: home-node
   spec:
     displayName: "Your Node Name"

     operator:
       email: "your-email@example.com"

     connectivity:
       type: cloudflare-tunnel  # or: tailscale, manual
       endpoint: your-node-id.lll-network.com

     location:
       description: "City, State/Country"
       coordinates:  # Optional but helpful
         latitude: 47.6062
         longitude: -122.3321
   ```

3. **Create a Pull Request** with:
   - Title: `Add node: <your-node-name>`
   - Description including your contact info and location

4. **Wait for review** - Admins will verify your submission

5. **Receive your API key** - Once approved, you'll receive your API key via email

### Review Criteria

We verify:
- ✅ Valid email address
- ✅ Legitimate location
- ✅ Proper manifest format
- ✅ No duplicate nodes
- ✅ Reasonable node density in area

### After Approval

1. Update your node's `.env` with the API key
2. Restart your node: `docker compose restart`
3. Your books will appear in network searches!

## Updating Your Node

### Infrastructure Changes

For changes to endpoint, connectivity type, or location:
- Submit a PR updating your manifest file

### Settings Changes

For privacy tier or allowed users:
- Use your node's settings API (no PR needed)
- Changes sync automatically to the network

## Removing Your Node

To leave the network:
1. Submit a PR removing your manifest file
2. Or contact network admins

Your local node will continue to work standalone.

## Code of Conduct

- Be respectful of other node operators
- Don't spam the network with fake nodes
- Keep your contact info up to date
- Report any issues you encounter

## Questions?

- Open an issue in this repository
- Email: support@littlelinkedlibrarian.com
