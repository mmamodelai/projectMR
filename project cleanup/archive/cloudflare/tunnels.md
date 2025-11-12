# Cloudflare Tunnels - Active Tunnels

## Active Tunnels

### conductor-tunnel
- **Tunnel ID**: `9b08819f-d471-405a-9923-d8687e88d604`
- **Name**: conductor-tunnel
- **Status**: inactive (needs configuration)
- **Created**: 2025-10-02T04:22:31.623434Z
- **Credentials**: `%USERPROFILE%\.cloudflared\9b08819f-d471-405a-9923-d8687e88d604.json`
- **Purpose**: Main tunnel for conductor project
- **Configuration**: Not yet configured
- **DNS**: Not yet set up

### smsn8n (ACTIVE - SMS Conductor)
- **Tunnel ID**: `2fbac668-5ee0-4ad7-aee6-208dd57d4d86`
- **Name**: smsn8n
- **Status**: ✅ HEALTHY & RUNNING
- **Created**: 2025-10-02T03:59:10.355363Z
- **Purpose**: SMS Conductor API tunnel for n8n integration
- **Configuration**: ✅ Configured with tunnel-config.yml
- **DNS**: ⏳ Pending CNAME record: smsn8n → 2fbac668-5ee0-4ad7-aee6-208dd57d4d86.cfargotunnel.com
- **URL**: https://smsn8n.marketsuite.co (once DNS added)
- **Service**: http://localhost:5001 (API server)
- **Last Updated**: 2025-10-02T04:52:45Z

### conductor-n8n (Unused)
- **Tunnel ID**: `dd828bc9-2b76-4402-8766-4816353c038c`
- **Name**: conductor-n8n
- **Status**: inactive
- **Created**: 2025-10-02T04:17:12.393674Z
- **Purpose**: Created but not used
- **Note**: Can be deleted if not needed

## Tunnel Management Commands

### List All Tunnels
```bash
python Olive/cloudflare_tunnel_manager.py list --token TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
```

### Create New Tunnel
```bash
python Olive/cloudflare_tunnel_manager.py create --name "tunnel-name" --token TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
```

### Delete Tunnel
```bash
python Olive/cloudflare_tunnel_manager.py delete --tunnel-id TUNNEL_ID --token TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
```

### Run Tunnel
```bash
cloudflared.exe tunnel run conductor-tunnel
```

## Configuration Status

| Tunnel | Created | Configured | DNS Set | Running |
|--------|---------|------------|---------|---------|
| conductor-tunnel | ✅ | ❌ | ❌ | ❌ |
| smsn8n | ✅ | ✅ | ⏳ | ✅ |
| conductor-n8n | ✅ | ❌ | ❌ | ❌ |

## Next Steps

1. **Configure conductor-tunnel**: Set up what service/port it should tunnel to
2. **Set up DNS**: Create subdomain routing for the tunnel
3. **Test tunnel**: Verify it works correctly
4. **Set up Windows service**: Make it start automatically
5. **Clean up unused tunnels**: Delete conductor-n8n if not needed

## API Token Info

- **Current Token**: TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
- **Expires**: 2025-11-30T23:59:59Z
- **Permissions**: Cloudflare Tunnel:Edit, DNS:Edit
- **Account ID**: ed835396a75f0a35ea698cc764615662

---

*Last Updated: 2025-10-01*
