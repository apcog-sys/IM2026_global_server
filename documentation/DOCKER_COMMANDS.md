# Docker Quick Commands Reference

## Initial Setup

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode (background)
docker-compose up -d --build

# Using quick start scripts
# Windows: docker-start.bat
# Linux/Mac: bash docker-start.sh
```

## View Status & Logs

```bash
# List all running containers
docker-compose ps

# View logs (all services)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f gs1_app
docker-compose logs -f mysql_db

# Last 100 lines
docker-compose logs --tail=100
```

## Stop & Start Services

```bash
# Stop all services (keeps containers)
docker-compose stop

# Start stopped services
docker-compose start

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart gs1_app

# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop and remove everything (delete data)
docker-compose down -v
```

## Database Access

```bash
# Access MySQL from host
mysql -h localhost -u root -proot gs1

# Execute MySQL command in container
docker exec gs1_mysql mysql -u root -proot gs1 -e "SHOW TABLES;"

# Access MySQL interactive shell
docker exec -it gs1_mysql mysql -u root -proot gs1

# Backup database
docker exec gs1_mysql mysqldump -u root -proot gs1 > backup.sql

# Restore database
docker exec -i gs1_mysql mysql -u root -proot gs1 < backup.sql
```

## Application Access

```bash
# Access application shell
docker exec -it gs1_app sh

# Run Python command in app
docker exec gs1_app python -c "import json; print(json.dumps({'test': 'ok'}))"

# View app config
docker exec gs1_app cat config.json
```

## Build & Update

```bash
# Rebuild without cache
docker-compose build --no-cache

# Rebuild specific service
docker-compose build --no-cache gs1_app

# Update only app (if no new dependencies)
docker-compose up gs1_app

# Update with new build
docker-compose up --build gs1_app
```

## Volume & Data Management

```bash
# List volumes
docker volume ls

# Inspect mysql_data volume
docker volume inspect global_server_mysql_data

# Remove unused volumes
docker volume prune

# Backup MySQL volume
docker run --rm -v global_server_mysql_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/mysql_backup.tar.gz -C /data .

# Restore MySQL volume
docker run --rm -v global_server_mysql_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/mysql_backup.tar.gz -C /data
```

## Network

```bash
# List networks
docker network ls

# Inspect gs1_network
docker network inspect global_server_gs1_network

# Test connectivity from app to mysql
docker exec gs1_app ping mysql_db
```

## Troubleshooting

```bash
# Check container stats (CPU, memory)
docker stats

# Inspect container details
docker inspect gs1_app
docker inspect gs1_mysql

# Check Docker daemon logs (Linux)
journalctl -u docker

# Verify MySQL health
docker-compose ps gs1_mysql

# Test application endpoint
curl http://localhost:9000/health

# Check if ports are in use
# Windows: netstat -ano | findstr :9000
# Linux: lsof -i :9000
```

## Production Deployment

```bash
# Use production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale gs1_app=2

# Update environment variables
docker-compose down
# Edit .env file
docker-compose up -d
```

## Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove all unused resources
docker system prune -a

# Full cleanup (keeps running containers)
docker system prune -f --volumes
```

## Health Checks

```bash
# Check app health
curl -s http://localhost:9000/health | head -c 100

# Check database health
docker exec gs1_mysql mysqladmin ping -u root -proot

# Wait for service
docker-compose up --wait

# Monitor service
watch docker-compose ps
```

## Tips

- Always backup MySQL data before `docker-compose down -v`
- Use `.env` file for production credentials (not in docker-compose.yml)
- Check `docker-compose.logs` if services fail to start
- MySQL takes 10-15 seconds to initialize; app waits with healthcheck
- For production, remove `--reload` flag from uvicorn command
- Use `docker-compose exec` instead of `docker exec` when not specific about container name
