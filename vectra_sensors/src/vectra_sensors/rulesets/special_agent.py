#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Rulesets API – Vectra Special Agent Konfigurationsformular
Dieses rule_spec steuert den Eintrag in Setup → Agents → Other integrations.

WICHTIG: Nur rule_spec_* hier – kein SpecialAgentConfig!
Das SpecialAgentConfig ist in server_side_calls/special_agent.py.
"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    Password,
    String,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _form_vectra_special_agent() -> Dictionary:
    return Dictionary(
        title=Title("Vectra NDR – Sensor Health via Brain API"),
        help_text=Help(
            "Vectra Brain REST API (/api/v2.5/health/sensors). "
            "API-Token: Brain UI → My Profile → API Token. "
            "Berechtigung: Detect view health."
        ),
        elements={
            "brain_host": DictElement(
                parameter_form=String(
                    title=Title("Brain Hostname / IP"),
                    help_text=Help(
                        "Hostname oder IP-Adresse des Vectra Brain (ohne https://)"
                    ),
                    field_size=FieldSize.MEDIUM,
                    prefill=DefaultValue("vectra-brain.example.com"),
                ),
                required=True,
            ),
            "api_token": DictElement(
                parameter_form=Password(
                    title=Title("API Token"),
                    help_text=Help(
                        "API-Token aus dem Brain UI "
                        "(My Profile → View/Generate API Token)"
                    ),
                ),
                required=True,
            ),
            "no_verify_ssl": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("SSL-Zertifikat nicht prüfen"),
                    help_text=Help(
                        "Deaktiviert die SSL-Zertifikatsprüfung. "
                        "Nur bei Self-Signed-Zertifikaten verwenden."
                    ),
                    prefill=DefaultValue(False),
                ),
                required=False,
            ),
        },
    )


rule_spec_vectra_sensors = SpecialAgent(
    name="vectra_sensors",
    title=Title("Vectra NDR – Sensor Health"),
    topic=Topic.NETWORKING,
    parameter_form=_form_vectra_special_agent,
)
