# Flask Production Application - Architecture Specification

**Version:** 1.0.0  
**Last Updated:** 2025-01-09  
**Status:** Design Phase  
**Target Deployment:** Dokploy Platform

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Component Specifications](#component-specifications)
6. [Security Architecture](#security-architecture)
7. [Database Design](#database-design)
8. [API Design](#api-design)
9. [Deployment Architecture](#deployment-architecture)
10. [Monitoring & Observability](#monitoring--observability)
11. [Performance Considerations](#performance-considerations)
12. [Development Workflow](#development-workflow)

---

## Executive Summary

### Purpose

This document defines the complete architecture for a production-ready Flask application designed for deployment via Dokploy. The application implements enterprise-grade features including comprehensive security, monitoring, scalability, and maintainability.

### Key Objectives

- ✅ Production-ready deployment with zero-downtime updates
- ✅ Enterprise security (CORS, CSP, HSTS, rate limiting, JWT auth)
- ✅ High availability with health checks and graceful degradation
- ✅ Comprehensive monitoring and observability
- ✅ Scalable architecture supporting horizontal scaling
- ✅ Developer-friendly with clear separation of concerns

### Target Audience

- DevOps Engineers
- Backend Developers
- Security Engineers
- System Architects

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Dokploy Platform                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              GitHub Webhook Integration                 │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Docker Compose Stack                       │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │    Nginx     │───▶│  Flask App   │───▶│  PostgreSQL  │ │
│  │ Reverse Proxy│    │  (Gunicorn)  │    │   Database   │ │
│  │  Port 80/443 │    │  Port 8000   │    │  Port 5432   │ │
│  └──────────────┘    └──────┬───────┘    └──────────────┘ │
│                              │                               │
│                              ▼                               │
│                      ┌──────────────┐                       │
│                      │    Redis     │                       │
│                      │ Cache/Queue  │                       │
│                      │  Port 6379   │                       │
│                      └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              External Services (Optional)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Prometheus  │  │    Sentry    │  │  CloudWatch  │     │
│  │   Metrics    │  │Error Tracking│  │   Logging    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. Client Request
   ↓
2. Nginx (SSL Termination, Rate Limiting, Static Files)
   ↓
3. Gunicorn (Load Balancing across Workers)
   ↓
4. Flask Application
   ├─→ Middleware Stack (Security, Logging, Auth)
   ├─→ Route Handler
   ├─→ Business Logic
   ├─→ Database (PostgreSQL)
   └─→ Cache (Redis)
   ↓
5. Response (JSON/HTML)
   ↓
6. Client
```

---

## Technology Stack

### Core Framework

| Component | Version | Purpose             |
| --------- | ------- | ------------------- |
| Python    | 3.11+   | Runtime environment |
| Flask     | 3.0.0   | Web framework       |
| Gunicorn  | 21.2.0  | WSGI HTTP server    |
| Gevent    | 23.9.1  | Async worker class  |

### Database & ORM

| Component        | Version   | Purpose              |
| ---------------- | --------- | -------------------- |
| PostgreSQL       | 15-alpine | Primary database     |
| SQLAlchemy       | 2.0.23    | ORM                  |
| Alembic          | 1.12.1    | Database migrations  |
| psycopg2-binary  | 2.9.9     | PostgreSQL adapter   |
| Flask-SQLAlchemy | 3.1.1     | Flask integration    |
| Flask-Migrate    | 4.0.5     | Migration management |

### Caching & Sessions

| Component     | Version  | Purpose               |
| ------------- | -------- | --------------------- |
| Redis         | 7-alpine | Cache & session store |
| redis-py      | 5.0.1    | Redis client          |
| Flask-Limiter | 3.5.0    | Rate limiting         |

### Security

| Component          | Version | Purpose              |
| ------------------ | ------- | -------------------- |
| Flask-CORS         | 4.0.0   | CORS handling        |
| Flask-JWT-Extended | 4.5.3   | JWT authentication   |
| bcrypt             | 4.1.1   | Password hashing     |
| cryptography       | 41.0.7  | Encryption utilities |

### Validation & Serialization

| Component       | Version | Purpose           |
| --------------- | ------- | ----------------- |
| marshmallow     | 3.20.1  | Schema validation |
| email-validator | 2.1.0   | Email validation  |

### Monitoring & Logging

| Component                 | Version | Purpose            |
| ------------------------- | ------- | ------------------ |
| prometheus-flask-exporter | 0.23.0  | Metrics export     |
| python-json-logger        | 2.0.7   | Structured logging |
| sentry-sdk                | 1.38.0  | Error tracking     |

### Infrastructure

| Component      | Version     | Purpose          |
| -------------- | ----------- | ---------------- |
| Docker         | 24.0+       | Containerization |
| Docker Compose | 2.20+       | Orchestration    |
| Nginx          | 1.25-alpine | Reverse proxy    |

---

## Project Structure

```
flask-production-app/
│
├── app/                                 # Application package
│   ├── __init__.py                     # Application factory
│   ├── main.py                         # Main Flask app entry point
│   ├── models.py                       # SQLAlchemy models
│   ├── schemas.py                      # Marshmallow schemas
│   │
│   ├── routes/                         # Route blueprints
│   │   ├── __init__.py
│   │   ├── api.py                      # API endpoints
│   │   ├── health.py                   # Health checks
│   │   └── auth.py                     # Authentication
│   │
│   ├── middleware/                     # Middleware components
│   │   ├── __init__.py
│   │   ├── error_handler.py            # Exception handling
│   │   ├── security.py                 # Security headers
│   │   ├── request_logger.py           # Request logging
│   │   └── rate_limiter.py             # Rate limiting
│   │
│   ├── utils/                          # Utility modules
│   │   ├── __init__.py
│   │   ├── validators.py               # Input validation
│   │   ├── decorators.py               # Custom decorators
│   │   ├── db_utils.py                 # Database helpers
│   │   └── cache_utils.py              # Cache helpers
│   │
│   └── config/                         # Configuration
│       ├── __init__.py
│       ├── config.py                   # Config classes
│       └── logging_config.py           # Logging setup
│
├── migrations/                         # Alembic migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── [migration_files].py
│
├── scripts/                            # Utility scripts
│   ├── init_db.py                      # Database initialization
│   ├── entrypoint.sh                   # Container entrypoint
│   └── healthcheck.sh                  # Health check script
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_api.py                     # API tests
│   ├── test_auth.py                    # Auth tests
│   ├── test_models.py                  # Model tests
│   └── test_middleware.py              # Middleware tests
│
├── nginx/                              # Nginx configuration
│   └── nginx.conf                      # Nginx config file
│
├── .github/                            # GitHub configuration
│   └── workflows/
│       └── deploy.yml                  # CI/CD pipeline
│
├── logs/                               # Application logs (gitignored)
├── static/                             # Static files
├── media/                              # User uploads (gitignored)
│
├── Dockerfile                          # Multi-stage build
├── docker-compose.yml                  # Service orchestration
├── .dockerignore                       # Docker exclusions
├── .env.example                        # Environment template
├── .gitignore                          # Git exclusions
├── requirements.txt                    # Python dependencies
├── requirements-dev.txt                # Dev dependencies
├── gunicorn.conf.py                   # Gunicorn config
├── prometheus.yml                      # Metrics config
├── README.md                           # Project documentation
├── ARCHITECTURE.md                     # This file
├── DEPLOYMENT.md                       # Deployment guide
├── API.md                              # API documentation
├── SECURITY.md                         # Security policy
├── CONTRIBUTING.md                     # Contribution guide
└── LICENSE                             # License file
```

---

## Component Specifications

### 1. Flask Application (`app/main.py`)

**Purpose:** Main application entry point with all core features

**Key Features:**

- Application factory pattern
- Blueprint registration
- Middleware stack initialization
- Database connection management
- Error handling setup
- CORS configuration
- Security headers
- Health check endpoints

**Code Structure:**

```python
def create_app(config_name='production'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Setup middleware
    setup_error_handlers(app)
    setup_security_headers(app)
    setup_request_logging(app)

    # Setup monitoring
    setup_prometheus_metrics(app)

    return app
```

### 2. Health Check Endpoints (`app/routes/health.py`)

**Endpoints:**

#### `/health` - Liveness Probe

```json
{
  "status": "healthy",
  "timestamp": "2025-01-09T07:00:00Z",
  "version": "1.0.0",
  "service": "flask-production-app"
}
```

#### `/readiness` - Readiness Probe

```json
{
  "status": "ready",
  "timestamp": "2025-01-09T07:00:00Z",
  "checks": {
    "database": {
      "status": "connected",
      "latency_ms": 5
    },
    "redis": {
      "status": "connected",
      "latency_ms": 2
    },
    "disk_space": {
      "status": "ok",
      "available_gb": 45.2
    }
  }
}
```

### 3. Configuration System (`app/config/config.py`)

**Configuration Classes:**

```python
class BaseConfig:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = 'INFO'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class TestingConfig(BaseConfig):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### 4. Database Models (`app/models.py`)

**Base Model:**

```python
class BaseModel(db.Model):
    """Base model with common fields"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Serialize to dictionary"""
        pass
```

**User Model:**

```python
class User(BaseModel):
    """User model"""
    __tablename__ = 'users'

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref='users')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
```

### 5. Middleware Stack

#### Error Handler (`app/middleware/error_handler.py`)

```python
class APIException(Exception):
    """Base API exception"""
    status_code = 500
    message = "Internal server error"

class BadRequestException(APIException):
    status_code = 400
    message = "Bad request"

class UnauthorizedException(APIException):
    status_code = 401
    message = "Unauthorized"

@app.errorhandler(APIException)
def handle_api_exception(error):
    """Handle API exceptions"""
    response = {
        'error': error.__class__.__name__,
        'message': error.message,
        'status_code': error.status_code,
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': g.get('request_id')
    }
    return jsonify(response), error.status_code
```

#### Security Headers (`app/middleware/security.py`)

```python
@app.after_request
def set_security_headers(response):
    """Set security headers"""
    nonce = secrets.token_urlsafe(16)

    response.headers['Content-Security-Policy'] = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
        f"style-src 'self' 'unsafe-inline'; "
        f"img-src 'self' data: https:; "
        f"font-src 'self' data:; "
        f"connect-src 'self'; "
        f"frame-ancestors 'none';"
    )
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    return response
```

#### Request Logger (`app/middleware/request_logger.py`)

```python
@app.before_request
def log_request():
    """Log incoming request"""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

    logger.info('Incoming request', extra={
        'request_id': g.request_id,
        'method': request.method,
        'path': request.path,
        'ip': request.remote_addr,
        'user_agent': request.user_agent.string
    })

@app.after_request
def log_response(response):
    """Log outgoing response"""
    execution_time = time.time() - g.start_time

    logger.info('Outgoing response', extra={
        'request_id': g.request_id,
        'status_code': response.status_code,
        'execution_time_ms': round(execution_time * 1000, 2)
    })

    return response
```

---

## Security Architecture

### 1. Authentication & Authorization

**JWT-Based Authentication:**

```python
# Token structure
{
    "sub": "user_id",
    "username": "john_doe",
    "roles": ["user", "admin"],
    "exp": 1704844800,
    "iat": 1704758400,
    "jti": "unique_token_id"
}

# Access token: 1 hour expiry
# Refresh token: 30 days expiry
```

**Role-Based Access Control (RBAC):**

```python
@jwt_required()
@role_required(['admin'])
def admin_only_endpoint():
    """Admin-only endpoint"""
    pass

@jwt_required()
@permission_required(['read:users', 'write:users'])
def user_management_endpoint():
    """User management endpoint"""
    pass
```

### 2. Input Validation

**Marshmallow Schemas:**

```python
class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

    @validates('password')
    def validate_password(self, value):
        """Validate password strength"""
        if not re.search(r'[A-Z]', value):
            raise ValidationError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValidationError('Password must contain lowercase letter')
        if not re.search(r'\d', value):
            raise ValidationError('Password must contain digit')
```

### 3. Rate Limiting

**Configuration:**

```python
# Global rate limit
RATELIMIT_DEFAULT = "100 per hour"

# Per-endpoint limits
@limiter.limit("10 per minute")
@app.route('/api/v1/login', methods=['POST'])
def login():
    pass

@limiter.limit("1000 per hour")
@app.route('/api/v1/data', methods=['GET'])
def get_data():
    pass
```

### 4. Security Headers

| Header                    | Value                           | Purpose               |
| ------------------------- | ------------------------------- | --------------------- |
| Content-Security-Policy   | See middleware                  | Prevent XSS attacks   |
| Strict-Transport-Security | max-age=31536000                | Force HTTPS           |
| X-Frame-Options           | DENY                            | Prevent clickjacking  |
| X-Content-Type-Options    | nosniff                         | Prevent MIME sniffing |
| X-XSS-Protection          | 1; mode=block                   | XSS protection        |
| Referrer-Policy           | strict-origin-when-cross-origin | Control referrer info |

---

## Database Design

### Schema Overview

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    permissions JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-Role association
CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);
```

### Connection Pooling

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,              # Number of connections to maintain
    'max_overflow': 40,           # Additional connections when pool is full
    'pool_pre_ping': True,        # Verify connections before use
    'pool_recycle': 3600,         # Recycle connections after 1 hour
    'pool_timeout': 30,           # Timeout for getting connection
    'echo': False                 # Don't log SQL in production
}
```

### Migration Strategy

```bash
# Create migration
flask db migrate -m "Add users table"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade

# Show current revision
flask db current

# Show migration history
flask db history
```

---

## API Design

### RESTful Endpoints

#### Authentication

```
POST   /auth/register          # Register new user
POST   /auth/login             # Login and get tokens
POST   /auth/refresh           # Refresh access token
POST   /auth/logout            # Logout (invalidate token)
GET    /auth/me                # Get current user info
```

#### Users

```
GET    /api/v1/users           # List users (paginated)
GET    /api/v1/users/:id       # Get user by ID
POST   /api/v1/users           # Create user (admin)
PUT    /api/v1/users/:id       # Update user
DELETE /api/v1/users/:id       # Delete user (soft delete)
```

#### Health Checks

```
GET    /health                 # Liveness probe
GET    /readiness              # Readiness probe
GET    /metrics                # Prometheus metrics
```

### Response Format

**Success Response:**

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "message": "User retrieved successfully",
  "metadata": {
    "timestamp": "2025-01-09T07:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Response:**

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Password too short"]
    }
  },
  "metadata": {
    "timestamp": "2025-01-09T07:00:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Pagination

```json
{
    "status": "success",
    "data": [...],
    "pagination": {
        "page": 1,
        "per_page": 20,
        "total_pages": 5,
        "total_items": 100,
        "has_next": true,
        "has_prev": false
    }
}
```

---

## Deployment Architecture

### Docker Multi-Stage Build

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y build-essential libpq-dev
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
RUN apt-get update && apt-get install -y libpq5 curl && \
    rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
```

### Docker Compose Services

```yaml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=securepass
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/app/static:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5

# Worker recycling
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "flask_app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

# Preload app
preload_app = True
```

---

## Monitoring & Observability

### Prometheus Metrics

**Exposed Metrics:**

```
# Request metrics
http_requests_total{method="GET",endpoint="/api/v1/users",status="200"}
http_request_duration_seconds{method="GET",endpoint="/api/v1/users"}

# Database metrics
database_connections_active
database_connections_idle
database_query_duration_seconds

# Redis metrics
redis_commands_total
redis_cache_hits_total
redis_cache_misses_total

# Application metrics
app_errors_total{type="ValidationError"}
app_active_users
```

**Prometheus Configuration:**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: "flask_app"
    static_configs:
      - targets: ["web:8000"]
    metrics_path: "/metrics"
```

### Structured Logging

**Log Format (JSON):**

```json
{
  "timestamp": "2025-01-09T07:00:00.123Z",
  "level": "INFO",
  "logger": "app.routes.api",
  "message": "User created successfully",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": 123,
  "ip_address": "192.168.1.1",
  "execution_time_ms": 45.2,
  "extra": {
    "username": "john_doe",
    "action": "user_creation"
  }
}
```

### Error Tracking (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv('FLASK_ENV', 'production'),
    release=os.getenv('APP_VERSION', '1.0.0')
)
```

---

## Performance Considerations

### Database Optimization

1. **Connection Pooling:** 20 base connections, 40 overflow
2. **Query Optimization:** Use indexes, avoid N+1 queries
3. **Lazy Loading:** Use `lazy='dynamic'` for large relationships
4. **Bulk Operations:** Use `bulk_insert_mappings()` for batch inserts

### Caching Strategy

```python
# Cache decorator
@cache.cached(timeout=300, key_prefix='user_list')
def get_users():
    return User.query.all()

# Cache invalidation
@cache.delete('user_list')
def create_user(data):
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    return user
```

### Rate Limiting

```python
# Global limit
RATELIMIT_DEFAULT = "100 per hour"

# Storage
RATELIMIT_STORAGE_URL = "redis://redis:6379/1"

# Key function (user-based)
def get_rate_limit_key():
    if current_user.is_authenticated:
        return f"user:{current_user.id}"
    return f"ip:{request.remote_addr}"
```

### Async Operations

```python
# Background tasks with Celery
@celery.task
def send_email(user_id, subject, body):
    user = User.query.get(user_id)
    # Send email logic
    pass

# Call async
send_email.delay(user.id, "Welcome", "Welcome to our app!")
```

---

## Development Workflow

### Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/flask-production-app.git
cd flask-production-app

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Setup environment
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
python scripts/init_db.py

# 6. Run migrations
flask db upgrade

# 7. Run development server
flask run --debug
```

### Docker Development

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Execute commands in container
docker-compose exec web flask db upgrade

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Code Quality

```bash
# Linting
flake8 app/

# Formatting
black app/

# Type checking
mypy app/

# Security scanning
bandit -r app/
safety check
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Deploy to Dokploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=app
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security checks
        run: |
          pip install bandit safety
          bandit -r app/
          safety check

  deploy:
    needs: [test, security]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Dokploy deployment
        run: |
          curl -X POST ${{ secrets.DOKPLOY_WEBHOOK_URL }} \
            -H "Authorization: Bearer ${{ secrets.DOKPLOY_API_TOKEN }}"
```

---

## Appendix

### Environment Variables Reference

| Variable        | Required | Default    | Description                          |
| --------------- | -------- | ---------- | ------------------------------------ |
| DATABASE_URL    | Yes      | -          | PostgreSQL connection string         |
| REDIS_URL       | Yes      | -          | Redis connection string              |
| SECRET_KEY      | Yes      | -          | Flask secret key (64+ chars)         |
| JWT_SECRET_KEY  | Yes      | -          | JWT signing key                      |
| FLASK_ENV       | No       | production | Environment (development/production) |
| LOG_LEVEL       | No       | INFO       | Logging level                        |
| ALLOWED_ORIGINS | No       | \*         | CORS allowed origins                 |
| SENTRY_DSN      | No       | -          | Sentry error tracking DSN            |
| MAX_WORKERS     | No       | auto       | Gunicorn worker count                |
| WORKER_TIMEOUT  | No       | 120        | Worker timeout in seconds            |

### Useful Commands

```bash
# Database
flask db init                    # Initialize migrations
flask db migrate -m "message"    # Create migration
flask db upgrade                 # Apply migrations
flask db downgrade               # Rollback migration

# Shell
flask shell                      # Open Flask shell

# Routes
flask routes                     # List all routes

# Custom commands
flask init-db                    # Initialize database
flask create-admin               # Create admin user
```

### Troubleshooting

**Common Issues:**

1. **Database connection refused**

   - Check DATABASE_URL
   - Ensure PostgreSQL is running
   - Verify network connectivity

2. **Redis connection error**

   - Check REDIS_URL
   - Ensure Redis is running
   - Check firewall rules

3. **Permission denied**

   - Check file ownership
   - Verify user permissions
   - Check Docker user mapping

4. **Out of memory**
   - Reduce worker count
   - Increase container memory
   - Check for memory leaks

---

## Version History

| Version | Date       | Changes                            |
| ------- | ---------- | ---------------------------------- |
| 1.0.0   | 2025-01-09 | Initial architecture specification |

---

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)

---

**Document Status:** ✅ Ready for Implementation  
**Next Step:** Begin Phase 1 - Project Setup & Repository Structure
