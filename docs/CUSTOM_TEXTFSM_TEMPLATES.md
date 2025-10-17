# Custom TextFSM Templates Feature

## Overview

The Network API Gateway now supports **custom TextFSM templates** that take priority over Netmiko's built-in parsers. This powerful feature allows you to:

- ✅ Parse output from any device, even those not supported by Netmiko
- ✅ Override Netmiko's built-in templates with your own parsing logic
- ✅ Support custom/proprietary devices using the `generic` device type
- ✅ Create templates for new commands not yet supported by Netmiko
- ✅ Share templates across your organization

## Quick Start

### 1. Create a Custom Template

Create a file in the `templates/` directory following the naming convention:

**Filename:** `templates/cisco_ios_show_ip_interface_brief.textfsm`

```textfsm
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+|unassigned)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

### 2. Use the Template

```bash
curl -X POST "http://localhost:8080/devices/myswitch/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show ip interface brief",
    "use_textfsm": true
  }'
```

The system will automatically use your custom template!

## How It Works

### Template Priority System

When you execute a command with `"use_textfsm": true`:

```
┌─────────────────────────────────────────┐
│  1. Check for Custom Template           │
│     templates/{device_type}_{command}   │
└────────────┬────────────────────────────┘
             │
             ▼
        ┌─────────┐
        │ Found?  │
        └────┬────┘
             │
      ┌──────┴──────┐
      │             │
     YES            NO
      │             │
      ▼             ▼
┌───────────┐  ┌──────────────────┐
│ Use       │  │ Use Netmiko      │
│ Custom    │  │ Built-in         │
│ Template  │  │ (if available)   │
└───────────┘  └──────────────────┘
```

### Template Naming Convention

**Pattern:** `{device_type}_{command_with_underscores}.textfsm`

The system automatically:
1. Converts command to lowercase
2. Replaces spaces with underscores
3. Preserves hyphens and other characters
4. Looks for matching template file

**Examples:**

| Device Type | Command | Template Filename |
|-------------|---------|-------------------|
| `cisco_ios` | `show ip route` | `cisco_ios_show_ip_route.textfsm` |
| `cisco_ios` | `show access-list` | `cisco_ios_show_access-list.textfsm` |
| `arista_eos` | `show version` | `arista_eos_show_version.textfsm` |
| `generic` | `display interface` | `generic_display_interface.textfsm` |
| `juniper_junos` | `show configuration` | `juniper_junos_show_configuration.textfsm` |

## Supported Device Types

The API now supports the following device types:

### Production Device Types
- `cisco_ios` - Cisco IOS devices
- `cisco_nxos` - Cisco Nexus switches
- `cisco_xe` - Cisco IOS-XE devices
- `cisco_asa` - Cisco ASA firewalls
- `juniper_junos` - Juniper JunOS devices
- `arista_eos` - Arista EOS switches
- `hp_procurve` - HP ProCurve switches
- `paloalto_panos` - Palo Alto PAN-OS firewalls
- `fortinet` - Fortinet FortiGate firewalls

### Generic Device Type
- `generic` - **Any device** (requires custom templates for parsing)

> The `generic` type is a special device type that relies entirely on custom TextFSM templates for command parsing.

## Using the Generic Device Type

The `generic` device type allows you to connect to **any** device that supports SSH:

### 1. Add a Generic Device

```bash
curl -X POST "http://localhost:8080/devices" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-device",
    "host": "192.168.1.100",
    "device_type": "generic",
    "username": "admin",
    "password": "password",
    "description": "Custom proprietary device"
  }'
```

### 2. Create a Template for Your Device

**File:** `templates/generic_show_status.textfsm`

```textfsm
Value HOSTNAME (\S+)
Value STATUS (active|inactive|degraded)
Value UPTIME (.+)
Value VERSION (\S+)

Start
  ^Hostname:\s+${HOSTNAME}
  ^Status:\s+${STATUS}
  ^Uptime:\s+${UPTIME}
  ^Software Version:\s+${VERSION} -> Record
```

### 3. Execute Commands

```bash
curl -X POST "http://localhost:8080/devices/custom-device/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show status",
    "use_textfsm": true
  }'
```

**Response:**

```json
{
  "success": true,
  "data": {
    "output": [
      {
        "HOSTNAME": "custom-device-01",
        "STATUS": "active",
        "UPTIME": "45 days, 3 hours, 22 minutes",
        "VERSION": "2.5.1"
      }
    ],
    "execution_time": 0.523
  },
  "metadata": {
    "device_id": 5,
    "device_name": "custom-device",
    "command": "show status",
    "timestamp": "2025-10-14T15:30:00.000000"
  }
}
```

## Template Development

### Basic Template Structure

```textfsm
# 1. VALUE DEFINITIONS - What data to extract
Value Required FIELD_NAME (regex_pattern)
Value OPTIONAL_FIELD (regex_pattern)
Value List REPEATING_FIELD (regex_pattern)

# 2. STATE MACHINE - How to parse
Start
  ^Pattern with ${FIELD_NAME} placeholders -> Record
  ^Another pattern -> Continue
  ^Error pattern -> Error
```

### Value Options

| Option | Description | Example |
|--------|-------------|---------|
| `Value` | Single value | `Value HOSTNAME (\S+)` |
| `Required` | Must match for valid record | `Value Required INTERFACE (\S+)` |
| `List` | Can have multiple values | `Value List IP_ADDRESS (\S+)` |
| `Filldown` | Carries to next record | `Value Filldown VRF (\S+)` |

### State Actions

| Action | Description |
|--------|-------------|
| `-> Record` | Save current values as a record |
| `-> Continue` | Continue matching in current state |
| `-> Next` | Move to next state |
| `-> Error` | Mark as error and stop |

### Complete Example

**Command Output (Cisco IOS):**
```
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1     10.0.0.1        YES NVRAM  up                    up
GigabitEthernet0/2     unassigned      YES NVRAM  administratively down down
```

**Template:** `cisco_ios_show_ip_interface_brief.textfsm`
```textfsm
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+|unassigned)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

**Parsed Output:**
```json
[
  {
    "INTERFACE": "GigabitEthernet0/0",
    "IP_ADDRESS": "192.168.1.1",
    "STATUS": "up",
    "PROTOCOL": "up"
  },
  {
    "INTERFACE": "GigabitEthernet0/1",
    "IP_ADDRESS": "10.0.0.1",
    "STATUS": "up",
    "PROTOCOL": "up"
  },
  {
    "INTERFACE": "GigabitEthernet0/2",
    "IP_ADDRESS": "unassigned",
    "STATUS": "administratively down",
    "PROTOCOL": "down"
  }
]
```

## Advanced Features

### Batch Commands with Custom Templates

```bash
curl -X POST "http://localhost:8080/devices/myswitch/execute-batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "show ip interface brief",
      "show version",
      "show ip route"
    ],
    "use_textfsm": true
  }'
```

Each command will:
1. Check for custom template
2. Use custom template if found
3. Fall back to Netmiko built-in if not found

### Template Metadata in Response

When using custom templates, the response includes metadata showing which parser was used:

```json
{
  "command": "show ip interface brief",
  "success": true,
  "output": [...],
  "parsed_with": "custom_template"
}
```

Possible values:
- `custom_template` - Used your custom template
- `netmiko_builtin` - Used Netmiko's built-in template
- `none` - No parsing (raw text output)

## Testing Templates

### Method 1: Python Script

```python
import textfsm

# Load template
with open('templates/cisco_ios_show_version.textfsm') as f:
    template = textfsm.TextFSM(f)

# Load sample output
with open('test_output.txt') as f:
    output = f.read()

# Parse
result = template.ParseText(output)
headers = template.header

# Display
for row in result:
    print(dict(zip(headers, row)))
```

### Method 2: Online Tester

Use [TextFSM Online Tester](https://textfsm.nornir.tech/):
1. Paste your template
2. Paste sample output
3. See parsed results immediately

### Method 3: Via API

```bash
# Test with real device
curl -X POST "http://localhost:8080/devices/testdevice/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "show version",
    "use_textfsm": true
  }'
```

## Best Practices

### 1. Template Organization

```
templates/
├── README.md                           # Documentation
├── cisco_ios_show_ip_interface_brief.textfsm
├── cisco_ios_show_ip_route.textfsm
├── cisco_ios_show_version.textfsm
├── arista_eos_show_version.textfsm
├── generic_show_custom_command.textfsm
└── .gitkeep                            # Keep directory in git
```

### 2. Template Testing

Always test templates with:
- ✅ Multiple device software versions
- ✅ Different output variations
- ✅ Edge cases (empty results, errors)
- ✅ Maximum and minimum data

### 3. Error Handling

Templates automatically fall back to Netmiko if:
- Template file doesn't exist
- Template parsing fails
- Regex doesn't match

### 4. Version Control

- Keep templates in Git
- Document regex patterns with comments
- Include sample output in comments
- Version templates when device OS changes

### 5. Naming Conventions

```python
# Good
cisco_ios_show_ip_route.textfsm
generic_display_system_status.textfsm

# Bad
ShowIPRoute.textfsm
template1.textfsm
cisco-ios-show-ip-route.textfsm
```

## Troubleshooting

### Template Not Loading

**Problem:** Template exists but isn't being used

**Solutions:**
1. Check filename matches exactly: `{device_type}_{command}.textfsm`
2. Verify command normalization (spaces → underscores, lowercase)
3. Check file is in `templates/` directory
4. Review logs: `docker logs network-api-gateway | grep template`

### Template Syntax Error

**Problem:** Template has parsing errors

**Solutions:**
1. Test template with online TextFSM tester
2. Validate regex patterns
3. Check for missing `Start` state
4. Verify all Value definitions have regex

### Wrong Output Format

**Problem:** Parsed output doesn't match expected format

**Solutions:**
1. Check device output matches your regex
2. Test with actual device output, not examples
3. Use `Value List` for repeating fields
4. Add `Filldown` for hierarchical data

### Custom Template Not Found

**Problem:** System uses Netmiko instead of custom template

**Check:**
```bash
# List available templates
ls -la templates/

# Check what system is looking for
# Device type: cisco_ios
# Command: "show ip route"
# Looking for: cisco_ios_show_ip_route.textfsm
```

## Performance Considerations

### Template Caching

- Templates are loaded on-demand
- Parsed on first use
- Minimal performance impact

### Large Outputs

For commands with large output:
- Use specific regex patterns
- Avoid greedy regex (`.+` when `\S+` works)
- Test template performance

### Concurrent Usage

- Templates are thread-safe
- No locking required
- Safe for concurrent command execution

## Migration Guide

### From Netmiko Built-in to Custom

If you want to override Netmiko's built-in template:

1. **Find the command** you want to override
2. **Create custom template** with same device_type and command
3. **Your template takes priority** automatically

Example:
```bash
# Netmiko has built-in for "show version"
# Create: templates/cisco_ios_show_version.textfsm
# Your template is now used instead!
```

### Reverting to Built-in

Simply delete or rename your custom template:
```bash
mv templates/cisco_ios_show_version.textfsm \
   templates/cisco_ios_show_version.textfsm.backup
```

## Resources

### Learning TextFSM
- [TextFSM Documentation](https://github.com/google/textfsm)
- [TextFSM Wiki](https://github.com/google/textfsm/wiki/TextFSM)
- [Online TextFSM Tester](https://textfsm.nornir.tech/)

### Example Templates
- [ntc-templates](https://github.com/networktocode/ntc-templates) - 1000+ templates
- [TextFSM Template Guide](https://github.com/google/textfsm/wiki/Code-Lab)

### Regex Resources
- [Regex101](https://regex101.com/) - Test regex patterns
- [RegexOne](https://regexone.com/) - Learn regex

## API Reference

### Execute Command with TextFSM

```bash
POST /devices/{device_identifier}/execute
```

**Request:**
```json
{
  "command": "show ip interface brief",
  "use_textfsm": true
}
```

**Response (with custom template):**
```json
{
  "success": true,
  "data": {
    "output": [
      {"INTERFACE": "Gi0/0", "IP_ADDRESS": "192.168.1.1", ...}
    ],
    "execution_time": 0.452
  },
  "metadata": {
    "device_id": 1,
    "device_name": "core-switch-01",
    "command": "show ip interface brief",
    "timestamp": "2025-10-14T15:30:00"
  }
}
```

### Batch Execution

```bash
POST /devices/{device_identifier}/execute-batch
```

**Request:**
```json
{
  "commands": ["show version", "show ip route"],
  "use_textfsm": true
}
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
        "output": [...],
        "parsed_with": "custom_template"
      },
      {
        "command": "show ip route",
        "success": true,
        "output": [...],
        "parsed_with": "netmiko_builtin"
      }
    ],
    "execution_time": 1.234
  }
}
```

## Examples Repository

Check the `templates/` directory for example templates:
- `cisco_ios_show_ip_interface_brief.textfsm` - Basic interface parsing
- See `templates/README.md` for more examples

## Contributing

Have a useful template? Consider:
1. Adding it to this repository
2. Sharing with the community
3. Contributing to ntc-templates project

## Summary

✅ **Custom templates take priority** over Netmiko's built-in parsers  
✅ **Generic device type** supports any device with custom templates  
✅ **Simple naming convention**: `{device_type}_{command}.textfsm`  
✅ **Automatic fallback** to Netmiko if custom template not found  
✅ **Easy to test** with multiple methods  
✅ **Production ready** with comprehensive error handling  

Start creating your custom templates today! 🚀
