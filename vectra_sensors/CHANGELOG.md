# Changelog – vectra_sensors

All notable changes to this plugin are documented here.

---

## [1.0.13] – 2026-04-15

### Changed
- Summary line now shows only `Paired | Last seen X ago` — IP and Version moved to details only.
- Removed redundant "Heartbeat age" label from `check_levels` output (same value as "Last seen"). Metric is still recorded.

---

## [1.0.12] – 2026-04-15

### Removed
- "Use HTTP instead of HTTPS" WATO option and `--http` agent flag — no longer needed.
- Configurable API path — hardcoded to `/api/v3.4/health` (Vectra Cloud Brain).

---

## [1.0.11] – 2026-04-15

### Fixed
- `check_levels()`: `levels_upper` must be passed as `("fixed", (warn, crit))` in `cmk.agent_based.v2` — plain tuples are not accepted and caused a `TypeError`.

---

## [1.0.10] – 2026-04-15

### Changed
- API path is now configurable via WATO ("API path" field). Default changed from `/api/v2.5/health/sensors` to `/api/v3.4/health` to match current Vectra Brain API versions. Older deployments can override the path manually.

---

## [1.0.9] – 2026-04-14

### Fixed
- Removed `notice_only=True` from `check_levels()` call — parameter does not exist in Checkmk 2.3's `cmk.agent_based.v2` API and caused a crash report on every check execution.

---

## [1.0.8] – 2026-04-14

### Added
- New WATO option "Use HTTP instead of HTTPS" (`--http` flag) for testing against non-TLS endpoints.

### Fixed
- `last_seen` parser now handles JavaScript `Date.toString()` format (e.g. `"Tue Apr 14 2026 21:35:35 GMT+0200 (...)"`) in addition to ISO 8601.
- `version` field: added fallback from `package_version` → `version` to handle API response variants.

---

## [1.0.7] – 2026-04-14

### Added
- Optional `Brain Port` field in WATO. If set, the API URL becomes `https://<host>:<port>/api/v2.5/health/sensors`. Defaults to 443 when omitted.
- New `--port` parameter in the special agent.

---

## [1.0.6] – 2026-04-14

### Fixed
- API token handling: `params["api_token"]` with `noop_parser` delivers a `Secret` object directly from Checkmk — not a plain string or tuple. Calling `str()` on it produced the config error `"Secret(id=..., format='%s', pass_safely=True)"`. The Secret object is now passed directly to `SpecialAgentCommand.command_arguments`, which resolves and masks it correctly at process launch.

---

## [1.0.5] – 2026-04-14

### Fixed
- Reverted manual `Secret()` wrapping introduced in v1.0.4 (incompatible with `noop_parser`).
- `no_verify_ssl` WATO field: replaced `BooleanChoice` (caused duplicate checkbox) with `FixedValue(True)` and `required=False`.
- `no_verify_ssl` WATO field: replaced `BooleanChoice` (caused duplicate checkbox) with `FixedValue(True)` and `required=False`. The outer DictElement checkbox now acts as the sole toggle.

---

## [1.0.4] – 2026-04-14

### Fixed
- Removed dead code in `get_sensors()`: the `resp.status != 200` branch was unreachable because `urllib` raises `HTTPError` for non-2xx responses before that check.

### Improved
- **Timeout**: Request timeout is now configurable via WATO (default: 30 s). The `--timeout` parameter is passed through to the special agent.
- **Documentation**: `_STATUS_STATE` mapping in the check plugin now lists all confirmed Vectra sensor states with their rationale. Unknown states fall back to WARN.

---

## [1.0.3] – 2026-04-14

### Changed
- All user-visible texts translated to English (WATO forms, check output, error messages).
- Removed placeholder text `vectra-brain.example.com` from the Brain Hostname / IP field.

---

## [1.0.2] – 2026-04-14

### Changed
- Author updated to `Martin Nigg` (removed organisation suffix).
- Plugin description shortened; justification for Brain-only data fetch removed.

### Improved
- Sensor status check now differentiates between states: `paired` → OK, `degraded` → WARN, `offline` / `disconnected` → CRIT. Previously all non-paired states were CRIT.
- Special agent: more informative error messages for HTTP 401, 403, and connection errors.
- `server_side_calls`: added `_extract_token()` to correctly handle the tuple format delivered by the Password form spec.
- Request timeout increased from 20 s to 30 s.

---

## [1.0.1] – 2026-04-14

### Initial release
- Special agent fetches sensor health data from Vectra Brain REST API (`/api/v2.5/health/sensors`).
- Discovers one service per sensor (keyed by sensor name or serial number).
- Checks pairing status and heartbeat age with configurable WARN/CRIT thresholds.
- Performance metric: `vectra_sensor_last_seen_minutes`.
