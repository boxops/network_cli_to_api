# Deployment Guide - Network API Gateway

## Table of Contents
1. [Remote Server Deployment](#remote-server-deployment)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Systemd Service](#systemd-service)
5. [Nginx Reverse Proxy](#nginx-reverse-proxy)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)

## Remote Server Deployment

### Quick Answer

**Your application is already configured to accept remote connections!** 

The app runs on `0.0.0.0:8080`, which listens on all network interfaces. You just need to:

1. Open firewall port 8080 on the server
2. Update CORS settings in `.env`
3. Access via `http://SERVER_IP:8080`

### Option 1: Direct Access (Quick Testing)

**Good for**: Quick testing, development, internal networks

#### Steps:

**1. On the server, open port 8080:**
```bash
# Ubuntu/Debian
sudo ufw allow 8080/tcp
sudo ufw enable
sudo ufw status

# RHEL/CentOS
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```

**2. Update `.env` file:**
```bash
# Add your server's IP to CORS_ORIGINS
CORS_ORIGINS=["http://localhost:8080","http://YOUR_SERVER_IP:8080"]

# For production, set DEBUG to false
DEBUG=false
```

**3. Start the application:**
```bash
./start.sh
```

**4. Access from your browser:**
```
http://YOUR_SERVER_IP:8080/docs
```

**That's it!** No code changes needed.

### Option 2: Production with Nginx + SSL (Recommended)

**Good for**: Production, public access, security

#### Why Use Nginx?

- ✅ SSL/TLS encryption (HTTPS)
- ✅ Better performance
- ✅ Load balancing
- ✅ Security headers
- ✅ Standard ports (80/443)

See the [Nginx Reverse Proxy](#nginx-reverse-proxy) section below for detailed setup.

### Testing Remote Access

**1. From another machine, test connectivity:**

```bash
# Test port is open
telnet YOUR_SERVER_IP 8080

# Test HTTP response
curl http://YOUR_SERVER_IP:8080/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"1.0.0","database":"connected"}
```

**2. From browser:**

```
http://YOUR_SERVER_IP:8080/docs
```

**3. Using the API:**

```bash
# From any machine
curl -X POST "http://YOUR_SERVER_IP:8080/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

### Common Scenarios

**Scenario 1: Internal Network Only**

```bash
# No firewall changes needed
# Access via: http://SERVER_LOCAL_IP:8080/docs
# CORS: CORS_ORIGINS=["http://SERVER_LOCAL_IP:8080"]
```

**Scenario 2: Public Internet Access (No Domain)**

```bash
# Open port: sudo ufw allow 8080/tcp
# Access via: http://PUBLIC_IP:8080/docs
# CORS: CORS_ORIGINS=["http://PUBLIC_IP:8080"]
# Security: Use Nginx + basic auth or VPN
```

**Scenario 3: Public Internet Access (With Domain)**

```bash
# Use Nginx with Let's Encrypt SSL
# Access via: https://api.yourdomain.com/docs
# CORS: CORS_ORIGINS=["https://api.yourdomain.com"]
# This is the most secure option
```

## Production Deployment

### System Requirements

**Minimum:**
- 2 CPU cores
- 2 GB RAM
- 10 GB disk space
- Ubuntu 20.04+ or RHEL 8+

**Recommended:**
- 4 CPU cores
- 4 GB RAM
- 20 GB disk space
- SSD storage

### Pre-deployment Checklist

- [ ] Server provisioned and accessible
- [ ] Python 3.8+ installed
- [ ] SSH access to network devices configured
- [ ] SSL/TLS certificates obtained
- [ ] Firewall rules configured
- [ ] Backup strategy defined
- [ ] Monitoring solution ready

### Manual Deployment

1. **Prepare the server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx

# Create application user
sudo useradd -m -s /bin/bash netapi
sudo usermod -aG sudo netapi
```

2. **Deploy application**
```bash
# Switch to application user
sudo su - netapi

# Clone repository
git clone <repository-url> /opt/network-api-gateway
cd /opt/network-api-gateway

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data session_logs logs
```

3. **Configure environment**
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# Generate secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with:
# - Generated SECRET_KEY
# - DEBUG=false
# - Proper DATABASE_URL (if using PostgreSQL)
# - Production CORS_ORIGINS
```

4. **Initialize database**
```bash
# Run the application once to create database
python -c "
from app.database import engine, Base
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())
"
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Prepare environment**
```bash
# Create project directory
mkdir -p /opt/network-api-gateway
cd /opt/network-api-gateway

# Clone or copy files
git clone <repository-url> .

# Configure environment
cp .env.example .env
nano .env  # Update with production values
```

2. **Deploy with Docker Compose**
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d
```

### Using Docker Only

```bash
# Build image
docker build -t network-api-gateway:latest .

# Run container
docker run -d \
  --name network-api-gateway \
  -p 8080:8080 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/session_logs:/app/session_logs \
  --restart unless-stopped \
  network-api-gateway:latest

# View logs
docker logs -f network-api-gateway

# Stop container
docker stop network-api-gateway
docker rm network-api-gateway
```

## Systemd Service

### Service Configuration

Create `/etc/systemd/system/network-api-gateway.service`:

```ini
[Unit]
Description=Network API Gateway
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=netapi
Group=netapi
WorkingDirectory=/opt/network-api-gateway
Environment="PATH=/opt/network-api-gateway/venv/bin"
EnvironmentFile=/opt/network-api-gateway/.env
ExecStart=/opt/network-api-gateway/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8080 \
  --workers 4 \
  --log-level info

# Restart policy
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/network-api-gateway/data /opt/network-api-gateway/session_logs

# Resource limits
LimitNOFILE=65535
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### Service Management

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable network-api-gateway

# Start service
sudo systemctl start network-api-gateway

# Check status
sudo systemctl status network-api-gateway

# View logs
sudo journalctl -u network-api-gateway -f

# Restart service
sudo systemctl restart network-api-gateway

# Stop service
sudo systemctl stop network-api-gateway
```

## Nginx Reverse Proxy

### Basic Configuration

Create `/etc/nginx/sites-available/network-api-gateway`:

```nginx
upstream network_api {
    server 127.0.0.1:8080;
}

server {
    listen 80;
    server_name api.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/network-api-access.log;
    error_log /var/log/nginx/network-api-error.log;

    # Client upload size
    client_max_body_size 10M;

    location / {
        proxy_pass http://network_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://network_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### Enable Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/network-api-gateway /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.example.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

## Security Hardening

### Application Security

1. **Environment Variables**
```bash
# Generate strong secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env
SECRET_KEY=<generated-key>
DEBUG=false
```

2. **Database Security**
```bash
# For PostgreSQL (recommended for production)
DATABASE_URL=postgresql+asyncpg://username:password@localhost/network_api

# Secure file permissions
chmod 600 /opt/network-api-gateway/.env
chown netapi:netapi /opt/network-api-gateway/.env
```

3. **Rate Limiting**

Update `app/main.py` to add rate limiting:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### Firewall Configuration

```bash
# Using UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Using firewalld (RHEL/CentOS)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### SSH Hardening

For accessing network devices:
```bash
# Generate SSH keys
ssh-keygen -t ed25519 -C "network-api-gateway"

# Configure SSH config
cat >> ~/.ssh/config << EOF
Host network-device-*
    StrictHostKeyChecking accept-new
    UserKnownHostsFile /opt/network-api-gateway/data/known_hosts
    IdentityFile /opt/network-api-gateway/data/ssh_key
EOF
```

## Monitoring & Logging

### Application Logging

Logs are written to:
- Console (stdout/stderr)
- Session logs: `/opt/network-api-gateway/session_logs/`

### Log Rotation

Create `/etc/logrotate.d/network-api-gateway`:

```
/opt/network-api-gateway/session_logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 netapi netapi
    sharedscripts
    postrotate
        systemctl reload network-api-gateway > /dev/null
    endscript
}
```

### Health Monitoring

Create monitoring script `/opt/network-api-gateway/healthcheck.sh`:

```bash
#!/bin/bash

ENDPOINT="http://localhost:8080/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT)

if [ "$RESPONSE" -eq 200 ]; then
    echo "OK: Application is healthy"
    exit 0
else
    echo "CRITICAL: Application health check failed (HTTP $RESPONSE)"
    exit 2
fi
```

Add to crontab:
```bash
*/5 * * * * /opt/network-api-gateway/healthcheck.sh
```

### Prometheus Metrics (Optional)

Install prometheus-fastapi-instrumentator:
```bash
pip install prometheus-fastapi-instrumentator
```

Update `app/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Access metrics at: `http://localhost:8080/metrics`

## Backup & Recovery

### Database Backup

**Important:** The database is stored in the `data/` directory to ensure persistence across container restarts.

For SQLite:
```bash
#!/bin/bash
# /opt/network-api-gateway/backup.sh

BACKUP_DIR="/opt/backups/network-api"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database (now in data/ directory)
cp /opt/network-api-gateway/data/network_gateway.db \
   $BACKUP_DIR/network_gateway_$DATE.db

# Backup .env
cp /opt/network-api-gateway/.env \
   $BACKUP_DIR/env_$DATE.bak

# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +7 -exec gzip {} \;

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Docker Backup:**
```bash
#!/bin/bash
# Backup for Docker deployment

BACKUP_DIR="/opt/backups/network-api"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup entire data directory (includes database)
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz \
    -C /path/to/network_cli_to_openapi data/

# Delete backups older than 30 days
find $BACKUP_DIR -name "data_backup_*.tar.gz" -mtime +30 -delete

echo "Docker backup completed: $DATE"
```

Schedule daily backups:
```bash
# Add to crontab
0 2 * * * /opt/network-api-gateway/backup.sh >> /var/log/network-api-backup.log 2>&1
```

### Recovery

```bash
# Stop service
sudo systemctl stop network-api-gateway

# Restore database
cp /opt/backups/network-api/network_gateway_YYYYMMDD_HHMMSS.db \
   /opt/network-api-gateway/network_gateway.db

# Restore .env
cp /opt/backups/network-api/env_YYYYMMDD_HHMMSS.bak \
   /opt/network-api-gateway/.env

# Fix permissions
chown netapi:netapi /opt/network-api-gateway/network_gateway.db
chown netapi:netapi /opt/network-api-gateway/.env
chmod 600 /opt/network-api-gateway/.env

# Start service
sudo systemctl start network-api-gateway
```

## Troubleshooting

### Common Issues

1. **Service won't start**
```bash
# Check logs
sudo journalctl -u network-api-gateway -n 50

# Check permissions
ls -la /opt/network-api-gateway/

# Verify Python environment
/opt/network-api-gateway/venv/bin/python --version
```

2. **Database errors**
```bash
# Check database file
ls -la /opt/network-api-gateway/network_gateway.db

# Test database connection
/opt/network-api-gateway/venv/bin/python -c "
from app.database import engine
import asyncio
asyncio.run(engine.connect())
"
```

3. **Network connectivity**
```bash
# Test device connectivity
ssh admin@device-ip

# Check firewall
sudo ufw status

# Verify network routes
ip route show
```

## Maintenance

### Updates

```bash
# Backup first!
/opt/network-api-gateway/backup.sh

# Pull latest code
cd /opt/network-api-gateway
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart network-api-gateway

# Verify
curl http://localhost:8080/health
```

### Database Migration

When switching to PostgreSQL:

```bash
# Export data from SQLite
python scripts/export_data.py

# Set up PostgreSQL
sudo apt install postgresql postgresql-contrib
sudo -u postgres createdb network_api

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/network_api

# Import data
python scripts/import_data.py

# Restart application
sudo systemctl restart network-api-gateway
```

## Support & Resources

- Documentation: `/docs` endpoint
- Health Check: `/health` endpoint  
- Logs: `/opt/network-api-gateway/session_logs/`
- System Logs: `journalctl -u network-api-gateway`

For issues: Check logs first, then review this guide's troubleshooting section.
