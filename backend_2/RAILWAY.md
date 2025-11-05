# Railway deployment configuration and documentation

## Railway Deployment

This application is configured for deployment on Railway.app using Docker.

### Files

- `Dockerfile`: Docker configuration for building the application
- `docker-compose.yml`: Local development with Docker Compose
- `railway.json`: Railway configuration file (uses Dockerfile)
- `.dockerignore`: Files excluded from Docker build context
- `requirements.txt`: Python dependencies

### Environment Variables

Set these in Railway dashboard under Variables:

**Required:**

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_PUBLISHABLE_KEY`: Supabase publishable key (for reads, respects RLS)
- `SUPABASE_SECRET_KEY`: Supabase secret key (for writes, bypasses RLS)
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `VAPI_SECRET_KEY`: Vapi webhook secret (for webhook authentication)
- `VAPI_API_KEY`: Vapi API key (for Vapi resource management)
- `PUBLIC_BACKEND_URL`: Public URL of this backend (e.g., https://your-app.railway.app)

**Optional:**

- `ENVIRONMENT`: Set to "production" for production, "development" enables hot-reload (default: "development")
- `PORT`: Railway sets this automatically (don't override)
- `CACHE_TTL_SECONDS`: Cache TTL in seconds (default: 60)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- `EMBEDDING_DIMENSIONS`: Embedding vector dimensions (default: 1536)
- `CORS_ORIGINS`: CORS allowed origins, comma-separated (default: "\*")
- `TWILIO_ACCOUNT_SID`: Twilio account SID (optional, for phone provisioning)
- `TWILIO_AUTH_TOKEN`: Twilio auth token (optional, for phone provisioning)

### Deployment Steps

1. **Create Railway Project:**

   - Go to https://railway.app
   - Create a new project
   - Connect your GitHub repository (or deploy from CLI)

2. **Set Environment Variables:**

   - Go to your service → Variables
   - Add all required environment variables listed above

3. **Deploy:**

   - Railway will detect Dockerfile and build the Docker image
   - The Dockerfile handles all dependencies and startup
   - The app will be available at the Railway-provided URL

4. **Update PUBLIC_BACKEND_URL:**
   - After first deployment, get your Railway URL
   - Update `PUBLIC_BACKEND_URL` variable with your Railway URL
   - Redeploy if needed

### Health Check

Railway will automatically check `/api/health` endpoint for health monitoring.

### Hot-Reload Mode

The Dockerfile supports hot-reload when `ENVIRONMENT=development`:

- Enables `--reload` flag for uvicorn
- Automatically restarts server when code changes are detected
- Useful for rapid iteration during development
- **Note**: Railway rebuilds Docker images on git push, so reload helps with file changes within the container

### Notes

- Railway sets `PORT` automatically - Dockerfile uses `${PORT:-8000}`
- The app binds to `0.0.0.0` to accept external connections
- Railway provides HTTPS automatically
- Logs are available in Railway dashboard
- Docker build includes all Python dependencies and system tools
- The Dockerfile installs PostgreSQL client for database connectivity
- Hot-reload enabled when `ENVIRONMENT=development` (useful for development/testing)

### Local Development with Docker

You can test locally using Docker Compose:

```bash
docker-compose up
```

This will:

- Build the Docker image
- Start the API on port 8000
- Enable hot-reload for development
- Mount local code directories for live updates
