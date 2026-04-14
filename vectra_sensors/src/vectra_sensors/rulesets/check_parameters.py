#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Rulesets API
Check-Parameter-Regel für Vectra Sensor Health
"""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic


def _parameter_form_vectra_sensors() -> Dictionary:
    return Dictionary(
        elements={
            "max_last_seen_warn": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Heartbeat-Alter WARN"),
                    help_text=Help(
                        "WARNING, wenn der letzte Heartbeat älter als dieser Wert ist. "
                        "Standard: 1 Stunde."
                    ),
                    displayed_magnitudes=[
                        TimeMagnitude.MINUTE,
                        TimeMagnitude.HOUR,
                        TimeMagnitude.DAY,
                    ],
                    prefill=DefaultValue(3600.0),
                ),
                required=False,
            ),
            "max_last_seen_crit": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Heartbeat-Alter CRIT"),
                    help_text=Help(
                        "CRITICAL, wenn der letzte Heartbeat älter als dieser Wert ist. "
                        "Standard: 24 Stunden."
                    ),
                    displayed_magnitudes=[
                        TimeMagnitude.MINUTE,
                        TimeMagnitude.HOUR,
                        TimeMagnitude.DAY,
                    ],
                    prefill=DefaultValue(86400.0),
                ),
                required=False,
            ),
        },
    )


rule_spec_vectra_sensors = CheckParameters(
    name="vectra_sensors",
    title=Title("Vectra NDR – Sensor Health Schwellwerte"),
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_vectra_sensors,
    condition=HostAndItemCondition(
        item_title=Title("Sensor Name"),
    ),
)
