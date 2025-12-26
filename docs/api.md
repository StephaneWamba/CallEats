# CallEats API Reference

REST API endpoints, request/response formats, and authentication.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: Configured via `PUBLIC_BACKEND_URL` environment variable

## Authentication

| Type             | Method        | Header                              |
| ---------------- | ------------- | ----------------------------------- |
| **Frontend API** | JWT           | `Authorization: Bearer <jwt_token>` |
| **Webhook API**  | Secret Header | `X-Vapi-Secret: <vapi_secret_key>`  |

JWT tokens from Supabase Auth. Webhook secret via `VAPI_SECRET_KEY` environment variable.

## Endpoints

### Health Check

**`GET /api/health`**

Check API health and database connectivity.

**Response:**

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Authentication

| Endpoint                   | Method | Description                         |
| -------------------------- | ------ | ----------------------------------- |
| `/api/auth/signup`         | POST   | Create new user account             |
| `/api/auth/login`          | POST   | Authenticate user and get JWT token |
| `/api/auth/logout`         | POST   | Logout user (invalidates session)   |
| `/api/auth/password-reset` | POST   | Request password reset email        |

**Request (signup/login):**

```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe" // signup only
}
```

**Response:**

```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "jwt_token"
}
```

### Restaurants

| Endpoint                                 | Method | Description                   |
| ---------------------------------------- | ------ | ----------------------------- |
| `/api/restaurants/me`                    | GET    | Get current user's restaurant |
| `/api/restaurants/{restaurant_id}/stats` | GET    | Get restaurant statistics     |

**Response (stats):**

```json
{
  "total_calls_today": 10,
  "menu_items_count": 25,
  "categories_count": 5,
  "phone_status": "active"
}
```

### Menu Items

| Endpoint                                    | Method | Description                                          |
| ------------------------------------------- | ------ | ---------------------------------------------------- |
| `/api/{restaurant_id}/menu-items`           | GET    | List menu items (filter: `category_id`, `available`) |
| `/api/{restaurant_id}/menu-items`           | POST   | Create menu item                                     |
| `/api/{restaurant_id}/menu-items/{item_id}` | PUT    | Update menu item                                     |
| `/api/{restaurant_id}/menu-items/{item_id}` | DELETE | Delete menu item                                     |

**Request (create/update):**

```json
{
  "name": "Pizza Margherita",
  "description": "Classic pizza",
  "price": 12.99,
  "category_id": "uuid",
  "available": true,
  "modifier_ids": ["uuid1", "uuid2"]
}
```

### Categories

| Endpoint                                        | Method | Description     |
| ----------------------------------------------- | ------ | --------------- |
| `/api/{restaurant_id}/categories`               | GET    | List categories |
| `/api/{restaurant_id}/categories`               | POST   | Create category |
| `/api/{restaurant_id}/categories/{category_id}` | PUT    | Update category |
| `/api/{restaurant_id}/categories/{category_id}` | DELETE | Delete category |

### Modifiers

| Endpoint                                       | Method | Description     |
| ---------------------------------------------- | ------ | --------------- |
| `/api/{restaurant_id}/modifiers`               | GET    | List modifiers  |
| `/api/{restaurant_id}/modifiers`               | POST   | Create modifier |
| `/api/{restaurant_id}/modifiers/{modifier_id}` | PUT    | Update modifier |
| `/api/{restaurant_id}/modifiers/{modifier_id}` | DELETE | Delete modifier |

### Operating Hours

| Endpoint                               | Method | Description                           |
| -------------------------------------- | ------ | ------------------------------------- |
| `/api/{restaurant_id}/operating-hours` | GET    | Get operating hours                   |
| `/api/{restaurant_id}/operating-hours` | PUT    | Update operating hours (replaces all) |

**Request (update):**

```json
[
  {
    "day_of_week": "Monday",
    "open_time": "09:00:00",
    "close_time": "22:00:00",
    "is_closed": false
  }
]
```

### Delivery Zones

| Endpoint                                        | Method | Description          |
| ----------------------------------------------- | ------ | -------------------- |
| `/api/{restaurant_id}/delivery-zones`           | GET    | List delivery zones  |
| `/api/{restaurant_id}/delivery-zones`           | POST   | Create delivery zone |
| `/api/{restaurant_id}/delivery-zones/{zone_id}` | PUT    | Update delivery zone |
| `/api/{restaurant_id}/delivery-zones/{zone_id}` | DELETE | Delete delivery zone |

**Request (create/update):**

```json
{
  "zone_name": "Downtown",
  "description": "Downtown delivery area",
  "delivery_fee": 5.00,
  "min_order": 20.00,
  "geometry": {...}
}
```

### Call History

| Endpoint               | Method | Description                                 |
| ---------------------- | ------ | ------------------------------------------- |
| `/api/calls`           | GET    | List call history (query: `limit`)          |
| `/api/calls/{call_id}` | GET    | Get single call record with full transcript |

**Response:**

```json
{
  "id": "uuid",
  "restaurant_id": "uuid",
  "started_at": "2024-01-01T10:00:00Z",
  "ended_at": "2024-01-01T10:05:00Z",
  "duration_seconds": 300,
  "caller": "+19308889330",
  "outcome": "completed",
  "messages": [
    {
      "role": "user",
      "content": "What's on your menu?"
    },
    {
      "role": "assistant",
      "content": "We have pizza, pasta..."
    }
  ],
  "cost": 0.15
}
```

### Embeddings

**`POST /api/embeddings/generate`**

Generate embeddings for restaurant content.

**Request:**

```json
{
  "restaurant_id": "uuid",
  "category": "menu"
}
```

**Response:**

```json
{
  "status": "success",
  "restaurant_id": "uuid",
  "embeddings_generated": 25
}
```

**Categories:** `menu`, `modifiers`, `hours`, `zones`

## Vapi Webhook Endpoints

### `POST /api/vapi/server`

Unified server webhook for Vapi events.

**Headers:**

```
X-Vapi-Secret: <vapi_secret_key>
```

**Event Types:**

- `assistant-request`: Maps phone number to restaurant_id
- `status-update`: Monitors call status
- `end-of-call-report`: Triggers call data retrieval

**Request (assistant-request):**

```json
{
  "message": {
    "type": "assistant-request",
    "call": {
      "id": "call_id",
      "phoneNumber": "+19308889330"
    }
  }
}
```

**Response:**

```json
{
  "metadata": {
    "restaurant_id": "uuid",
    "phoneNumber": "+19308889330"
  }
}
```

### `POST /api/vapi/knowledge-base`

Knowledge base tool call endpoint for vector search.

**Headers:**

```
X-Vapi-Secret: <vapi_secret_key>
X-Restaurant-Id: <restaurant_id> (optional, can be in metadata)
```

**Request:**

```json
{
  "message": {
    "toolCalls": [
      {
        "id": "tool_call_id",
        "function": {
          "name": "get_menu_info",
          "arguments": {
            "query": "What's on your menu?"
          }
        }
      }
    ]
  },
  "metadata": {
    "restaurant_id": "uuid"
  }
}
```

**Response:**

```json
{
  "toolCallId": "tool_call_id",
  "result": "We have pizza, pasta, and salads...",
  "items": [
    {
      "name": "Pizza Margherita",
      "description": "Classic pizza",
      "price": "$12.99"
    }
  ]
}
```

### `POST /api/vapi/cache/invalidate`

Invalidate cache entries.

**Request:**

```json
{
  "restaurant_id": "uuid",
  "category": "menu"
}
```

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message",
  "request_id": "request_id_string"
}
```

**Status Codes:**

- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `404`: Not Found
- `422`: Unprocessable Entity
- `429`: Too Many Requests (rate limit exceeded)
- `500`: Internal Server Error
- `502`: Bad Gateway (external API error)

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Strict Endpoints**: Lower limits for expensive operations
- **Webhook Endpoints**: Higher limits for Vapi.ai webhooks

Rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Request IDs

All requests include unique request ID for tracing:

- **Header**: `X-Request-ID` (optional, auto-generated if not provided)
- **Response**: Included in error responses
- **Logs**: Request ID included in all log entries
