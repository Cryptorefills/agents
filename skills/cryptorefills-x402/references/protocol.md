# x402 Protocol

The [x402 protocol](https://docs.x402.org/) enables machine-to-machine payments using HTTP 402 Payment Required. Cryptorefills implements x402 v2 with USDC on Base.

## Two-Phase Flow

```
Client                              Server
  │                                   │
  │  POST /v1/orders (no sig)         │
  │──────────────────────────────────→│
  │                                   │
  │  HTTP 402 + PAYMENT-REQUIRED      │
  │←──────────────────────────────────│
  │                                   │
  │  [decode requirements]            │
  │  [sign EIP-712 authorization]     │
  │                                   │
  │  POST /v1/orders + PAYMENT-SIG    │
  │──────────────────────────────────→│
  │                                   │
  │  [verify sig, settle on-chain]    │
  │                                   │
  │  HTTP 200 + order receipt         │
  │←──────────────────────────────────│
```

**Phase 1**: Client sends a normal order request. Server responds with 402 and payment requirements.
**Phase 2**: Client signs a USDC transfer authorization and re-sends the request with the signature header. Server verifies, settles on-chain, and fulfills the order.

## PAYMENT-REQUIRED Header

The 402 response includes a `PAYMENT-REQUIRED` header with base64url-encoded JSON:

```json
{
  "x402Version": 2,
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:8453",
      "maxAmountRequired": "25000000",
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913",
      "extra": {
        "name": "USDC",
        "decimals": 6
      },
      "payTo": "0xRecipientWalletAddress",
      "description": "$25.00 Amazon Gift Card"
    }
  ],
  "resource": "POST /v1/orders"
}
```

| Field | Meaning |
|-------|---------|
| `scheme` | Always `"exact"` — pay the exact amount specified |
| `network` | `eip155:8453` — Base mainnet |
| `maxAmountRequired` | USDC in atomic units (6 decimals). `25000000` = $25.00 |
| `asset` | USDC contract address on Base |
| `payTo` | Destination wallet address for this specific order |
| `description` | Human-readable description of the purchase |

## EIP-3009: transferWithAuthorization

The payment uses [EIP-3009](https://eips.ethereum.org/EIPS/eip-3009) `transferWithAuthorization`, which allows a third party to transfer tokens from a signer's account using a signed authorization. No prior `approve()` transaction needed — a single signature authorizes the transfer.

## EIP-712 Typed Data Structure

The signature follows [EIP-712](https://eips.ethereum.org/EIPS/eip-712) structured data signing.

### Domain

```json
{
  "name": "USD Coin",
  "version": "2",
  "chainId": 8453,
  "verifyingContract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913"
}
```

### Types

```json
{
  "TransferWithAuthorization": [
    { "name": "from", "type": "address" },
    { "name": "to", "type": "address" },
    { "name": "value", "type": "uint256" },
    { "name": "validAfter", "type": "uint256" },
    { "name": "validBefore", "type": "uint256" },
    { "name": "nonce", "type": "bytes32" }
  ]
}
```

### Values

| Field | Source |
|-------|--------|
| `from` | Agent's wallet address |
| `to` | `payTo` from PAYMENT-REQUIRED |
| `value` | `maxAmountRequired` from PAYMENT-REQUIRED |
| `validAfter` | `0` (immediately valid) |
| `validBefore` | `expiresAt` from the 402 response (Unix timestamp in seconds). Typical window: ~15 minutes. |
| `nonce` | Cryptographically random 32-byte hex (e.g., `0x` + 64 hex chars) |

## PAYMENT-SIGNATURE Header

After signing, construct the response header as base64url-encoded JSON:

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "eip155:8453",
  "payload": {
    "signature": "0x<65-byte hex signature>",
    "authorization": {
      "from": "0xAgentWallet",
      "to": "0xPayToAddress",
      "value": "25000000",
      "validAfter": "0",
      "validBefore": "1720000000",
      "nonce": "0x<random-32-bytes-hex>"
    }
  }
}
```

Base64url-encode this JSON and set it as the `PAYMENT-SIGNATURE` header value.

## Security Considerations

- **Verify amount**: Always check `maxAmountRequired` against your spending limit before signing
- **Verify payTo**: Confirm the destination address is associated with Cryptorefills
- **Nonce uniqueness**: Never reuse a nonce — generate a fresh random value for each transaction
- **Expiry**: Set `validBefore` to a reasonable future time (the order's payment deadline)
- **Domain verification**: Ensure the EIP-712 domain matches the USDC contract on Base (chain 8453)
- **Wallet isolation**: Use a dedicated wallet with limited USDC balance for agent operations
