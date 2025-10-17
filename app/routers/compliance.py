"""Configuration compliance router"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime

from app.schemas import ComplianceRequest, ComplianceResponse
from app.models import User
from app.auth import get_current_user
from app.services import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Configuration Compliance"])


@router.post("/check", response_model=ComplianceResponse)
async def check_configuration_compliance(
    compliance_data: ComplianceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Check configuration compliance between backup and intended configurations

    This endpoint compares a backup/current configuration against an intended
    configuration using specified features. It uses the netutils compliance
    library to perform detailed configuration analysis.

    **No device interaction required** - you provide both configurations directly.

    **Features** define what sections of the configuration to check:
    - `name`: Feature identifier (e.g., "ntp", "snmp")
    - `ordered`: Whether line order matters for compliance
    - `section`: Configuration prefixes to match (e.g., ["ntp"], ["interface"])

    **Returns compliance details:**
    - `actual`: Current configuration for the feature
    - `intended`: Desired configuration for the feature
    - `missing`: Lines that should be present but aren't
    - `extra`: Lines that are present but shouldn't be
    - `compliant`: Overall compliance status (True/False)
    - `ordered_compliant`: Compliance with order considered
    - `unordered_compliant`: Compliance without order

    **Example request:**
    ```json
    {
      "features": [
        {
          "name": "ntp",
          "ordered": true,
          "section": ["ntp"]
        }
      ],
      "backup": "ntp server 192.168.1.1\\nntp server 192.168.1.2 prefer",
      "intended": "ntp server 192.168.1.1\\nntp server 192.168.1.5 prefer",
      "network_os": "cisco_ios"
    }
    ```
    """
    # Prepare features for compliance check
    features = [
        {"name": f.name, "ordered": f.ordered, "section": f.section}
        for f in compliance_data.features
    ]

    # Run compliance check
    try:
        compliance_result = ComplianceService.check_compliance(
            features=features,
            backup_config=compliance_data.backup,
            intended_config=compliance_data.intended,
            network_os=compliance_data.network_os,
        )

        # Calculate overall compliance
        overall_compliant = all(
            feature_result.get("compliant", False) for feature_result in compliance_result.values()
        )

        # Count features by compliance status
        compliant_count = sum(
            1 for result in compliance_result.values() if result.get("compliant", False)
        )
        non_compliant_count = len(compliance_result) - compliant_count

        # Format response
        return {
            "success": True,
            "data": compliance_result,
            "metadata": {
                "network_os": compliance_data.network_os,
                "timestamp": datetime.utcnow().isoformat(),
                "overall_compliant": overall_compliant,
                "total_features": len(compliance_result),
                "compliant_features": compliant_count,
                "non_compliant_features": non_compliant_count,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance check failed: {str(e)}",
        )


@router.get("/features")
async def get_compliance_feature_examples(
    current_user: User = Depends(get_current_user),
):
    """
    Get example feature definitions for compliance checks

    Returns a list of common feature definitions that can be used as templates
    for compliance checking. Each feature includes:
    - `name`: Feature identifier
    - `ordered`: Whether order matters
    - `section`: Configuration prefixes to match
    - `description`: What the feature checks

    **Example response:**
    ```json
    {
      "features": [
        {
          "name": "ntp",
          "ordered": true,
          "section": ["ntp"],
          "description": "NTP server configuration"
        }
      ]
    }
    ```
    """
    examples = ComplianceService.create_feature_examples()
    return {"features": examples, "count": len(examples)}


@router.get("/supported-platforms")
async def get_supported_platforms(
    current_user: User = Depends(get_current_user),
):
    """
    Get list of supported network platforms for compliance checking

    Returns the list of network operating systems that support compliance
    checking through the netutils library.

    **Example response:**
    ```json
    {
      "platforms": [
        "cisco_ios",
        "cisco_nxos",
        "arista_eos",
        "juniper_junos"
      ]
    }
    ```
    """
    platforms = ComplianceService.get_supported_network_os()
    return {"platforms": platforms, "count": len(platforms)}
