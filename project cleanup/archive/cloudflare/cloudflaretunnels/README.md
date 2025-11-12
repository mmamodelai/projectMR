# Cloudflare Tunnel Management Scripts

## Overview
This folder contains scripts for managing Cloudflare Tunnels for the SMS Conductor system.

## Files

### Python Scripts
- **`add_dns_record.py`** - Add DNS CNAME record for tunnel subdomain
- **`cloudflare_tunnel_manager.py`** - Complete tunnel management (from parent directory)

### Batch Scripts
- **`add_dns_record.bat`** - Windows batch script to add DNS record
- **`create_tunnel.bat`** - Create tunnel and configuration file
- **`setup_complete_tunnel.bat`** - Complete setup: create tunnel + DNS + start

## API Tokens

### DNS Token (Required for DNS operations)
```
Token: 4STsv9xjfAHZK8EmtiRpFdcvAe8UJSSAbZ1zpQpf
Permissions: DNS:Edit, Zone:Read
Account: ed835396a75f0a35ea698cc764615662
Zone: marketsuite.co
```

### Tunnel Token (Required for tunnel operations)
```
Token: TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
Permissions: Cloudflare Tunnel:Edit
Account: ed835396a75f0a35ea698cc764615662
```

## Usage Examples

### Quick Setup (Complete)
```bash
# Create tunnel, add DNS, and start
setup_complete_tunnel.bat smsn8n smsn8n
```

### Manual Setup
```bash
# Step 1: Create tunnel
create_tunnel.bat smsn8n smsn8n

# Step 2: Add DNS record (after getting tunnel ID)
add_dns_record.bat smsn8n 2fbac668-5ee0-4ad7-aee6-208dd57d4d86

# Step 3: Start tunnel
cloudflared.exe tunnel --config tunnel-config.yml run smsn8n
```

### Python Scripts
```bash
# Add DNS record
python add_dns_record.py --subdomain smsn8n --tunnel-id 2fbac668-5ee0-4ad7-aee6-208dd57d4d86

# List tunnels
python cloudflare_tunnel_manager.py list --token TYE2lFSm41EUOubi67uzJsI37z-YjElBmRZkj67A
```

## Current Active Tunnel

### smsn8n Tunnel
- **Tunnel ID**: `2fbac668-5ee0-4ad7-aee6-208dd57d4d86`
- **Name**: `smsn8n`
- **URL**: `https://smsn8n.marketsuite.co`
- **Service**: `http://localhost:5001` (API server)
- **Status**: ✅ HEALTHY & RUNNING
- **DNS**: ✅ CNAME record added
- **Created**: 2025-10-02T03:59:10.355363Z

## Configuration Files

### tunnel-config.yml
```yaml
tunnel: smsn8n
credentials-file: C:\Users\Xbmc\.cloudflared\2fbac668-5ee0-4ad7-aee6-208dd57d4d86.json

ingress:
  - hostname: smsn8n.marketsuite.co
    service: http://localhost:5001
  - service: http_status:404
```

## Troubleshooting

### Common Issues
1. **DNS not resolving**: Wait 1-2 minutes for propagation
2. **Tunnel not connecting**: Check if API server is running on localhost:5001
3. **Permission errors**: Verify API tokens have correct permissions

### Test Commands
```bash
# Test tunnel health
curl https://smsn8n.marketsuite.co/api/health

# Test message sending
curl -X POST "https://smsn8n.marketsuite.co/api/messages/send" \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+16199773020","message":"Test message"}'
```

## Success Metrics
- ✅ Tunnel created and running
- ✅ DNS record added and resolving
- ✅ API server responding through tunnel
- ✅ n8n workflow connecting successfully
- ✅ End-to-end SMS flow working

---
*Last Updated: 2025-10-02*
*Status: Production Ready*
