# Legal Intel Dashboard - Complete Setup Guide

**Production-Grade Installation & Configuration**

This guide provides step-by-step instructions for setting up the Legal Intel Dashboard for development and production environments.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [API Keys Configuration](#api-keys-configuration)
4. [Installation](#installation)
5. [Running the Application](#running-the-application)
6. [Verification & Testing](#verification--testing)
7. [Advanced Configuration](#advanced-configuration)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 2 cores
- RAM: 8 GB
- Disk: 10 GB free space
- OS: macOS, Linux, or Windows with WSL2

**Recommended:**
- CPU: 4+ cores
- RAM: 16 GB
- Disk: 20 GB free space
- SSD storage

### Required Software

#### 1. Docker Desktop

**macOS:**
```bash
# Download from: https://www.docker.com/products/docker-desktop/
# Or install via Homebrew:
brew install --cask docker

# Verify installation
docker --version  # Should be 20.10.0 or higher
docker-compose --version  # Should be 2.0.0 or higher
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

**Windows:**
```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop/

# Enable WSL2 backend (recommended)
# Follow: https://docs.docker.com/desktop/windows/wsl/
```

#### 2. Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# Windows
# Download from: https://git-scm.com/download/win

# Verify
git --version
```

#### 3. Optional Tools

**For database management:**
```bash
# TablePlus (recommended)
# Download from: https://tableplus.com/

# Or pgAdmin
# Download from: https://www.pgadmin.org/download/
```

**For API testing:**
```bash
# Postman
# Download from: https://www.postman.com/downloads/

# Or HTTPie
pip install httpie
```

---

## Environment Setup

### 1. Clone the Repository

```bash
# Navigate to your projects directory
cd ~/Documents  # or your preferred location

# Clone the repository (if using git)
git clone <repository-url> legal_intel_dashboard
cd legal_intel_dashboard

# Or if you have the files already
cd legal_intel_dashboard
```

### 2. Configure Docker Resources

Docker needs sufficient resources to run all services.

**Docker Desktop (macOS/Windows):**

1. Open Docker Desktop
2. Go to **Settings/Preferences** → **Resources**
3. Configure:
   - **CPUs**: 4 (minimum 2)
   - **Memory**: 8 GB (minimum 6 GB)
   - **Swap**: 2 GB
   - **Disk image size**: 60 GB
4. Click **Apply & Restart**

**Docker on Linux:**

Resources are managed by the system. Ensure your machine has:
- At least 8 GB RAM available
- At least 20 GB disk space in `/var/lib/docker`

### 3. Create Environment File

```bash
# Copy the environment template
cp .env.example .env

# Or create manually if template doesn't exist
touch .env
```

---

## API Keys Configuration

The application requires API keys from OpenAI and/or Anthropic for AI-powered features.

### Option 1: OpenAI (Recommended)

**Get API Key:**

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-...`)
5. ⚠️ **Save it immediately** - you won't be able to see it again

**Add to .env:**

```bash
# Open .env file
nano .env  # or use your preferred editor

# Add the key
OPENAI_API_KEY=sk-your-actual-key-here
```

**Pricing (as of 2024):**
- GPT-4o-mini: ~$0.15 per 1M tokens (very affordable)
- Expected cost: $1-5 per 100 documents

### Option 2: Anthropic Claude

**Get API Key:**

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new key
5. Copy the key

**Add to .env:**

```bash
ANTHROPIC_API_KEY=your-anthropic-key-here
```

**Pricing:**
- Claude 3.5 Sonnet: ~$3 per 1M input tokens
- Expected cost: $2-8 per 100 documents

### Complete Environment Configuration

Edit your `.env` file with all required variables:

```bash
# =============================================================================
# Legal Intel Dashboard - Environment Configuration
# =============================================================================

# -----------------------------------------------------------------------------
# AI Provider API Keys (at least one required)
# -----------------------------------------------------------------------------
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here  # Optional

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=legal_intel
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Connection string (constructed from above)
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@db:5432/legal_intel

# -----------------------------------------------------------------------------
# Redis Configuration
# -----------------------------------------------------------------------------
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# -----------------------------------------------------------------------------
# Celery Configuration
# -----------------------------------------------------------------------------
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
DEBUG=true
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-change-in-production-use-openssl-rand-hex-32

# Database connection pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# -----------------------------------------------------------------------------
# Frontend Configuration
# -----------------------------------------------------------------------------
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# -----------------------------------------------------------------------------
# Monitoring & Error Tracking (Optional)
# -----------------------------------------------------------------------------
# SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
# SENTRY_ENVIRONMENT=development

# -----------------------------------------------------------------------------
# Security (Production)
# -----------------------------------------------------------------------------
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# -----------------------------------------------------------------------------
# Email Configuration (Optional)
# -----------------------------------------------------------------------------
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# EMAIL_FROM=noreply@yourdomain.com
```

### Security Best Practices

**⚠️ Important:**

1. **Never commit `.env` to git:**
   ```bash
   # .gitignore should already include:
   .env
   .env.local
   .env.*.local
   ```

2. **Generate strong secret key:**
   ```bash
   # On macOS/Linux
   openssl rand -hex 32
   
   # Then use the output as SECRET_KEY in .env
   ```

3. **Production passwords:**
   - Change default PostgreSQL password
   - Use strong, unique passwords
   - Store secrets in a vault (AWS Secrets Manager, HashiCorp Vault, etc.)

---

## Installation

### 1. Make Scripts Executable

```bash
# Make the run script executable
chmod +x run_containers.sh

# Verify
ls -la run_containers.sh
# Should show: -rwxr-xr-x ... run_containers.sh
```

### 2. Build Docker Images

This step downloads all dependencies and builds the application images.

```bash
# Build all images (first time or after code changes)
docker-compose build

# Or use the run script (it builds automatically)
./run_containers.sh
```

**Expected output:**
```
[+] Building 120.5s (34/34) FINISHED
 => [backend internal] load build definition from Dockerfile
 => [frontend internal] load build definition from Dockerfile
 => [db internal] load build definition from Dockerfile
 ...
Successfully built 12a34b56c78d
Successfully tagged legal_intel_dashboard_backend:latest
Successfully tagged legal_intel_dashboard_frontend:latest
```

**Build time:** 3-10 minutes (depending on internet speed)

### 3. Initialize Database

The database is initialized automatically on first run, but you can verify:

```bash
# Start only the database first (optional)
docker-compose up -d db

# Wait for database to be ready
docker-compose exec db pg_isready -U postgres

# Expected output:
# /var/run/postgresql:5432 - accepting connections
```

---

## Running the Application

### Development Mode

**Start all services:**

```bash
./run_containers.sh
```

**What happens:**
1. ✅ Starts PostgreSQL database
2. ✅ Starts Redis cache
3. ✅ Runs database migrations automatically
4. ✅ Creates test user (ID: 1, Email: test@example.com)
5. ✅ Starts FastAPI backend with hot reload
6. ✅ Starts Celery worker for background tasks
7. ✅ Starts Celery Flower for monitoring
8. ✅ Starts Next.js frontend with hot reload

**Expected output:**
```
✅ Starting Legal Intel Dashboard in dev mode...

Creating network "legal_intel_network"...
Creating volume "postgres_data"...
Creating volume "redis_data"...

Starting services:
✓ PostgreSQL database (port 5432)
✓ Redis cache (port 6379)
✓ Backend API (port 8000)
✓ Celery worker
✓ Celery Flower (port 5555)
✓ Frontend (port 3000)

⏳ Waiting for services to be ready...
✓ Database is healthy
✓ Redis is healthy
✓ Backend is healthy

🚀 Application is ready!

Access points:
  📊 Dashboard:     http://localhost:3000
  🔧 API Docs:      http://localhost:8000/api/v1/docs
  ❤️  Health Check:  http://localhost:8000/api/v1/monitoring/health
  🌺 Celery Monitor: http://localhost:5555

Test User:
  📧 Email:    test@example.com
  🔑 Password: testpassword123 (if auth is enabled)

View logs:
  docker-compose logs -f backend
  docker-compose logs -f frontend
  docker-compose logs -f celery_worker

Press Ctrl+C to stop all services
```

### Production Mode

**Start in production mode:**

```bash
./run_containers.sh prod
```

**Differences from development:**
- Uses `docker-compose.prod.yml`
- Optimized builds (multi-stage Docker)
- Multiple backend workers (4 processes)
- Multiple Celery workers (3 workers)
- Nginx reverse proxy with caching
- No hot reload (for stability)
- Production-grade logging
- Resource limits enforced

### Service Status

**Check all services:**

```bash
docker-compose ps
```

**Expected output:**
```
NAME                     STATUS              PORTS
legal_intel_backend      Up 2 minutes        0.0.0.0:8000->8000/tcp
legal_intel_frontend     Up 2 minutes        0.0.0.0:3000->3000/tcp
legal_intel_db           Up 2 minutes        0.0.0.0:5432->5432/tcp
legal_intel_redis        Up 2 minutes        0.0.0.0:6379->6379/tcp
legal_intel_celery       Up 2 minutes        
legal_intel_flower       Up 2 minutes        0.0.0.0:5555->5555/tcp
```

All services should show **"Up"** status.

---

## Verification & Testing

### 1. Health Checks

**Backend API:**
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-10-05T12:00:00Z",
  "checks": {
    "database": "ok",
    "redis": "ok"
  }
}
```

**Frontend:**
```bash
curl http://localhost:3000
```

Should return HTML (200 OK).

### 2. Database Connection

**Connect to PostgreSQL:**
```bash
docker-compose exec db psql -U postgres -d legal_intel
```

**Verify tables:**
```sql
\dt

-- Expected output:
--  public | alembic_version      | table | postgres
--  public | document_chunks      | table | postgres
--  public | document_metadata    | table | postgres
--  public | documents            | table | postgres
--  public | queries              | table | postgres
--  public | users                | table | postgres
```

**Check test user:**
```sql
SELECT id, email, full_name FROM users;

-- Expected output:
--  id |       email       | full_name
-- ----+-------------------+-----------
--   1 | test@example.com  | Test User
```

**Exit:**
```sql
\q
```

### 3. API Documentation

Open in browser:
```
http://localhost:8000/api/v1/docs
```

You should see an interactive Swagger UI with all API endpoints.

**Test an endpoint:**
1. Click on **GET /api/v1/documents**
2. Click **"Try it out"**
3. Enter `user_id: 1`
4. Click **"Execute"**
5. Should return `200 OK` with empty list `[]`

### 4. Upload Test Document

**Using the UI:**

1. Go to http://localhost:3000
2. Navigate to **Upload** page
3. Drag and drop a PDF or DOCX file
4. Wait for processing (10-30 seconds)
5. Check dashboard for updated statistics

**Using API (curl):**

```bash
# Upload a test document
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test_documents/01_nda_abudhabi_tech.docx" \
  -F "user_id=1"
```

**Expected response:**
```json
{
  "total": 1,
  "successful": 1,
  "failed": 0,
  "documents": [
    {
      "document_id": 1,
      "filename": "01_nda_abudhabi_tech.docx",
      "status": "processing",
      "message": "Document uploaded successfully and queued for processing"
    }
  ]
}
```

### 5. Check Celery Processing

**View Flower dashboard:**
```
http://localhost:5555
```

You should see:
- Active workers: 1
- Processed tasks: 1+
- Task details and status

**Check logs:**
```bash
docker-compose logs -f celery_worker
```

Look for:
```
✅ Document processed successfully: <document_id>
✅ Generated X embeddings for document
```

---

## Advanced Configuration

### Custom Ports

If default ports are in use, modify `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3001:3000"  # Change from 3000 to 3001
  
  backend:
    ports:
      - "8001:8000"  # Change from 8000 to 8001
```

Update frontend environment:
```bash
# In .env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

### Scaling Workers

**Increase Celery workers:**

```yaml
# docker-compose.yml
services:
  celery_worker:
    deploy:
      replicas: 3  # Run 3 worker processes
```

**Or scale manually:**
```bash
docker-compose up -d --scale celery_worker=3
```

### Database Backups

**Manual backup:**
```bash
# Create backup
docker-compose exec db pg_dump -U postgres legal_intel > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
docker-compose exec -T db psql -U postgres legal_intel < backup_20241005_120000.sql
```

**Automated backups:**

Add to crontab:
```bash
# Backup daily at 2 AM
0 2 * * * cd /path/to/legal_intel_dashboard && docker-compose exec -T db pg_dump -U postgres legal_intel > backups/backup_$(date +\%Y\%m\%d).sql
```

### Custom Middleware

Add custom middleware by editing:
- Backend: `backend/app/main.py`
- Frontend: `frontend/middleware.ts`

### Environment-Specific Configs

Create separate env files:

```bash
.env.development
.env.staging
.env.production
```

Load specific config:
```bash
docker-compose --env-file .env.production up -d
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Configure CORS_ORIGINS
- [ ] Set up SSL/TLS certificates
- [ ] Enable Sentry error tracking
- [ ] Configure email service
- [ ] Set up database backups
- [ ] Configure firewall rules
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Test all endpoints
- [ ] Review logs for errors
- [ ] Load test the application

### Docker Swarm Deployment

**Initialize swarm:**
```bash
docker swarm init
```

**Deploy stack:**
```bash
docker stack deploy -c docker-compose.prod.yml legal_intel
```

**Monitor services:**
```bash
docker service ls
docker service logs legal_intel_backend
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests (if available) or create:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-intel-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: legal_intel_backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

### Cloud Deployment

**AWS:**
- Use ECS/Fargate for containers
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for file storage
- CloudWatch for logging

**GCP:**
- Use Cloud Run or GKE
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Storage for files
- Cloud Logging

**Azure:**
- Use Container Instances or AKS
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Blob Storage for files
- Azure Monitor

---

## Troubleshooting

### Issue: Ports Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:3000: bind: address already in use
```

**Solution:**
```bash
# Find what's using the port
lsof -i :3000

# Kill the process
kill -9 <PID>

# Or change the port in docker-compose.yml
```

### Issue: Database Connection Failed

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Check database is running:**
   ```bash
   docker-compose ps db
   ```

2. **Restart database:**
   ```bash
   docker-compose restart db
   ```

3. **Check logs:**
   ```bash
   docker-compose logs db
   ```

4. **Verify credentials in .env:**
   ```bash
   cat .env | grep POSTGRES
   ```

### Issue: Frontend Not Loading

**Error:** `502 Bad Gateway` or blank page

**Solutions:**

1. **Check frontend logs:**
   ```bash
   docker-compose logs frontend
   ```

2. **Rebuild frontend:**
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

3. **Clear browser cache:**
   - Press `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

4. **Check API URL:**
   ```bash
   # In .env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

### Issue: Celery Tasks Not Processing

**Error:** Documents stay in "processing" state

**Solutions:**

1. **Check Celery worker:**
   ```bash
   docker-compose ps celery_worker
   docker-compose logs celery_worker
   ```

2. **Restart worker:**
   ```bash
   docker-compose restart celery_worker
   ```

3. **Check Redis connection:**
   ```bash
   docker-compose exec redis redis-cli ping
   # Should return: PONG
   ```

4. **View Flower dashboard:**
   ```
   http://localhost:5555
   ```

### Issue: Out of Memory

**Error:** Container crashes or system slow

**Solutions:**

1. **Increase Docker memory:**
   - Docker Desktop → Settings → Resources → Memory: 8-16 GB

2. **Reduce Celery concurrency:**
   ```yaml
   # docker-compose.yml
   celery_worker:
     command: celery -A app.core.celery_app worker --loglevel=info --concurrency=2
   ```

3. **Stop unused services:**
   ```bash
   docker-compose stop flower
   ```

### Issue: API Keys Not Working

**Error:** `OpenAI API error` or `Anthropic API error`

**Solutions:**

1. **Verify keys in .env:**
   ```bash
   cat .env | grep API_KEY
   ```

2. **Check for extra spaces:**
   ```bash
   # Bad:
   OPENAI_API_KEY= sk-your-key-here  # Space after =
   
   # Good:
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

4. **Test keys directly:**
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

### Issue: Migrations Failed

**Error:** `alembic.util.exc.CommandError`

**Solutions:**

1. **Check migration status:**
   ```bash
   docker-compose exec backend alembic history
   docker-compose exec backend alembic current
   ```

2. **Manually run migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **Reset database (⚠️ deletes all data):**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Issue: Can't Upload Documents

**Error:** `Foreign key constraint violation` or `500 Internal Server Error`

**Solutions:**

1. **Check test user exists:**
   ```bash
   docker-compose exec db psql -U postgres -d legal_intel -c "SELECT * FROM users WHERE id=1;"
   ```

2. **Create test user manually:**
   ```bash
   docker-compose exec backend python3 scripts/create_test_user.py
   ```

3. **Check backend logs:**
   ```bash
   docker-compose logs backend | grep ERROR
   ```

### Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   docker-compose logs > logs.txt
   ```

2. **System information:**
   ```bash
   docker version
   docker-compose version
   docker stats --no-stream
   ```

3. **Share error details:**
   - Full error message
   - Steps to reproduce
   - Environment (OS, Docker version)
   - Relevant logs

---

## Next Steps

After successful setup:

1. ✅ **Upload test documents** (provided in `test_documents/`)
2. ✅ **Try natural language queries** via the Query page
3. ✅ **Explore the dashboard** for insights
4. ✅ **Review API documentation** at `/api/v1/docs`
5. ✅ **Check monitoring** at Flower dashboard
6. ✅ **Review optional enhancements** in `OPTIONAL_ENHANCEMENTS_IMPLEMENTATION_GUIDE.md`

### Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **LangChain**: https://python.langchain.com/docs/
- **Docker**: https://docs.docker.com/
- **PostgreSQL**: https://www.postgresql.org/docs/

### Support

For technical issues or questions:
- Review the [README.md](README.md)
- Check the [Troubleshooting](#troubleshooting) section
- Review Docker logs
- Consult API documentation

---

**Setup Version**: 1.0  
**Last Updated**: October 5, 2025  
**Status**: Production Ready ✅

---

Built with ❤️ for production environments
