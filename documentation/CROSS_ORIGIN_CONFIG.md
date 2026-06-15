# Cross-Origin Configuration - Frontend to Global Server

## Architecture

```
┌──────────────────────────────────┐
│  Frontend Application (Port 8000) │
│  - Web UI                         │
│  - Form Handling                  │
│  - API Requests                   │
└────────────────┬──────────────────┘
                 │
         HTTP Requests
                 │
                 ▼
┌──────────────────────────────────┐
│  Global Server (Port 9000)        │
│  - FastAPI Backend                │
│  - Database Management            │
│  - Certificate Registration       │
│  - CORS Enabled                   │
└──────────────────────────────────┘
```

---

## Configuration Changes Made

### 1. CORS Middleware (gs1.py)

The Global Server on port 9000 is configured to accept requests from the Frontend on port 8000.

```python
# Add CORS middleware for cross-origin requests from frontend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",      # Frontend - localhost
        "http://127.0.0.1:8000",      # Frontend - loopback IP
        "http://localhost",            # Fallback
        "http://127.0.0.1",            # Fallback
        "*"                            # Wildcard (open)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

### 2. Response Handling

The `/api/security-servers/register` endpoint returns proper `JSONResponse`:

```python
@app.post("/api/security-servers/register")
async def register_security_server(registration: SecurityServerRegistration):
    # ... validation and database logic ...
    
    response_data = {
        "status": "success",
        "message": "Security server registered successfully with dual certificates",
        "registration": { ... },
        "certificates": { ... },
        "crt_files": { ... },
        "metadata": { ... }
    }
    
    return JSONResponse(status_code=200, content=response_data)
```

---

## Frontend API Calls

The frontend on port 8000 can now make API calls to the Global Server on port 9000:

### Example Request

```javascript
// Frontend on port 8000
const response = await fetch('/api/security-servers/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registrationData)
});
```

**Note**: The frontend uses relative paths (`/api/...`) which are resolved based on the current origin. When the frontend is served from port 8000, these requests would typically need the full URL. However, if both are on the same host, the relative paths work fine.

### For Separate Hosts/Machines

If the frontend and backend are on different machines, update the frontend URLs:

```javascript
// Example: Backend API on different machine
const API_BASE_URL = 'http://192.168.1.100:9000';

const response = await fetch(`${API_BASE_URL}/api/security-servers/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(registrationData)
});
```

---

## Supported API Endpoints

All these endpoints are accessible from the frontend on port 8000:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/init-db` | Initialize database tables |
| POST | `/api/test-connection` | Test database connection |
| POST | `/api/save-db-config` | Save database configuration |
| POST | `/api/security-servers/request-certificates` | Request dual certificates from CA |
| POST | `/api/security-servers/register` | Register security server with verified certs |
| GET | `/api/security-servers/registrations` | Get all registrations |
| GET | `/api/security-servers/{server_id}` | Get specific server details |
| PUT | `/api/security-servers/{server_id}` | Update server registration |
| DELETE | `/api/security-servers/{server_id}` | Delete server registration |
| POST | `/api/network-config` | Add network configuration |
| GET | `/api/network-config` | Get all network configs |
| PUT | `/api/network-config/{id}` | Update network config |
| DELETE | `/api/network-config/{id}` | Delete network config |
| POST | `/api/security-entities` | Create security entity |
| GET | `/api/security-entities` | Get all security entities |
| PUT | `/api/security-entities/{id}` | Update security entity |
| DELETE | `/api/security-entities/{id}` | Delete security entity |

---

## Testing the Configuration

### 1. Start Global Server (Port 9000)

```bash
# Terminal 1
cd c:\Users\Sahique\Desktop\new_workspace\2026\Information_mediator_v2\global_server
python gs1.py
```

**Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:9000
```

### 2. Start Frontend Application (Port 8000)

```bash
# Terminal 2
# Your frontend application on port 8000
# (Could be another Python/Node.js app, etc.)
```

### 3. Test the Connection

**From Browser Console (Frontend on port 8000)**:
```javascript
// Test CORS - should work now
fetch('http://localhost:9000/api/security-servers/registrations')
  .then(r => r.json())
  .then(data => console.log('Success:', data))
  .catch(e => console.log('Error:', e))
```

### 4. Test Registration Form

1. Open frontend application on `http://localhost:8000`
2. Navigate to "System Configuration" → "Global Server Configuration"
3. Fill in all required fields
4. Click "Register to Global Server"
5. You should receive a success message with certificate file information

---

## Pre-Configured Origins

The Global Server accepts requests from:

| Origin | Purpose |
|--------|---------|
| `http://localhost:8000` | Development frontend (named domain) |
| `http://127.0.0.1:8000` | Development frontend (loopback IP) |
| `http://localhost` | Fallback for port 80 |
| `http://127.0.0.1` | Fallback for port 80 |
| `*` | Wildcard (allows all origins) |

---

## Troubleshooting

### Issue: 404 Error on `/security-servers/register`

**Check**: Ensure the Global Server is running on port 9000

```bash
netstat -ano | findstr :9000
```

### Issue: CORS Error (No 'Access-Control-Allow-Origin' header)

**Check**: Verify frontend is making request to correct port
- Frontend: `http://localhost:8000`
- Backend API: `http://localhost:9000/api/...`

### Issue: Connection Refused

**Check**: 
1. Frontend and backend are on the same machine or connected network
2. Firewall isn't blocking port 9000
3. Global Server is running

---

## Environment Details

- **Frontend Application**: Port 8000
- **Global Server API**: Port 9000
- **Database**: localhost:3306 (MySQL)
- **Protocol**: HTTP
- **CORS**: Enabled for cross-origin requests

