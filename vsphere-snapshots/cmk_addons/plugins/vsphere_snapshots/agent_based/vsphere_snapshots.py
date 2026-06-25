#!/usr/bin/env python3
"""Checkmk check plugin for VMware vSphere snapshots."""

import json
import re
from datetime import datetime

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
)

DATE_RE = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


def _unpack_levels(levels_param) -> tuple[float | None, float | None]:
    """Unpack a SimpleLevels value into (warn, crit) or (None, None)."""
    if levels_param is None:
        return None, None
    kind, value = levels_param
    if kind == "fixed":
        return value[0], value[1]
    return None, None


def _level_state(value: float, warn: float | None, crit: float | None) -> State:
    if crit is not None and value >= crit:
        return State.CRIT
    if warn is not None and value >= warn:
        return State.WARN
    return State.OK


def _check_description_date(description: str, missing_state: str) -> tuple[State, str]:
    bad_state = State.CRIT if missing_state == "crit" else State.WARN
    desc = description.strip()
    if not desc:
        return bad_state, "Description empty - no date present"
    if not DATE_RE.match(desc):
        return bad_state, f"Description '{desc}' does not match format DD.MM.YYYY"
    try:
        datetime.strptime(desc, "%d.%m.%Y")
    except ValueError:
        return bad_state, f"Invalid date in description: '{desc}'"
    return State.OK, f"Deletion date: {desc}"


def _check_single_snapshot(snap: dict, params: dict) -> list[tuple[State, str]]:
    results = []
    name = snap["name"]
    age_days = snap["age_days"]
    size_bytes = snap["size_bytes"]
    size_gb = size_bytes / (1024**3)
    description = snap.get("description", "")
    missing_date_state = params.get("missing_date_state", "warn")

    age_warn, age_crit = _unpack_levels(params.get("age_levels"))
    size_warn, size_crit = _unpack_levels(params.get("size_levels"))

    # Age
    age_state = _level_state(age_days, age_warn, age_crit)
    if age_state == State.CRIT:
        results.append((State.CRIT, f"Snapshot '{name}': age {age_days:.1f} days (>= {age_crit} days)"))
    elif age_state == State.WARN:
        results.append((State.WARN, f"Snapshot '{name}': age {age_days:.1f} days (>= {age_warn} days)"))
    else:
        results.append((State.OK, f"Snapshot '{name}': age {age_days:.1f} days"))

    # Size
    if size_bytes > 0:
        size_state = _level_state(size_gb, size_warn, size_crit)
        if size_state == State.CRIT:
            results.append((State.CRIT, f"Snapshot '{name}': size {size_gb:.2f} GB (>= {size_crit:.1f} GB)"))
        elif size_state == State.WARN:
            results.append((State.WARN, f"Snapshot '{name}': size {size_gb:.2f} GB (>= {size_warn:.1f} GB)"))
        else:
            results.append((State.OK, f"Snapshot '{name}': size {size_gb:.2f} GB"))
    else:
        results.append((State.OK, f"Snapshot '{name}': size not available"))

    # Date in description
    date_state, date_msg = _check_description_date(description, missing_date_state)
    results.append((date_state, f"Snapshot '{name}': {date_msg}"))

    return results


def _emit_snapshot_results(snapshots: list, params: dict) -> CheckResult:
    count = len(snapshots)
    count_warn, count_crit = _unpack_levels(params.get("count_levels"))
    count_state = _level_state(count, count_warn, count_crit)

    if count_state == State.CRIT:
        yield Result(state=State.CRIT, summary=f"{count} snapshot(s) found (>= {count_crit})")
    elif count_state == State.WARN:
        yield Result(state=State.WARN, summary=f"{count} snapshot(s) found (>= {count_warn})")
    else:
        yield Result(state=State.OK, summary=f"{count} snapshot(s) found")

    for snap in snapshots:
        for state, msg in _check_single_snapshot(snap, params):
            if state == State.OK:
                yield Result(state=State.OK, notice=msg)
            else:
                yield Result(state=state, summary=msg)


# ---------------------------------------------------------------------------
# Section: vsphere_snapshots  (per VM via piggyback)
# ---------------------------------------------------------------------------


def parse_vsphere_snapshots(string_table: StringTable):
    if not string_table:
        return None
    try:
        return json.loads(string_table[0][0])
    except (json.JSONDecodeError, IndexError):
        return None


agent_section_vsphere_snapshots = AgentSection(
    name="vsphere_snapshots",
    parse_function=parse_vsphere_snapshots,
)


def discover_vsphere_snapshots(section) -> DiscoveryResult:
    if section and section.get("snapshots"):
        yield Service()


def check_vsphere_snapshots(params: dict, section) -> CheckResult:
    if section is None:
        return
    snapshots = section.get("snapshots", [])
    if not snapshots:
        yield Result(state=State.OK, summary="No snapshots found")
        return
    yield from _emit_snapshot_results(snapshots, params)


check_plugin_vsphere_snapshots = CheckPlugin(
    name="vsphere_snapshots",
    service_name="VMware Snapshots",
    discovery_function=discover_vsphere_snapshots,
    check_function=check_vsphere_snapshots,
    check_default_parameters={
        "age_levels": ("fixed", (7.0, 30.0)),
        "missing_date_state": "warn",
    },
    check_ruleset_name="vsphere_snapshots",
)


# ---------------------------------------------------------------------------
# Section: vsphere_snapshots_all  (unassigned VMs on fallback host)
# ---------------------------------------------------------------------------


def parse_vsphere_snapshots_all(string_table: StringTable):
    vms = []
    for line in string_table:
        try:
            vms.append(json.loads(line[0]))
        except (json.JSONDecodeError, IndexError):
            pass
    return vms if vms else None


agent_section_vsphere_snapshots_all = AgentSection(
    name="vsphere_snapshots_all",
    parse_function=parse_vsphere_snapshots_all,
)


def discover_vsphere_snapshots_all(section) -> DiscoveryResult:
    if not section:
        return
    for vm_data in section:
        if vm_data.get("snapshots"):
            yield Service(item=vm_data["vm_name"])


def check_vsphere_snapshots_all(item: str, params: dict, section) -> CheckResult:
    if section is None:
        return
    vm_data = next((v for v in section if v["vm_name"] == item), None)
    if vm_data is None:
        yield Result(state=State.UNKNOWN, summary=f"VM '{item}' no longer found")
        return
    snapshots = vm_data.get("snapshots", [])
    if not snapshots:
        yield Result(state=State.OK, summary="No snapshots found")
        return
    yield from _emit_snapshot_results(snapshots, params)


check_plugin_vsphere_snapshots_all = CheckPlugin(
    name="vsphere_snapshots_all",
    service_name="VMware Snapshots %s",
    discovery_function=discover_vsphere_snapshots_all,
    check_function=check_vsphere_snapshots_all,
    check_default_parameters={
        "age_levels": ("fixed", (7.0, 30.0)),
        "missing_date_state": "warn",
    },
    check_ruleset_name="vsphere_snapshots",
)
