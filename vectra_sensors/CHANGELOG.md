# Changelog – vectra_sensors

All notable changes to this plugin are documented here.

---

## [1.0.4] – 2026-04-14

### Fixed
- Removed dead code in `get_sensors()`: the `resp.status != 200` branch was unreachable because `urllib` raises `HTTPError` for non-2xx responses before that check.

### Improved
- **Security**: API token is now wrapped in `Secret` (cmk.server_side_calls.v1) so Checkmk masks it in process listings and the UI.
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
