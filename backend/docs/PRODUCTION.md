# Production Deployment Guide

Production deployment considerations and best practices for the Restaurant Voice Assistant backend.

## Prerequisites

- Production Supabase project
- Production OpenAI API key (with billing enabled)
- Production Vapi account
- Production Twilio account (for phone provisioning)
- Container hosting platform (Render, Railway, AWS, etc.)

## Environment Configuration

### Required Variables

Set all production environment variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=sk-proj-...
VAPI_API_KEY=your_vapi_key
VAPI_SECRET_KEY=your_webhook_secret
PUBLIC_BACKEND_URL=https://your-production-url.com
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=your_token
ENVIRONMENT=production
```

### Recommended Production Settings

```bash
# Security
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend.com,https://admin.your-frontend.com

# Performance
CACHE_TTL_SECONDS=300  # 5 minutes for production (reduces API calls)

# Embeddings (optional, defaults are fine)
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
```

## Deployment Considerations

### Database

- **Connection Pooling**: Supabase handles this automatically, but monitor connection limits
- **Migrations**: Run all migrations in order before deployment
- **Backups**: Enable Supabase automatic backups
- **Extensions**: Ensure `pgvector` and `postgis` are enabled

### Caching

- **Single Instance**: In-memory cache works fine
- **Multiple Instances**: Use Redis for shared caching:
  ```python
  # Consider replacing TTLCache with Redis
  # Prevents cache misses when load balancing across instances
  ```

### Background Tasks

- **Current**: FastAPI BackgroundTasks (per-instance)
- **Scaling**: For multiple instances, consider:
  - Celery with Redis broker
  - AWS SQS / Google Cloud Tasks
  - Ensures embedding generation works across all instances

### Webhook Reliability

- **Current**: 30-second delayed API fetch (thread-based)
- **Works**: Per-instance, sufficient for moderate traffic
- **Scale**: For high traffic, consider:
  - Queue-based retry mechanism
  - Scheduled job to fetch missing calls

## Monitoring

### Health Checks

Use `/api/health` endpoint for monitoring:

- Checks Supabase connectivity
- Checks OpenAI connectivity
- Checks Vapi connectivity
- Returns HTTP 503 if critical services down

### Logging

- **Development**: Full debug logs with request IDs
- **Production**: INFO level logs, request IDs included
- **Log Aggregation**: Use service like:
  - Datadog
  - LogRocket
  - CloudWatch (AWS)
  - Google Cloud Logging

### Key Metrics to Monitor

1. **API Response Times**: Should be < 500ms for most endpoints
2. **Embedding Generation**: Background task completion rate
3. **Cache Hit Rate**: Higher is better (reduces OpenAI costs)
4. **Call History Capture**: Ensure webhook fallback mechanism works
5. **Phone Assignment Success Rate**: Monitor failures

## Security Best Practices

1. **Environment Variables**: Never commit `.env` to version control
2. **Service Role Key**: Keep `SUPABASE_SERVICE_ROLE_KEY` secret (bypasses RLS)
3. **Vapi Secret**: Rotate `VAPI_SECRET_KEY` periodically
4. **CORS**: Restrict `CORS_ORIGINS` to specific domains (not `*`)
5. **Rate Limiting**: Consider adding rate limiting middleware
6. **HTTPS Only**: All production URLs must be HTTPS

## Performance Optimization

### Database

- **Indexes**: Already optimized, but monitor query performance
- **RLS Policies**: Efficient, but review if seeing slow queries
- **Connection Pooling**: Supabase handles automatically

### Caching

- **TTL**: Increase `CACHE_TTL_SECONDS` for production (reduces OpenAI API calls)
- **Redis**: Use for multi-instance deployments
- **Cache Warming**: Consider pre-generating embeddings for popular queries

### Embeddings

- **Background Generation**: Runs async, doesn't block API
- **Batch Processing**: Current implementation handles batches efficiently
- **Error Handling**: Failures logged but don't affect main requests

## Scaling Strategy

### Vertical Scaling

- Increase container resources (CPU, memory)
- Sufficient for moderate traffic (< 1000 requests/minute)

### Horizontal Scaling

- Run multiple backend instances behind load balancer
- **Considerations**:
  - In-memory cache won't be shared (use Redis)
  - Background tasks run per-instance (use Celery)
  - Database connection limits may be reached

### Database Scaling

- Supabase automatically scales PostgreSQL
- Monitor connection pool usage
- Consider read replicas for heavy read workloads

## Backup and Recovery

### Database Backups

- Supabase provides automatic daily backups
- Point-in-time recovery available (Supabase Pro plan)
- Test restore procedures regularly

### Application Data

- Restaurant data: Stored in Supabase (backed up)
- Call history: Stored in Supabase (backed up)
- Embeddings: Can be regenerated (stored in Supabase)

## Cost Optimization

### OpenAI Costs

- **Caching**: Increase `CACHE_TTL_SECONDS` to reduce API calls
- **Model**: `text-embedding-3-small` is cost-effective
- **Batch Generation**: Current implementation batches efficiently

### Vapi Costs

- **Shared Assistant**: Single assistant for all restaurants (cost-efficient)
- **Phone Numbers**: Twilio pricing applies per number

### Infrastructure Costs

- **Supabase**: Scales with usage
- **Container Hosting**: Choose platform based on traffic
- **Monitoring**: Many platforms include basic monitoring

## Troubleshooting

### High API Response Times

- Check database query performance
- Monitor embedding generation (background tasks)
- Consider increasing cache TTL
- Review Supabase connection pool usage

### Missing Call History

- Check webhook delivery (Vapi Dashboard)
- Verify 30-second fallback mechanism is working
- Check logs for API fetch errors
- Ensure `VAPI_API_KEY` has access to call data

### Embedding Generation Failures

- Check OpenAI API key and billing
- Review logs for specific errors
- Manually trigger via `/api/embeddings/generate`
- Verify restaurant data exists before generation

## Next Steps

- Set up monitoring and alerting
- Configure backups and recovery procedures
- Test load balancing (if using multiple instances)
- Review and optimize database queries
- Implement Redis for shared caching (if needed)
