"""Netmiko service for SSH/CLI operations"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

from app.models import Device
from app.config import settings
from app.utils.textfsm_loader import get_custom_template, parse_with_template

logger = logging.getLogger(__name__)

# Thread pool for blocking SSH operations
executor = ThreadPoolExecutor(max_workers=settings.max_ssh_connections)


class NetmikoService:
    """Service for managing SSH connections to network devices"""

    @staticmethod
    def _build_device_params(device: Device) -> Dict[str, Any]:
        """Build Netmiko connection parameters from Device model"""
        params = {
            "device_type": device.device_type,
            "host": device.host,
            "username": device.username,
            "password": device.password,
            "port": device.port,
            "timeout": device.timeout,
            "session_log": f"session_logs/{device.name}.log" if device.session_log else None,
        }

        if device.secret:
            params["secret"] = device.secret

        return params

    @staticmethod
    async def test_connection(device: Device) -> Dict[str, Any]:
        """Test connection to a device"""
        start_time = datetime.utcnow()

        try:
            device_params = NetmikoService._build_device_params(device)

            # Run in executor since Netmiko is blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor, NetmikoService._test_connection_sync, device_params
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "message": "Connection successful",
                "device_name": device.name,
                "execution_time": execution_time,
                "prompt": result.get("prompt", ""),
            }

        except NetmikoAuthenticationException as e:
            logger.error(f"Authentication failed for {device.name}: {str(e)}")
            return {"success": False, "error": "Authentication failed", "device_name": device.name}
        except NetmikoTimeoutException as e:
            logger.error(f"Connection timeout for {device.name}: {str(e)}")
            return {"success": False, "error": "Connection timeout", "device_name": device.name}
        except Exception as e:
            logger.error(f"Connection error for {device.name}: {str(e)}")
            return {"success": False, "error": str(e), "device_name": device.name}

    @staticmethod
    def _test_connection_sync(device_params: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous connection test"""
        with ConnectHandler(**device_params) as conn:
            prompt = conn.find_prompt()
            return {"prompt": prompt}

    @staticmethod
    async def execute_command(
        device: Device, command: str, use_textfsm: bool = False
    ) -> Dict[str, Any]:
        """Execute a single command on a device"""
        start_time = datetime.utcnow()

        try:
            device_params = NetmikoService._build_device_params(device)

            # Run in executor
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                executor, NetmikoService._execute_command_sync, device_params, command, use_textfsm
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "data": {"output": output, "execution_time": execution_time},
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "command": command,
                    "timestamp": start_time.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Command execution error for {device.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "command": command,
                    "timestamp": start_time.isoformat(),
                },
            }

    @staticmethod
    def _execute_command_sync(
        device_params: Dict[str, Any], command: str, use_textfsm: bool
    ) -> str:
        """Synchronous command execution with custom TextFSM template support"""
        with ConnectHandler(**device_params) as conn:
            # If TextFSM parsing is requested, try custom template first
            if use_textfsm:
                try:
                    # Try to get custom template
                    custom_template = get_custom_template(device_params["device_type"], command)

                    if custom_template:
                        # Execute command without TextFSM, get raw output
                        raw_output = conn.send_command(command, use_textfsm=False)
                        # Parse with custom template
                        parsed_output = parse_with_template(custom_template, raw_output)
                        logger.info(
                            f"Used custom template for {device_params['device_type']}: {command}"
                        )
                        return parsed_output
                    else:
                        # No custom template, fall back to Netmiko's built-in
                        logger.debug(
                            f"No custom template found for {device_params['device_type']}: {command}, using Netmiko built-in"
                        )
                        output = conn.send_command(command, use_textfsm=True)
                        return output
                except Exception as e:
                    logger.error(f"Error using custom template: {str(e)}, falling back to Netmiko")
                    # Fall back to Netmiko if custom template fails
                    output = conn.send_command(command, use_textfsm=True)
                    return output
            else:
                # No TextFSM requested, just execute normally
                output = conn.send_command(command, use_textfsm=False)
                return output

    @staticmethod
    async def execute_commands_batch(
        device: Device, commands: List[str], use_textfsm: bool = False
    ) -> Dict[str, Any]:
        """Execute multiple commands on a device"""
        start_time = datetime.utcnow()

        try:
            device_params = NetmikoService._build_device_params(device)

            # Run in executor
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                executor,
                NetmikoService._execute_commands_batch_sync,
                device_params,
                commands,
                use_textfsm,
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "data": {"results": results, "execution_time": execution_time},
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "commands_count": len(commands),
                    "timestamp": start_time.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Batch command execution error for {device.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "timestamp": start_time.isoformat(),
                },
            }

    @staticmethod
    def _execute_commands_batch_sync(
        device_params: Dict[str, Any], commands: List[str], use_textfsm: bool
    ) -> List[Dict[str, Any]]:
        """Synchronous batch command execution with custom TextFSM template support"""
        results = []
        with ConnectHandler(**device_params) as conn:
            for command in commands:
                try:
                    # If TextFSM parsing is requested, try custom template first
                    if use_textfsm:
                        try:
                            custom_template = get_custom_template(
                                device_params["device_type"], command
                            )

                            if custom_template:
                                raw_output = conn.send_command(command, use_textfsm=False)
                                parsed_output = parse_with_template(custom_template, raw_output)
                                results.append(
                                    {
                                        "command": command,
                                        "success": True,
                                        "output": parsed_output,
                                        "parsed_with": "custom_template",
                                    }
                                )
                                continue
                        except Exception as e:
                            logger.warning(f"Custom template failed for '{command}': {str(e)}")

                    # Fall back to standard execution
                    output = conn.send_command(command, use_textfsm=use_textfsm)
                    results.append(
                        {
                            "command": command,
                            "success": True,
                            "output": output,
                            "parsed_with": "netmiko_builtin" if use_textfsm else "none",
                        }
                    )
                except Exception as e:
                    results.append({"command": command, "success": False, "error": str(e)})
        return results

    @staticmethod
    async def send_config_commands(
        device: Device, commands: List[str], save_config: bool = True
    ) -> Dict[str, Any]:
        """Send configuration commands to a device"""
        start_time = datetime.utcnow()

        try:
            device_params = NetmikoService._build_device_params(device)

            # Run in executor
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                executor,
                NetmikoService._send_config_commands_sync,
                device_params,
                commands,
                save_config,
            )

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "success": True,
                "data": {
                    "output": output,
                    "execution_time": execution_time,
                    "config_saved": save_config,
                },
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "commands_count": len(commands),
                    "timestamp": start_time.isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Config command execution error for {device.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {
                    "device_id": device.id,
                    "device_name": device.name,
                    "timestamp": start_time.isoformat(),
                },
            }

    @staticmethod
    def _send_config_commands_sync(
        device_params: Dict[str, Any], commands: List[str], save_config: bool
    ) -> str:
        """Synchronous configuration command execution"""
        with ConnectHandler(**device_params) as conn:
            output = conn.send_config_set(commands)
            if save_config:
                conn.save_config()
            return output
