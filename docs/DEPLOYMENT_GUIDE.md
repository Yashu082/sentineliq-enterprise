# SentinelIQ Enterprise - Deployment Guide

## Deployment Options

### 1. Docker Deployment (Recommended)

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Backend Dockerfile

The backend includes a Dockerfile for containerization:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend-fastapi
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - FRONTEND_ORIGIN=http://localhost:3000
      - LOG_LEVEL=INFO
    volumes:
      - ./backend-fastapi/sentineliq.db:/app/sentineliq.db
    restart: unless-stopped

  frontend:
    build: ./frontend-react
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

#### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Kubernetes Deployment

#### Prerequisites
- kubectl configured
- Kubernetes cluster (minikube, GKE, EKS, AKS)

#### Backend Deployment

Create `k8s/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentineliq-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentineliq-backend
  template:
    metadata:
      labels:
        app: sentineliq-backend
    spec:
      containers:
      - name: backend
        image: your-registry/sentineliq-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: sentineliq-secrets
              key: gemini-api-key
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: sentineliq-secrets
              key: groq-api-key
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: sentineliq-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sentineliq-backend-service
spec:
  selector:
    app: sentineliq-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Secrets Management

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sentineliq-secrets
type: Opaque
stringData:
  gemini-api-key: "your-gemini-api-key"
  groq-api-key: "your-groq-api-key"
  secret-key: "your-jwt-secret-key"
```

#### Deploy to Kubernetes

```bash
# Apply secrets
kubectl apply -f k8s/secrets.yaml

# Apply deployment
kubectl apply -f k8s/backend-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/sentineliq-backend
```

### 3. Cloud Platform Deployment

#### AWS Deployment

**EC2 Deployment**:
1. Launch EC2 instance (Ubuntu 22.04)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Run docker-compose

**Elastic Beanstalk**:
1. Create EB application
2. Use Docker platform
3. Deploy using EB CLI
4. Configure environment variables in EB console

#### Google Cloud Platform

**Cloud Run**:
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/sentineliq-backend

# Deploy to Cloud Run
gcloud run deploy sentineliq-backend \
  --image gcr.io/PROJECT-ID/sentineliq-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure Deployment

**Azure Container Instances**:
```bash
# Create resource group
az group create --name sentineliq-rg --location eastus

# Create container instance
az container create \
  --resource-group sentineliq-rg \
  --name sentineliq-backend \
  --image your-registry/sentineliq-backend:latest \
  --ports 8000 \
  --environment-variables GEMINI_API_KEY=$GEMINI_API_KEY
```

## Environment Configuration

### Production Environment Variables

```env
# API Keys (Required)
GEMINI_API_KEY=your_production_gemini_key
GROQ_API_KEY=your_production_groq_key

# Security (Required)
SECRET_KEY=your_strong_random_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS (Required)
FRONTEND_ORIGIN=https://your-frontend-domain.com

# Logging (Optional)
LOG_LEVEL=INFO

# Database (Optional - for PostgreSQL migration)
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Security Best Practices

1. **Never commit `.env` files** to version control
2. **Use strong secrets** (minimum 32 characters for JWT secret)
3. **Rotate API keys** regularly
4. **Use secret management** (AWS Secrets Manager, Azure Key Vault, etc.)
5. **Enable HTTPS** in production
6. **Configure firewall rules** to restrict access
7. **Regular security audits** of dependencies

## Database Migration (SQLite to PostgreSQL)

### Why Migrate?

- Better concurrency support
- Horizontal scaling capability
- Better performance for large datasets
- Built-in replication and backup
- Advanced features (JSON, full-text search)

### Migration Steps

1. **Set up PostgreSQL instance**
   - Cloud: AWS RDS, Google Cloud SQL, Azure Database
   - Self-hosted: Install PostgreSQL on server

2. **Update dependencies**
```bash
pip install psycopg2-binary sqlalchemy
```

3. **Update database manager** to use SQLAlchemy
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

4. **Migrate existing data**
```python
# Export from SQLite
sqlite3 sentineliq.db .dump > backup.sql

# Import to PostgreSQL
psql -U user -d dbname < backup.sql
```

5. **Update environment variables**
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

## Monitoring & Logging

### Structured Logging

Logs are output in JSON format for easy parsing:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "level": "INFO",
  "logger": "main",
  "message": "Request received",
  "module": "main",
  "function": "run_audit",
  "line": 42
}
```

### Log Aggregation

**ELK Stack**:
- Filebeat to ship logs
- Logstash to parse logs
- Elasticsearch to store logs
- Kibana to visualize logs

**CloudWatch** (AWS):
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Metrics Collection

**Prometheus + Grafana**:
1. Add Prometheus metrics to FastAPI
2. Deploy Prometheus server
3. Configure Grafana dashboards

## Health Checks

### Health Endpoint

The `/health` endpoint returns component status:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "components": {
    "database": "healthy",
    "llm_primary": "configured",
    "llm_failover": "configured"
  }
}
```

### Load Balancer Configuration

Configure health checks in your load balancer:

- **Path**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Healthy Threshold**: 2
- **Unhealthy Threshold**: 3

## Backup Strategy

### Database Backups

**SQLite**:
```bash
# Simple file copy
cp sentineliq.db sentineliq.db.backup

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp sentineliq.db /backups/sentineliq_$DATE.db
find /backups -name "sentineliq_*.db" -mtime +7 -delete
```

**PostgreSQL**:
```bash
# pg_dump
pg_dump -U user dbname > backup.sql

# Automated with cron
0 2 * * * pg_dump -U user dbname > /backups/db_$(date +\%Y\%m\%d).sql
```

### Disaster Recovery

1. **Regular backups** (daily for production)
2. **Off-site storage** (S3, Glacier, etc.)
3. **Restore testing** (monthly)
4. **Documentation** (keep this guide updated)

## Performance Tuning

### Backend Optimization

1. **Increase worker count**:
```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

2. **Enable Gunicorn**:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Add caching layer** (Redis):
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

### Frontend Optimization

1. **Build for production**:
```bash
npm run build
```

2. **Serve static files** via CDN
3. **Enable gzip compression**
4. **Implement browser caching**

## Scaling Strategy

### Horizontal Scaling

1. **Deploy multiple backend instances**
2. **Use load balancer** (Nginx, HAProxy, AWS ALB)
3. **Shared database** (PostgreSQL)
4. **Shared session store** (Redis)

### Vertical Scaling

1. **Increase CPU cores**
2. **Add more RAM**
3. **Use SSD storage**
4. **Optimize database queries**

## Troubleshooting

### Common Deployment Issues

**Container won't start**:
- Check logs: `docker logs <container-id>`
- Verify environment variables
- Check port conflicts

**Database connection errors**:
- Verify database is running
- Check connection string
- Ensure network connectivity

**LLM API failures**:
- Verify API keys are valid
- Check rate limits
- Review failover logs

**High memory usage**:
- Monitor with `docker stats`
- Increase memory limits
- Check for memory leaks

## CI/CD Pipeline

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      run: |
        docker build -t your-registry/sentineliq-backend:${{ github.sha }} ./backend-fastapi
        docker push your-registry/sentineliq-backend:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/sentineliq-backend backend=your-registry/sentineliq-backend:${{ github.sha }}
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] Strong secrets configured
- [ ] API keys stored securely
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Database backups enabled
- [ ] Logging enabled
- [ ] Monitoring configured
- [ ] Dependencies updated regularly
