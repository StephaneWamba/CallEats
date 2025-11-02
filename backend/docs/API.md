# API Reference

Complete API endpoint documentation for the Restaurant Voice Assistant backend.

## Authentication

The API supports **dual authentication**:

1. **JWT (Frontend Users)**: `Authorization: Bearer <token>` from Supabase Auth
2. **X-Vapi-Secret (Webhooks/Admin)**: `X-Vapi-Secret: <secret>` header

**Authentication Priority:**

- Endpoints accept either JWT or X-Vapi-Secret
- JWT authenticated users can only access their own restaurant's data
- X-Vapi-Secret provides admin access (for webhooks, scripts, etc.)

**Example with JWT:**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example with X-Vapi-Secret:**

```http
X-Vapi-Secret: your_vapi_secret_key
```

## Base URL

- Local: `http://localhost:8000`
- Production: Your deployed URL

## Endpoints

### Health Check

#### `GET /api/health`

Enhanced health check endpoint with service connectivity checks.

**Features:**

- Checks connectivity to all external services (Supabase, OpenAI, Vapi)
- Returns detailed status for each service
- Measures latency for performance monitoring

**Response (All Healthy):**

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "service": "restaurant-voice-assistant",
  "checks": {
    "supabase": {
      "status": "healthy",
      "latency_ms": 12.5
    },
    "openai": {
      "status": "healthy",
      "latency_ms": 145.3
    },
    "vapi": {
      "status": "healthy",
      "latency_ms": 89.2,
      "assistants": 1
    }
  }
}
```

**Response (Degraded - 503):**

If any critical service (Supabase or OpenAI) is unhealthy, returns HTTP 503:

```json
{
  "status": "degraded",
  "timestamp": "2025-01-01T12:00:00Z",
  "service": "restaurant-voice-assistant",
  "checks": {
    "supabase": {
      "status": "healthy",
      "latency_ms": 12.5
    },
    "openai": {
      "status": "unhealthy",
      "error": "Connection timeout"
    },
    "vapi": {
      "status": "not_configured"
    }
  }
}
```

**Status Codes:**

- `200`: All critical services healthy
- `503`: One or more critical services unhealthy

---

### Authentication

#### `POST /api/auth/register`

Register a new user with Supabase Auth.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d"
}
```

**Response:**

```json
{
  "message": "Registration successful.",
  "user_id": "bf99640a-d5e5-4ba8-b29c-85e0f3869302",
  "email": "user@example.com"
}
```

#### `POST /api/auth/login`

Login and receive JWT tokens.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "user": {
    "id": "bf99640a-d5e5-4ba8-b29c-85e0f3869302",
    "email": "user@example.com"
  }
}
```

#### `GET /api/auth/me`

Get current authenticated user information. Requires JWT.

**Response:**

```json
{
  "user_id": "bf99640a-d5e5-4ba8-b29c-85e0f3869302",
  "email": "user@example.com",
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "role": "user"
}
```

---

### Restaurants

#### `POST /api/restaurants`

Create a new restaurant with optional automatic phone assignment.

**Headers:**

- JWT or `X-Vapi-Secret` (required)

**Request Body:**

```json
{
  "name": "Le Bistro Français",
  "api_key": "optional_custom_api_key",
  "assign_phone": true,
  "force_twilio": false
}
```

**Parameters:**

- `name` (required): Restaurant name
- `api_key` (optional): Custom API key (auto-generated if not provided)
- `assign_phone` (optional, default: `true`): Automatically assign phone number
- `force_twilio` (optional, default: `false`): Skip existing phones, force Twilio creation

**Response:**

```json
{
  "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "name": "Le Bistro Français",
  "api_key": "api_key_abc123",
  "phone_number": "+19014994418",
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Phone Assignment Behavior:**

- If `assign_phone=true` and `force_twilio=false`: Tries existing unassigned phones first, then Twilio if available
- If `assign_phone=true` and `force_twilio=true`: Skips existing phones, directly creates Twilio number
- Returns `phone_number: null` if assignment fails (restaurant is still created successfully)
- **Failure Reasons**: Missing VAPI_API_KEY, missing PUBLIC_BACKEND_URL, no shared assistant, Twilio quota exceeded, Twilio credentials missing

---

### Vapi Webhooks

#### `POST /api/vapi/server`

Unified Vapi server webhook endpoint that routes events based on message type. Handles `assistant-request`, `end-of-call-report`, `status-update`, and other server events.

**Headers:**

- `X-Vapi-Secret` (required)

**Important**: Vapi webhooks are unreliable - final "ended" webhooks often don't arrive. The system automatically schedules a fallback API fetch 30 seconds after a call ends to retrieve complete call data (transcript, duration, cost). This ensures call history is always captured even if webhooks fail.

**Request Body (assistant-request):**

```json
{
  "message": {
    "type": "assistant-request",
    "phoneNumber": {
      "number": "+19014994418"
    },
    "call": {
      "id": "call_abc123"
    }
  }
}
```

**Response (assistant-request):**

```json
{
  "metadata": {
    "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
    "phoneNumber": "+19014994418"
  }
}
```

**Request Body (end-of-call-report):**

```json
{
  "message": {
    "type": "end-of-call-report",
    "call": {
      "id": "call_abc123",
      "startedAt": "2025-01-01T12:00:00Z",
      "endedAt": "2025-01-01T12:05:00Z",
      "duration": 300,
      "from": "+1234567890",
      "status": "ended",
      "messages": [...]
    },
    "phoneNumber": {
      "number": "+19014994418"
    }
  }
}
```

**Response (end-of-call-report):**

```json
{
  "success": true,
  "call_id": "uuid-of-stored-call"
}
```

**Returns:** `{}` for unknown message types or if phone number not found in mappings.

#### `POST /api/vapi/knowledge-base`

Main Vapi webhook endpoint for Function Tool calls. Performs vector similarity search and returns results.

**Headers:**

- `X-Vapi-Secret` (required)
- `X-Restaurant-Id` (optional, can be in metadata instead)

**Request Body:**

```json
{
  "message": {
    "toolCalls": [
      {
        "id": "call_abc123",
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
    "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d"
  }
}
```

**Tool Names:**

- `get_menu_info` → category: `menu`
- `get_modifiers_info` → category: `modifiers`
- `get_hours_info` → category: `hours`
- `get_zones_info` → category: `zones`

**Restaurant ID Resolution:**

1. `X-Restaurant-Id` header
2. Query parameter `restaurant_id`
3. Request metadata `restaurant_id`
4. Extract from phone number in request body

**Response:**

```json
{
  "results": [
    {
      "toolCallId": "call_abc123",
      "result": "Croissant - Buttery French pastry - $3.50\n\nBaguette - Fresh bread - $2.00",
      "metadata": {
        "items": [
          {
            "type": "menu_item",
            "name": "Croissant",
            "price": 3.5,
            "description": "Buttery French pastry",
            "score": 0.95
          }
        ]
      }
    }
  ]
}
```

**Error Responses:**

- `401`: Invalid `X-Vapi-Secret`
- `422`: Missing `restaurant_id` or invalid request format

---

### Categories

Manage menu item categories (replaces free-form category text).

#### `GET /api/restaurants/{restaurant_id}/categories`

List all categories for a restaurant, ordered by display_order and name.

**Headers:**

- JWT or `X-Vapi-Secret`

**Response:**

```json
[
  {
    "id": "abc-123",
    "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
    "name": "Appetizers",
    "description": "Small dishes to start your meal",
    "display_order": 0,
    "created_at": "2025-01-01T12:00:00Z",
    "updated_at": "2025-01-01T12:00:00Z"
  }
]
```

#### `POST /api/restaurants/{restaurant_id}/categories`

Create a new category.

**Request Body:**

```json
{
  "name": "Appetizers",
  "description": "Small dishes to start your meal",
  "display_order": 0
}
```

#### `PUT /api/restaurants/{restaurant_id}/categories/{category_id}`

Update a category. All fields optional.

**Request Body:**

```json
{
  "name": "Starters",
  "display_order": 1
}
```

#### `DELETE /api/restaurants/{restaurant_id}/categories/{category_id}`

Delete a category. Menu items with this category will have their `category_id` set to NULL automatically.

---

### Menu Items

#### `GET /api/restaurants/{restaurant_id}/menu-items`

List all menu items for a restaurant, ordered by category and name.

**Response includes:**

- `category_id`: UUID reference to categories table (nullable)
- `category`: Category name (for backward compatibility)
- `modifiers`: List of linked modifiers (if any)

#### `POST /api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers`

Link a modifier to a menu item.

**Request Body:**

```json
{
  "modifier_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "is_required": false,
  "display_order": 1
}
```

#### `GET /api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers`

List all modifiers linked to a menu item.

**Response:**

```json
[
  {
    "id": "link-uuid",
    "menu_item_id": "item-uuid",
    "modifier_id": "modifier-uuid",
    "modifier": {
      "id": "modifier-uuid",
      "name": "Extra Cheese",
      "price": "2.5"
    },
    "is_required": false,
    "display_order": 1,
    "created_at": "2025-01-01T12:00:00Z"
  }
]
```

#### `DELETE /api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers/{modifier_id}`

Unlink a modifier from a menu item.

---

### Delivery Zones

#### `GET /api/restaurants/{restaurant_id}/zones/check`

Check if coordinates are within any delivery zone (PostGIS spatial query).

**Query Parameters:**

- `lat` (required): Latitude (-90 to 90)
- `lng` (required): Longitude (-180 to 180)

**Response:**

```json
{
  "in_zone": true,
  "zone": {
    "id": "zone-uuid",
    "zone_name": "Downtown",
    "delivery_fee": 4.5,
    "min_order": 25.0,
    "boundary_geojson": {
      "type": "Polygon",
      "coordinates": [[[...]]]
    }
  }
}
```

Returns `{"in_zone": false}` if point is not in any zone.

#### `POST /api/restaurants/{restaurant_id}/zones/{zone_id}/boundary`

Set delivery zone boundary using GeoJSON (Polygon or MultiPolygon).

**Request Body:**

```json
{
  "boundary": {
    "type": "Polygon",
    "coordinates": [
      [
        [-74.006, 40.7128],
        [-73.995, 40.7128],
        [-73.995, 40.72],
        [-74.006, 40.72],
        [-74.006, 40.7128]
      ]
    ]
  }
}
```

**Response:**

```json
{
  "success": true,
  "boundary": {
    "id": "zone-uuid",
    "zone_name": "Downtown",
    "boundary": {
      "type": "Polygon",
      "coordinates": [[[...]]]
    },
    "center": {
      "type": "Point",
      "coordinates": [-74.0005, 40.7164]
    }
  }
}
```

#### `GET /api/restaurants/{restaurant_id}/zones/{zone_id}/map`

Get delivery zone boundary as GeoJSON Feature for map integration.

**Response:**

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[...]]]
  },
  "properties": {
    "zone_id": "zone-uuid",
    "zone_name": "Downtown"
  }
}
```

---

### Embeddings

**Automatic Embedding Generation:**

All CRUD operations on menu items, modifiers, categories, operating hours, and delivery zones automatically trigger background embedding generation:

- **POST/PUT/DELETE** on menu items → generates `menu` embeddings
- **POST/PUT/DELETE** on modifiers → generates `modifiers` embeddings
- **POST/PUT/DELETE** on categories → generates `menu` embeddings (affects menu display)
- **PUT/DELETE** on operating hours → generates `hours` embeddings
- **POST/PUT/DELETE** on delivery zones → generates `zones` embeddings

Embedding generation runs asynchronously in the background and does not block the API response. You can also manually trigger embedding generation using the endpoint below.

#### `POST /api/embeddings/generate`

Manually generate embeddings for restaurant data (menu, modifiers, hours, zones). Typically not needed since embeddings are generated automatically on data changes.

**Headers:**

- `X-Vapi-Secret` (required) - Only X-Vapi-Secret is supported (not JWT)

**Request Body:**

```json
{
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "category": "menu"
}
```

**Parameters:**

- `restaurant_id` (required): Restaurant UUID
- `category` (optional): Specific category to generate (`menu`, `modifiers`, `hours`, `zones`). If omitted, generates for all categories.

**Response:**

```json
{
  "status": "success",
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "embeddings_generated": 23
}
```

#### `POST /api/embeddings/cache/invalidate`

Force invalidate cache for a restaurant/category.

**Headers:**

- `X-Vapi-Secret` (required) - Only X-Vapi-Secret is supported (not JWT)

**Request Body:**

```json
{
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "category": "menu"
}
```

**Parameters:**

- `restaurant_id` (required): Restaurant UUID
- `category` (optional): Specific category to invalidate. If omitted, invalidates all categories.

**Response:**

```json
{
  "status": "success",
  "message": "Cache cleared for restaurant 04529052-b3dd-43c1-a534-c18d8c0f4c6d"
}
```

---

### Call History

#### `GET /api/calls`

List call history for a restaurant. Messages are filtered to include only `role` and `content` fields.

**Headers:**

- JWT or `X-Vapi-Secret` (required)
- `X-Restaurant-Id` (optional, if using JWT)

**Query Parameters:**

- `restaurant_id` (optional): Restaurant UUID (if not in header, required for JWT users)
- `limit` (optional, default: 50, max: 200): Maximum number of results

**Example:**

```bash
GET /api/calls?restaurant_id=04529052-b3dd-43c1-a534-c18d8c0f4c6d&limit=10
```

**Response:**

```json
{
  "data": [
    {
      "id": "call_abc123",
      "started_at": "2025-01-01T12:00:00Z",
      "ended_at": "2025-01-01T12:05:00Z",
      "duration_seconds": 300,
      "caller": "+1234567890",
      "outcome": "completed",
      "messages": [
        {
          "role": "user",
          "content": "What's on your menu?"
        },
        {
          "role": "bot",
          "content": "We have croissants, baguettes..."
        }
      ]
    }
  ]
}
```

#### `GET /api/calls/{call_id}`

Get a single call record with full transcript. Messages are filtered to include only `role` and `content` fields.

**Headers:**

- JWT or `X-Vapi-Secret` (required)
- `X-Restaurant-Id` (optional, if using JWT)

**Query Parameters:**

- `restaurant_id` (optional): Restaurant UUID (required for JWT users)

**Response:**

```json
{
  "id": "call_abc123",
  "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
  "started_at": "2025-01-01T12:00:00Z",
  "ended_at": "2025-01-01T12:05:00Z",
  "duration_seconds": 300,
  "caller": "+1234567890",
  "outcome": "ended",
  "messages": [
    {
      "role": "user",
      "content": "What's on your menu?"
    },
    {
      "role": "bot",
      "content": "We have croissants, baguettes..."
    }
  ],
  "cost": 0.2455
}
```

**Note**: Call records are created automatically via Vapi webhooks (`/api/vapi/server`). Manual creation is not supported.

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message"
}
```

**Common Status Codes:**

- `401`: Authentication failed (invalid JWT or `X-Vapi-Secret`)
- `403`: Forbidden (user cannot access restaurant data)
- `404`: Resource not found
- `422`: Validation error (missing required field, invalid format)
- `500`: Internal server error

## Request ID Tracking

All API responses include an `X-Request-ID` header for request tracking and debugging.

**Header:**

```http
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Usage:**

- Automatically generated for each request
- Included in all error responses
- Used in server logs for correlation
- Shortened to 8 characters in logs for readability
- Can be provided by client (for request tracing)

**Example:**

```bash
curl -H "X-Request-ID: my-custom-id" http://localhost:8000/api/health
```

## Response Formatting

- All timestamps are in ISO 8601 format (UTC)
- All UUIDs are lowercase with hyphens
- Phone numbers are in E.164 format (e.g., `+19014994418`)

## Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These are available in development mode and show all endpoints, request/response schemas, and allow testing directly from the browser.
