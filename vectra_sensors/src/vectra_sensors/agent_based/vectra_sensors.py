#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Check Plugin: Vectra Sensor Health
Uses the cmk.agent_based.v2 API

All sensor data is fetched exclusively via the Vectra Brain REST API,
as Vectra sensors are hardened and do not run a Checkmk agent.
"""

from collections.abc import Mapping
from datetime import datetime, timezone
import json
import re
from typing import Any

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    StringTable,
    check_levels,
)


# ──────────────────────────────────────────────────────────────
# Status mapping
# Known Vectra sensor states and their Checkmk equivalents.
#
# Confirmed states (Vectra NDR API v2.5):
#   "paired"       – sensor is active and reporting normally  → OK
#   "degraded"     – sensor is reachable but has issues       → WARN
#   "offline"      – sensor is not reachable                  → CRIT
#   "disconnected" – sensor lost connection to Brain          → CRIT
#
# Any unknown state (e.g. "initializing", "updating") falls back to WARN
# so that transient states do not trigger false alarms.
# ──────────────────────────────────────────────────────────────

_STATUS_STATE: dict[str, State] = {
    "paired":       State.OK,
    "degraded":     State.WARN,
    "offline":      State.CRIT,
    "disconnected": State.CRIT,
}


def _sensor_check_state(status: str) -> State:
    """Returns the Checkmk state for a given sensor status.
    Unknown statuses fall back to WARN."""
    return _STATUS_STATE.get(status.lower(), State.WARN)


# ──────────────────────────────────────────────────────────────
# Parser
# ──────────────────────────────────────────────────────────────

def parse_vectra_sensors(string_table: StringTable) -> list[dict] | None:
    if not string_table:
        return None
    try:
        raw = "".join("".join(line) for line in string_table)
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        return parsed.get("sensors", [])
    except (json.JSONDecodeError, ValueError, AttributeError):
        return None


agent_section_vectra_sensors = AgentSection(
    name="vectra_sensors",
    parse_function=parse_vectra_sensors,
)


# ──────────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────────

def _last_seen_age_seconds(last_seen: str) -> float | None:
    # Try ISO 8601 first (production API)
    try:
        dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (ValueError, TypeError):
        pass

    # Fallback: JavaScript Date.toString() format
    # e.g. "Tue Apr 14 2026 21:35:35 GMT+0200 (Mitteleuropäische Sommerzeit)"
    try:
        cleaned = re.sub(r"\s*\([^)]*\)", "", last_seen).strip()
        dt = datetime.strptime(cleaned, "%a %b %d %Y %H:%M:%S GMT%z")
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (ValueError, TypeError):
        pass

    return None


def _format_age(seconds: float) -> str:
    if seconds < 120:
        return f"{seconds:.0f} sec."
    if seconds < 7200:
        return f"{seconds / 60:.0f} min."
    if seconds < 172800:
        return f"{seconds / 3600:.1f} h"
    return f"{seconds / 86400:.1f} days"


# ──────────────────────────────────────────────────────────────
# Discovery
# ──────────────────────────────────────────────────────────────

def discover_vectra_sensors(section: list[dict]) -> DiscoveryResult:
    for sensor in section:
        name = sensor.get("name") or sensor.get("serial_number") or "unknown"
        yield Service(item=name)


# ──────────────────────────────────────────────────────────────
# Check
# ──────────────────────────────────────────────────────────────

def check_vectra_sensors(
    item: str,
    params: Mapping[str, Any],
    section: list[dict],
) -> CheckResult:

    warn_age = params.get("max_last_seen_warn", 3600)
    crit_age = params.get("max_last_seen_crit", 86400)

    sensor = next(
        (s for s in section if (s.get("name") or s.get("serial_number")) == item),
        None,
    )

    if sensor is None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Sensor '{item}' not found in API response",
        )
        return

    status    = sensor.get("status", "unknown").lower()
    last_seen = sensor.get("last_seen", "")
    serial    = sensor.get("serial_number", "n/a")
    version   = sensor.get("package_version") or sensor.get("version", "n/a")
    ip        = sensor.get("ip_address", "n/a")
    location  = sensor.get("location") or "–"
    luid      = sensor.get("luid", "n/a")

    cmk_state = _sensor_check_state(status)

    # Non-paired states: no heartbeat check required
    if cmk_state != State.OK:
        yield Result(
            state=cmk_state,
            summary=f"Status: {status.upper()} | IP: {ip} | S/N: {serial}",
            details=(
                f"  Status:    {status}\n"
                f"  IP:        {ip}\n"
                f"  Serial:    {serial}\n"
                f"  Version:   {version}\n"
                f"  Location:  {location}\n"
                f"  LUID:      {luid}"
            ),
        )
        return

    if not last_seen:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Paired, but no last_seen timestamp | IP: {ip}",
        )
        return

    age = _last_seen_age_seconds(last_seen)
    if age is None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Cannot parse last_seen timestamp: '{last_seen}'",
        )
        return

    if age >= crit_age:
        hb_state = State.CRIT
    elif age >= warn_age:
        hb_state = State.WARN
    else:
        hb_state = State.OK

    age_str = _format_age(age)

    yield Result(
        state=hb_state,
        summary=f"Paired | Last seen {age_str} ago",
        details=(
            f"  Status:    {status}\n"
            f"  Last seen: {last_seen} ({age_str} ago)\n"
            f"  IP:        {ip}\n"
            f"  Serial:    {serial}\n"
            f"  Version:   {version}\n"
            f"  Location:  {location}\n"
            f"  LUID:      {luid}"
        ),
    )

    yield from check_levels(
        age / 60,
        metric_name="vectra_sensor_last_seen_minutes",
        levels_upper=("fixed", (warn_age / 60, crit_age / 60)),
        render_func=lambda v: f"{v:.1f} min",
    )


check_plugin_vectra_sensors = CheckPlugin(
    name="vectra_sensors",
    service_name="Vectra Sensor %s",
    discovery_function=discover_vectra_sensors,
    check_function=check_vectra_sensors,
    check_default_parameters={
        "max_last_seen_warn": 3600,
        "max_last_seen_crit": 86400,
    },
    check_ruleset_name="vectra_sensors",
)
