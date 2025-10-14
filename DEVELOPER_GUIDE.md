# Network Automation API Gateway - Developer Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Development Setup](#development-setup)
4. [API Usage](#api-usage)
5. [Extending the Application](#extending-the-application)
6. [Testing](#testing)
7. [Deployment](#deployment)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Docker (optional)
- SSH access to network devices

### Local Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd network_cli_to_openapi
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application**
```bash
./start.sh
# Or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API**
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Docker Setup

1. **Using Docker Compose**
```bash
docker-compose up -d
```

2. **Build manually**
```bash
docker build -t network-api-gateway .
docker run -p 8000:8000 --env-file .env network-api-gateway
```

## Architecture Overview

### Directory Structure
```
network_cli_to_openapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── logging_config.py    # Logging configuration
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── devices.py       # Device management endpoints
│   │   └── commands.py      # Command execution endpoints
│   └── services/
│       ├── __init__.py
│       └── netmiko_service.py  # Netmiko integration
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_devices.py
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── start.sh
└── README.md
```

### Components

1. **FastAPI Application** (`app/main.py`)
   - Main application entry point
   - Router registration
   - Middleware configuration
   - Lifespan events

2. **Authentication** (`app/auth.py`)
   - JWT token generation and validation
   - Password hashing with bcrypt
   - Role-based access control (RBAC)

3. **Database** (`app/database.py`, `app/models.py`)
   - Async SQLAlchemy with SQLite
   - User and Device models
   - Session management

4. **Netmiko Service** (`app/services/netmiko_service.py`)
   - SSH connection management
   - Command execution
   - Configuration management

## Development Setup

### Environment Variables

Key environment variables in `.env`:

```bash
# Application
APP_NAME="Network API Gateway"
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///./network_gateway.db

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Database Initialization

The database is automatically initialized on first run. Default admin user:
- Username: `admin`
- Password: `changeme` (change immediately!)

## API Usage

### Authentication

1. **Login and get token**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. **Use token in requests**
```bash
export TOKEN="your-access-token"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/auth/me
```

### Device Management

1. **Add a device**
```bash
curl -X POST "http://localhost:8000/devices" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "core-switch-01",
    "host": "192.168.1.1",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco123",
    "port": 22,
    "timeout": 30
  }'
```

2. **List devices**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/devices
```

3. **Test device connection**
```bash
curl -X POST "http://localhost:8000/devices/1/test" \
  -H "Authorization: Bearer $TOKEN"
```

### Command Execution

1. **Execute single command**
```bash
curl -X POST "http://localhost:8000/devices/1/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show version",
    "use_textfsm": false
  }'
```

2. **Execute multiple commands**
```bash
curl -X POST "http://localhost:8000/devices/1/execute-batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["show version", "show ip interface brief"],
    "use_textfsm": false
  }'
```

3. **Get running configuration**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/devices/1/config
```

4. **Update configuration**
```bash
curl -X POST "http://localhost:8000/devices/1/config" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "interface GigabitEthernet0/1",
      "description Uplink to Core",
      "no shutdown"
    ],
    "save_config": true
  }'
```

5. **Get interfaces (with TextFSM parsing)**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/devices/1/interfaces
```

## Extending the Application

### Adding a New Endpoint

1. Create a new router in `app/routers/`:

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter(prefix="/custom", tags=["Custom"])

@router.get("/example")
async def custom_endpoint(current_user = Depends(get_current_user)):
    return {"message": "Custom endpoint"}
```

2. Register the router in `app/main.py`:

```python
from app.routers import custom
app.include_router(custom.router)
```

### Adding Custom Command Parsers

Create a parser in `app/services/parsers.py`:

```python
import re

def parse_custom_output(output: str) -> dict:
    """Custom parser for specific command output"""
    # Your parsing logic here
    return {"parsed_data": "value"}
```

### Adding New Device Types

Update `app/schemas.py` to add new device types:

```python
device_type: Literal["cisco_ios", "cisco_nxos", "juniper_junos", "arista_eos", "new_vendor"]
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_auth.py -v
```

### Writing Tests

Example test:
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_my_endpoint(client: AsyncClient, auth_headers):
    response = await client.get("/my-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Deployment

### Production Checklist

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Configure proper DATABASE_URL
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Review CORS settings

### Using Docker in Production

```bash
# Build production image
docker build -t network-api-gateway:prod .

# Run with production settings
docker run -d \
  --name network-api-gateway \
  -p 8000:8000 \
  --env-file .env.production \
  -v $(pwd)/data:/app/data \
  network-api-gateway:prod
```

### Systemd Service (Alternative)

Create `/etc/systemd/system/network-api-gateway.service`:

```ini
[Unit]
Description=Network API Gateway
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/network-api-gateway
Environment="PATH=/opt/network-api-gateway/venv/bin"
ExecStart=/opt/network-api-gateway/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable network-api-gateway
sudo systemctl start network-api-gateway
```

## Security Considerations

1. **Credential Management**
   - Never commit `.env` files
   - Use environment variables or secrets management
   - Rotate credentials regularly

2. **Network Security**
   - Use SSH keys where possible
   - Implement network segmentation
   - Use VPN for remote access

3. **API Security**
   - Always use HTTPS in production
   - Implement rate limiting
   - Monitor for suspicious activity
   - Keep dependencies updated

## Troubleshooting

### Common Issues

1. **Connection Timeout**
   - Check device IP and port
   - Verify firewall rules
   - Increase timeout value

2. **Authentication Failed**
   - Verify credentials
   - Check device enable password
   - Ensure SSH is enabled on device

3. **Database Locked**
   - SQLite doesn't support high concurrency
   - Consider PostgreSQL for production

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review logs in `logs/` directory
- Check session logs in `session_logs/` for device interactions

## License

See LICENSE file for details.
