# Network API Gateway - Getting Started

## 🎉 Quick Start

The **Network Automation API Gateway** is a production-ready FastAPI application that bridges traditional CLI-only network devices with modern REST APIs.

### Prerequisites
- Python 3.8 or higher
- SSH access to network devices
- Docker (optional)

### Installation & Setup

#### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd network_cli_to_openapi

# Run the setup script (creates venv automatically)
python3 setup.py

# Start the application
./start.sh
```

#### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: Docker

```bash
# Using Docker Compose
docker-compose up -d

# Or build manually
docker build -t network-api-gateway .
docker run -p 8000:8000 --env-file .env network-api-gateway
```

### Access the Application

Once running, access:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Default Credentials

**⚠️ Change these immediately after first login!**

```
Username: admin
Password: changeme
```

## 📚 First Steps

### 1. Login and Get Access Token

Using the interactive docs at `/docs`:

1. Click on **POST /auth/token**
2. Click "Try it out"
3. Enter credentials (admin/changeme)
4. Click "Execute"
5. Copy the `access_token` from the response

Or using curl:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=changeme"
```

### 2. Authorize in Swagger UI

1. Click the **Authorize** button at the top
2. Enter: `Bearer YOUR_ACCESS_TOKEN`
3. Click "Authorize"
4. Now all API requests will include your token

### 3. Add Your First Device

**POST /devices**

```json
{
  "name": "core-switch-01",
  "host": "192.168.1.10",
  "device_type": "cisco_ios",
  "username": "admin",
  "password": "cisco123",
  "port": 22,
  "timeout": 30,
  "description": "Core distribution switch"
}
```

Supported device types:
- `cisco_ios` - Cisco IOS/IOS-XE
- `cisco_nxos` - Cisco NX-OS
- `juniper_junos` - Juniper JunOS
- `arista_eos` - Arista EOS
- And 100+ more from Netmiko

### 4. Test Device Connection

**POST /devices/{device_id}/test**

```bash
# Test the device connection
curl -X POST "http://localhost:8000/devices/1/test" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Execute Commands

**POST /devices/{device_id}/execute**

```json
{
  "command": "show version"
}
```

Or execute multiple commands:

**POST /devices/{device_id}/execute/batch**

```json
{
  "commands": [
    "show version",
    "show ip interface brief",
    "show running-config | include hostname"
  ]
}
```

### 6. Get Device Configuration

**GET /devices/{device_id}/config**

```bash
curl "http://localhost:8000/devices/1/config" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Common Configuration

### Environment Variables (.env)

```bash
# Application Settings
APP_NAME="Network API Gateway"
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-generated-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///./network_gateway.db

# CORS Settings
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Connection Pooling
MAX_SSH_CONNECTIONS=50
SSH_TIMEOUT=30
```

### Generate Secure SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📖 API Endpoints Overview

### Authentication
- `POST /auth/register` - Register new user (Admin only)
- `POST /auth/token` - Login and get access token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Device Management
- `GET /devices` - List all devices
- `POST /devices` - Add new device
- `GET /devices/{id}` - Get device details
- `PUT /devices/{id}` - Update device
- `DELETE /devices/{id}` - Delete device
- `POST /devices/{id}/test` - Test connection

### Command Execution
- `POST /devices/{id}/execute` - Execute single command
- `POST /devices/{id}/execute/batch` - Execute multiple commands
- `POST /devices/{id}/config` - Send configuration commands
- `GET /devices/{id}/config` - Get running configuration

### System
- `GET /health` - Health check
- `GET /ready` - Readiness check
- `GET /` - API information

## 👥 User Roles

### Admin
- Full access to all operations
- Can create/modify/delete users
- Can manage all devices
- Can execute any commands

### Operator
- Can add and modify devices
- Can execute commands
- Cannot manage users

### Read-Only
- Can view devices
- Can view configurations
- Cannot execute commands
- Cannot modify anything

## 🔐 Security Best Practices

### 1. Change Default Credentials

```bash
# Create new admin user via API, then delete default admin
POST /auth/register
{
  "username": "your_admin",
  "email": "admin@company.com",
  "password": "strong_password",
  "role": "ADMIN"
}
```

### 2. Use Strong SECRET_KEY

```bash
# Never use the example key in production
# Generate a new one:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Enable HTTPS

See `DEPLOYMENT.md` for Nginx + SSL setup

### 4. Set DEBUG=false

```bash
# In .env for production
DEBUG=false
LOG_LEVEL=WARNING
```

### 5. Secure Device Credentials

- Use service accounts with minimal privileges
- Rotate credentials regularly
- Consider using SSH keys instead of passwords
- Store passwords encrypted in production databases

## 🎨 Advanced Features

### Custom TextFSM Templates

Create custom parsing templates for any device command:

**1. Create a template file:**

```bash
# File: templates/cisco_ios_show_ip_interface_brief.textfsm
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+|unassigned)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

**2. Execute command with TextFSM:**

```bash
curl -X POST "http://localhost:8000/devices/myswitch/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "show ip interface brief",
    "use_textfsm": true
  }'
```

**Result:** Structured JSON instead of raw text! 

See [CUSTOM_TEXTFSM_TEMPLATES.md](CUSTOM_TEXTFSM_TEMPLATES.md) for complete guide.

### Generic Device Type

Support any device (even proprietary/custom ones):

```bash
# Add a generic device
curl -X POST "http://localhost:8000/devices" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "custom-device",
    "host": "192.168.1.100",
    "device_type": "generic",
    "username": "admin",
    "password": "password"
  }'
```

Then create custom templates in `templates/generic_*.textfsm` to parse output!

## 🐛 Troubleshooting

### Application won't start

```bash
# Check if port 8000 is already in use
sudo netstat -tulpn | grep 8000

# Check logs
tail -f logs/*.log

# Verify Python version
python3 --version  # Should be 3.8+

# Verify virtual environment is activated
which python  # Should point to venv/bin/python
```

### Authentication fails

```bash
# Verify token is valid
# Tokens expire after 30 minutes by default
# Request a new token via /auth/token

# Check if user is active
# Admin can check via database or /auth/me endpoint
```

### Device connection fails

```bash
# Common issues:
1. Incorrect credentials
2. Wrong device_type
3. SSH not enabled on device
4. Firewall blocking port 22
5. Network connectivity issues

# Test manually:
ssh username@device_ip

# Check device logs:
# View session_logs/ directory for detailed connection logs
```

### Database errors

```bash
# Reset database (development only!)
rm network_gateway.db
# Restart application - it will recreate tables

# Check database file permissions
ls -la network_gateway.db
```

## 📝 Example Workflows

### Workflow 1: Add and Configure a New Switch

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
response = requests.post(f"{BASE_URL}/auth/token", 
    data={"username": "admin", "password": "changeme"})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# 2. Add device
device = {
    "name": "sw-01",
    "host": "192.168.1.10",
    "device_type": "cisco_ios",
    "username": "cisco",
    "password": "cisco123"
}
response = requests.post(f"{BASE_URL}/devices", json=device, headers=headers)
device_id = response.json()["id"]

# 3. Test connection
response = requests.post(f"{BASE_URL}/devices/{device_id}/test", headers=headers)
print(response.json())

# 4. Execute commands
commands = {
    "commands": [
        "show version",
        "show ip interface brief",
        "show inventory"
    ]
}
response = requests.post(f"{BASE_URL}/devices/{device_id}/execute/batch", 
    json=commands, headers=headers)
print(response.json())
```

### Workflow 2: Bulk Configuration Backup

```python
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

# Get all devices
response = requests.get(f"{BASE_URL}/devices", headers=headers)
devices = response.json()

# Backup each device configuration
backups = {}
for device in devices:
    device_id = device["id"]
    response = requests.get(f"{BASE_URL}/devices/{device_id}/config", 
        headers=headers)
    
    if response.status_code == 200:
        config = response.json()["output"]
        backups[device["name"]] = config
        
        # Save to file
        filename = f"backup_{device['name']}_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            f.write(config)

print(f"Backed up {len(backups)} devices")
```

### Workflow 3: Execute Command on Multiple Devices

```python
import requests
import concurrent.futures

BASE_URL = "http://localhost:8000"
token = "YOUR_ACCESS_TOKEN"
headers = {"Authorization": f"Bearer {token}"}

def execute_command(device_id, command):
    response = requests.post(
        f"{BASE_URL}/devices/{device_id}/execute",
        json={"command": command},
        headers=headers
    )
    return response.json()

# Get all device IDs
response = requests.get(f"{BASE_URL}/devices", headers=headers)
device_ids = [d["id"] for d in response.json()]

# Execute command on all devices in parallel
command = "show version"
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(execute_command, device_id, command) 
               for device_id in device_ids]
    
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

print(f"Executed command on {len(results)} devices")
```

## 📊 What's Implemented

### ✅ Core Features
- JWT token-based authentication
- Role-based access control (Admin, Operator, Read-Only)
- Device CRUD operations
- Multi-vendor support (100+ device types via Netmiko)
- Single and batch command execution
- Configuration management
- Connection testing
- Async operations with connection pooling

### ✅ API Features
- Auto-generated OpenAPI documentation
- Interactive Swagger UI
- Request/response validation
- Comprehensive error handling
- CORS support
- Health check endpoints

### ✅ Production Features
- Structured JSON logging
- Request correlation IDs
- Docker containerization
- Environment-based configuration
- Database migrations support
- Session logging

## 📚 Next Steps

1. Read `DEPLOYMENT.md` for production deployment
2. Check `QUICK_REFERENCE.md` for API examples
3. Review `DEVELOPER_GUIDE.md` for extending the application
4. See example code in `tests/` directory

## 🆘 Need Help?

- Check application logs in `logs/` directory
- View session logs in `session_logs/` for device connection details
- Use `/health` endpoint to verify application status
- Check environment variables in `.env` file
- Review the interactive API docs at `/docs`

## ⚠️ Important Notes

1. **Change default admin password immediately**
2. **Generate a new SECRET_KEY for production**
3. **Set DEBUG=false in production**
4. **Use HTTPS in production (see DEPLOYMENT.md)**
5. **Regularly backup your database**
6. **Monitor logs for security issues**
7. **Keep dependencies updated**

---

For detailed developer documentation, see `DEVELOPER_GUIDE.md`  
For deployment instructions, see `DEPLOYMENT.md`  
For quick API reference, see `QUICK_REFERENCE.md`
