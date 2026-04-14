#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Rulesets API – Vectra Special Agent configuration form
This rule_spec controls the entry under Setup → Agents → Other integrations.

NOTE: Only rule_spec_* here – no SpecialAgentConfig!
The SpecialAgentConfig is in server_side_calls/special_agent.py.
"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    FieldSize,
    FixedValue,
    Integer,
    Password,
    String,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _form_vectra_special_agent() -> Dictionary:
    return Dictionary(
        title=Title("Vectra NDR – Sensor Health via Brain API"),
        help_text=Help(
            "Vectra Brain REST API (/api/v2.5/health/sensors). "
            "API token: Brain UI → My Profile → API Token. "
            "Required permission: Detect view health."
        ),
        elements={
            "brain_host": DictElement(
                parameter_form=String(
                    title=Title("Brain Hostname / IP"),
                    help_text=Help(
                        "Hostname or IP address of the Vectra Brain (without https://)"
                    ),
                    field_size=FieldSize.MEDIUM,
                ),
                required=True,
            ),
            "api_token": DictElement(
                parameter_form=Password(
                    title=Title("API Token"),
                    help_text=Help(
                        "API token from the Brain UI "
                        "(My Profile → View/Generate API Token)"
                    ),
                ),
                required=True,
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Request timeout (seconds)"),
                    help_text=Help(
                        "Timeout for the Brain API request in seconds. "
                        "Increase this value if the Brain is slow to respond. "
                        "Default: 30 seconds."
                    ),
                    prefill=DefaultValue(30),
                ),
                required=False,
            ),
            "no_verify_ssl": DictElement(
                parameter_form=FixedValue(
                    value=True,
                    title=Title("Do not verify SSL certificate"),
                    help_text=Help(
                        "Disables SSL certificate verification. "
                        "Use only with self-signed certificates."
                    ),
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
