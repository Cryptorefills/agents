# x402 REST API Reference

Base URL: `https://x402.cryptorefills.com`

Manifest: `https://x402.cryptorefills.com/.well-known/x402.json`

## GET /v1/brands

Discover brands available in a country.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country_code` | string (query) | Yes | Lowercase ISO 3166-1 Alpha-2 (e.g., `us`, `it`, `br`) |

**Response** (200): Array of brand objects.

| Field | Description |
|-------|-------------|
| `brand_name` | Brand identifier — use in `/v1/catalog` queries |
| `family` | Brand name (e.g., "Amazon.com", "Steam", "eSIM") |
| `category` | Product category (e.g., "e-commerce", "gaming", "food") |
| `min` | Minimum denomination (informational) |
| `max` | Maximum denomination (informational) |

**Example**:
```http
GET /v1/brands?country_code=us
```

## GET /v1/catalog

Get products and pricing for a specific brand.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `country_code` | string (query) | Yes | Lowercase ISO 3166-1 Alpha-2 |
| `brand_name` | string (query) | Conditional | Brand name from `/v1/brands`. At least one of `brand_name` or `family_name` required |
| `family_name` | string (query) | Conditional | Filter by brand name (from `/v1/brands` `family` field) |

**Response** (200): Array of product objects.

| Field | Description |
|-------|-------------|
| `product_id` | Use in `items[].product_id` when ordering |
| `price_usdc` | Indicative USDC price (actual amount confirmed in 402) |
| `denomination` | Fixed face value (e.g., "25"). Null for range products |
| `min_value` | Minimum amount for range products |
| `max_value` | Maximum amount for range products |
| `product_value_required` | If true, must set `items[].product_value` in order |

**Example**:
```http
GET /v1/catalog?country_code=us&brand_name=Amazon.com
```

## POST /v1/orders

Two-phase order endpoint.

### Phase 1: Get Payment Requirements

Send order without `PAYMENT-SIGNATURE` header.

**Request body**:
```json
{
  "email": "delivery@example.com",
  "items": [
    {
      "product_id": "abc123",
      "beneficiary_account": "recipient@example.com",
      "product_value": 25
    }
  ],
  "callback_url": "https://example.com/webhook"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | Yes | Contact email for the order |
| `items` | array | Yes | Products to purchase |
| `items[].product_id` | string | Yes | From `/v1/catalog` |
| `items[].beneficiary_account` | string | Yes | Email or account to receive the voucher |
| `items[].product_value` | number | Conditional | Required for range products (USD amount) |
| `callback_url` | string | No | Webhook URL for order state notifications |

**Response** (402): `PAYMENT-REQUIRED` header with base64url-encoded payment instructions.

### Phase 2: Submit Payment

Re-send the same request body with the `PAYMENT-SIGNATURE` header.

**Additional header**:
```
PAYMENT-SIGNATURE: <base64url-encoded JSON with x402Version, scheme, network, payload>
```

See `protocol.md` for the signature format.

**Response** (200):
```json
{
  "order_id": "cr_abc123",
  "status": "processing",
  "email": "delivery@example.com",
  "estimated_delivery_seconds": 60,
  "poll_url": "/v1/orders/cr_abc123",
  "deliveries": []
}
```

| Field | Description |
|-------|-------------|
| `order_id` | Unique order identifier |
| `status` | `processing`, `completed`, `failed`, `expired` |
| `estimated_delivery_seconds` | Typical delivery time |
| `poll_url` | Path to check order status |
| `deliveries` | Array of delivered items (empty initially) |

## GET /v1/orders/{order_id}

Poll for order status and voucher delivery.

**Response** (200):
```json
{
  "order_id": "cr_abc123",
  "status": "completed",
  "deliveries": [
    {
      "delivery_state": "completed",
      "brand_name": "Amazon.com",
      "product_name": "Amazon $25",
      "voucher_code": "XXXX-YYYY-ZZZZ",
      "pin": "1234",
      "url": "https://www.amazon.com/gc/redeem"
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `status` | `processing` → `completed` or `failed` or `expired` |
| `deliveries[].delivery_state` | `pending`, `completed`, `failed` |
| `deliveries[].voucher_code` | Gift card code |
| `deliveries[].pin` | PIN if required by the brand |
| `deliveries[].url` | Redemption URL if applicable |

**Polling**: Every 5–10 seconds until `status` is `completed` or `failed`.

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request — invalid body, missing required fields |
| 402 | Payment required — normal phase 1 response |
| 404 | Order or product not found |
| 422 | Validation failed — invalid product_id, amount out of range |
| 403 | Forbidden — invalid or expired payment signature |
| 500 | Server error — retry after a delay |
