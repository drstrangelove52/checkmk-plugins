#!/usr/bin/env python3
"""WATO rule for VMware vSphere snapshot check parameters."""

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Float,
    InputHint,
    Integer,
    LevelDirection,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostCondition, Topic


def _form_vsphere_snapshots_parameters() -> Dictionary:
    return Dictionary(
        title=Title("VMware Snapshot Thresholds"),
        elements={
            "count_levels": DictElement(
                parameter_form=SimpleLevels[int](
                    title=Title("Snapshot count"),
                    help_text=Help("Warn/crit if a VM has this many or more snapshots."),
                    form_spec_template=Integer(unit_symbol="snapshots"),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(3, 5)),
                ),
            ),
            "age_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Snapshot age"),
                    help_text=Help("Warn/crit if a snapshot is older than this value."),
                    form_spec_template=Float(unit_symbol="days"),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(7.0, 30.0)),
                ),
            ),
            "size_levels": DictElement(
                parameter_form=SimpleLevels[float](
                    title=Title("Snapshot size"),
                    help_text=Help("Warn/crit if a snapshot is larger than this value."),
                    form_spec_template=Float(unit_symbol="GB"),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=InputHint(value=(10.0, 50.0)),
                ),
            ),
            "missing_date_state": DictElement(
                parameter_form=SingleChoice(
                    title=Title("State if description date is missing or invalid"),
                    help_text=Help(
                        "Each snapshot must have exactly a date in the format DD.MM.YYYY "
                        "in its description - the date only, no additional text. "
                        "This setting defines the state if the date is missing or invalid."
                    ),
                    elements=[
                        SingleChoiceElement(name="warn", title=Title("WARNING")),
                        SingleChoiceElement(name="crit", title=Title("CRITICAL")),
                    ],
                    prefill=DefaultValue("warn"),
                ),
            ),
        },
    )


rule_spec_vsphere_snapshots = CheckParameters(
    name="vsphere_snapshots",
    title=Title("VMware Snapshot Thresholds"),
    topic=Topic.CLOUD,
    parameter_form=_form_vsphere_snapshots_parameters,
    condition=HostCondition(),
)
