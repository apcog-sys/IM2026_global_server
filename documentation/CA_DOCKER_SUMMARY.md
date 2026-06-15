# CA Service Docker Implementation Summary

## Files Created

### In CA_management/ directory:

1. **Dockerfile** ✅
   - Builds Python 3.11 image with CA service
   - Installs cryptography and FastAPI dependencies
   - Exposes port 9002
   - Runs ca_service.py on startup
   - Includes health checks

2. **requirements.txt** ✅
   - fastapi, uvicorn, pydantic
   - mysql-connector-python, cryptography
   - requests, python-multipart

3. **DOCKER_README.md** ✅
   - Comprehensive documentation
   - Setup instructions
   - Troubleshooting guide
   - Production considerations

4. **.dockerignore** ✅
   - Excludes unnecessary files from build
   - Keeps image lightweight

5. **DOCKER_COMMANDS.md** ✅
   - Quick reference for common commands
   - Build, run, debug instructions
   - Integration testing examples

### In root directory (updated):

6. **docker-compose.yml** ✅
   - Added `ca_service` service
   - Connects to MySQL
   - Network integration with GS1 app
   - Persistent PKI volume: `ca_pki_data`

7. **docker-start.sh** (updated) ✅
   - Added CA service access points
   - Updated logging commands

8. **docker-start.bat** (updated) ✅
   - Windows version with CA service info

## Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Compose Network              │
│           (gs1_network bridge)              │
│                                             │
│  ┌──────────────┐    ┌──────────────┐     │
│  │  GS1 App     │    │  CA Service  │     │
│  │ (9000)       │←→  │  (9002)      │     │
│  │ gs1_app      │    │  ca_service  │     │
│  └──────────────┘    └──────────────┘     │
│         ↓                    ↓             │
│  ┌────────────────────────────────────┐   │
│  │      MySQL Database                │   │
│  │   gs1_mysql (3306)                 │   │
│  │   Database: gs1                    │   │
│  │   User: root / root                │   │
│  └────────────────────────────────────┘   │
│         ↓                    ↓             │
│  ┌──────────────────────────────────────┐ │
│  │      Volume: mysql_data              │ │
│  │      Volume: ca_pki_data             │ │
│  └──────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Services

### GS1 Application Service
- **Container**: gs1_app
- **Port**: 9000
- **Image**: Built from root Dockerfile
- **Depends on**: MySQL (healthy)
- **Volume**: Current directory mounted at /app

### CA Service
- **Container**: ca_service
- **Port**: 9002
- **Image**: Built from CA_management/Dockerfile
- **Depends on**: MySQL (healthy)
- **Volumes**: 
  - Current directory at /app
  - ca_pki_data at /app/CA_management/pki

### MySQL Database
- **Container**: gs1_mysql
- **Port**: 3306
- **Image**: mysql:8.0
- **Root Password**: root
- **Database**: gs1
- **Volume**: mysql_data (persistent)

## How to Use

### Quick Start (All Services)
```bash
# Run from root directory
docker-compose up --build
```

### Start Only CA Service
```bash
# With all dependencies
docker-compose up --build ca_service
```

### Build CA Service Image Only
```bash
cd CA_management
docker build -t ca_service:latest .
```

### Run CA Service Standalone
```bash
docker run -d \
  --name ca_service \
  -p 9002:9002 \
  -e MYSQL_HOST=host.docker.internal \
  -v ca_pki_data:/app/CA_management/pki \
  ca_service:latest
```

## Access Points

Once running:

| Service | URL | Port | Container |
|---------|-----|------|-----------|
| GS1 Web UI | http://localhost:9000 | 9000 | gs1_app |
| GS1 API | http://localhost:9000/api | 9000 | gs1_app |
| CA Service | http://localhost:9002 | 9002 | ca_service |
| CA API | http://localhost:9002/api | 9002 | ca_service |
| MySQL | localhost:3306 | 3306 | gs1_mysql |

## CA Service Endpoints

```
POST /api/certificates/generate-auth        Generate AUTH certificate
POST /api/certificates/generate-sign        Generate SIGN certificate
POST /api/certificates/generate-both        Generate both certificates
POST /api/certificates/sign-csr              Sign a CSR
GET  /api/certificates/ca-root               Download CA root cert
GET  /api/certificates/{server_id}/chain     Get certificate chain
GET  /api/certificates/{cert_id}             Get certificate details
GET  /api/certificates/server/{server_id}    Get all server certificates
GET  /health                                 Health check
```

## File Organization

```
global_server/
├─ Dockerfile                    # GS1 app image
├─ docker-compose.yml            # Multi-container orchestration
├─ docker-start.sh               # Linux/Mac startup script
├─ docker-start.bat              # Windows startup script
├─ .dockerignore                 # Files to exclude from build
├─ requirements.txt              # GS1 dependencies
├─ gs1.py                        # FastAPI application
├─ index.html                    # Frontend
├─ config.json                   # Auto-generated DB config
│
├─ CA_management/
│  ├─ Dockerfile                 # CA service image ✨ NEW
│  ├─ requirements.txt            # CA dependencies ✨ NEW
│  ├─ .dockerignore               # CA ignore rules ✨ NEW
│  ├─ DOCKER_README.md            # CA Docker docs ✨ NEW
│  ├─ DOCKER_COMMANDS.md          # CA Docker commands ✨ NEW
│  ├─ ca_service.py              # FastAPI CA service
│  ├─ certificate_manager.py      # Certificate management
│  ├─ ca_authority.py            # PKI implementation
│  ├─ __init__.py
│  │
│  ├─ pki/
│  │  ├─ certs/                  # Generated certificates
│  │  └─ keys/                   # Private keys
│  │
│  └─ documents/                 # Documentation
│
└─ Other files...
```

## Commands Reference

### Start Services
```bash
# All services
docker-compose up --build

# Only CA service
docker-compose up --build ca_service

# View logs
docker-compose logs -f ca_service
```

### Stop Services
```bash
# Stop
docker-compose stop ca_service

# Stop all
docker-compose stop

# Remove containers (keep data)
docker-compose down

# Remove everything (delete data)
docker-compose down -v
```

### Access Container
```bash
# Shell access
docker exec -it ca_service sh

# Run command
docker exec ca_service python --version

# View logs
docker logs ca_service
docker logs -f ca_service
```

### Health Checks
```bash
# CA Service health
curl http://localhost:9002/health

# GS1 health
curl http://localhost:9000/health

# MySQL health
docker exec gs1_mysql mysqladmin ping -u root -proot
```

## Integration Points

### GS1 App → CA Service
GS1 calls CA at: `http://ca_service:9002/api/certificates/*`

Example from gs1.py:
```python
ca_service_url = "http://ca_service:9002/api/certificates"
ca_response = requests.post(endpoint, json=payload, timeout=10)
```

### Both → MySQL Database
Both services connect to: `mysql_db:3306`
- User: root
- Password: root
- Database: gs1

## Volumes

### mysql_data
- **Path**: /var/lib/mysql
- **Purpose**: Persists MySQL data
- **Persists across**: Container restarts, docker-compose down

### ca_pki_data
- **Path**: /app/CA_management/pki
- **Contains**: 
  - certs/ (Generated certificates)
  - keys/ (Private keys)
- **Purpose**: Persists PKI infrastructure
- **Persists across**: Container restarts, docker-compose down

## Network

All services on bridge network: **gs1_network**

Service-to-service communication:
- GS1 → CA: `http://ca_service:9002`
- CA → MySQL: `mysql_db:3306`
- GS1 → MySQL: `mysql_db:3306`

External access:
- GS1: `http://localhost:9000`
- CA: `http://localhost:9002`
- MySQL: `localhost:3306`

## Dependencies

### Python Packages
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **cryptography**: PKI/TLS operations
- **mysql-connector-python**: Database access
- **requests**: HTTP client

### System Packages
- **python:3.11-slim**: Base image
- **gcc**: C compiler for cryptography

## Environment Variables

| Variable | CA Value | GS1 Value | Purpose |
|----------|----------|-----------|---------|
| MYSQL_HOST | mysql_db | mysql_db | Database host |
| MYSQL_PORT | 3306 | 3306 | Database port |
| MYSQL_USER | root | root | Database user |
| MYSQL_PASSWORD | root | root | Database password |
| PYTHONPATH | /app | - | Python module path |

## Health Checks

**CA Service Health Check:**
- Endpoint: GET /health
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3 before unhealthy

Check status:
```bash
docker inspect ca_service --format='{{json .State.Health}}'
```

## Troubleshooting

### CA Service won't start
```bash
# Check logs
docker-compose logs ca_service

# Verify MySQL is ready
docker-compose logs mysql_db

# Manually test MySQL
docker exec -it gs1_mysql mysql -u root -proot -e "SELECT 1"
```

### Port 9002 already in use
Edit docker-compose.yml:
```yaml
ca_service:
  ports:
    - "9003:9002"  # Use 9003 externally
```

### Certificate generation fails
```bash
# Check permissions
docker exec ca_service ls -la /app/CA_management/pki/

# Verify volume mount
docker inspect ca_service | grep -A 5 Mounts
```

### Connection between services fails
```bash
# Test GS1 → CA connectivity
docker exec gs1_app curl http://ca_service:9002/health

# Test CA → MySQL connectivity
docker exec ca_service python -c "import mysql.connector; print('OK')"
```

## Production Deployment

For production:

1. **Update passwords** in docker-compose.yml
2. **Use .env file** for secrets
3. **Remove --reload** for production FastAPI
4. **Set resource limits**
5. **Enable HTTPS/TLS** between services
6. **Use production-grade secrets management**
7. **Enable logging aggregation**
8. **Regular backups** of volumes
9. **Security scanning** of images
10. **Monitoring and alerting**

## Next Steps

1. ✅ Docker setup complete
2. Test local: `docker-compose up --build`
3. Access at http://localhost:9000 and http://localhost:9002
4. Test CA endpoints: `curl http://localhost:9002/health`
5. Generate certificates through CA
6. Verify integration with GS1 app
7. Prepare for production deployment

## Support Files

- **DOCKER_SETUP.md** - Complete Docker documentation
- **DOCKER_COMMANDS.md** - Quick reference commands
- **CA_management/DOCKER_README.md** - CA-specific documentation
- **CA_management/DOCKER_COMMANDS.md** - CA command reference
