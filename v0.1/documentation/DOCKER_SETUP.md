# Docker Setup for Global Server (GS1)

This Docker setup includes both the FastAPI application (gs1.py) and MySQL database.

## Prerequisites
- Docker installed (v20.10+)
- Docker Compose installed (v1.29+)

## Quick Start

### 1. Build and Run the Application

```bash
# Navigate to the project directory
cd global_server

# Start both services (MySQL + Application)
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 2. Access the Application

- **Web UI**: http://localhost:9000
- **API Endpoints**: http://localhost:9000/api/*
- **Health Check**: http://localhost:9000/health

### 3. Database Connection

The MySQL database is automatically initialized with the schema from `schema.sql`

**Connection Details:**
- Host: `localhost` (or `mysql_db` from within containers)
- Port: `3306`
- Username: `root`
- Password: `root`
- Database: `gs1`

## Docker Services

### MySQL Service (mysql_db)
- Image: `mysql:8.0`
- Container name: `gs1_mysql`
- Port: `3306`
- Volume: `mysql_data` (persists database)
- Auto-initializes with `schema.sql`

### Application Service (gs1_app)
- Built from: `Dockerfile` (Python 3.11)
- Container name: `gs1_app`
- Port: `9000`
- Auto-generates `config.json` with correct DB connection
- Waits for MySQL to be healthy before starting

## File Structure

```
global_server/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container orchestration
├── .dockerignore           # Exclude files from Docker build
├── requirements.txt        # Python dependencies
├── gs1.py                  # FastAPI application
├── index.html              # Frontend UI
├── config.json             # Auto-generated, DB configuration
├── schema.sql              # Database schema
└── CA_management/          # CA Service (optional)
```

## Common Commands

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f gs1_app
docker-compose logs -f mysql_db
```

### Stop services
```bash
docker-compose stop
```

### Remove containers (keep data)
```bash
docker-compose down
```

### Remove everything including data
```bash
docker-compose down -v
```

### Rebuild images
```bash
docker-compose build --no-cache
```

### Execute commands in container
```bash
# Access MySQL
docker exec -it gs1_mysql mysql -u root -proot gs1

# Access app shell
docker exec -it gs1_app sh
```

## Environment Variables

The application automatically creates `config.json` with these values:

```json
{
  "database": {
    "host": "mysql_db",
    "port": 3306,
    "username": "root",
    "password": "root",
    "database": "gs1"
  }
}
```

To customize, edit `docker-compose.yml` environment section.

## Network

Both services communicate on the `gs1_network` bridge network:
- Application connects to: `mysql_db:3306`
- External access to app: `localhost:9000`

## Troubleshooting

### Application won't start
```bash
# Check logs
docker-compose logs gs1_app

# Verify MySQL is healthy
docker-compose ps
```

### Connection refused error
- Wait 15 seconds for MySQL to initialize
- Check MySQL is running: `docker-compose ps`
- Verify network: `docker network inspect gs1_network`

### Database errors
```bash
# Reinitialize database
docker-compose down -v
docker-compose up --build
```

### Port already in use
- Change port in `docker-compose.yml`:
  ```yaml
  ports:
    - "9001:9000"  # Use 9001 instead
  ```

## Production Notes

For production deployment:

1. **Remove `--reload` flag** in docker-compose.yml
   ```yaml
   command: uvicorn gs1:app --host 0.0.0.0 --port 9000
   ```

2. **Change database credentials**
   - Update `docker-compose.yml` environment variables
   - Update `MYSQL_ROOT_PASSWORD`, `MYSQL_PASSWORD`

3. **Use environment secrets**
   - Create `.env` file
   - Reference in `docker-compose.yml`: `${MYSQL_PASSWORD}`

4. **Persistent volumes**
   - Database data persists in `mysql_data` volume
   - Use named volumes for production

5. **Security**
   - Change default passwords
   - Use `.env` for sensitive data
   - Restrict network access
   - Enable MySQL authentication plugin verification

## Development

To rebuild the image after changes:
```bash
docker-compose build --no-cache gs1_app
docker-compose up gs1_app
```

Or with only application rebuild (if dependencies haven't changed):
```bash
docker-compose up --build gs1_app
```
