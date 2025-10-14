# Netmiko Connection Parameters Guide

## Overview

This guide documents the extended Netmiko ConnectHandler parameters available for device management in the Network API Gateway. These parameters provide fine-grained control over SSH connections and command execution behavior.

## Device Parameters

### Basic Connection Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | *required* | Unique device name (1-100 chars) |
| `host` | string | *required* | IP address or hostname (1-255 chars) |
| `device_type` | string | *required* | Device platform (see supported types below) |
| `username` | string | *required* | SSH username (1-100 chars) |
| `password` | string | *required* | SSH password (min 1 char) |
| `secret` | string\|null | `null` | Enable mode secret (see Enable Mode section) |
| `port` | integer | `22` | SSH port (1-65535) |
| `timeout` | integer | `30` | Command timeout in seconds (1-300) |
| `session_log` | boolean | `false` | Enable session logging to file |

### Advanced Netmiko Parameters

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `global_delay_factor` | integer | `1` | 1-10 | Multiplier for all delays (increase for slow devices) |
| `fast_cli` | boolean | `false` | - | Disable delays for faster execution |
| `conn_timeout` | integer | `10` | 1-120 | TCP connection timeout in seconds |
| `auth_timeout` | integer\|null | `null` | 1-120 | Authentication phase timeout in seconds |
| `banner_timeout` | integer | `15` | 1-120 | Banner read timeout in seconds |
| `read_timeout_override` | integer\|null | `null` | 1-300 | Override read timeout for all operations |
| `keepalive` | integer | `0` | 0-300 | SSH keepalive interval in seconds (0=disabled) |

## Enable Mode Secret

The `secret` parameter controls enable mode behavior with three distinct states:

### 1. No Enable Mode (`secret: null`)
Device does not require enable mode or you don't want to enter it.

```json
{
  "secret": null
}
```

**Use case**: Devices that don't have enable mode (Linux servers, some network devices)

### 2. Enable Without Password (`secret: ""`)
Device requires entering enable mode, but no password is needed.

```json
{
  "secret": ""
}
```

**Use case**: Devices configured with `enable secret` that is blank

### 3. Enable With Password (`secret: "password123"`)
Device requires enable mode with a specific password.

```json
{
  "secret": "myenablesecret"
}
```

**Use case**: Most production network devices with enable passwords configured

## Supported Device Types

- `cisco_ios` - Cisco IOS devices
- `cisco_nxos` - Cisco Nexus devices
- `cisco_xe` - Cisco IOS-XE devices
- `cisco_asa` - Cisco ASA firewalls
- `juniper_junos` - Juniper Junos devices
- `arista_eos` - Arista EOS devices
- `hp_procurve` - HP ProCurve switches
- `paloalto_panos` - Palo Alto PAN-OS firewalls
- `fortinet` - Fortinet FortiGate firewalls
- `generic` - Generic SSH devices (use this for unsupported platforms)

## Parameter Usage Examples

### Example 1: Basic Arista Device
```json
{
  "name": "ceos01",
  "host": "172.20.20.2",
  "device_type": "arista_eos",
  "username": "admin",
  "password": "admin",
  "secret": "",
  "port": 22,
  "timeout": 30,
  "session_log": false,
  "description": "Arista cEOS lab device"
}
```

### Example 2: Slow Cisco Device with Increased Delays
```json
{
  "name": "old-router",
  "host": "192.168.1.1",
  "device_type": "cisco_ios",
  "username": "admin",
  "password": "cisco123",
  "secret": "enable123",
  "global_delay_factor": 3,
  "fast_cli": false,
  "conn_timeout": 30,
  "auth_timeout": 60,
  "description": "Legacy router - needs longer timeouts"
}
```

### Example 3: Fast Modern Device
```json
{
  "name": "nexus-core",
  "host": "10.0.0.1",
  "device_type": "cisco_nxos",
  "username": "netadmin",
  "password": "securepass",
  "secret": null,
  "fast_cli": true,
  "global_delay_factor": 1,
  "keepalive": 30,
  "description": "Core Nexus switch - optimized for speed"
}
```

### Example 4: Device Behind Slow WAN Link
```json
{
  "name": "remote-site",
  "host": "203.0.113.50",
  "device_type": "cisco_ios",
  "username": "admin",
  "password": "remote123",
  "secret": "enable123",
  "conn_timeout": 60,
  "timeout": 120,
  "read_timeout_override": 120,
  "keepalive": 60,
  "description": "Remote site over slow WAN - extended timeouts"
}
```

### Example 5: Generic Linux Server
```json
{
  "name": "jumphost",
  "host": "10.1.1.100",
  "device_type": "generic",
  "username": "sysadmin",
  "password": "linux123",
  "secret": null,
  "port": 22,
  "session_log": true,
  "description": "Linux jump host"
}
```

## Creating Devices via API

### Using cURL

```bash
# Get authentication token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}' \
  | jq -r '.access_token')

# Create device
curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "router01",
    "host": "192.168.1.1",
    "device_type": "cisco_ios",
    "username": "admin",
    "password": "cisco123",
    "secret": "enable123",
    "fast_cli": true,
    "global_delay_factor": 1
  }'
```

### Using Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "admin", "password": "changeme"}
)
token = response.json()["access_token"]

# Create device
headers = {"Authorization": f"Bearer {token}"}
device_data = {
    "name": "switch01",
    "host": "10.0.0.10",
    "device_type": "arista_eos",
    "username": "admin",
    "password": "admin",
    "secret": "",
    "port": 22,
    "timeout": 30,
    "fast_cli": True,
    "global_delay_factor": 1,
    "conn_timeout": 10,
    "keepalive": 30,
    "description": "Access switch"
}

response = requests.post(
    "http://localhost:8000/devices",
    headers=headers,
    json=device_data
)
device = response.json()
print(f"Created device: {device['name']} (ID: {device['id']})")
```

## Parameter Tuning Guidelines

### When to Increase `global_delay_factor`

- Devices with slow processors or heavy CPU load
- Commands that take a long time to complete
- Devices that occasionally drop characters
- Terminal server connections

**Recommended values:**
- Normal devices: `1`
- Slower devices: `2-3`
- Very slow devices: `4-5`

### When to Enable `fast_cli`

- Modern devices with fast processors
- Lab environments where speed is important
- Devices with minimal latency

**Warning**: May cause issues on slower devices or over high-latency links.

### When to Adjust Timeouts

| Timeout Parameter | Increase When | Typical Value |
|-------------------|---------------|---------------|
| `conn_timeout` | Device takes long to respond to TCP SYN | 10-30s |
| `auth_timeout` | Authentication is slow (AAA, RADIUS, TACACS+) | 30-60s |
| `banner_timeout` | Large or slow-loading banners | 15-30s |
| `timeout` | Commands take long to execute | 30-120s |
| `read_timeout_override` | Global read timeout for all operations | 60-300s |

### When to Use `keepalive`

- Long-running operations that may trigger idle timeouts
- Connections through firewalls or NAT devices
- Intermittent network issues

**Recommended value**: `30-60` seconds for production, `0` (disabled) for lab

## API Response Example

When you retrieve a device, all parameters are returned (except sensitive data like `password` and `secret`):

```json
{
  "id": 1,
  "name": "ceos01",
  "host": "172.20.20.2",
  "device_type": "arista_eos",
  "username": "admin",
  "port": 22,
  "timeout": 30,
  "session_log": false,
  "global_delay_factor": 1,
  "fast_cli": true,
  "conn_timeout": 10,
  "auth_timeout": 30,
  "banner_timeout": 15,
  "read_timeout_override": null,
  "keepalive": 0,
  "description": "Arista cEOS device with enable mode (no secret)",
  "is_active": true,
  "created_at": "2025-10-14T18:23:58",
  "updated_at": null
}
```

## Updating Device Parameters

You can update any parameter (including Netmiko parameters) using PATCH:

```bash
curl -X PATCH http://localhost:8000/devices/ceos01 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fast_cli": false,
    "global_delay_factor": 2,
    "timeout": 60
  }'
```

## Troubleshooting

### Connection Timeouts

**Symptom**: "Connection timeout" errors

**Solution**:
1. Increase `conn_timeout` to 30-60 seconds
2. Verify network connectivity
3. Check firewall rules

### Authentication Failures

**Symptom**: "Authentication failed" errors

**Solution**:
1. Verify credentials
2. Increase `auth_timeout` if using external AAA
3. Check enable secret if applicable

### Command Execution Timeouts

**Symptom**: Commands timeout before completing

**Solution**:
1. Increase `timeout` parameter
2. Use `read_timeout_override` for global increase
3. Increase `global_delay_factor` for slow devices

### Garbled or Incomplete Output

**Symptom**: Command output is truncated or corrupted

**Solution**:
1. Increase `global_delay_factor` to 2-3
2. Disable `fast_cli` if enabled
3. Increase `banner_timeout` and `timeout`

## Best Practices

1. **Start with defaults**: Use default parameters first, only tune if needed
2. **Enable session logging** during troubleshooting (`session_log: true`)
3. **Use descriptive names**: Include location, role, or function in device name
4. **Document special settings**: Use `description` field to note why non-default values are used
5. **Test in lab first**: Validate parameter combinations in non-production environments
6. **Monitor performance**: Track command execution times to optimize settings
7. **Secure secrets**: Change default admin password immediately in production

## Migration from Existing Database

If you have an existing database without the new parameters, run the migration:

```bash
# Inside Docker container
docker exec -it network-api-gateway bash
python migrations/add_netmiko_parameters.py

# Verify
python migrations/add_netmiko_parameters.py --verify
```

See `migrations/README.md` for detailed migration instructions.

## Additional Resources

- [Netmiko Documentation](https://github.com/ktbyers/netmiko)
- [TextFSM Templates](templates/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Main README](README.md)
