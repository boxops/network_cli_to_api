# Model Context Protocol (MCP) Server Implementation Guide

## Overview

This document outlines how to create a Model Context Protocol (MCP) server for the Network API Gateway, enabling AI agents (like Claude, ChatGPT, etc.) to directly interact with network devices through natural language.

## What is MCP?

The Model Context Protocol (MCP) is an open protocol developed by Anthropic that standardizes how AI applications interact with external data sources and tools. It enables AI assistants to:

- Access real-time data from various sources
- Execute actions through defined tools
- Maintain context across interactions
- Provide structured responses

## Benefits of MCP for Network Automation

1. **Natural Language Control**: AI agents can manage network devices using conversational commands
2. **Intelligent Troubleshooting**: Agents can analyze outputs and suggest fixes
3. **Automated Documentation**: Generate network documentation from device configurations
4. **Change Planning**: AI can plan and validate configuration changes before applying
5. **Multi-Device Orchestration**: Coordinate changes across multiple devices intelligently

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   AI Agent      │ ◄─MCP─► │   MCP Server     │ ◄─API─► │  Network API    │
│  (Claude, etc)  │         │  (Python/TypeScript)        │    Gateway      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ Tools/Resources
                                     ▼
                            ┌──────────────────┐
                            │  - list_devices  │
                            │  - execute_cmd   │
                            │  - get_config    │
                            │  - send_config   │
                            │  - batch_exec    │
                            └──────────────────┘
```

## Implementation Options

### Option 1: Python MCP Server (Recommended)

**Advantages:**
- Same language as main application
- Easy integration with existing codebase
- Official MCP Python SDK available
- Can share models and schemas

**Requirements:**
```bash
pip install mcp anthropic-mcp-server
```

### Option 2: TypeScript MCP Server

**Advantages:**
- Official SDK from Anthropic
- Rich ecosystem and tooling
- Better for standalone deployments

**Requirements:**
```bash
npm install @modelcontextprotocol/sdk
```

## MCP Server Structure

### 1. Server Definition

```python
# mcp_server/server.py
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
import httpx
import os

# Configuration
API_URL = os.getenv("NETWORK_API_URL", "http://localhost:8080")
API_USERNAME = os.getenv("NETWORK_API_USERNAME", "admin")
API_PASSWORD = os.getenv("NETWORK_API_PASSWORD", "changeme")

# Create server instance
server = Server("network-automation-mcp")

# Global auth token
auth_token = None
```

### 2. Resources (Read-only data sources)

```python
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available network resources"""
    return [
        types.Resource(
            uri="network://devices",
            name="Network Devices",
            description="List of all configured network devices",
            mimeType="application/json",
        ),
        types.Resource(
            uri="network://device-types",
            name="Supported Device Types",
            description="List of supported network device platforms",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read network resource data"""
    await ensure_authenticated()
    
    if uri == "network://devices":
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/devices",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            return response.text
    
    elif uri == "network://device-types":
        device_types = [
            "cisco_ios", "cisco_nxos", "cisco_xe", "cisco_asa",
            "juniper_junos", "arista_eos", "hp_procurve",
            "paloalto_panos", "fortinet", "nokia_srl", "nokia_sros", "generic"
        ]
        return json.dumps(device_types, indent=2)
    
    raise ValueError(f"Unknown resource: {uri}")
```

### 3. Tools (Actions AI can execute)

```python
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available network automation tools"""
    return [
        types.Tool(
            name="list_devices",
            description="List all configured network devices with their details",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        types.Tool(
            name="execute_command",
            description="Execute a command on a specific network device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device ID, name, or IP address",
                    },
                    "command": {
                        "type": "string",
                        "description": "Command to execute (e.g., 'show version')",
                    },
                    "use_textfsm": {
                        "type": "boolean",
                        "description": "Parse output with TextFSM",
                        "default": False,
                    },
                },
                "required": ["device", "command"],
            },
        ),
        types.Tool(
            name="get_device_config",
            description="Retrieve running configuration from a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device ID, name, or IP address",
                    },
                },
                "required": ["device"],
            },
        ),
        types.Tool(
            name="send_config",
            description="Send configuration commands to a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device ID, name, or IP address",
                    },
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of configuration commands",
                    },
                    "save_config": {
                        "type": "boolean",
                        "description": "Save configuration after applying",
                        "default": True,
                    },
                },
                "required": ["device", "commands"],
            },
        ),
        types.Tool(
            name="batch_execute",
            description="Execute multiple commands on a device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device ID, name, or IP address",
                    },
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of commands to execute",
                    },
                    "use_textfsm": {
                        "type": "boolean",
                        "description": "Parse outputs with TextFSM",
                        "default": False,
                    },
                },
                "required": ["device", "commands"],
            },
        ),
        types.Tool(
            name="test_connection",
            description="Test connectivity to a network device",
            inputSchema={
                "type": "object",
                "properties": {
                    "device": {
                        "type": "string",
                        "description": "Device ID, name, or IP address",
                    },
                },
                "required": ["device"],
            },
        ),
        types.Tool(
            name="add_device",
            description="Add a new network device to the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Unique device name"},
                    "host": {"type": "string", "description": "IP address or hostname"},
                    "device_type": {"type": "string", "description": "Device platform type"},
                    "username": {"type": "string", "description": "SSH username"},
                    "password": {"type": "string", "description": "SSH password"},
                    "secret": {"type": "string", "description": "Enable secret (optional)"},
                    "port": {"type": "integer", "description": "SSH port", "default": 22},
                    "description": {"type": "string", "description": "Device description"},
                },
                "required": ["name", "host", "device_type", "username", "password"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute network automation tools"""
    await ensure_authenticated()
    
    async with httpx.AsyncClient() as client:
        if name == "list_devices":
            response = await client.get(
                f"{API_URL}/devices",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "execute_command":
            device = arguments["device"]
            command = arguments["command"]
            use_textfsm = arguments.get("use_textfsm", False)
            
            response = await client.post(
                f"{API_URL}/devices/{device}/execute",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"command": command, "use_textfsm": use_textfsm}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "get_device_config":
            device = arguments["device"]
            response = await client.get(
                f"{API_URL}/devices/{device}/config",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "send_config":
            device = arguments["device"]
            commands = arguments["commands"]
            save_config = arguments.get("save_config", True)
            
            response = await client.post(
                f"{API_URL}/devices/{device}/config",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"commands": commands, "save_config": save_config}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "batch_execute":
            device = arguments["device"]
            commands = arguments["commands"]
            use_textfsm = arguments.get("use_textfsm", False)
            
            response = await client.post(
                f"{API_URL}/devices/{device}/execute-batch",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"commands": commands, "use_textfsm": use_textfsm}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "test_connection":
            device = arguments["device"]
            response = await client.get(
                f"{API_URL}/devices/{device}/test",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        elif name == "add_device":
            response = await client.post(
                f"{API_URL}/devices",
                headers={"Authorization": f"Bearer {auth_token}"},
                json=arguments
            )
            response.raise_for_status()
            return [types.TextContent(type="text", text=response.text)]
        
        raise ValueError(f"Unknown tool: {name}")


async def ensure_authenticated():
    """Ensure we have a valid authentication token"""
    global auth_token
    
    if auth_token is None:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/auth/login",
                json={"username": API_USERNAME, "password": API_PASSWORD}
            )
            response.raise_for_status()
            data = response.json()
            auth_token = data["access_token"]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="network-automation",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 4. Prompts (Pre-configured AI workflows)

```python
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available network automation prompts"""
    return [
        types.Prompt(
            name="troubleshoot_interface",
            description="Troubleshoot interface issues on a device",
            arguments=[
                types.PromptArgument(
                    name="device",
                    description="Device to troubleshoot",
                    required=True,
                ),
                types.PromptArgument(
                    name="interface",
                    description="Interface name (e.g., GigabitEthernet0/1)",
                    required=True,
                ),
            ],
        ),
        types.Prompt(
            name="backup_configs",
            description="Backup configurations from all devices",
            arguments=[],
        ),
        types.Prompt(
            name="audit_devices",
            description="Perform security audit on network devices",
            arguments=[],
        ),
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """Generate network automation prompts"""
    
    if name == "troubleshoot_interface":
        device = arguments.get("device", "")
        interface = arguments.get("interface", "")
        
        return types.GetPromptResult(
            description=f"Troubleshooting {interface} on {device}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""Please troubleshoot interface {interface} on device {device}.

Steps to perform:
1. Check interface status with 'show ip interface brief' or equivalent
2. Check interface errors with 'show interfaces {interface}'
3. Check interface configuration
4. Analyze any error counters or issues
5. Provide recommendations for fixing any problems found

Please execute the necessary commands and provide a detailed analysis."""
                    ),
                )
            ],
        )
    
    elif name == "backup_configs":
        return types.GetPromptResult(
            description="Backup all device configurations",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text="""Please backup configurations from all network devices.

Steps:
1. List all devices
2. For each active device:
   - Retrieve running configuration
   - Save to a timestamped file
   - Verify backup was successful
3. Provide summary of backup operation"""
                    ),
                )
            ],
        )
    
    raise ValueError(f"Unknown prompt: {name}")
```

## Installation and Setup

### 1. Project Structure

```
network_cli_to_openapi/
├── app/                          # Main API application
├── mcp_server/                   # MCP Server (NEW)
│   ├── __init__.py
│   ├── server.py                 # Main MCP server
│   ├── requirements.txt          # MCP dependencies
│   └── README.md                 # MCP documentation
├── docker-compose.yml
└── README.md
```

### 2. MCP Server Dependencies

Create `mcp_server/requirements.txt`:
```
mcp>=0.9.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

### 3. Environment Configuration

Create `mcp_server/.env`:
```bash
NETWORK_API_URL=http://localhost:8080
NETWORK_API_USERNAME=admin
NETWORK_API_PASSWORD=changeme
```

### 4. Docker Integration

Add to `docker-compose.yml`:
```yaml
services:
  api:
    # ... existing config ...

  mcp-server:
    build:
      context: .
      dockerfile: mcp_server/Dockerfile
    container_name: network-mcp-server
    environment:
      - NETWORK_API_URL=http://api:8080
      - NETWORK_API_USERNAME=${MCP_API_USERNAME:-admin}
      - NETWORK_API_PASSWORD=${MCP_API_PASSWORD:-changeme}
    depends_on:
      - api
    networks:
      - network-api
    stdin_open: true
    tty: true
```

### 5. MCP Server Dockerfile

Create `mcp_server/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mcp_server/ .

CMD ["python", "server.py"]
```

## Claude Desktop Integration

### Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "network-automation": {
      "command": "python",
      "args": ["/path/to/network_cli_to_openapi/mcp_server/server.py"],
      "env": {
        "NETWORK_API_URL": "http://localhost:8080",
        "NETWORK_API_USERNAME": "admin",
        "NETWORK_API_PASSWORD": "changeme"
      }
    }
  }
}
```

## Usage Examples

### Example 1: List Devices
```
User: "Show me all configured network devices"

Claude: [Uses list_devices tool]
```

### Example 2: Execute Command
```
User: "Get the interface status from router-01"

Claude: [Uses execute_command with device="router-01", command="show ip interface brief", use_textfsm=true]
```

### Example 3: Configuration Change
```
User: "Add VLAN 100 with name 'Engineering' to switch-core-01"

Claude: [Uses send_config with device="switch-core-01", commands=["vlan 100", "name Engineering"]]
```

### Example 4: Complex Workflow
```
User: "Audit all Cisco devices and check for any interfaces in err-disabled state"

Claude: 
1. [Uses list_devices to get all devices]
2. [Filters Cisco devices]
3. [Uses execute_command on each with "show interfaces status"]
4. [Analyzes output for err-disabled interfaces]
5. [Provides summary and recommendations]
```

## Security Considerations

1. **Authentication**: MCP server authenticates with Network API Gateway
2. **Authorization**: Inherits RBAC from main application
3. **Secrets Management**: Use environment variables, never hardcode
4. **Audit Logging**: All MCP actions logged in main application
5. **Rate Limiting**: Implement in MCP server to prevent abuse
6. **Network Isolation**: Run MCP server in trusted network segment

## Testing

```bash
# Test MCP server standalone
cd mcp_server
python server.py

# Test with Claude Desktop
# Open Claude Desktop and try:
# "List all network devices"
# "Show interface status on router-01"
```

## Benefits Summary

✅ **Natural Language Interface**: Network engineers use conversational commands  
✅ **Intelligent Automation**: AI understands context and suggests best practices  
✅ **Multi-Device Orchestration**: Coordinate changes across fleet  
✅ **Automated Documentation**: Generate reports and documentation  
✅ **Troubleshooting Assistant**: AI analyzes outputs and suggests fixes  
✅ **Change Validation**: AI can plan and validate before applying  
✅ **Learning Tool**: Great for training new engineers  

## Next Steps

1. Create `mcp_server/` directory structure
2. Implement basic MCP server with authentication
3. Add core tools (list, execute, config)
4. Test with Claude Desktop
5. Add prompts for common workflows
6. Document usage patterns
7. Deploy to production

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)
- [Network API Gateway Docs](README.md)
