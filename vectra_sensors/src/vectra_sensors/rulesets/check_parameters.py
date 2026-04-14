#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Rulesets API
Check parameter rule for Vectra Sensor Health
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
                    title=Title("Heartbeat age WARN"),
                    help_text=Help(
                        "WARNING if the last heartbeat is older than this value. "
                        "Default: 1 hour."
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
                    title=Title("Heartbeat age CRIT"),
                    help_text=Help(
                        "CRITICAL if the last heartbeat is older than this value. "
                        "Default: 24 hours."
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
    title=Title("Vectra NDR – Sensor Health Thresholds"),
    topic=Topic.NETWORKING,
    parameter_form=_parameter_form_vectra_sensors,
    condition=HostAndItemCondition(
        item_title=Title("Sensor Name"),
    ),
)
