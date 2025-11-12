# Next Steps for Blaze API Access

## Current Status
- ✅ Partner Key (production): `30117b29cdcf44d7a7f4a766e8d398e7`
- ✅ Authorization Key (production): ends `66285925`
- ✅ Production host confirmed: `https://api.partners.blaze.me`
- ✅ Credentials verified working with light tests (members, transactions)

## Light Verification Tests (PowerShell)

Members (last 24h, limit 1):

```powershell
$headers = @{
  partner_key   = '30117b29cdcf44d7a7f4a766e8d398e7'
  Authorization = '48f5dd5e57234145a233c79e66285925'
  Accept        = 'application/json'
  'Content-Type'= 'application/json'
}
$end   = [DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()
$start = [DateTimeOffset]::UtcNow.AddDays(-1).ToUnixTimeMilliseconds()
$u1 = "https://api.partners.blaze.me/api/v1/partner/members?startDate=$start&endDate=$end&limit=1"
Invoke-WebRequest -Uri $u1 -Headers $headers -Method GET
```

Transactions (limit 1):

```powershell
$u2 = 'https://api.partners.blaze.me/api/v1/partner/transactions?limit=1'
Invoke-WebRequest -Uri $u2 -Headers $headers -Method GET
```

## Notes
- Members requires valid startDate/endDate (epoch ms) if provided; ensure endDate > startDate.
- Transactions endpoint supports `limit`, returns `values` array.

## Next Steps
1. Add paginated fetch (range + skip/limit) utilities for members and transactions.
2. Map Blaze responses to Supabase schema for initial ingestion tests.
3. Document error handling and rate-limit backoff per Blaze rules.
