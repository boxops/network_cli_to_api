"""Custom TextFSM template loader

This module provides functionality to load custom TextFSM templates
that take priority over Netmiko's built-in templates.
"""

import os
from pathlib import Path
from typing import Optional
import textfsm

# Templates directory relative to project root
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def get_template_filename(device_type: str, command: str) -> str:
    """
    Generate the template filename based on device type and command.

    Args:
        device_type: Device type (e.g., 'cisco_ios', 'arista_eos')
        command: Command string (e.g., 'show ip route')

    Returns:
        Template filename (e.g., 'cisco_ios_show_ip_route.textfsm')

    Examples:
        >>> get_template_filename('cisco_ios', 'show ip route')
        'cisco_ios_show_ip_route.textfsm'
        >>> get_template_filename('arista_eos', 'show version')
        'arista_eos_show_version.textfsm'
    """
    # Normalize command: lowercase, replace spaces with underscores
    # Keep hyphens and other valid filename characters
    normalized_command = command.lower().strip().replace(" ", "_")

    # Remove consecutive underscores (if any were created)
    while "__" in normalized_command:
        normalized_command = normalized_command.replace("__", "_")

    return f"{device_type}_{normalized_command}.textfsm"


def get_custom_template(device_type: str, command: str) -> Optional[textfsm.TextFSM]:
    """
    Load a custom TextFSM template if it exists.

    Args:
        device_type: Device type (e.g., 'cisco_ios', 'arista_eos')
        command: Command string (e.g., 'show ip route')

    Returns:
        TextFSM object if custom template exists, None otherwise

    Raises:
        Exception: If template exists but cannot be parsed
    """
    template_filename = get_template_filename(device_type, command)
    template_path = TEMPLATES_DIR / template_filename

    if not template_path.exists():
        return None

    try:
        with open(template_path, "r") as template_file:
            template = textfsm.TextFSM(template_file)
        return template
    except Exception as e:
        raise Exception(f"Failed to load custom template '{template_filename}': {str(e)}")


def parse_with_template(template: textfsm.TextFSM, output: str) -> list:
    """
    Parse command output using a TextFSM template.

    Args:
        template: TextFSM template object
        output: Command output string to parse

    Returns:
        List of dictionaries with parsed data

    Example:
        >>> template = get_custom_template('cisco_ios', 'show ip route')
        >>> output = "Gateway of last resort is not set\\n..."
        >>> result = parse_with_template(template, output)
        >>> # Returns: [{'network': '10.0.0.0', 'mask': '8', ...}, ...]
    """
    # Reset template to ensure clean state
    template.Reset()

    # Parse the output
    parsed = template.ParseText(output)

    # Convert to list of dictionaries
    headers = template.header
    result = []
    for row in parsed:
        result.append(dict(zip(headers, row)))

    return result


def list_custom_templates(device_type: Optional[str] = None) -> list[str]:
    """
    List all available custom templates.

    Args:
        device_type: Optional device type to filter templates

    Returns:
        List of template filenames

    Examples:
        >>> list_custom_templates()
        ['cisco_ios_show_ip_route.textfsm', 'arista_eos_show_version.textfsm']
        >>> list_custom_templates('cisco_ios')
        ['cisco_ios_show_ip_route.textfsm', 'cisco_ios_show_interfaces.textfsm']
    """
    if not TEMPLATES_DIR.exists():
        return []

    templates = []
    for file in TEMPLATES_DIR.glob("*.textfsm"):
        if device_type is None or file.name.startswith(f"{device_type}_"):
            templates.append(file.name)

    return sorted(templates)
