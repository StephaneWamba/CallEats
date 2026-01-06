# CallEats Architecture

System architecture, data flows, and design decisions.

## System Overview

Multi-tenant voice assistant system with:

- **FastAPI Backend**: REST API with async support and middleware stack
- **Vapi.ai**: Voice assistant platform for phone calls
- **Supabase**: PostgreSQL with pgvector for vector search
- **React Frontend**: TypeScript SPA dashboard
- **Redis Cache**: Distributed caching with in-memory fallback
- **Sentry**: Error tracking and monitoring

## Architecture Diagram

```mermaid
graph TB
    subgraph "Voice Layer"
        A[Customer Phone Call] --> B[Vapi.ai Voice Assistant]
        B --> C[GPT-4o-mini LLM]
    end

    subgraph "API Layer"
        B --> D[FastAPI Backend]
        D --> E[Auth Middleware]
        D --> F[Rate Limiting]
        D --> G[Request Validation]
    end

    subgraph "Domain Layer"
        D --> H[Phone Mapping Service]
        D --> I[Vector Search Service]
        D --> J[Call History Service]
        D --> K[Embedding Service]
    end

    subgraph "Infrastructure Layer"
        H --> L[Supabase Database]
        I --> M[OpenAI API]
        I --> N[pgvector Search]
        J --> O[Vapi API]
        K --> M
        L --> P[Redis Cache]
    end

    subgraph "Frontend Layer"
        Q[React SPA] --> D
        Q --> R[Restaurant Dashboard]
        Q --> S[Menu Builder]
        Q --> T[Call History]
    end

    style A fill:#3b82f6
    style B fill:#8b5cf6
    style D fill:#10b981
    style I fill:#f59e0b
    style L fill:#06b6d4
    style Q fill:#ef4444
```

## Multi-Tenant Design

### Tenant Isolation

```mermaid
graph TB
    subgraph "Data Isolation"
        A[All Queries] --> B[Filter by restaurant_id]
        B --> C[RLS Policies]
        B --> D[Vector Search Filter]
        B --> E[Cache Key Prefix]
    end
    
    subgraph "Isolation Layers"
        C --> F[Database Level]
        D --> G[Application Level]
        E --> H[Cache Level]
    end
    
    style B fill:#10b981
    style C fill:#f59e0b
```

All data scoped by `restaurant_id`:
- **Database**: RLS policies in Supabase
- **Application**: All queries filter by `restaurant_id`
- **Vector Search**: Restaurant-scoped embeddings
- **Cache**: `restaurant_id` in cache keys

### Phone Number Routing

```mermaid
sequenceDiagram
    participant C as Customer
    participant V as Vapi.ai
    participant B as Backend
    participant DB as Database
    
    C->>V: Calls restaurant phone
    V->>B: assistant-request (phone)
    B->>DB: Lookup restaurant_id
    DB-->>B: restaurant_id
    B->>B: Inject metadata
    B-->>V: Restaurant context
    Note over V,B: All tool calls include restaurant_id
```

Shared Vapi.ai assistant routes calls via phone number → `restaurant_id` mapping.

## Voice Assistant Integration

### Vapi.ai Workflow

```mermaid
sequenceDiagram
    participant C as Customer
    participant V as Vapi.ai
    participant B as Backend
    participant DB as Database

    C->>V: Phone Call
    V->>B: assistant-request (phone)
    B->>DB: Lookup restaurant_id
    DB-->>B: restaurant_id
    B-->>V: Metadata

    C->>V: "What's on your menu?"
    V->>B: Tool Call (get_menu_info)
    B->>DB: Vector Search
    DB-->>B: Results
    B-->>V: Formatted Response
    V->>C: Voice Response
```

### Function Tools

| Tool | Category | Purpose |
|------|----------|---------|
| `get_menu_info` | menu | Menu items and descriptions |
| `get_modifiers_info` | modifiers | Add-ons and extras |
| `get_hours_info` | hours | Operating hours |
| `get_zones_info` | zones | Delivery zones and fees |

### Tool Call Processing

1. Extract query from Vapi request
2. Resolve `restaurant_id` (header/query/metadata/phone)
3. Map tool name → category
4. Vector search with `restaurant_id` filter
5. Format response with metadata for TTS

## Vector Search Pipeline

### Embedding Generation

```mermaid
graph LR
    A[Menu Item] --> B[Format Content]
    B --> C[OpenAI Embedding API]
    C --> D[1536-dim Vector]
    D --> E[Store in pgvector]
    
    style C fill:#10b981
    style E fill:#06b6d4
```

Content format: `"{name} - {description} - ${price}"`

Stored in `document_embeddings`:
- `restaurant_id`, `category`, `content`, `metadata` (JSONB), `embedding` (1536d)

### Search Flow

```mermaid
graph TB
    A[User Query] --> B[Generate Embedding]
    B --> C{Cache Hit?}
    C -->|Yes| D[Return Cached]
    C -->|No| E[pgvector Search]
    E --> F[Filter restaurant_id]
    F --> G[Filter category]
    G --> H[Top 5 Results]
    H --> I[Cache 60s TTL]
    I --> J[Format Response]
    
    style C fill:#f59e0b
    style E fill:#06b6d4
    style I fill:#8b5cf6
```

### Search Function

PostgreSQL function with HNSW index:

```sql
CREATE FUNCTION search_documents(
    query_embedding vector(1536),
    query_restaurant_id uuid,
    query_category text DEFAULT NULL,
    match_count int DEFAULT 5
) RETURNS TABLE (content text, metadata jsonb, similarity float);

CREATE INDEX idx_document_embeddings_vector
ON document_embeddings USING hnsw (embedding vector_cosine_ops);
```

## Call Management

### Webhook Events & Fallback

```mermaid
sequenceDiagram
    participant V as Vapi.ai
    participant B as Backend
    participant T as Background Thread
    participant DB as Database
    
    V->>B: assistant-request
    V->>B: status-update (ringing)
    B->>T: Schedule fetch (30s delay)
    V->>B: status-update (in-progress)
    V->>B: end-of-call-report (optional)
    T->>V: Fetch call data (fallback)
    V-->>T: Complete call data
    T->>DB: Store call history
```

**Webhook Events**: `assistant-request`, `status-update`, `end-of-call-report`

**Fallback**: Background thread fetches call data 30s after "ringing" status to ensure complete data capture.

### Call Data Storage

`call_history` table: `restaurant_id`, `started_at`, `ended_at`, `duration_seconds`, `caller`, `outcome`, `messages` (filtered transcript), `cost`

## Caching Strategy

### Cache Architecture

```mermaid
graph TB
    A[Request] --> B{Cache Layer}
    B -->|Primary| C[Redis]
    B -->|Fallback| D[In-Memory TTLCache]
    C --> E[Distributed Cache]
    D --> F[Single Instance]
    
    style C fill:#ef4444
    style D fill:#f59e0b
```

Two-tier: Redis (distributed) → In-Memory (fallback)

### Cache Keys & TTL

| Key Pattern | TTL | Purpose |
|------------|-----|---------|
| `cache:{restaurant_id}:{category}:{query}` | 60s | Search results |
| `call_phone:{call_id}` | 1h | Call mappings |

### Cache Invalidation

Automatic on data changes:
- Menu update → Clear `cache:{restaurant_id}:menu:*`
- Modifier update → Clear `cache:{restaurant_id}:modifiers:*`
- Hours update → Clear `cache:{restaurant_id}:hours:*`
- Zone update → Clear `cache:{restaurant_id}:zones:*`

## Middleware Stack

```mermaid
graph TB
    A[Incoming Request] --> B[RequestIDMiddleware]
    B --> C[ValidationMiddleware]
    C --> D[TimeoutMiddleware]
    D --> E[AuthMiddleware]
    E --> F[SlowAPIMiddleware]
    F --> G[CORSMiddleware]
    G --> H[SecurityHeadersMiddleware]
    H --> I[Application Handler]
    
    style E fill:#f59e0b
    style F fill:#ef4444
```

Applied in order: Request ID → Validation → Timeout (30s) → Auth (JWT/Secret) → Rate Limiting → CORS → Security Headers

## Frontend Architecture

### Component Structure

```
src/
├── pages/          # Route pages
├── components/     # Reusable components
│   ├── common/     # Button, Modal, Toast
│   ├── layout/     # Layout, Sidebar, Header
│   ├── menu/       # Menu components
│   └── dashboard/  # Dashboard components
├── features/       # Feature hooks/utilities
├── api/            # API client
├── contexts/       # Auth, Toast, Sidebar
└── hooks/          # Custom hooks
```

### State Management

- **React Query**: Server state, caching, background refetch
- **React Context**: Auth, toast, sidebar state
- **Local State**: Component-specific `useState`

### API Client

Centralized client: base URL, interceptors, error handling, auth token injection, request ID tracking.

## Database Schema

### Core Tables

```mermaid
erDiagram
    RESTAURANTS ||--o{ RESTAURANT_PHONE_MAPPINGS : has
    RESTAURANTS ||--o{ CATEGORIES : has
    RESTAURANTS ||--o{ MENU_ITEMS : has
    RESTAURANTS ||--o{ OPERATING_HOURS : has
    RESTAURANTS ||--o{ DELIVERY_ZONES : has
    RESTAURANTS ||--o{ DOCUMENT_EMBEDDINGS : has
    RESTAURANTS ||--o{ CALL_HISTORY : has
    CATEGORIES ||--o{ MENU_ITEMS : contains
    MENU_ITEMS }o--o{ MODIFIERS : "has many"
    MENU_ITEMS }o--o{ DOCUMENT_EMBEDDINGS : "embeds to"
    
    RESTAURANTS {
        uuid id PK
        string name
        string api_key
    }
    MENU_ITEMS {
        uuid id PK
        uuid restaurant_id FK
        uuid category_id FK
        string name
        decimal price
    }
    DOCUMENT_EMBEDDINGS {
        uuid id PK
        uuid restaurant_id FK
        vector embedding
        text category
    }
```

**Core Tables**: `restaurants`, `restaurant_phone_mappings`, `categories`, `menu_items`, `modifiers`, `menu_item_modifiers`, `operating_hours`, `delivery_zones`, `document_embeddings`, `call_history`

**Indexes**: Restaurant-scoped indexes, HNSW vector index, composite indexes

**RLS**: All tables with policies (Service Role: full access, Authenticated: read, Anonymous: none)

## Security

### Authentication

```mermaid
graph LR
    A[Request] --> B{Request Type}
    B -->|Frontend| C[JWT Token]
    B -->|Webhook| D[X-Vapi-Secret]
    C --> E[Supabase Auth]
    D --> F[Secret Validation]
    
    style C fill:#10b981
    style D fill:#f59e0b
```

- **Frontend**: JWT tokens from Supabase Auth
- **Webhooks**: X-Vapi-Secret header validation

### Authorization & Protection

- **Tenant Isolation**: All queries filter by `restaurant_id`
- **RLS Policies**: Database-level access control
- **Rate Limiting**: Per-user and per-endpoint
- **Request Validation**: Size limits, format validation
- **Security Headers**: CSP, HSTS, X-Frame-Options

## Error Handling

### Exception Hierarchy

| Exception | Status Code |
|-----------|-------------|
| `NotFoundError` | 404 |
| `AuthenticationError` | 401 |
| `ValidationError` | 400 |
| `VapiAPIError` | 502 |
| `RestaurantVoiceAssistantError` | 500 |

### Error Tracking

Sentry integration with request ID tracking and user context from JWT.

## Performance Optimizations

**Backend**: Async operations, connection pooling, background tasks, caching

**Frontend**: Code splitting, lazy loading, React Query caching, optimistic updates

**Database**: Strategic indexes, HNSW vector index, connection pooling, query optimization

## Deployment

| Service | Platform | Details |
|---------|----------|---------|
| Backend | Railway | Python 3.12, Uvicorn, `/api/health` endpoint |
| Frontend | Vercel | Vite build, CDN assets, client-side routing |
| Database | Supabase | PostgreSQL + pgvector, SQL migrations, daily backups |

## Monitoring & Observability

**Error Tracking**: Sentry with stack traces, user context, request context, environment tagging

**Logging**: Structured JSON logs with request IDs, log levels (DEBUG/INFO/WARNING/ERROR)

**Health Checks**: Backend `/api/health` (DB connectivity), Frontend (Vercel status), Database (Supabase status)

## Future Enhancements

1. Real-time updates via WebSocket for live call monitoring
2. Analytics dashboard with call analytics and query patterns
3. Multi-language support for voice assistant
4. Order integration with POS systems
5. Advanced analytics: intent analysis, sentiment
6. A/B testing for prompts and responses
7. Custom voices per restaurant
