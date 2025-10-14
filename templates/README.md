# Custom TextFSM Templates

This directory contains custom TextFSM templates for parsing network device command output.

## Overview

Custom templates in this directory take **priority** over Netmiko's built-in TextFSM templates. This allows you to:
- Create templates for commands not supported by Netmiko
- Override Netmiko's built-in templates with custom parsing logic
- Support the `generic` device type with custom templates

## Naming Convention

Template filenames must follow this pattern:

```
{device_type}_{command_with_underscores}.textfsm
```

### Examples:

| Command | Device Type | Template Filename |
|---------|-------------|-------------------|
| `show ip route` | `cisco_ios` | `cisco_ios_show_ip_route.textfsm` |
| `show version` | `arista_eos` | `arista_eos_show_version.textfsm` |
| `show interfaces` | `generic` | `generic_show_interfaces.textfsm` |
| `show access-list` | `cisco_ios` | `cisco_ios_show_access-list.textfsm` |
| `show running-config` | `juniper_junos` | `juniper_junos_show_running-config.textfsm` |

**Rules:**
- Device type prefix (e.g., `cisco_ios_`)
- Command text with **spaces replaced by underscores**
- Hyphens and other characters **preserved as-is**
- `.textfsm` file extension
- All lowercase (automatically normalized)

## How It Works

When you execute a command with `"use_textfsm": true`:

1. **Custom Template Check**: System looks for a matching template in this directory
2. **Custom Template Used**: If found, uses your custom template to parse output
3. **Fallback to Netmiko**: If not found, uses Netmiko's built-in template (if available)
4. **Raw Output**: If no templates exist, returns unparsed output

## Creating Custom Templates

### 1. TextFSM Basics

TextFSM uses regular expressions to parse semi-formatted text. A template has two parts:

- **Value definitions**: Define what data to extract
- **State machine**: Define how to parse the text

### 2. Example Template

Here's a simple template for `show ip interface brief`:

```textfsm
Value INTERFACE (\S+)
Value IP_ADDRESS (\S+)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

### 3. Template Structure

```textfsm
# Value definitions (what to extract)
Value Required FIELD_NAME (regex_pattern)
Value OPTIONAL_FIELD (regex_pattern)
Value List REPEATING_FIELD (regex_pattern)

# State machine (how to parse)
Start
  ^regex_with_${FIELD_NAME}_placeholders -> Record
  ^another_pattern -> Continue
  ^Error -> Next
```

### 4. Common Value Options

- `Value` - Single value per record
- `Value Required` - Must match for record to be valid
- `Value List` - Can have multiple values (becomes array)
- `Value Filldown` - Carries value forward to next record

## Testing Templates

### Test your template using Python:

```python
import textfsm

# Load template
with open('templates/cisco_ios_show_ip_route.textfsm') as f:
    template = textfsm.TextFSM(f)

# Sample output
output = """
Gateway of last resort is not set
      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.1.1.0/24 is directly connected, GigabitEthernet0/1
L        10.1.1.1/32 is directly connected, GigabitEthernet0/1
"""

# Parse
result = template.ParseText(output)
headers = template.header

# Display
for row in result:
    print(dict(zip(headers, row)))
```

### Test via API:

```bash
curl -X POST "http://localhost:8000/devices/mydevice/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "show ip route",
    "use_textfsm": true
  }'
```

## Generic Device Type

The `generic` device type allows you to connect to any device and use custom templates for parsing:

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

# Execute with custom template (must exist: templates/generic_show_status.textfsm)
curl -X POST "http://localhost:8000/devices/custom-device/execute" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "show status",
    "use_textfsm": true
  }'
```

## Template Examples

### Example 1: Cisco IOS - Show IP Interface Brief

**Filename:** `cisco_ios_show_ip_interface_brief.textfsm`

```textfsm
Value Required INTERFACE (\S+)
Value IP_ADDRESS (\d+\.\d+\.\d+\.\d+|unassigned)
Value STATUS (up|down|administratively down)
Value PROTOCOL (up|down)

Start
  ^${INTERFACE}\s+${IP_ADDRESS}\s+\w+\s+\w+\s+${STATUS}\s+${PROTOCOL} -> Record
```

### Example 2: Generic Device - Custom Command

**Filename:** `generic_show_custom_status.textfsm`

```textfsm
Value DEVICE_ID (\S+)
Value STATUS (\w+)
Value UPTIME (.+)

Start
  ^Device:\s+${DEVICE_ID}
  ^Status:\s+${STATUS}
  ^Uptime:\s+${UPTIME} -> Record
```

## Resources

- [TextFSM Documentation](https://github.com/google/textfsm)
- [TextFSM Template Guide](https://github.com/google/textfsm/wiki/TextFSM)
- [ntc-templates Repository](https://github.com/networktocode/ntc-templates) - 1000+ examples
- [Online TextFSM Tester](https://textfsm.nornir.tech/)

## Troubleshooting

### Template Not Loading

1. Check filename follows naming convention exactly
2. Verify file has `.textfsm` extension
3. Check file is in `templates/` directory
4. Review application logs for parsing errors

### Template Not Parsing

1. Test template syntax with sample data
2. Verify regex patterns match your device output
3. Check for Required fields that aren't matching
4. Use online TextFSM tester for debugging

### Wrong Template Used

1. Verify device_type is correct in device configuration
2. Check command normalization (spaces → underscores)
3. Review application logs to see which template loaded

## Contributing Templates

If you create useful templates, consider:
1. Adding them to this repository
2. Sharing with the community
3. Contributing to [ntc-templates](https://github.com/networktocode/ntc-templates)

## Best Practices

1. **Test Thoroughly**: Test templates with various output formats
2. **Document Regex**: Add comments explaining complex patterns
3. **Handle Variations**: Account for different device software versions
4. **Use Required Wisely**: Only mark truly essential fields as Required
5. **Version Control**: Keep templates in version control
6. **Naming Consistency**: Follow the naming convention strictly
