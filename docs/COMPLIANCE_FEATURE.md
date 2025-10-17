# Configuration Compliance Checking

## Overview

The Configuration Compliance feature enables automated validation of configurations by comparing a backup/current configuration against an intended (desired) configuration. This is a **standalone configuration comparison tool** that requires no device interaction - you provide both configurations directly.

**Use Cases:**
- **Configuration Auditing** - Verify configurations match corporate standards
- **Change Validation** - Ensure changes were applied correctly  
- **Drift Detection** - Identify unauthorized configuration changes
- **Pre-deployment Validation** - Test configs before deployment
- **Compliance Reporting** - Generate reports for auditors
- **Security Posture** - Validate security configurations

## How It Works

```
┌─────────────────┐
│   API Request   │  ← backup config + intended config + features
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  netutils       │  ← Parse and compare configurations
│  Compliance     │     based on network_os type
│  Engine         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Compliance     │  ← Detailed results per feature:
│  Results        │     - missing lines
                        - extra lines
                        - Overall compliance
```

## API Endpoints

The compliance feature exposes three RESTful API endpoints (all under `/compliance`):

### 1. Check Configuration Compliance
- **Endpoint**: `POST /compliance/check`
- **Authentication**: Required (Bearer token)
- **Description**: Compare backup and intended configurations

**Request Body:**
```json
{
  "features": [
    {
      "name": "ntp",
      "ordered": true,
      "section": ["ntp"]
    }
  ],
  "backup": "ntp server 192.168.1.1\nntp server 192.168.1.2 prefer",
  "intended": "ntp server 192.168.1.1\nntp server 192.168.1.5 prefer",
  "network_os": "cisco_ios"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ntp": {
      "actual": "ntp server 192.168.1.1\nntp server 192.168.1.2 prefer",
      "intended": "ntp server 192.168.1.1\nntp server 192.168.1.5 prefer",
      "missing": "ntp server 192.168.1.5 prefer",
      "extra": "ntp server 192.168.1.2 prefer",
      "compliant": false,
      "ordered_compliant": false,
      "unordered_compliant": false,
      "cannot_parse": false
    }
  },
  "metadata": {
    "network_os": "cisco_ios",
    "timestamp": "2025-10-17T12:00:00",
    "overall_compliant": false,
    "total_features": 1,
    "compliant_features": 0,
    "non_compliant_features": 1
  }
}
```

### 2. Get Feature Examples

**GET** `/compliance/features`

Get pre-defined feature templates for common use cases.

**Response:**
```json
{
  "features": [
    {
      "name": "hostname",
      "ordered": true,
      "section": ["hostname"],
      "description": "Device hostname configuration"
    },
    {
      "name": "ntp",
      "ordered": true,
      "section": ["ntp"],
      "description": "NTP server configuration"
    }
  ],
  "count": 10
}
```

### 3. Get Supported Platforms

**GET** `/compliance/supported-platforms`

List network platforms that support compliance checking.

**Response:**
```json
{
  "platforms": [
    "cisco_ios",
    "cisco_nxos",
    "cisco_xe",
    "cisco_asa",
    "arista_eos",
    "juniper_junos",
    "paloalto_panos",
    "fortinet",
    "hp_procurve",
    "generic"
  ],
  "count": 10
}
```

## Core Concepts

### Features

A **feature** defines a specific aspect of configuration to check:

```json
{
  "name": "ntp",
  "ordered": true,
  "section": ["ntp"]
}
```

**Components:**
- `name` - Identifier for the feature (e.g., "ntp", "snmp", "interfaces")
- `ordered` - Whether line order matters (`true`) or not (`false`)
- `section` - Configuration prefixes to match (e.g., `["ntp"]`, `["interface"]`)

### Ordered vs Unordered

**Ordered (`true`)** - Line sequence matters:
```
# Compliant
ntp server 10.0.0.1
ntp server 10.0.0.2

# Non-compliant (wrong order)
ntp server 10.0.0.2
ntp server 10.0.0.1
```

**Unordered (`false`)** - Lines can be in any order:
```
# Both compliant
access-list 10 permit 10.0.0.0 0.255.255.255
access-list 10 permit 192.168.1.0 0.0.0.255

# Also compliant (different order)
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 permit 10.0.0.0 0.255.255.255
```

### Compliance States

Each feature returns multiple compliance indicators:

- **`compliant`** - Overall compliance (ordered if ordered=true, else unordered)
- **`ordered_compliant`** - Strict compliance including line order
- **`unordered_compliant`** - Compliance ignoring line order
- **`missing`** - Lines in intended but not in backup
- **`extra`** - Lines in backup but not in intended
- **`cannot_parse`** - Whether parsing encountered issues

## Usage Examples

### Example 1: Basic NTP Compliance Check

```bash
# Get authentication token
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}' | jq -r '.access_token')

# Check NTP configuration compliance
curl -X POST http://localhost:8080/compliance/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {
        "name": "ntp",
        "ordered": true,
        "section": ["ntp"]
      }
    ],
    "backup": "ntp server 192.168.1.1\nntp server 192.168.1.2 prefer",
    "intended": "ntp server 192.168.1.1\nntp server 192.168.1.5 prefer",
    "network_os": "cisco_ios"
  }' | jq .
```

### Example 2: Multi-Feature Compliance Check

```bash
curl -X POST http://localhost:8080/compliance/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {
        "name": "hostname",
        "ordered": true,
        "section": ["hostname"]
      },
      {
        "name": "ntp",
        "ordered": true,
        "section": ["ntp"]
      },
      {
        "name": "snmp",
        "ordered": false,
        "section": ["snmp-server"]
      },
      {
        "name": "logging",
        "ordered": false,
        "section": ["logging"]
      }
    ],
    "backup": "hostname SWITCH-01\nntp server 10.0.0.1\nsnmp-server community public RO\nlogging host 10.0.1.100",
    "intended": "hostname SWITCH-01\nntp server 10.0.0.1\nsnmp-server community public RO\nlogging host 10.0.1.100",
    "network_os": "cisco_ios"
  }' | jq .
```

### Example 3: Interface Configuration Compliance

```bash
curl -X POST http://localhost:8080/compliance/check \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [
      {
        "name": "GigabitEthernet0/0",
        "ordered": false,
        "section": ["interface GigabitEthernet0/0"]
      },
      {
        "name": "GigabitEthernet0/1",
        "ordered": false,
        "section": ["interface GigabitEthernet0/1"]
      }
    ],
    "backup": "interface GigabitEthernet0/0\n ip address 10.0.0.1 255.255.255.0\n no shutdown",
    "intended": "interface GigabitEthernet0/0\n ip address 10.0.0.1 255.255.255.0\n no shutdown\n description WAN",
    "network_os": "cisco_ios"
  }' | jq .
```

### Example 4: Using Python

```python
import requests
import json

# Configuration
API_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "changeme"

# Step 1: Authenticate
auth_response = requests.post(
    f"{API_URL}/auth/login",
    json={"username": USERNAME, "password": PASSWORD}
)
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Step 2: Define compliance check
compliance_request = {
    "features": [
        {
            "name": "ntp",
            "ordered": True,
            "section": ["ntp"]
        },
        {
            "name": "snmp",
            "ordered": False,
            "section": ["snmp-server"]
        }
    ],
    "backup": "ntp server 10.0.0.1\nsnmp-server community public RO",
    "intended": "ntp server 10.0.0.1\nntp server 10.0.0.2\nsnmp-server community private RW",
    "network_os": "cisco_ios"
}

# Step 3: Check compliance
response = requests.post(
    f"{API_URL}/compliance/check",
    headers=headers,
    json=compliance_request
)

result = response.json()

# Step 4: Process results
if result["success"]:
    print(f"Overall Compliant: {result['metadata']['overall_compliant']}")
    print(f"Features Checked: {result['metadata']['total_features']}")
    
    for feature_name, feature_result in result["data"].items():
        print(f"\n{feature_name}:")
        print(f"  Compliant: {feature_result['compliant']}")
        if not feature_result['compliant']:
            print(f"  Missing: {feature_result['missing']}")
            print(f"  Extra: {feature_result['extra']}")
```

## Common Feature Definitions

Here are pre-defined feature templates for common use cases (available via `/compliance/features`):

### 1. Hostname
```json
{
  "name": "hostname",
  "ordered": true,
  "section": ["hostname"],
  "description": "Device hostname configuration"
}
```

### 2. NTP Servers
```json
{
  "name": "ntp",
  "ordered": true,
  "section": ["ntp"],
  "description": "NTP server configuration"
}
```

### 3. SNMP
```json
{
  "name": "snmp",
  "ordered": false,
  "section": ["snmp-server"],
  "description": "SNMP configuration"
}
```

### 4. Logging
```json
{
  "name": "logging",
  "ordered": false,
  "section": ["logging"],
  "description": "Logging and syslog configuration"
}
```

### 5. AAA (Authentication, Authorization, Accounting)
```json
{
  "name": "aaa",
  "ordered": true,
  "section": ["aaa"],
  "description": "AAA configuration"
}
```

### 6. Interfaces
```json
{
  "name": "interfaces",
  "ordered": false,
  "section": ["interface"],
  "description": "Interface configurations"
}
```

### 7. Routing
```json
{
  "name": "routing",
  "ordered": false,
  "section": ["ip route", "router"],
  "description": "Static and dynamic routing"
}
```

### 8. Access Lists
```json
{
  "name": "acl",
  "ordered": true,
  "section": ["access-list", "ip access-list"],
  "description": "Access control lists"
}
```

### 9. VLANs
```json
{
  "name": "vlan",
  "ordered": false,
  "section": ["vlan"],
  "description": "VLAN configuration"
}
```

### 10. Banner
```json
{
  "name": "banner",
  "ordered": true,
  "section": ["banner"],
  "description": "Login and MOTD banners"
}
```

## Supported Network Operating Systems

The following platforms are supported (via `/compliance/supported-platforms`):

| Platform | Network OS Value | Common Devices |
|----------|-----------------|----------------|
| Cisco IOS | `cisco_ios` | Routers, Switches (Catalyst 2960, 3850, ISR) |
| Cisco NX-OS | `cisco_nxos` | Nexus switches (5k, 7k, 9k) |
| Cisco IOS-XE | `cisco_xe` | Catalyst 9000, ISR 4000 |
| Cisco ASA | `cisco_asa` | ASA Firewalls |
| Arista EOS | `arista_eos` | Arista switches |
| Juniper Junos | `juniper_junos` | Juniper routers/switches |
| Palo Alto PAN-OS | `paloalto_panos` | PA firewalls |
| Fortinet | `fortinet` | FortiGate firewalls |
| HP ProCurve | `hp_procurve` | HP switches |
| Generic | `generic` | Fallback for other platforms |

## Use Cases

### 1. Pre-Deployment Configuration Validation

Before deploying configuration changes:

```python
# Compare current config vs proposed config
compliance_check = {
    "features": [...],
    "backup": current_running_config,
    "intended": proposed_new_config,
    "network_os": "cisco_ios"
}
# Verify changes are correct before deployment
```

### 2. Post-Change Validation

After applying changes:

```python
# Fetch new running config from device (using /devices/{id}/config endpoint)
# Compare against intended config
# Verify all changes were applied successfully
```

### 3. Configuration Drift Detection

Periodic audits:

```python
# Compare current config vs baseline/standard
# Identify unauthorized changes
# Generate compliance reports
```

### 4. Security Compliance Auditing

Validate security features:

```python
features = [
    {"name": "aaa", "ordered": True, "section": ["aaa"]},
    {"name": "banner", "ordered": True, "section": ["banner"]},
    {"name": "acl", "ordered": True, "section": ["access-list"]}
]
# Check security configs meet corporate policy
```

### 5. Multi-Device Standardization

Ensure consistency across fleet:

```python
# Use same intended config as baseline
# Check all devices against baseline
# Report devices that are non-compliant
```

## Best Practices

### 1. Feature Granularity

**Good** - Specific features:
```json
[
  {"name": "ntp", "section": ["ntp"]},
  {"name": "snmp", "section": ["snmp-server"]}
]
```

**Avoid** - Too broad:
```json
[
  {"name": "everything", "section": [""]}  // Too generic
]
```

### 2. Ordered vs Unordered

- Use `ordered: true` for:
  - Access lists (order matters for permit/deny)
  - AAA configuration
  - Route maps
  - Banners

- Use `ordered: false` for:
  - SNMP settings
  - Logging hosts
  - Interface configs
  - VLANs

### 3. Section Prefixes

Be specific with section prefixes:

```json
// Good - Specific interface
{"name": "Gi0/0", "section": ["interface GigabitEthernet0/0"]}

// Better - All GigabitEthernet interfaces
{"name": "gigabit_interfaces", "section": ["interface GigabitEthernet"]}
```

### 4. Configuration Format

Ensure configurations are properly formatted:
- Remove timestamps/comments
- Normalize whitespace
- Use consistent line endings (`\n`)

### 5. Error Handling

Always check the response:

```python
if result["success"]:
    if result["metadata"]["overall_compliant"]:
        print("✓ All features compliant")
    else:
        print(f"✗ {result['metadata']['non_compliant_features']} features non-compliant")
        # Handle non-compliance
else:
    print("Error in compliance check")
```

## Troubleshooting

### Issue: `cannot_parse: true`

**Cause**: Configuration doesn't match expected format for network_os

**Solution**:
- Verify `network_os` is correct
- Check configuration format matches platform
- Try `network_os: "generic"` as fallback

### Issue: False positives (compliant when shouldn't be)

**Cause**: Section prefix too broad or incorrect

**Solution**:
```json
// Instead of
{"section": ["ntp"]}

// Be more specific
{"section": ["ntp server"]}
```

### Issue: Features showing empty actual/intended

**Cause**: Section prefix doesn't match any config lines

**Solution**:
- Review backup/intended configs
- Verify section prefix matches actual command syntax
- Check for typos in section names

### Issue: All features non-compliant

**Cause**: Configuration format mismatch or encoding issues

**Solution**:
- Ensure consistent line endings (`\n`)
- Remove extra whitespace
- Verify configurations are plain text (not base64)

## Integration Tips

### With Existing Config Management

```python
# Example: Integration with Git-stored configs
import os

# Read configs from files
with open('configs/backup/router01.txt') as f:
    backup_config = f.read()

with open('configs/intended/router01.txt') as f:
    intended_config = f.read()

# Run compliance check
result = check_compliance(backup_config, intended_config, "cisco_ios")
```

### Combined with Device Config Retrieval

```python
# Step 1: Get config from device using API
device_config_response = requests.post(
    f"{API_URL}/devices/router-01/config",
    headers=headers,
    json={"commands": ["show running-config"]}
)
backup_config = device_config_response.json()["data"]["show running-config"]["output"]

# Step 2: Compare with intended config
compliance_result = requests.post(
    f"{API_URL}/compliance/check",
    headers=headers,
    json={
        "features": STANDARD_FEATURES,
        "backup": backup_config,
        "intended": INTENDED_CONFIG,
        "network_os": "cisco_ios"
    }
)
```

### Workflow Automation

```python
# Example: Automated compliance checking
def audit_device_config(backup_config, intended_config, network_os):
    """Run compliance check and return results"""
    result = api.check_compliance(
        features=STANDARD_FEATURES,
        backup=backup_config,
        intended=intended_config,
        network_os=network_os
    )
    
    # Log results
    if not result["metadata"]["overall_compliant"]:
        send_alert(f"Device non-compliant: {result}")
    
    return result
```

### Reporting

```python
# Generate compliance report
def generate_compliance_report(results):
    """Create compliance report from results"""
    report = {
        "timestamp": results["metadata"]["timestamp"],
        "overall_status": "PASS" if results["metadata"]["overall_compliant"] else "FAIL",
        "summary": {
            "total": results["metadata"]["total_features"],
            "compliant": results["metadata"]["compliant_features"],
            "non_compliant": results["metadata"]["non_compliant_features"]
        },
        "details": []
    }
    
    for feature, data in results["data"].items():
        if not data["compliant"]:
            report["details"].append({
                "feature": feature,
                "missing": data["missing"],
                "extra": data["extra"]
            })
    
    return report
```

## API Reference Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/compliance/check` | POST | Yes | Check config compliance |
| `/compliance/features` | GET | Yes | Get feature examples |
| `/compliance/supported-platforms` | GET | Yes | Get supported platforms |

## Related Documentation

- [API Endpoints](API_ENDPOINTS.md) - Complete API reference
- [Getting Started](GETTING_STARTED.md) - Initial setup guide
- [Netmiko Parameters](NETMIKO_PARAMETERS_GUIDE.md) - Device connection parameters
- [MCP Server Guide](MCP_SERVER_GUIDE.md) - AI agent integration

## Additional Resources

- [netutils Documentation](https://netutils.readthedocs.io/)
- [netutils Compliance](https://netutils.readthedocs.io/en/latest/user/lib_use_cases/config_compliance/)
- [Configuration Management Best Practices](https://www.ciscolive.com/)
