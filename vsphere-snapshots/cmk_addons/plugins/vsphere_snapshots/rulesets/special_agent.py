#!/usr/bin/env python3
"""WATO rule for the VMware vSphere Snapshot Special Agent."""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    Integer,
    Password,
    String,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _form_special_agent_vsphere_snapshots() -> Dictionary:
    return Dictionary(
        title=Title("VMware vSphere Snapshots"),
        elements={
            "user": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Username"),
                    help_text=Help("e.g. administrator@vsphere.local"),
                    field_size=FieldSize.MEDIUM,
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Password"),
                    help_text=Help(
                        "Password for the vCenter user. "
                        "Recommended: store the password in the Checkmk password store."
                    ),
                    migrate=migrate_to_password,
                ),
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Port"),
                    help_text=Help("HTTPS port of the vCenter (default: 443)."),
                    prefill=DefaultValue(443),
                ),
            ),
            "no_ssl_verify": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    title=Title("Disable SSL certificate verification"),
                    help_text=Help(
                        "Skip SSL validation. Recommended for test environments only."
                    ),
                ),
            ),
            "fallback_host": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Fallback host"),
                    help_text=Help(
                        "Checkmk hostname for VMs that have no dedicated Checkmk host "
                        "(e.g. VMs without VMware Tools). This host must exist in Checkmk."
                    ),
                    field_size=FieldSize.MEDIUM,
                ),
            ),
        },
    )


rule_spec_special_agent_vsphere_snapshots = SpecialAgent(
    name="vsphere_snapshots",
    title=Title("VMware vSphere Snapshots"),
    topic=Topic.CLOUD,
    parameter_form=_form_special_agent_vsphere_snapshots,
    help_text=Help(
        "Connects via vSphere API (pyVmomi) to a vCenter and checks all VMs for snapshots. "
        "A service is created per VM monitoring age, size, and the required deletion date "
        "in the snapshot description. The piggyback hostname is taken from the VMware Tools "
        "guest hostname (FQDN). VMs without VMware Tools are assigned to the fallback host."
    ),
)
