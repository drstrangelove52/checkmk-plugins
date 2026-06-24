#!/usr/bin/env python3
"""
WATO-Regel für den VMware vSphere Snapshot Special Agent.
"""

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
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _form_special_agent_vsphere_snapshots() -> Dictionary:
    return Dictionary(
        title=Title("VMware vSphere Snapshots"),
        elements={
            "hostname": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("vCenter Hostname / IP"),
                    help_text=Help("Hostname oder IP-Adresse des vCenter Servers."),
                    field_size=FieldSize.MEDIUM,
                ),
            ),
            "user": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Benutzername"),
                    help_text=Help("z.B. administrator@vsphere.local"),
                    field_size=FieldSize.MEDIUM,
                ),
            ),
            "password": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Passwort"),
                    help_text=Help(
                        "Passwort für den vCenter-Benutzer. "
                        "Empfehlung: Passwort im Checkmk Passwort-Speicher ablegen."
                    ),
                ),
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Port"),
                    help_text=Help("HTTPS-Port des vCenter (Standard: 443)."),
                    prefill=DefaultValue(443),
                ),
            ),
            "no_ssl_verify": DictElement(
                required=True,
                parameter_form=BooleanChoice(
                    title=Title("SSL-Zertifikat nicht prüfen"),
                    help_text=Help(
                        "SSL-Validierung deaktivieren. Nur für Testumgebungen empfohlen."
                    ),
                    label=Title("Deaktivieren"),
                ),
            ),
            "fallback_host": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Sammel-Host"),
                    help_text=Help(
                        "Checkmk-Hostname, unter dem VMs gelistet werden, "
                        "die keinen eigenen Checkmk-Host haben. "
                        "Dieser Host muss in Checkmk existieren."
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
        "Verbindet sich per vSphere API (pyVmomi) mit einem vCenter und prüft "
        "alle VMs auf Snapshots. Je VM wird ein Service erzeugt, der Alter, "
        "Grösse und das Pflichtdatum in der Beschreibung überwacht. "
        "Der Piggyback-Hostname wird aus dem VMware-Tools-Gasthostnamen (FQDN) bezogen. "
        "VMs ohne VMware Tools werden dem Sammel-Host zugewiesen."
    ),
)
