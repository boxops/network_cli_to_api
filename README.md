# Network Automation API Gateway

<div align="center">

**Transform CLI-only network devices into modern REST APIs**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

[Quick Start](#-quick-start) •
[Features](#-features) •
[Documentation](#-documentation) •
[API Demo](#-api-demo) •
[Contributing](#-contributing)

</div>

---

## 🎯 What is this?

A **production-ready FastAPI application** that bridges the gap between traditional CLI-only network devices and modern REST APIs. Instead of manually SSH'ing into network devices, you can now manage them through simple HTTP requests.

### The Problem
- Network devices only support CLI via SSH
- Automation requires complex expect scripts
- No standardized API interface
- Difficult to integrate with modern applications

### The Solution
This gateway provides:
- **REST API** endpoints for all network operations
- **Multi-vendor** support (Cisco, Juniper, Arista, and 100+ more)
- **Authentication** with JWT tokens and role-based access
- **Auto-generated** interactive documentation
- **Async operations** for managing multiple devices concurrently

### Simple Example

```bash
# Instead of this:
ssh admin@192.168.1.1
> show version
> show ip interface brief
> exit

# Do this - reference devices by ID, name, or IP:
curl -X POST "http://api.example.com/devices/core-switch-01/execute" \
  -H "Authorization: Bearer <token>" \
  -d '{"command": "show version"}'
```

---

## ✨ Features

### 🔐 Authentication & Security
- JWT token-based authentication
- Role-based access control (Admin, Operator, Read-Only)
- Secure credential storage with encryption
- Token refresh mechanism

### 🖥️ Device Management
- Full CRUD operations for devices
- Support for 100+ device types via Netmiko
- **Generic device type** for custom/proprietary devices
- Connection testing and validation
- Bulk operations

### ⚡ Command Execution
- Execute single or batch commands
- Read and write configurations
- **Custom TextFSM templates** with priority over built-in parsers
- TextFSM parsing for structured output
- Async execution with connection pooling

### 🎯 Flexible Device Identification
- Reference devices by **ID**, **Name**, or **IP Address**
- Same endpoint works with all three identifier types
- Backward compatible with existing ID-based calls
- More intuitive and user-friendly API

### 📚 Documentation
- Auto-generated OpenAPI/Swagger UI
- Interactive API testing at `/docs`
- Complete request/response examples
- Comprehensive guides

### 🚀 Production Ready
- Docker containerization
- Health check endpoints
- Structured JSON logging
- Request correlation IDs
- CORS support
- Environment-based configuration

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/boxops/network_cli_to_openapi.git
cd network_cli_to_openapi

# Run automated setup (creates virtual environment)
python3 setup.py

# Start the application
./start.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Option 3: Docker

```bash
# Using Docker Compose
docker-compose up -d

# Or manually
docker build -t network-api-gateway .
docker run -p 8080:8080 network-api-gateway
```

### Access the Application

Once running, open your browser:

- **📖 API Documentation**: http://localhost:8080/docs
- **🔍 Alternative Docs**: http://localhost:8080/redoc
- **💚 Health Check**: http://localhost:8080/health

**Default credentials**: `admin` / `changeme` (⚠️ Change immediately!)

---

## 🎮 API Demo

### 1. Login and Get Token

```bash
curl -X POST "http://localhost:8080/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=changeme"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Add a Network Device

```bash
curl -X POST "http://localhost:8080/devices" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "core-switch-01",
    "host": "192.168.1.10",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco123"
  }'
```

### 3. Execute Commands

```bash
# Single command - use device ID, name, or IP address
curl -X POST "http://localhost:8080/devices/core-switch-01/execute" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"command": "show version"}'

# By IP address
curl -X POST "http://localhost:8080/devices/192.168.1.10/execute" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"command": "show version"}'

# Multiple commands (batch execution)
curl -X POST "http://localhost:8080/devices/core-switch-01/execute-batch" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "commands": [
      "show version",
      "show ip interface brief",
      "show running-config | include hostname"
    ]
  }'
```

### 4. Get Device Configuration

```bash
curl "http://localhost:8080/devices/1/config" \
  -H "Authorization: Bearer <your_token>"
```

**💡 Tip**: Use the interactive documentation at `/docs` to try all endpoints in your browser!

---

## 📚 Documentation

Comprehensive guides are available:

| Document | Purpose | Audience |
|----------|---------|----------|
| **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** | Navigation guide | Everyone |
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Quick start & tutorials | Users |
| **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** | Development & extension | Developers |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production deployment | DevOps |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | API endpoint reference | API Users |
| **[DEVICE_IDENTIFIER_FEATURE.md](DEVICE_IDENTIFIER_FEATURE.md)** | Flexible device identification | API Users |
| **[CUSTOM_TEXTFSM_TEMPLATES.md](CUSTOM_TEXTFSM_TEMPLATES.md)** | Custom TextFSM templates | Developers |

**Start here**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - it helps you find exactly what you need!

---

## 💡 Usage Examples

### Custom TextFSM Templates

Create custom parsing templates that take priority over Netmiko's built-in parsers:

```bash
# 1. Create a template: templates/cisco_ios_show_ip_interface_brief.textfsm
# 2. Execute command with TextFSM parsing
curl -X POST "http://localhost:8080/devices/core-switch-01/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "show ip interface brief",
    "use_textfsm": true
  }'
```

**Template Example:**
```textfsm
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+|unassigned)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

See [CUSTOM_TEXTFSM_TEMPLATES.md](CUSTOM_TEXTFSM_TEMPLATES.md) for complete guide.

### Flexible Device Identification

All device-related endpoints support three ways to identify devices:

```bash
# By Device ID (backward compatible)
curl -X POST "http://localhost:8080/devices/1/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "show version"}'

# By Device Name (recommended - more readable)
curl -X POST "http://localhost:8080/devices/core-switch-01/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "show version"}'

# By IP Address (convenient for ad-hoc queries)
curl -X POST "http://localhost:8080/devices/192.168.1.10/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"command": "show version"}'
```

**Lookup Priority**: ID (if numeric) → Name → IP Address

See [DEVICE_IDENTIFIER_FEATURE.md](DEVICE_IDENTIFIER_FEATURE.md) for detailed documentation.

### Common Operations

```bash
# Get device information by name
curl -X GET "http://localhost:8080/devices/datacenter-router" \
  -H "Authorization: Bearer $TOKEN"

# Test connection by IP
curl -X POST "http://localhost:8080/devices/192.168.1.1/test" \
  -H "Authorization: Bearer $TOKEN"

# Update device using name
curl -X PUT "http://localhost:8080/devices/edge-switch-02" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"description": "Edge switch in building 2"}'

# Get running config by name
curl -X GET "http://localhost:8080/devices/core-router/config" \
  -H "Authorization: Bearer $TOKEN"

# Execute batch commands by IP
curl -X POST "http://localhost:8080/devices/10.0.0.1/execute-batch" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "commands": [
      "show version",
      "show inventory",
      "show ip route summary"
    ]
  }'
```

---

## 🏗️ Architecture

```
┌─────────────┐
│   Client    │  (Browser, curl, Python, etc.)
└──────┬──────┘
       │ HTTP/HTTPS
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌────────────┐  ┌─────────────────┐   │
│  │   Auth     │  │   Routers       │   │
│  │  (JWT)     │  │ /devices        │   │
│  └────────────┘  │ /commands       │   │
│                  │ /auth           │   │
│  ┌────────────┐  └─────────────────┘   │
│  │  Database  │  ┌─────────────────┐   │
│  │ (SQLite/   │  │  Netmiko        │   │
│  │PostgreSQL) │  │  Service        │   │
│  └────────────┘  └─────────────────┘   │
└─────────────────────┬───────────────────┘
                      │ SSH (Port 22)
                      ▼
       ┌──────────────────────────────┐
       │    Network Devices           │
       │  • Cisco IOS/NX-OS           │
       │  • Juniper JunOS             │
       │  • Arista EOS                │
       │  • 100+ more via Netmiko     │
       └──────────────────────────────┘
```

**Key Components**:
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Async ORM for database operations
- **Netmiko**: Multi-vendor SSH library
- **JWT**: Secure token-based authentication
- **Pydantic**: Data validation and settings management

---

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Framework** | FastAPI 0.104+ | Async web framework with auto docs |
| **SSH/CLI** | Netmiko 4.3+ | Multi-vendor network device support |
| **Database** | SQLAlchemy 2.0 + SQLite/PostgreSQL | Async ORM and data persistence |
| **Authentication** | JWT (python-jose) | Secure token-based auth |
| **Validation** | Pydantic 2.5+ | Request/response validation |
| **Server** | Uvicorn | High-performance ASGI server |
| **Testing** | Pytest | Comprehensive test suite |
| **Containerization** | Docker | Easy deployment |

**Python Version**: 3.8+

---

## 📋 API Endpoints

### Authentication
- `POST /auth/register` - Register new user (Admin only)
- `POST /auth/token` - Login and get access token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Device Management
- `GET /devices` - List all devices
- `POST /devices` - Add new device
- `GET /devices/{device_identifier}` - Get device details (by ID, name, or IP)
- `PUT /devices/{device_identifier}` - Update device (by ID, name, or IP)
- `DELETE /devices/{device_identifier}` - Delete device (by ID, name, or IP)
- `POST /devices/{device_identifier}/test` - Test device connection

### Command Execution
- `POST /devices/{device_identifier}/execute` - Execute single command
- `POST /devices/{device_identifier}/execute-batch` - Execute multiple commands
- `POST /devices/{device_identifier}/config` - Send configuration commands
- `GET /devices/{device_identifier}/config` - Get running configuration
- `GET /devices/{device_identifier}/interfaces` - Get interface status

> **💡 Pro Tip:** All device endpoints support flexible identifiers - use device ID (e.g., `1`), device name (e.g., `core-switch-01`), or IP address (e.g., `192.168.1.10`).

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /ready` - Readiness check

**Full API documentation**: http://localhost:8080/docs (when running)

---

## 👥 User Roles

| Role | Permissions |
|------|-------------|
| **Admin** | Full access: manage users, devices, and execute all commands |
| **Operator** | Add/modify devices, execute commands, view configurations |
| **Read-Only** | View devices and configurations only |

---

## 🔐 Security Features

- ✅ JWT token-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Password hashing with bcrypt
- ✅ Secure credential storage
- ✅ CORS protection
- ✅ Request correlation IDs for audit trails
- ✅ Configurable token expiration
- ✅ Session logging for compliance

**Security Best Practices**:
1. Change default admin password immediately
2. Use HTTPS in production (see [DEPLOYMENT.md](DEPLOYMENT.md))
3. Generate strong SECRET_KEY
4. Set `DEBUG=false` in production
5. Regularly update dependencies

---

## 🐳 Deployment

### Quick Deploy to Remote Server

```bash
# 1. Open firewall port
sudo ufw allow 8080/tcp

# 2. Update CORS in .env
CORS_ORIGINS=["http://YOUR_SERVER_IP:8080"]

# 3. Start application
./start.sh

# 4. Access from anywhere
http://YOUR_SERVER_IP:8080/docs
```

### Production Deployment with Nginx + SSL

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for:
- Nginx reverse proxy setup
- SSL/TLS with Let's Encrypt
- Systemd service configuration
- Docker deployment
- Security hardening
- Monitoring and logging
- Backup strategies

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# View coverage report
open htmlcov/index.html
```

---

## 🛠️ Development

### Prerequisites
- Python 3.8+
- SSH access to network devices (for testing)
- Git

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/boxops/network_cli_to_openapi.git
cd network_cli_to_openapi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies including dev tools
pip install -r requirements.txt

# Run in development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### Project Structure

```
network_cli_to_openapi/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication utilities
│   ├── logging_config.py    # Logging configuration
│   ├── routers/             # API endpoints
│   │   ├── auth.py
│   │   ├── devices.py
│   │   └── commands.py
│   └── services/            # Business logic
│       └── netmiko_service.py
├── tests/                   # Test suite
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
├── docker-compose.yml       # Container orchestration
└── docs/                    # Documentation
```

See **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** for detailed development instructions.

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Write tests for new features
- Follow PEP 8 style guide
- Update documentation
- Add type hints
- Keep commits atomic and descriptive

---

## 📝 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Application
APP_NAME="Network API Gateway"
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///./network_gateway.db

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# SSH
MAX_SSH_CONNECTIONS=50
SSH_TIMEOUT=30
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐛 Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Verify virtual environment
which python  # Should point to venv/bin/python

# Check logs
tail -f logs/*.log
```

**Can't connect to device**
```bash
# Test SSH manually
ssh username@device_ip

# Check device type is correct
# See: https://github.com/ktbyers/netmiko#supported-devices

# View session logs
ls -la session_logs/
```

**Authentication fails**
```bash
# Tokens expire after 30 minutes
# Request a new token via /auth/token

# Verify credentials
# Default: admin / changeme
```

For more help, see **[GETTING_STARTED.md](GETTING_STARTED.md)** troubleshooting section.

---

## 📊 Performance

- **API Response Time**: < 500ms (excluding device communication)
- **Concurrent Connections**: 100+ devices
- **Availability Target**: 99.5%
- **Database**: SQLite (dev), PostgreSQL recommended (production)

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework
- **[Netmiko](https://github.com/ktbyers/netmiko)** - Multi-vendor SSH library
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit

---

## 📞 Support

- **Documentation**: Start with [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
- **API Docs**: http://localhost:8080/docs (when running)
- **Issues**: Open an issue on GitHub
- **Discussions**: GitHub Discussions

---

## 🗺️ Roadmap

- [ ] GraphQL API support
- [ ] WebSocket for real-time updates
- [ ] Advanced TextFSM parsing templates
- [ ] Multi-threading for batch operations
- [ ] Ansible integration
- [ ] Terraform provider
- [ ] Web UI dashboard
- [ ] Support for NETCONF/RESTCONF
- [ ] Enhanced audit logging
- [ ] Rate limiting per endpoint

---

<div align="center">

**Made with ❤️ for Network Engineers**

[⬆ Back to Top](#network-automation-api-gateway)

</div>
