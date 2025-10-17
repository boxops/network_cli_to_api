# API Endpoints Reference

## Quick Reference Guide

Complete reference for all Network API Gateway endpoints with examples.

## Base URL

```
http://localhost:8080
```

## Authentication

All endpoints (except `/health`, `/ready`, and `/auth/login`) require JWT authentication.

### Get Authentication Token

```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Use token in subsequent requests:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}' | jq -r '.access_token')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/devices
```

---

## Device Management Endpoints

### List All Devices

**GET** `/devices`

Lists all configured network devices (excludes passwords and secrets).

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices | jq .
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "router-01",
    "host": "192.168.1.1",
    "device_type": "cisco_ios",
    "username": "admin",
    "port": 22,
    "timeout": 30,
    "session_log": false,
    "global_delay_factor": 1,
    "fast_cli": false,
    "conn_timeout": 10,
    "auth_timeout": null,
    "banner_timeout": 15,
    "read_timeout_override": null,
    "keepalive": 0,
    "description": "Core router",
    "is_active": true,
    "created_at": "2025-10-14T12:00:00",
    "updated_at": null
  }
]
```

### Get Device by ID/Name/IP

**GET** `/devices/{device_identifier}`

Retrieve specific device by ID, name, or IP address.

```bash
# By ID
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/1 | jq .

# By name
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/router-01 | jq .

# By IP
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/192.168.1.1 | jq .
```

### Create Device

**POST** `/devices`

Add a new network device (Admin or Operator role required).

```bash
curl -X POST http://localhost:8080/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "switch-01",
    "host": "192.168.1.10",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco123",
    "secret": "enable123",
    "port": 22,
    "timeout": 30,
    "session_log": false,
    "global_delay_factor": 1,
    "fast_cli": false,
    "conn_timeout": 10,
    "description": "Access switch"
  }' | jq .
```

**Required fields:**
- `name` - Unique device name
- `host` - IP address or hostname
- `device_type` - Platform type (see supported types below)
- `username` - SSH username
- `password` - SSH password

**Optional fields:**
- `secret` - Enable password (null/""/"password")
- `port` - SSH port (default: 22)
- `timeout` - Command timeout (default: 30)
- `session_log` - Enable session logging (default: false)
- `global_delay_factor` - Delay multiplier (default: 1)
- `fast_cli` - Fast mode (default: false)
- `conn_timeout` - Connection timeout (default: 10)
- `auth_timeout` - Authentication timeout (default: null)
- `banner_timeout` - Banner timeout (default: 15)
- `read_timeout_override` - Read timeout override (default: null)
- `keepalive` - Keepalive interval (default: 0)
- `description` - Device description

**Supported Device Types:**
- `cisco_ios`, `cisco_nxos`, `cisco_xe`, `cisco_asa`
- `juniper_junos`, `arista_eos`
- `hp_procurve`, `paloalto_panos`, `fortinet`
- `generic` - For any SSH device

### Update Device

**PUT** `/devices/{device_identifier}`

Update device configuration (Admin or Operator role required).

```bash
curl -X PUT http://localhost:8080/devices/switch-01 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "switch-01",
    "host": "192.168.1.10",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "newpassword",
    "fast_cli": true,
    "description": "Updated access switch"
  }' | jq .
```

### Delete Device

**DELETE** `/devices/{device_identifier}`

Remove a device from the system (Admin role required).

```bash
curl -X DELETE http://localhost:8080/devices/switch-01 \
  -H "Authorization: Bearer $TOKEN"
```

### Test Device Connection

**GET** `/devices/{device_identifier}/test`

Test SSH connectivity to a device.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/router-01/test | jq .
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "device_name": "router-01",
  "execution_time": 1.234,
  "prompt": "router-01#"
}
```

---

## Command Execution Endpoints

### Execute Single Command

**POST** `/devices/{device_identifier}/execute`

Execute a single command on a device.

```bash
curl -X POST http://localhost:8080/devices/router-01/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show version",
    "use_textfsm": false
  }' | jq .
```

**With TextFSM Parsing:**
```bash
curl -X POST http://localhost:8080/devices/router-01/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show ip interface brief",
    "use_textfsm": true
  }' | jq .
```

**Response:**
```json
{
  "success": true,
  "data": {
    "output": "...",
    "execution_time": 0.543
  },
  "metadata": {
    "device_id": 1,
    "device_name": "router-01",
    "command": "show version",
    "timestamp": "2025-10-14T12:00:00"
  }
}
```

### Execute Batch Commands

**POST** `/devices/{device_identifier}/execute-batch`

Execute multiple commands on a device.

```bash
curl -X POST http://localhost:8080/devices/router-01/execute-batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "show version",
      "show ip interface brief",
      "show ip route"
    ],
    "use_textfsm": true
  }' | jq .
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "command": "show version",
        "success": true,
        "output": "..."
      },
      {
        "command": "show ip interface brief",
        "success": true,
        "output": [...]
      }
    ],
    "execution_time": 2.145
  },
  "metadata": {
    "device_id": 1,
    "device_name": "router-01",
    "commands_count": 3,
    "timestamp": "2025-10-14T12:00:00"
  }
}
```

---

## Configuration Management Endpoints

### Get Device Configuration

**GET** `/devices/{device_identifier}/config`

Retrieve running configuration from a device.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/router-01/config | jq .
```

**Automatically uses correct command:**
- Cisco: `show running-config`
- Juniper: `show configuration`
- Arista: `show running-config`

**Response:**
```json
{
  "success": true,
  "data": {
    "output": "Building configuration...\n\nCurrent configuration : 1234 bytes\n!...",
    "execution_time": 1.234
  },
  "metadata": {
    "device_id": 1,
    "device_name": "router-01",
    "command": "show running-config",
    "timestamp": "2025-10-14T12:00:00"
  }
}
```

### Send Configuration Commands

**POST** `/devices/{device_identifier}/config`

Send configuration commands to a device (Operator or Admin role required).

```bash
# Add VLAN
curl -X POST http://localhost:8080/devices/switch-01/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "vlan 100",
      "name Engineering"
    ],
    "save_config": true
  }' | jq .

# Configure interface
curl -X POST http://localhost:8080/devices/router-01/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "interface GigabitEthernet0/1",
      "description Uplink to Core",
      "ip address 10.0.0.1 255.255.255.0",
      "no shutdown"
    ],
    "save_config": true
  }' | jq .

# Multiple config sections
curl -X POST http://localhost:8080/devices/router-01/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "hostname NEW-ROUTER-01",
      "ip domain-name example.com",
      "ntp server 10.0.0.100"
    ],
    "save_config": false
  }' | jq .
```

**Request Parameters:**
- `commands` - Array of configuration commands
- `save_config` - Save configuration after applying (default: true)

**Response:**
```json
{
  "success": true,
  "data": {
    "output": "configure terminal\nEnter configuration commands...\n",
    "execution_time": 2.345
  },
  "metadata": {
    "device_id": 1,
    "device_name": "switch-01",
    "timestamp": "2025-10-14T12:00:00"
  }
}
```

---

## Special Purpose Endpoints

### Get Interface Status

**GET** `/devices/{device_identifier}/interfaces`

Get parsed interface status using TextFSM.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/router-01/interfaces | jq .
```

**Automatically uses correct command:**
- Cisco/Arista: `show ip interface brief`
- Juniper: `show interfaces terse`

**Response (parsed with TextFSM):**
```json
{
  "success": true,
  "data": {
    "output": [
      {
        "interface": "GigabitEthernet0/0",
        "ip_address": "10.0.0.1",
        "status": "up",
        "protocol": "up"
      },
      {
        "interface": "GigabitEthernet0/1",
        "ip_address": "192.168.1.1",
        "status": "up",
        "protocol": "up"
      }
    ],
    "execution_time": 0.856
  },
  "metadata": {
    "device_id": 1,
    "device_name": "router-01",
    "command": "show ip interface brief",
    "timestamp": "2025-10-14T12:00:00"
  }
}
```

---

## User Management Endpoints

### Register New User

**POST** `/auth/register`

Create a new user account (Admin role required).

```bash
curl -X POST http://localhost:8080/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "email": "engineer1@example.com",
    "password": "securepassword",
    "role": "operator"
  }' | jq .
```

**Roles:**
- `read_only` - View devices and execute read-only commands
- `operator` - Read + create/update devices and send config
- `admin` - Full access including user management

### Get Current User

**GET** `/auth/me`

Get information about the currently authenticated user.

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/auth/me | jq .
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-10-14T10:00:00",
  "updated_at": null
}
```

---

## Health & Status Endpoints

### Health Check

**GET** `/health`

Check API health status (no authentication required).

```bash
curl http://localhost:8080/health | jq .
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T12:00:00.123456",
  "version": "0.1.0",
  "database": "connected"
}
```

### Readiness Check

**GET** `/ready`

Check if API is ready to handle requests (no authentication required).

```bash
curl http://localhost:8080/ready
```

**Response:**
```json
{"status": "ready"}
```

---

## Complete Examples

### Example 1: Add Device and Test

```bash
# Authenticate
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}' | jq -r '.access_token')

# Add device
curl -X POST http://localhost:8080/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "core-switch",
    "host": "10.0.0.1",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco123",
    "secret": "enable123"
  }' | jq .

# Test connection
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/core-switch/test | jq .

# Get interfaces
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/core-switch/interfaces | jq .
```

### Example 2: Configuration Workflow

```bash
# Get current config
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices/router-01/config > backup.json

# Send new config
curl -X POST http://localhost:8080/devices/router-01/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "interface GigabitEthernet0/2",
      "description New Link",
      "ip address 10.1.1.1 255.255.255.0",
      "no shutdown"
    ],
    "save_config": true
  }' | jq .

# Verify change
curl -X POST http://localhost:8080/devices/router-01/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show ip interface brief",
    "use_textfsm": true
  }' | jq .
```

### Example 3: Bulk Operations

```bash
# Get all devices
DEVICES=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/devices | jq -r '.[].name')

# Execute command on all devices
for device in $DEVICES; do
  echo "=== $device ==="
  curl -s -X POST http://localhost:8080/devices/$device/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "show version", "use_textfsm": false}' | jq -r '.data.output'
done
```

---

## Error Responses

### Authentication Error (401)
```json
{
  "detail": "Could not validate credentials"
}
```

### Authorization Error (403)
```json
{
  "detail": "Not enough permissions"
}
```

### Not Found (404)
```json
{
  "detail": "Device not found with identifier: router-99"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "device_type"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

### Server Error (500)
```json
{
  "detail": "Command execution failed"
}
```

---

## Rate Limiting

Currently no rate limiting implemented. Consider implementing for production:
- Per user: 100 requests/minute
- Per device: 10 commands/minute
- Config changes: 5/minute

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

## See Also

- [Main README](README.md)
- [Netmiko Parameters Guide](NETMIKO_PARAMETERS_GUIDE.md)
- [TextFSM Templates](templates/README.md)
- [MCP Server Guide](MCP_SERVER_GUIDE.md)
