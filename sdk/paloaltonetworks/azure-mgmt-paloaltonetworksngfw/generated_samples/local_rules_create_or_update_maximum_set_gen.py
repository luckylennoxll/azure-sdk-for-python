# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is regenerated.
# --------------------------------------------------------------------------

from azure.identity import DefaultAzureCredential
from azure.mgmt.paloaltonetworksngfw import PaloAltoNetworksNgfwMgmtClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-paloaltonetworksngfw
# USAGE
    python local_rules_create_or_update_maximum_set_gen.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""


def main():
    client = PaloAltoNetworksNgfwMgmtClient(
        credential=DefaultAzureCredential(),
        subscription_id="2bf4a339-294d-4c25-b0b2-ef649e9f5c27",
    )

    response = client.local_rules.begin_create_or_update(
        resource_group_name="firewall-rg",
        local_rulestack_name="lrs1",
        priority="1",
        resource={
            "properties": {
                "actionType": "Allow",
                "applications": ["app1"],
                "auditComment": "example comment",
                "category": {"feeds": ["feed"], "urlCustom": ["https://microsoft.com"]},
                "decryptionRuleType": "SSLOutboundInspection",
                "description": "description of local rule",
                "destination": {
                    "cidrs": ["1.0.0.1/10"],
                    "countries": ["India"],
                    "feeds": ["feed"],
                    "fqdnLists": ["FQDN1"],
                    "prefixLists": ["PL1"],
                },
                "enableLogging": "DISABLED",
                "etag": "c18e6eef-ba3e-49ee-8a85-2b36c863a9d0",
                "inboundInspectionCertificate": "cert1",
                "negateDestination": "TRUE",
                "negateSource": "TRUE",
                "protocol": "HTTP",
                "protocolPortList": ["80"],
                "provisioningState": "Accepted",
                "ruleName": "localRule1",
                "ruleState": "DISABLED",
                "source": {"cidrs": ["1.0.0.1/10"], "countries": ["India"], "feeds": ["feed"], "prefixLists": ["PL1"]},
                "tags": [{"key": "keyName", "value": "value"}],
            }
        },
    ).result()
    print(response)


# x-ms-original-file: specification/paloaltonetworks/resource-manager/PaloAltoNetworks.Cloudngfw/preview/2022-08-29-preview/examples/LocalRules_CreateOrUpdate_MaximumSet_Gen.json
if __name__ == "__main__":
    main()
