# Vectra NDR – Sensor Health Monitoring

Checkmk plugin that monitors the health of **Vectra NDR virtual sensors** via the Vectra Brain REST API.

## Overview

Vectra sensors are hardened virtual appliances — they do not run a Checkmk agent. All health data is fetched exclusively from the Vectra Brain REST API (`/api/v3.4/health`). The plugin creates one Checkmk service per sensor discovered on the Brain.

## Requirements

- Checkmk 2.3 or later
- Vectra Brain with API access
- API token with **Detect view health** permission  
  *(Brain UI → My Profile → View/Generate API Token)*

## Installation

1. Download the latest `.mkp` file from the [releases](../../releases) page.
2. In Checkmk: **Setup → Extension packages → Upload package**
3. Activate changes.

## Configuration

Navigate to **Setup → Agents → Other integrations → Vectra NDR – Sensor Health**.

| Field | Required | Description |
|---|---|---|
| Brain Hostname / IP | Yes | Hostname or IP of the Vectra Brain (without `https://`) |
| Brain Port | No | TCP port, default: 443 |
| API Token | Yes | Token from Brain UI |
| Request timeout (seconds) | No | Default: 30 s |
| Do not verify SSL certificate | No | For self-signed certificates only |

Assign the rule to the Checkmk host that represents your Vectra Brain.

## What the plugin checks

For each sensor discovered on the Brain, two aspects are evaluated:

**Pairing status**

| Sensor state | Checkmk state |
|---|---|
| `paired` | OK |
| `degraded` | WARN |
| `offline` | CRIT |
| `disconnected` | CRIT |
| unknown | WARN |

**Heartbeat age** (`last_seen`)  
Time elapsed since the sensor last contacted the Brain. Thresholds are configurable via **Setup → Service monitoring rules → Vectra NDR – Sensor Health Thresholds**.

| Default threshold | State |
|---|---|
| > 1 hour | WARN |
| > 24 hours | CRIT |

## Service output

```
Vectra Sensor <name>   OK   Paired | Last seen 4 min. ago
```

The service detail view shows: status, last seen timestamp, IP address, serial number, software version, location, and LUID.

A performance metric (`vectra_sensor_last_seen_minutes`) is recorded for graphing.

