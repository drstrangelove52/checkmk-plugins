# VMware vSphere Snapshot Plugin – Deployment

## Voraussetzungen

```bash
# pyVmomi auf dem Checkmk-Server installieren (als Site-User)
pip3 install pyVmomi
```

## Dateistruktur auf dem Checkmk-Server

Alle Pfade relativ zum Site-Verzeichnis, z.B. `/omd/sites/cmk/`.

```
local/lib/python3/cmk/special_agents/
    agent_vsphere_snapshots.py

local/lib/python3/cmk/plugins/vsphere_snapshots/
    __init__.py
    agent_based/
        __init__.py
        vsphere_snapshots.py
    rulesets/
        __init__.py
        special_agent.py
        check_parameters.py
    server_side_calls/
        __init__.py
        special_agent.py
```

## Deployment

```bash
# Als Site-User (su - cmk)
SITE_LOCAL=/omd/sites/cmk/local

# Special Agent
mkdir -p $SITE_LOCAL/lib/python3/cmk/special_agents/
cp special_agents/agent_vsphere_snapshots.py \
   $SITE_LOCAL/lib/python3/cmk/special_agents/

# Plugin-Paket
PLUGIN_DIR=$SITE_LOCAL/lib/python3/cmk/plugins/vsphere_snapshots
mkdir -p $PLUGIN_DIR/{agent_based,rulesets,server_side_calls}

cp lib/python3/cmk/plugins/vsphere_snapshots/__init__.py $PLUGIN_DIR/
cp lib/python3/cmk/plugins/vsphere_snapshots/agent_based/* $PLUGIN_DIR/agent_based/
cp lib/python3/cmk/plugins/vsphere_snapshots/rulesets/*    $PLUGIN_DIR/rulesets/
cp lib/python3/cmk/plugins/vsphere_snapshots/server_side_calls/* $PLUGIN_DIR/server_side_calls/

# Checkmk neu laden
cmk -R
```

## Konfiguration in Checkmk

### 1. Sammel-Host anlegen

In Setup → Hosts einen Host anlegen, z.B. `vcenter-snapshots`.
Kein Monitoring-Agent, kein Ping – dieser Host erhält seine Daten nur via Piggyback.

Unter „Data Sources" → „No data sources" oder Piggyback aktivieren.

### 2. vCenter-Host anlegen

Host für das vCenter anlegen, z.B. `vcenter01`.
Unter „Data Sources" → „Special agents" → „VMware vSphere Snapshots" konfigurieren:

- **vCenter Hostname**: `vcenter01.pe.lan`
- **Benutzername**: `administrator@vsphere.local`
- **Passwort**: im Passwort-Speicher hinterlegen, dann auswählen
- **Sammel-Host**: `vcenter-snapshots` (muss als Host existieren)
- **Nur Hostname**: aktivieren, wenn vCenter FQDNs verwendet, Checkmk aber Kurznamen

### 3. Schwellwerte konfigurieren

Setup → Services → Service monitoring rules → „VMware Snapshot Schwellwerte"

### 4. Service Discovery

Nach der Konfiguration Service Discovery auf dem vCenter-Host und dem Sammel-Host ausführen.

## Verhalten

- **VMs mit eigenem Checkmk-Host**: Piggyback-Daten erscheinen direkt auf dem VM-Host.  
  Service heisst: `VMware Snapshots`
- **VMs ohne Checkmk-Host**: Erscheinen auf dem Sammel-Host.  
  Service heisst: `VMware Snapshots <VM-Name>`

## Snapshot-Beschreibung (Datum-Pflicht)

Jeder Snapshot **muss** in der Beschreibung genau ein Datum im Format `TT.MM.JJJJ` enthalten –
nur das Datum, kein weiterer Text. Dieses Datum wird von einem Cleanup-Script verwendet.

Beispiel einer gültigen Beschreibung: `15.12.2024`

Fehlt das Datum oder ist das Format falsch, wechselt der Service in WARN oder CRIT
(konfigurierbar unter „VMware Snapshot Schwellwerte").
