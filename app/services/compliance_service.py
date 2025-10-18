"""Configuration compliance service using netutils"""

from typing import Dict, Any, List
from datetime import datetime
import logging
from netutils.config.compliance import compliance as netutils_compliance

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for configuration compliance checking"""

    @staticmethod
    def check_compliance(
        features: List[Dict[str, Any]],
        backup_config: str,
        intended_config: str,
        network_os: str,
    ) -> Dict[str, Any]:
        """
        Check configuration compliance using netutils

        Args:
            features: List of feature definitions with name, ordered, and section
            backup_config: Actual configuration from device
            intended_config: Intended/desired configuration
            network_os: Network OS type (e.g., 'cisco_ios', 'arista_eos')

        Returns:
            Dictionary with compliance results per feature

        Example:
            features = [
                {
                    "name": "ntp",
                    "ordered": True,
                    "section": ["ntp"]
                }
            ]
            result = check_compliance(features, actual, intended, "cisco_ios")
        """
        try:
            logger.info(f"Checking compliance for {network_os} with {len(features)} features")

            # Call netutils compliance function
            # Note: netutils uses 'string' for the last parameter
            compliance_result = netutils_compliance(
                features=features,
                backup=backup_config,
                intended=intended_config,
                network_os=network_os,
                cfg_type="string",  # Configuration type is string (not file path)
            )

            logger.info(f"Compliance check completed: {len(compliance_result)} features analyzed")
            return compliance_result

        except Exception as e:
            logger.error(f"Compliance check error: {str(e)}")
            raise

    @staticmethod
    def format_compliance_result(
        compliance_result: Dict[str, Any], device_name: str, device_id: int
    ) -> Dict[str, Any]:
        """
        Format compliance result for API response

        Args:
            compliance_result: Raw compliance result from netutils
            device_name: Name of the device checked
            device_id: ID of the device checked

        Returns:
            Formatted response dictionary
        """
        # Calculate overall compliance
        overall_compliant = all(
            feature_result.get("compliant", False) for feature_result in compliance_result.values()
        )

        # Count features by compliance status
        compliant_count = sum(
            1 for result in compliance_result.values() if result.get("compliant", False)
        )
        non_compliant_count = len(compliance_result) - compliant_count

        return {
            "success": True,
            "data": compliance_result,
            "metadata": {
                "device_id": device_id,
                "device_name": device_name,
                "timestamp": datetime.utcnow().isoformat(),
                "overall_compliant": overall_compliant,
                "total_features": len(compliance_result),
                "compliant_features": compliant_count,
                "non_compliant_features": non_compliant_count,
            },
        }

    @staticmethod
    def get_supported_network_os() -> List[str]:
        """
        Get list of supported network operating systems

        Returns:
            List of supported network OS identifiers
        """
        # Based on netutils parser support
        return [
            "cisco_ios",
            "cisco_nxos",
            "cisco_xe",
            "cisco_asa",
            "arista_eos",
            "juniper_junos",
            "paloalto_panos",
            "fortinet",
            "hp_procurve",
            "nokia_sros",
            "generic",
        ]

    @staticmethod
    def create_feature_examples() -> List[Dict[str, Any]]:
        """
        Get example feature definitions for common use cases

        Returns:
            List of example feature definitions
        """
        return [
            {
                "name": "hostname",
                "ordered": True,
                "section": ["hostname"],
                "description": "Device hostname configuration",
            },
            {
                "name": "ntp",
                "ordered": True,
                "section": ["ntp"],
                "description": "NTP server configuration",
            },
            {
                "name": "snmp",
                "ordered": False,
                "section": ["snmp-server"],
                "description": "SNMP configuration",
            },
            {
                "name": "logging",
                "ordered": False,
                "section": ["logging"],
                "description": "Syslog configuration",
            },
            {
                "name": "aaa",
                "ordered": True,
                "section": ["aaa", "tacacs", "radius"],
                "description": "AAA and authentication configuration",
            },
            {
                "name": "interfaces",
                "ordered": False,
                "section": ["interface"],
                "description": "Interface configurations",
            },
            {
                "name": "routing",
                "ordered": False,
                "section": ["router", "route", "ip route"],
                "description": "Routing protocol configuration",
            },
            {
                "name": "acl",
                "ordered": True,
                "section": ["access-list", "ip access-list"],
                "description": "Access control lists",
            },
            {
                "name": "vlan",
                "ordered": False,
                "section": ["vlan"],
                "description": "VLAN configuration",
            },
            {
                "name": "banner",
                "ordered": True,
                "section": ["banner"],
                "description": "Login banners",
            },
        ]
