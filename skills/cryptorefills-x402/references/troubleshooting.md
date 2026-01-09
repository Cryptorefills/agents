# x402 Troubleshooting

Error handling and recovery for x402 autonomous purchases.

## Signature Errors

### Invalid Signature
**Symptom**: 400 or 403 after submitting PAYMENT-SIGNATURE
**Causes and fixes**:

| Cause | Fix |
|-------|-----|
| Wrong EIP-712 domain | Use domain: `name: "USD Coin"`, `version: "2"`, `chainId: 8453`, `verifyingContract: 0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` |
| Wrong chain ID | Must be `8453` (Base mainnet) |
| Wrong USDC address | Must be `0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913` |
| Expired `validBefore` | Set to a future timestamp. If expired, restart from phase 1 |
| Reused nonce | Generate a fresh random 32-byte nonce per transaction |
| Wrong `to` address | Must match `payTo` from the 402 response exactly |
| Wrong `value` | Must match `maxAmountRequired` from 402 exactly |

### Signature Format Error
**Symptom**: Header parsing fails
**Fix**: Ensure `PAYMENT-SIGNATURE` value is valid base64url-encoded JSON matching the schema in `protocol.md`. Check that no padding or encoding issues exist.

## Balance Errors

### Insufficient USDC Balance
**Symptom**: On-chain transaction reverts after signature accepted
**Fix**: Check USDC balance on Base before signing:
```
balanceOf(agentWalletAddress) on 0x833589fCD6eDb6E08f4c7C32D4f71b54bDA02913
```
Ensure balance >= `maxAmountRequired`.

### Wrong Token
**Symptom**: Balance check shows sufficient funds but transfer fails
**Fix**: Verify you're checking USDC (not USDT, DAI, or native ETH) on Base chain specifically.

## Timeout Errors

### Payment Deadline Expired
**Symptom**: 402 payment requirements expired before signature submission (typical window: ~15 minutes from `expiresAt` field)
**Fix**: Restart from phase 1 — send a new POST without signature to get fresh payment requirements with a new deadline.

### Order Expired
**Symptom**: `GET /v1/orders/{id}` returns `status: "expired"`
**Fix**: Create a new order. Expired orders cannot be paid or recovered. Contact support@cryptorefills.com if payment was sent before expiry.

## Network Errors

### Wrong Chain
**Symptom**: Wallet connected to Ethereum mainnet, Polygon, Arbitrum, etc.
**Fix**: x402 endpoint uses Base (chain 8453) exclusively. Switch wallet network to Base.

### Transaction Pending
**Symptom**: Order stays in `processing` for longer than expected
**Fix**: Check Base block explorer for the transaction. Network congestion may delay settlement. Continue polling.

## API Errors

### Brand Not Found
**Symptom**: Empty catalog results
**Fix**: Verify `brand_name` matches exactly (case-sensitive) from `/v1/brands` response. Check `country_code` is lowercase.

### Product Not Available
**Symptom**: 422 on order creation
**Fix**: Product may be out of stock or discontinued. Re-query `/v1/catalog` for current availability.

### Invalid Product Value
**Symptom**: 422 when ordering range product
**Fix**: Ensure `product_value` is within `min_value`–`max_value` from catalog. Must be a number, not a string.

### Missing Beneficiary Account
**Symptom**: 400 on order creation
**Fix**: Every item needs `beneficiary_account` — an email address for delivery.

## Recovery Patterns

| Scenario | Action |
|----------|--------|
| Signature rejected | Check all EIP-712 fields, regenerate nonce, retry |
| 402 expired | Re-POST without signature to get fresh requirements |
| Order expired | Create new order with same products |
| Insufficient balance | Fund wallet with USDC on Base, then retry |
| Server 500 | Wait 30 seconds, retry once. If persistent, try later |
| Order failed | Check error details in response. Contact support@cryptorefills.com with order_id and tx hash |
