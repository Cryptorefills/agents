---
name: cryptorefills-x402
description: "Autonomous agent commerce — buy gift cards, top up phones, get eSIMs with USDC on Base (Ethereum L2) via x402 protocol. No account, no OAuth, no API key. For AI agents with crypto wallets. 10,500+ brands, 180+ countries."
compatibility: "Requires: (1) HTTP client for REST API calls, (2) Ethereum wallet with USDC on Base (chain 8453), (3) EIP-712 signing capability for EIP-3009 transferWithAuthorization. No account or API key needed."
metadata:
  author: cryptorefills
  version: "1.1.0"
  homepage: "https://www.cryptorefills.com"
  repository: "https://github.com/cryptorefills/agents"
---

# Cryptorefills x402 — Autonomous Agent Commerce

Fully autonomous purchasing for AI agents with crypto wallets. No accounts, no OAuth, no API keys — just USDC on Base and a signing key.

Built on the [x402 protocol](https://docs.x402.org/) — HTTP 402 Payment Required as a machine-to-machine payment standard.

**For human-guided purchases with multiple payment methods**, follow the instructions in **cryptorefills-buy** instead.
**For browse-only catalog exploration**, follow **cryptorefills-catalog** instead.

When the user needs multi-currency payment options or human-guided purchasing, switch to the cryptorefills-buy skill instructions.

## When to Activate

- Agent has a wallet with USDC on Base and can sign EIP-712 messages
- Task requires autonomous purchasing without human payment interaction
- No account setup, OAuth flow, or API key management is desired
- Keywords: "buy with USDC", "autonomous purchase", "agent commerce", "x402 payment", "programmatic gift card"
- Use case: automated gift card procurement, travel eSIM provisioning, programmatic rewards

## Requirements

| Requirement | Details |
|-------------|---------|
| USDC on Base | Chain 8453, contract `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` |
| EIP-712 signing | Wallet must sign typed data for `transferWithAuthorization` (EIP-3009) |
| HTTP client | Standard REST API calls (GET, POST) |
| Account | **None required** |

## Spending Safeguards

Autonomous agents spending real money require strict controls:

- **Set a per-session spending limit** before starting (e.g., $50 max)
- **Verify the order amount** from the 402 response before signing — never sign blindly
- **Use a dedicated wallet** with only the necessary USDC balance
- **Log every transaction**: order_id, product, amount, wallet address, tx hash
- **Never sign for more** than the `maxAmountRequired` in the 402 response
- **Validate `payTo` address** — confirm it matches Cryptorefills' expected address
- Digital goods are non-refundable once delivered

## Base URL

```
https://x402.atomicrails.com
```

Manifest: `https://x402.atomicrails.com/.well-known/x402.json`

## Core Workflow

```
GET /v1/brands          → discover brands
GET /v1/catalog         → get products and prices
POST /v1/orders         → receive 402 with payment requirements
   ↓ sign EIP-712
POST /v1/orders         → submit with PAYMENT-SIGNATURE → receive 200
GET /v1/orders/{id}     → poll until delivered
```

## Step-by-Step

### 1. Browse Brands

```http
GET /v1/brands?country_code=us
```

Returns available brands for the country. Each entry includes `brand_name`, `family`, `category`, `min`, `max`.

Use `brand_name` values in the next step. Country codes are **lowercase** ISO 3166-1 Alpha-2 (`us`, `it`, `br`). Note: MCP skills use uppercase — different endpoint.

### 2. Get Catalog

```http
GET /v1/catalog?country_code=us&brand_name=Amazon.com
```

Returns products with `product_id`, `price_usdc`, `denomination` (fixed) or `min_value`/`max_value` (range).

- **Fixed products**: Use `product_id` directly. Price is shown as `price_usdc`.
- **Range products**: `product_value_required` flag indicates you must set `items[].product_value` to the desired amount.

### 3. Create Order — Phase 1 (Get Payment Requirements)

```bash
curl -X POST https://x402.atomicrails.com/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "email": "delivery@example.com",
    "items": [{
      "product_id": "abc123",
      "beneficiary_account": "recipient@example.com",
      "product_value": 25
    }]
  }'
# → HTTP 402 with PAYMENT-REQUIRED header
# product_value is required for range products; omit for fixed-denomination products
```

**Server responds with HTTP 402** and a `PAYMENT-REQUIRED` header containing base64url-encoded JSON:

```json
{
  "x402Version": 2,
  "accepts": [{
    "scheme": "exact",
    "network": "eip155:8453",
    "maxAmountRequired": "25000000",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913",
    "extra": { "name": "USDC", "decimals": 6 },
    "payTo": "0x...",
    "description": "$25.00 Amazon Gift Card"
  }],
  "expiresAt": 1720003600
}
```

Key fields:
- `maxAmountRequired` — USDC amount in atomic units (6 decimals). `25000000` = $25.00
- `payTo` — destination wallet for this order session
- `network` — must be `eip155:8453` (Base)
- `expiresAt` — Unix timestamp (seconds) when the payment offer expires. Use this as `validBefore` when signing. Typical window: ~15 minutes from order creation

### 4. Sign Payment

Construct an EIP-712 signature for `transferWithAuthorization` (EIP-3009):

**Domain**: USDC contract on Base
**Types**: `TransferWithAuthorization(address from, address to, uint256 value, uint256 validAfter, uint256 validBefore, bytes32 nonce)`

| Field | Value |
|-------|-------|
| `from` | Your wallet address |
| `to` | `payTo` from 402 response |
| `value` | `maxAmountRequired` from 402 response |
| `validAfter` | `0` |
| `validBefore` | `expiresAt` value from the 402 response (Unix seconds) |
| `nonce` | Random 32-byte hex |

Sign with your wallet's private key. See `references/protocol.md` for exact EIP-712 typed data structure.

### 5. Complete Order — Phase 2

Re-POST the same order with the `PAYMENT-SIGNATURE` header:

```bash
curl -X POST https://x402.atomicrails.com/v1/orders \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <base64url-encoded JSON>" \
  -d '{ ...same body as phase 1... }'
# → HTTP 200 with order receipt
```

The `PAYMENT-SIGNATURE` header contains base64url-encoded JSON:

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "eip155:8453",
  "payload": {
    "signature": "0x...",
    "authorization": {
      "from": "0xYourWallet",
      "to": "0xPayToAddress",
      "value": "25000000",
      "validAfter": "0",
      "validBefore": "1720000000",
      "nonce": "0xRandomBytes32"
    }
  }
}
```

**Server responds with HTTP 200**:
```json
{
  "order_id": "cr_abc123",
  "status": "processing",
  "estimated_delivery_seconds": 60,
  "poll_url": "/v1/orders/cr_abc123"
}
```

### 6. Track Delivery

```http
GET /v1/orders/{order_id}
```

Poll every 5–10 seconds until `status` is `completed` or `failed`.

When `completed`, the `deliveries` array contains:
- `voucher_code` — gift card redemption code
- `pin` — PIN if required
- `url` — redemption URL if applicable
- `brand_name`, `product_name` — what was purchased

## Critical Gotchas

- **USDC contract**: Must be exactly `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` on Base
- **Chain ID**: Must be `8453` (Base mainnet). Wrong chain = invalid signature
- **Amount precision**: Use the exact `maxAmountRequired` from 402 — do not round or modify
- **Payment timeout**: The 402 `expiresAt` field gives the deadline (~15 min). Sign and resubmit before it expires
- **Country codes**: **Lowercase** for x402 endpoints (`us`, not `US`). MCP skills use uppercase
- **Brand names**: Case-sensitive — use exact values from `/v1/brands` response
- **Nonce**: Must be unique per transaction. Use a cryptographically random 32-byte value
- **EIP-712 domain**: Must match the USDC contract's domain separator on Base

## References

Load references only when you need deeper detail than what's in this skill file.

| File | Load when... | Content |
|------|-------------|---------|
| `references/protocol.md` | You need the exact EIP-712 domain, types, and signature encoding | x402 two-phase flow, EIP-712 typed data, EIP-3009 details |
| `references/endpoints.md` | You need exact request/response schemas for an API call | REST API reference for all x402 endpoints |
| `references/troubleshooting.md` | A request fails or returns an unexpected status | Error handling and recovery patterns |
