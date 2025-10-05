# Legal Intel Dashboard

A production-grade legal document intelligence platform built with FastAPI, Next.js, and AI-powered analysis.

## 🚀 Features

### Document Management
- **Smart Upload**: Drag-and-drop interface for PDF and DOCX files
- **Async Processing**: Background processing with Celery for scalability
- **AI-Powered Extraction**: Automatic extraction of:
  - Parties and counterparties
  - Agreement dates and amounts
  - Governing law and jurisdiction
  - Document types and categories

### Natural Language Queries
- Ask questions about your documents in plain English
- Intelligent query understanding with fallback mechanisms
- Structured JSON results ready for export

### Real-time Dashboard
- Live statistics and key metrics
- Agreement type distribution charts
- Jurisdiction breakdown visualizations
- Document processing status tracking

### Production-Ready Architecture
- **Performance**: Redis caching, connection pooling, request deduplication
- **Reliability**: Rate limiting, health checks, structured logging
- **Scalability**: Horizontal scaling support, Celery workers
- **Observability**: Prometheus metrics, Sentry error tracking, Flower monitoring

## 🏗️ Architecture

### Backend (FastAPI)
- Async PostgreSQL with pgvector for vector search
- Celery with Redis for background tasks
- LangChain integration for LLM orchestration
- Production middleware: rate limiting, caching, logging

### Frontend (Next.js + React)
- TypeScript with strict type checking
- React Query for data fetching and caching
- Zustand for state management
- Recharts for data visualization
- Responsive design with Tailwind CSS

### Infrastructure
- Docker Compose for local development
- Nginx reverse proxy for production
- PostgreSQL 16 with pgvector extension
- Redis for caching and task queue

## 📋 Prerequisites

- Docker & Docker Compose (v3.8+)
- 8GB+ RAM available for Docker
- OpenAI and/or Anthropic API keys

## 🚀 Quick Start

### 1. Clone and Configure

```bash
cd legal_intel_dashboard

# Copy environment template
cp .env.example .env

# Add your API keys to .env
nano .env  # or use your preferred editor
```

Required API keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/

### 2. Start the Application

```bash
# Make script executable (first time only)
chmod +x run_containers.sh

# Start in development mode
./run_containers.sh

# Or for production mode
./run_containers.sh prod
```

### 3. Access the Application

- **Dashboard**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/v1/docs
- **API Health**: http://localhost:8000/api/v1/monitoring/health
- **Celery Monitor**: http://localhost:5555

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation and configuration
- [API Documentation](http://localhost:8000/api/v1/docs) - Interactive API docs (when running)

## 🛠️ Development

### Project Structure

```
.
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── api/      # REST endpoints
│   │   ├── core/     # Configuration & database
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   └── tasks/    # Celery tasks
│   └── requirements.txt
├── frontend/         # Next.js application
│   ├── src/
│   │   ├── api/     # API client
│   │   ├── app/     # Pages (App Router)
│   │   ├── components/ # React components
│   │   └── hooks/   # Custom hooks
│   └── package.json
└── docker-compose.yml
```

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Database Migrations

Migrations are handled automatically with Alembic autogenerate:

```bash
# Modify a model in backend/app/models/
# Then generate migration automatically
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Apply migrations (or just restart backend - runs automatically)
docker-compose exec backend alembic upgrade head

# View migration history
docker-compose exec backend alembic history
```

See [Backend Migrations Guide](backend/MIGRATIONS.md) for full documentation.

### Database Access

```bash
# PostgreSQL shell
docker-compose exec db psql -U postgres -d legal_intel
```

## 🔧 Configuration

### Environment Variables

Key variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `POSTGRES_PASSWORD` | Database password | postgres |
| `DEBUG` | Enable debug mode | true |
| `LOG_LEVEL` | Logging level | INFO |

### Scaling

The application supports horizontal scaling:

**Development:**
```yaml
# docker-compose.yml
backend:
  deploy:
    replicas: 2  # Multiple API servers

celery_worker:
  deploy:
    replicas: 3  # Multiple workers
```

**Production:**
Use `docker-compose.prod.yml` which includes:
- Load-balanced backend with Nginx
- Multiple Celery workers
- Optimized resource limits
- Prometheus metrics

## 🔍 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/monitoring/health

# Response format:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

### Metrics

Prometheus-compatible metrics at:
```
http://localhost:8000/api/v1/monitoring/metrics
```

### Celery Monitoring

Flower dashboard:
```
http://localhost:5555
```

View active tasks, worker status, and task history.

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using port 3000/8000
lsof -i :3000

# Change port in docker-compose.yml if needed
```

**Database connection errors:**
```bash
# Check database health
docker-compose ps db

# Restart database
docker-compose restart db
```

**Out of memory:**
- Increase Docker memory allocation (Docker Desktop → Settings → Resources)
- Reduce Celery concurrency in `docker-compose.yml`

**API key errors:**
- Verify keys are set in `.env`
- Ensure no extra spaces or quotes around keys
- Check keys are valid at provider dashboard

### Clean Reset

To completely reset (⚠️ deletes all data):

```bash
docker-compose down -v
docker-compose up -d
```

## 🔐 Security

- Default passwords are for development only
- API keys should be environment variables
- Use HTTPS in production (Nginx configuration included)
- Rate limiting enabled by default
- Input validation with Pydantic

## 📊 Performance

### Optimizations Included

- **Backend**:
  - Connection pooling (10 connections, 20 overflow)
  - Redis caching with TTL
  - Rate limiting (100 requests/minute)
  - Async database operations
  - Celery task queues

- **Frontend**:
  - React Query caching
  - Request deduplication
  - Debounced inputs
  - Code splitting
  - Image optimization

### Expected Performance

- Document upload: < 1s (file save)
- Metadata extraction: 10-30s (async)
- Query execution: 2-5s
- Dashboard load: < 500ms (cached)

## 🤝 Contributing

This project was built following production-grade best practices:

- Type safety with TypeScript/Pydantic
- Comprehensive error handling
- Structured logging
- Health checks and monitoring
- Scalable architecture
- Clean code organization

## 📝 License

Provided for evaluation purposes.

## 🎯 Key Technologies

- **Backend**: FastAPI, SQLAlchemy, Celery, LangChain
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16 with pgvector
- **Cache**: Redis 7
- **AI**: OpenAI GPT-4, Anthropic Claude
- **Deployment**: Docker, Docker Compose, Nginx
- **Monitoring**: Prometheus, Grafana, Sentry, Flower

---

Built with ❤️ for production environments
