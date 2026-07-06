# CA Service Docker Setup

This Dockerfile creates a Docker image for the CA Service (Certificate Authority) that runs independently on port 9002.

## Files Required

The Docker build uses these CA management files:
```
CA_management/
├── Dockerfile                    # Docker image definition
├── requirements.txt              # Python dependencies
├── ca_service.py                # Main CA service
├── certificate_manager.py        # Certificate management
├── ca_authority.py              # PKI authority implementation
├── __init__.py
├── pki/
│   ├── certs/                   # Generated certificates storage
│   └── keys/                    # Private keys storage
└── documents/                   # Documentation
```

## Build & Run

### Build CA Service Image Only
```bash
cd CA_management
docker build -t ca_service:latest .
```

### Run CA Service Container Alone
```bash
# Requires MySQL running on localhost:3306
docker run -d \
  --name ca_service_container \
  -p 9002:9002 \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_PORT=3306 \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=root \
  -v ca_pki_data:/app/CA_management/pki \
  ca_service:latest
```

### Run with Docker Compose (Complete Stack)
```bash
# From root directory
docker-compose up --build ca_service

# Or start all services
docker-compose up --build
```

## Services

When using docker-compose, both services are available:

- **GS1 Application**: http://localhost:9000
  - Port: 9000
  - Container: gs1_app

- **CA Service**: http://localhost:9002
  - Port: 9002
  - Container: ca_service

- **MySQL Database**: localhost:3306
  - Container: gs1_mysql
  - User: root / Password: root

## Network Communication

Services communicate via bridge network `gs1_network`:
- CA Service → MySQL: `mysql_db:3306`
- GS1 App → CA Service: `ca_service:9002`
- GS1 App → MySQL: `mysql_db:3306`

## Dependencies

### Python Packages
- `fastapi==0.104.1` - Web framework
- `uvicorn==0.24.0` - ASGI server
- `pydantic==2.5.0` - Data validation
- `cryptography==41.0.7` - PKI operations
- `mysql-connector-python==8.2.0` - Database access
- `requests==2.31.0` - HTTP client

### System Packages
- `gcc` - C compiler for cryptography module compilation

## Volumes

### ca_pki_data
Persists PKI data across container restarts:
- Generated certificates in `certs/`
- Private keys in `keys/`
- Certificate metadata

Mount path: `/app/CA_management/pki`

## Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `MYSQL_HOST` | `mysql_db` | Database server |
| `MYSQL_PORT` | `3306` | Database port |
| `MYSQL_USER` | `root` | Database user |
| `MYSQL_PASSWORD` | `root` | Database password |
| `PYTHONPATH` | `/app` | Python module path |
| `PYTHONDONTWRITEBYTECODE` | `1` | Skip .pyc generation |
| `PYTHONUNBUFFERED` | `1` | Unbuffered output |

## Health Check

The Dockerfile includes a health check that:
- Runs every 30 seconds
- Queries the `/health` endpoint
- Has 3 retry attempts
- Timeout: 10 seconds

Check health status:
```bash
docker inspect --format='{{json .State.Health}}' ca_service
```

## Useful Commands

### View CA Service Logs
```bash
docker-compose logs -f ca_service
```

### Access CA Service Shell
```bash
docker exec -it ca_service sh
```

### Check CA Service Health
```bash
curl http://localhost:9002/health
```

### Rebuild CA Service Image
```bash
docker-compose build --no-cache ca_service
```

### Restart CA Service Only
```bash
docker-compose restart ca_service
```

### Stop CA Service
```bash
docker-compose stop ca_service
```

### Remove CA Service Container
```bash
docker-compose rm ca_service
```

## Certificate Directory Structure

Inside the container `/app/CA_management/pki/`:

```
pki/
├── certs/
│   ├── ca-root.crt           # CA root certificate
│   ├── server_auth_*.crt     # Server authentication certs
│   └── server_sign_*.crt     # Server signing certs
└── keys/
    ├── ca-root.key           # CA private key
    ├── server_auth_*.key     # Server auth private keys
    └── server_sign_*.key     # Server sign private keys
```

## API Endpoints

Once running, access these endpoints:

```
POST /api/certificates/generate-auth        - Generate AUTH certificate
POST /api/certificates/generate-sign        - Generate SIGN certificate
POST /api/certificates/generate-both        - Generate both certificates
POST /api/certificates/sign-csr              - Sign a CSR
GET  /api/certificates/ca-root               - Download CA root certificate
GET  /api/certificates/{server_id}/chain     - Get certificate chain
GET  /api/certificates/{cert_id}             - Get certificate details
GET  /api/certificates/server/{server_id}    - Get all server certificates
GET  /health                                 - Health check
```

## Troubleshooting

### CA Service fails to start
```bash
# Check logs
docker-compose logs ca_service

# Verify MySQL connection
docker exec ca_service python -c "import mysql.connector; print('MySQL OK')"
```

### Certificate files not persisting
```bash
# Verify volume is mounted
docker inspect ca_service | grep -A 5 Mounts

# Check volume contents
docker volume inspect ca_service_ca_pki_data
```

### Connection refused to MySQL
```bash
# Wait longer for MySQL to initialize
docker-compose up ca_service
# It will retry until MySQL is healthy
```

### Port 9002 already in use
Edit `docker-compose.yml` to use a different port:
```yaml
ca_service:
  ports:
    - "9003:9002"  # Use external port 9003
```

## Production Considerations

1. **Remove `--reload` flag** in production (auto-reload is enabled in dev)
2. **Use secrets manager** for database credentials
3. **Enable HTTPS/TLS** between services
4. **Persist PKI data** in production-grade storage
5. **Use `.env` file** for configuration
6. **Set resource limits** (CPU, memory)
7. **Enable logging aggregation**
8. **Run security scans** on images

Example production compose section:
```yaml
ca_service:
  image: ca_service:1.0.0
  # ... other config
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.25'
        memory: 256M
```

## Integration with GS1 App

The CA Service is automatically integrated when using docker-compose:

1. GS1 app calls CA endpoints at: `http://ca_service:9002/api/...`
2. Both services connect to same MySQL database
3. Certificates generated by CA are stored and used by GS1
4. All services are on the same `gs1_network`

Test integration:
```bash
# From within gs1_app container
docker exec gs1_app curl http://ca_service:9002/health
```

## Development vs Production

### Development (Default)
- Auto-reload enabled
- Hot-reloading of changes
- Verbose logging
- Containers restart on definition change

### Production
- No auto-reload
- Minimal logging
- Security hardening
- Proper error handling
- Resource constraints
- Separate network policies
