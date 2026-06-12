# f24ecall — SMS-Benachrichtigungs-Plugin für Checkmk

Checkmk-Notification-Plugin zum Versand von SMS-Alarmen über die [F24 eCall](https://ecall-messaging.com) HTTPS-API.

Basiert auf [ecallch](https://github.com/HeinleinSupport/check_mk_extensions/tree/cmk2.4/notifications/ecallch) von Heinlein Support GmbH.

## Voraussetzungen

- Checkmk 2.3.0 oder neuer
- F24 eCall-Konto mit aktivierter HTTP/HTTPS-Schnittstelle (muss beim eCall-Support explizit freigeschaltet werden)
- Mobilnummer des Kontakts im Feld **Pager-Adresse** in Checkmk hinterlegt

## Installation

1. **Setup → Extension packages** — MKP-Datei hochladen
2. Paket aktivieren
3. **Activate changes**

## Konfiguration

### 1. Notification-Parameter anlegen

**Setup → Notifications → Notification parameters → f24ecall → Add parameter set**

| Feld | Beschreibung |
|---|---|
| **User Name** | Benutzername des eCall-Kontos |
| **Password** | Passwort des eCall-Kontos (wird maskiert gespeichert) |
| **SMS Message Template** | Optionale Nachrichtenvorlage mit `$VARIABLE$`-Platzhaltern (siehe unten). Wird das Feld leer gelassen, wird ein sinnvoller Standard verwendet. |

### 2. Notification-Regel anlegen

**Setup → Notifications → Add rule**

| Feld | Wert |
|---|---|
| **Notification method** | f24ecall |
| **Parameters** | Zuvor angelegten Parameter-Set auswählen |
| **Contacts** | Kontakt mit hinterlegter Mobilnummer im Feld Pager-Adresse |

## SMS-Nachrichtenvorlagen

Das Feld **SMS Message Template** unterstützt `$VARIABLE$`-Platzhalter aus dem Checkmk-Benachrichtigungskontext. Die Nachricht wird auf 160 Zeichen gekürzt.

### Allgemeine Variablen

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `$NOTIFICATIONTYPE$` | Art der Benachrichtigung | `PROBLEM`, `RECOVERY`, `ACKNOWLEDGEMENT`, `FLAPPINGSTART`, `FLAPPINGSTOP`, `DOWNTIMESTART`, `DOWNTIMEEND`, `CUSTOM` |
| `$NOTIFICATIONCOMMENT$` | Kommentar (bei ACK, Downtime, Custom) | |
| `$CONTACTNAME$` | Benutzername des Checkmk-Kontakts | |
| `$LONGDATETIME$` | Datum und Uhrzeit (lang) | `Mon Apr 27 15:30:00 2026` |
| `$SHORTDATETIME$` | Datum und Uhrzeit (kurz) | `2026-04-27 15:30:00` |
| `$WHAT$` | `HOST` oder `SERVICE` | |

### Host-Variablen

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `$HOSTNAME$` | Hostname | `srv-web-01` |
| `$HOSTALIAS$` | Alias des Hosts | |
| `$HOSTADDRESS$` | IP-Adresse des Hosts | |
| `$HOSTSTATE$` | Zustand des Hosts | `UP`, `DOWN`, `UNREACHABLE` |
| `$HOSTOUTPUT$` | Plugin-Ausgabe des Host-Checks | |
| `$HOSTDOWNTIME$` | Anzahl aktiver Downtimes | |

### Service-Variablen

| Variable | Beschreibung | Beispiel |
|---|---|---|
| `$SERVICEDESC$` | Service-Name | `CPU load` |
| `$SERVICESTATE$` | Zustand des Services | `OK`, `WARNING`, `CRITICAL`, `UNKNOWN` |
| `$SERVICEOUTPUT$` | Plugin-Ausgabe inkl. Messwert und Schwellwerte | `CRITICAL - Load 95% (warn/crit at 80%/90%)` |
| `$SERVICEPERFDATA$` | Performance-Daten (Rohdaten) | |
| `$SERVICEDOWNTIME$` | Anzahl aktiver Downtimes | |

### Acknowledgement-Variablen

| Variable | Beschreibung |
|---|---|
| `$NOTIFICATIONAUTHOR$` | Wer die Meldung bestätigt hat |
| `$NOTIFICATIONCOMMENT$` | Kommentar zur Bestätigung |

## Beispiel-Vorlagen

**Host (Standard):**
```
$NOTIFICATIONTYPE$: $HOSTNAME$ $HOSTSTATE$ $HOSTOUTPUT$
```
→ `PROBLEM: srv-web-01 DOWN PING timeout`

**Service (Standard):**
```
$NOTIFICATIONTYPE$: $HOSTNAME$ $SERVICEDESC$ $SERVICESTATE$ $SERVICEOUTPUT$
```
→ `PROBLEM: srv-web-01 CPU load CRITICAL Load 95% (warn/crit at 80%/90%)`

**Kompakt mit Zeitstempel:**
```
$SHORTDATETIME$ $NOTIFICATIONTYPE$ $HOSTNAME$ $SERVICESTATE$ $SERVICEDESC$
```

**Acknowledgement:**
```
ACK $HOSTNAME$ $SERVICEDESC$ von $NOTIFICATIONAUTHOR$: $NOTIFICATIONCOMMENT$
```

## Links

- [F24 eCall HTTP/HTTPS API-Dokumentation](https://ecall-messaging.com/schnittstellen-und-dokumente/http-https/)
- [Checkmk Notifications](https://docs.checkmk.com/latest/de/notifications.html)
- [Checkmk Benachrichtigungsvariablen](https://docs.checkmk.com/latest/de/notifications.html#environment_variables)

## Lizenz

GNU GPL v2
