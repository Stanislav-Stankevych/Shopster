# API Examples

Quick reference for interacting with the Shopster REST API. Replace `TOKEN` and `BASE_URL` (`http://localhost:8000` locally or `http://159.89.27.194:8000` in demo) as needed.

## Authentication

```bash
curl -X POST "$BASE_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo-pass"}'
```

Response:
```json
{
  "refresh": "…",
  "access": "…"
}
```

Refresh:
```bash
curl -X POST "$BASE_URL/api/auth/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "REFRESH_TOKEN"}'
```

## Products

List products with filters:
```bash
curl "$BASE_URL/api/products/?search=diffuser&category=home&min_price=1000&ordering=-price"
```

Retrieve a single product (slug):
```bash
curl "$BASE_URL/api/products/aromadiffuzor-breeze/"
```

## Cart

Create or fetch a cart:
```bash
curl -X POST "$BASE_URL/api/carts/" -H "Content-Type: application/json"
```

Add/update an item:
```bash
curl -X POST "$BASE_URL/api/carts/{cart_id}/items/" \
  -H "Content-Type: application/json" \
  -d '{"product": 63, "quantity": 2}'
```

## Orders

Checkout requires auth (Bearer token):
```bash
curl -X POST "$BASE_URL/api/orders/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "cart": "cart_uuid",
        "shipping_address": "Lenina 1, Moscow",
        "payment_method": "card"
      }'
```

## Blog

List published posts:
```bash
curl "$BASE_URL/api/content/posts/?page=1&tag=algolia"
```

Retrieve by slug:
```bash
curl "$BASE_URL/api/content/posts/aroma-diffusers-guide/"
```

## Admin-Specific

Create product (staff token required):
```bash
curl -X POST "$BASE_URL/api/products/" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
        "name": "New Candle",
        "price": "1990.00",
        "currency": "RUB",
        "category": 50,
        "short_description": "Hand poured candle."
      }'
```

> Full schema: `GET $BASE_URL/api/schema/` (downloadable JSON/YAML).

