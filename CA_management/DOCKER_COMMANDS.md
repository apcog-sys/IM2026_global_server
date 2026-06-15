# CA Service Docker Quick Commands

## Build CA Service Image Only

```bash
# From root directory
cd CA_management
docker build -t ca_service:latest .

# With tag and version
docker build -t ca_service:1.0.0 .
```

## Run CA Service Standalone

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

## With Docker Compose (Complete Stack)

```bash
# Start only CA Service
docker-compose up --build ca_service

# Start all services (GS1 + DB + CA)
docker-compose up --build

# Run in background
docker-compose up -d --build ca_service
```

## Access CA Service

```bash
# Health check
curl http://localhost:9002/health

# Get CA root certificate
curl http://localhost:9002/api/certificates/ca-root

# View logs
docker-compose logs -f ca_service

# Access container shell
docker exec -it ca_service sh
```

## Stop & Clean

```bash
# Stop CA service
docker-compose stop ca_service

# Restart CA service
docker-compose restart ca_service

# Remove CA service container
docker-compose rm ca_service

# Remove all (keep data)
docker-compose down

# Remove everything including data
docker-compose down -v
```

## Rebuild After Changes

```bash
# Rebuild CA image (no cache)
docker-compose build --no-cache ca_service

# Rebuild and restart
docker-compose up --build ca_service
```

## Check Image Size & Details

```bash
# List images
docker images | grep ca_service

# Inspect image
docker inspect ca_service:latest

# Image history
docker history ca_service:latest
```

## Environment Setup for CA Service

If running standalone (not with docker-compose), set these environment variables:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=root
export PYTHONPATH=/app

# Then run
docker run -d \
  -p 9002:9002 \
  -e MYSQL_HOST=$MYSQL_HOST \
  -e MYSQL_PORT=$MYSQL_PORT \
  -e MYSQL_USER=$MYSQL_USER \
  -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
  -v ca_pki_data:/app/CA_management/pki \
  ca_service:latest
```

## Network Modes

### Standalone with Host MySQL
```bash
docker run -d \
  --network host \
  -p 9002:9002 \
  -v ca_pki_data:/app/CA_management/pki \
  ca_service:latest
```

### With Docker Network
```bash
# Create custom network
docker network create ca_network

# Run CA and MySQL on network
docker run -d \
  --name mysql_for_ca \
  --network ca_network \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0

docker run -d \
  --name ca_service_container \
  --network ca_network \
  -p 9002:9002 \
  -e MYSQL_HOST=mysql_for_ca \
  -v ca_pki_data:/app/CA_management/pki \
  ca_service:latest
```

## Debugging

```bash
# Check if service is running
docker ps | grep ca_service

# Check service logs
docker logs ca_service

# Real-time logs
docker logs -f ca_service

# Install debugging tools
docker exec ca_service sh -c "apt-get update && apt-get install -y curl"

# Test MySQL connection from container
docker exec ca_service python -c "
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='mysql_db',
        user='root',
        password='root',
        database='gs1'
    )
    print('MySQL connection OK')
    conn.close()
except Exception as e:
    print(f'MySQL error: {e}')
"
```

## Volume Management

```bash
# List volumes
docker volume ls | grep ca

# Inspect CA PKI volume
docker volume inspect ca_service_ca_pki_data

# Backup volume
docker run --rm -v ca_pki_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/ca_pki_backup.tar.gz -C /data .

# Restore volume
docker run --rm -v ca_pki_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/ca_pki_backup.tar.gz -C /data

# Clean volume (delete data!)
docker volume rm ca_pki_data
```

## Performance & Resources

```bash
# Check container resource usage
docker stats ca_service

# Set resource limits
docker run -d \
  --name ca_service_container \
  --cpus 0.5 \
  --memory 512m \
  -p 9002:9002 \
  ca_service:latest

# View in docker-compose
docker-compose top ca_service
```

## Security

```bash
# Run as non-root user (requires Dockerfile modification)
docker run -d \
  --user 1000:1000 \
  -p 9002:9002 \
  ca_service:latest

# View security options
docker inspect ca_service --format='{{json .HostConfig.SecurityOpt}}'

# Run with read-only filesystem
docker run -d \
  --read-only \
  --tmpfs /tmp \
  -p 9002:9002 \
  ca_service:latest
```

## Compose Service-Specific Commands

```bash
# Scale CA service (if using swarm)
docker-compose up --scale ca_service=3

# Execute command in running service
docker-compose exec ca_service python --version

# Pause/unpause service
docker-compose pause ca_service
docker-compose unpause ca_service

# View service dependencies
docker-compose config | grep -A 10 ca_service
```

## Integration Testing

```bash
# Test CA → GS1 communication
docker-compose exec gs1_app curl http://ca_service:9002/health

# Test both services
curl http://localhost:9000/health
curl http://localhost:9002/health

# Generate certificate through CA
curl -X POST http://localhost:9002/api/certificates/generate-auth \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "TEST_SERVER",
    "server_name": "Test Server",
    "organization": "Test Org",
    "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
    "certificate_type": "auth"
  }'
```
