# Quick Reference Guide

## 🚀 Getting Started (1 minute)

```bash
# 1. Setup
./setup.py

# 2. Start
./start.sh

# 3. Access
# Open http://localhost:8080/docs
# Login: admin / changeme
```

## 📍 Essential Endpoints

### Authentication
```bash
# Login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'

# Get current user
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/auth/me
```

### Device Management
```bash
# Add device
curl -X POST http://localhost:8080/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "switch-01",
    "host": "192.168.1.1",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "password"
  }'

# List devices
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/devices

# Test connection (by name, ID, or IP)
curl -X POST http://localhost:8080/devices/switch-01/test \
  -H "Authorization: Bearer <token>"
```

> **💡 Tip**: All device endpoints accept **ID** (e.g., `1`), **Name** (e.g., `switch-01`), or **IP** (e.g., `192.168.1.1`)

### Command Execution
```bash
# Execute command (using device name)
curl -X POST http://localhost:8080/devices/switch-01/execute \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"command":"show version"}'

# Get config (using IP address)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/devices/192.168.1.1/config

# Update config (using device ID)
curl -X POST http://localhost:8080/devices/1/config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": ["interface gi0/1","description Test"],
    "save_config": true
  }'
```

## 🔑 Environment Variables

```bash
# Security
SECRET_KEY=<generate-with-openssl-rand>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///./network_gateway.db

# Application
DEBUG=false
LOG_LEVEL=INFO
```

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs -f

# Rebuild
docker-compose build --no-cache

# Shell access
docker-compose exec api sh
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_auth.py -v

# Watch mode
pytest-watch
```

## 📊 Monitoring

```bash
# Health check
curl http://localhost:8080/health

# Readiness check
curl http://localhost:8080/ready

# Application logs
tail -f logs/app.log

# Session logs
tail -f session_logs/device-name.log
```

## 🛠️ Common Tasks

```bash
# Format code
make format

# Run linters
make lint

# Install dependencies
make install

# Run application
make run

# Clean up
make clean
```

## 🔒 Security Checklist

- [ ] Change default admin password
- [ ] Generate new SECRET_KEY
- [ ] Set DEBUG=false in production
- [ ] Configure CORS_ORIGINS properly
- [ ] Use HTTPS in production
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Review user roles

## 📁 Important Files

```
.env                    # Environment configuration
app/main.py            # Application entry point
app/config.py          # Settings management
app/routers/           # API endpoints
app/services/          # Business logic
tests/                 # Test suite
requirements.txt       # Dependencies
docker-compose.yml     # Docker setup
```

## 🆘 Troubleshooting

### Service won't start
```bash
# Check logs
journalctl -u network-api-gateway -n 50

# Verify Python
python --version

# Check dependencies
pip list
```

### Connection fails
```bash
# Test SSH manually
ssh admin@device-ip

# Check firewall
sudo ufw status

# Verify credentials
# Check device logs
```

### Database errors
```bash
# Check file permissions
ls -la network_gateway.db

# Reset database
rm network_gateway.db
# Restart app to recreate
```

## 📚 Documentation Links

- **API Docs**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Developer Guide**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 🎯 Quick Examples

### Python Client
```python
import requests

# Login
response = requests.post(
    "http://localhost:8080/auth/login",
    json={"username": "admin", "password": "changeme"}
)
token = response.json()["access_token"]

# Execute command
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8080/devices/1/execute",
    headers=headers,
    json={"command": "show version"}
)
print(response.json())
```

### JavaScript/Fetch
```javascript
// Login
const loginResponse = await fetch('http://localhost:8080/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'changeme'})
});
const {access_token} = await loginResponse.json();

// Execute command
const commandResponse = await fetch('http://localhost:8080/devices/1/execute', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({command: 'show version'})
});
const result = await commandResponse.json();
```

## 🔄 Backup & Restore

```bash
# Backup
cp network_gateway.db backups/backup-$(date +%Y%m%d).db
cp .env backups/env-$(date +%Y%m%d).bak

# Restore
cp backups/backup-YYYYMMDD.db network_gateway.db
cp backups/env-YYYYMMDD.bak .env
systemctl restart network-api-gateway
```

## 📞 Support

- Check `/docs` for API documentation
- Review logs for errors
- Test device connectivity manually
- Verify credentials and permissions

## ⚡ Performance Tips

1. Use connection pooling (enabled by default)
2. Implement caching for frequently accessed data
3. Use batch operations when possible
4. Monitor session_logs for slow commands
5. Consider PostgreSQL for production

## 🎓 Learning Path

1. Start with `/docs` to explore API
2. Read DEVELOPER_GUIDE.md for architecture
3. Review code in `app/` directory
4. Run tests to see examples
5. Extend with custom endpoints

---

**Need more help?** Check the full documentation in DEVELOPER_GUIDE.md and DEPLOYMENT.md
