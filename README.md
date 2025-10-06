# Legal Intel Dashboard

A production-grade legal document intelligence platform built with FastAPI, Next.js, and AI-powered analysis.

## Features

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
- Automatic UI updates via WebSocket push

### Production-Ready Architecture
- **Performance**: Redis caching, connection pooling, request deduplication
- **Reliability**: Rate limiting, health checks, structured logging
- **Scalability**: Horizontal scaling support, Celery workers
- **Observability**: Prometheus metrics, Sentry error tracking, Flower monitoring

## 🏗️ Architecture

### Backend (FastAPI)
- Async PostgreSQL with pgvector for vector search
- Celery with Redis for background tasks
- **WebSocket + Redis Pub/Sub**: Real-time updates (3-6x more efficient than polling)
- LangChain integration for LLM orchestration
- Production middleware: rate limiting, caching, logging

### Frontend (Next.js + React)
- TypeScript with strict type checking
- **WebSocket Integration**: Instant document status updates
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

- **Dashboard**: http://localhost:3000 (redirects to login)
- **API Docs**: http://localhost:8000/api/v1/docs
- **API Health**: http://localhost:8000/api/v1/monitoring/health
- **Celery Monitor**: http://localhost:5555

### 4. Login with Test User

The application includes a pre-configured test user:

**Login Credentials:**
- **Email**: `test@example.com`
- **Password**: `testpassword123`

**Login Process:**
1. Navigate to http://localhost:3000
2. You'll be automatically redirected to the login page
3. Enter the test credentials above
4. Click "Sign in" to access the dashboard

**Note**: The test user is created automatically when the backend starts up.

## 📚 Documentation

- [Setup Guide](SETUP_GUIDE.md) - Detailed installation and configuration
- [WebSocket Efficiency Analysis](WEBSOCKET_EFFICIENCY_ANALYSIS.md) - Real-time updates performance deep-dive
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

#### Backend Tests

The backend includes comprehensive pytest tests for API endpoints, authentication, and document processing.

```bash
# Run all tests
docker-compose exec backend pytest

# Run tests with coverage report
docker-compose exec backend pytest --cov=app --cov-report=html

# Run tests with verbose output
docker-compose exec backend pytest -v

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run specific test function
docker-compose exec backend pytest tests/test_auth.py::test_login

# Run tests matching a pattern
docker-compose exec backend pytest -k "auth"

# Run tests in parallel (faster)
docker-compose exec backend pytest -n auto
```

**Coverage Report**: After running with `--cov-report=html`, open `backend/htmlcov/index.html` in your browser.

#### Frontend Tests

The frontend uses Jest and React Testing Library for component and integration tests.

```bash
# Run all tests (inside Docker)
docker-compose exec frontend npm test

# Run tests in watch mode (for development)
docker-compose exec frontend npm run test:watch

# Run tests with coverage report
docker-compose exec frontend npm run test:coverage

# Run tests locally (outside Docker)
cd frontend
npm install  # First time only
npm test
```

**Test Files**: All test files follow the pattern `*.test.tsx` or `*.test.ts`

**Coverage Report**: After running with coverage, open `frontend/coverage/lcov-report/index.html` in your browser.

#### Running Tests Locally (Without Docker)

**Backend:**
```bash
cd backend

# Create virtual environment (first time only)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/legal_intel_test"
export REDIS_URL="redis://localhost:6379/1"

# Run tests
pytest
```

**Frontend:**
```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

#### Test Configuration

- **Backend**: Configuration in `backend/pytest.ini`
- **Frontend**: Configuration in `frontend/jest.config.js`
- **Jest Setup**: `frontend/jest.setup.js` (includes testing-library/jest-dom)

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

### Real-Time Updates: WebSocket vs Polling

**We chose WebSocket for maximum efficiency:**

| Metric | Polling | WebSocket | Improvement |
|--------|---------|-----------|-------------|
| Network requests | 6 per doc | 1 + 2 events | **3x less** |
| Update latency | 0-5s | <100ms | **25x faster** |
| Database queries | 6 per doc | 1 per doc | **6x fewer** |
| Bandwidth (100 users) | 600KB | 200KB | **3x less** |

**For 1000+ concurrent users:** WebSocket scales linearly while polling creates exponential load.

See [WEBSOCKET_EFFICIENCY_ANALYSIS.md](WEBSOCKET_EFFICIENCY_ANALYSIS.md) for detailed benchmarks.

### Optimizations Included

- **Backend**:
  - **WebSocket + Redis Pub/Sub**: Real-time push notifications
  - Connection pooling (10 connections, 20 overflow)
  - Redis caching with TTL
  - Rate limiting (100 requests/minute)
  - Async database operations
  - Celery task queues

- **Frontend**:
  - **WebSocket Auto-Reconnection**: Zero-config real-time updates
  - React Query caching
  - Request deduplication
  - Debounced inputs
  - Code splitting
  - Image optimization

### Expected Performance

- Document upload: < 1s (file save)
- Status update (WebSocket): < 100ms
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
