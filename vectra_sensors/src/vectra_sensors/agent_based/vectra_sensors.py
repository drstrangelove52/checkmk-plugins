#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checkmk 2.3 Check Plugin: Vectra Sensor Health
Verwendet die neue cmk.agent_based.v2 API

Da Vectra-Sensoren gehärtet sind, werden alle Statusinformationen
ausschliesslich über die Vectra Brain REST API abgerufen.
"""

from collections.abc import Mapping
from datetime import datetime, timezone
import json
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
# Status-Mapping
# Bekannte Vectra-Sensor-Zustände und deren Checkmk-Zuordnung
# ──────────────────────────────────────────────────────────────

_STATUS_STATE: dict[str, State] = {
    "paired":       State.OK,
    "degraded":     State.WARN,
    "offline":      State.CRIT,
    "disconnected": State.CRIT,
}

def _sensor_check_state(status: str) -> State:
    """Gibt den Checkmk-Status für einen Sensor-Zustand zurück.
    Unbekannte Zustände werden als WARN behandelt."""
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
# Hilfsfunktionen
# ──────────────────────────────────────────────────────────────

def _last_seen_age_seconds(last_seen: str) -> float | None:
    try:
        dt = datetime.fromisoformat(last_seen.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except (ValueError, TypeError):
        return None


def _format_age(seconds: float) -> str:
    if seconds < 120:
        return f"{seconds:.0f} Sek."
    if seconds < 7200:
        return f"{seconds / 60:.0f} Min."
    if seconds < 172800:
        return f"{seconds / 3600:.1f} Std."
    return f"{seconds / 86400:.1f} Tage"


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
            summary=f"Sensor '{item}' nicht in API-Antwort gefunden",
        )
        return

    status    = sensor.get("status", "unknown").lower()
    last_seen = sensor.get("last_seen", "")
    serial    = sensor.get("serial_number", "n/a")
    version   = sensor.get("package_version", "n/a")
    ip        = sensor.get("ip_address", "n/a")
    location  = sensor.get("location") or "–"
    luid      = sensor.get("luid", "n/a")

    cmk_state = _sensor_check_state(status)

    # Nicht-paired Zustände: kein Heartbeat-Check mehr nötig
    if cmk_state != State.OK:
        yield Result(
            state=cmk_state,
            summary=f"Status: {status.upper()} | IP: {ip} | S/N: {serial}",
            details=(
                f"  Status:    {status}\n"
                f"  IP:        {ip}\n"
                f"  Serial:    {serial}\n"
                f"  Version:   {version}\n"
                f"  Standort:  {location}\n"
                f"  LUID:      {luid}"
            ),
        )
        return

    if not last_seen:
        yield Result(
            state=State.UNKNOWN,
            summary=f"Gepaart, aber kein last_seen-Timestamp | IP: {ip}",
        )
        return

    age = _last_seen_age_seconds(last_seen)
    if age is None:
        yield Result(
            state=State.UNKNOWN,
            summary=f"last_seen konnte nicht geparst werden: '{last_seen}'",
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
        summary=(
            f"Paired | Heartbeat vor {age_str} | "
            f"IP: {ip} | Version: {version}"
        ),
        details=(
            f"  Status:    {status}\n"
            f"  Last Seen: {last_seen} (vor {age_str})\n"
            f"  IP:        {ip}\n"
            f"  Serial:    {serial}\n"
            f"  Version:   {version}\n"
            f"  Standort:  {location}\n"
            f"  LUID:      {luid}"
        ),
    )

    yield from check_levels(
        age / 60,
        metric_name="vectra_sensor_last_seen_minutes",
        levels_upper=(warn_age / 60, crit_age / 60),
        label="Heartbeat-Alter",
        render_func=lambda v: f"{v:.1f} min",
        notice_only=True,
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
