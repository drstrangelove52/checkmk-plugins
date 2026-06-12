# f24ecall — SMS Notification Plugin for Checkmk

Checkmk notification plugin that sends SMS alerts via the [F24 eCall](https://ecall-messaging.com) HTTPS API.

Based on [ecallch](https://github.com/HeinleinSupport/check_mk_extensions/tree/cmk2.4/notifications/ecallch) by Heinlein Support GmbH.

## Requirements

- Checkmk 2.3.0 or later
- F24 eCall account with the HTTP/HTTPS API unlocked (must be enabled by eCall support)
- The contact's mobile number stored in the **Pager address** field in Checkmk

## Installation

1. **Setup → Extension packages** — upload the `.mkp` file
2. Activate the package
3. **Activate changes**

## Configuration

### 1. Create notification parameters

**Setup → Notifications → Notification parameters → f24ecall → Add parameter set**

| Field | Description |
|---|---|
| **User Name** | Your eCall account username |
| **Password** | Your eCall account password (stored masked) |
| **SMS Message Template** | Optional custom message template (see below). If left empty, a sensible default is used. |

### 2. Create notification rule

**Setup → Notifications → Add rule**

| Field | Value |
|---|---|
| **Notification method** | f24ecall |
| **Parameters** | Select the parameter set created above |
| **Contacts** | Contact with a mobile number in the Pager address field |

## SMS Message Templates

The **SMS Message Template** field supports `$VARIABLE$` placeholders from the Checkmk notification context. The message is truncated to 160 characters.

### General variables

| Variable | Description | Example |
|---|---|---|
| `$NOTIFICATIONTYPE$` | Type of notification | `PROBLEM`, `RECOVERY`, `ACKNOWLEDGEMENT`, `FLAPPINGSTART`, `FLAPPINGSTOP`, `DOWNTIMESTART`, `DOWNTIMEEND`, `CUSTOM` |
| `$NOTIFICATIONCOMMENT$` | Comment (for ACK, Downtime, Custom) | |
| `$CONTACTNAME$` | Checkmk username of the contact | |
| `$LONGDATETIME$` | Date and time (long format) | `Mon Apr 27 15:30:00 2026` |
| `$SHORTDATETIME$` | Date and time (short format) | `2026-04-27 15:30:00` |
| `$WHAT$` | `HOST` or `SERVICE` | |

### Host variables

| Variable | Description | Example |
|---|---|---|
| `$HOSTNAME$` | Hostname | `srv-web-01` |
| `$HOSTALIAS$` | Host alias | |
| `$HOSTADDRESS$` | Host IP address | |
| `$HOSTSTATE$` | Host state | `UP`, `DOWN`, `UNREACHABLE` |
| `$HOSTOUTPUT$` | Host check plugin output | |
| `$HOSTDOWNTIME$` | Number of active downtimes | |

### Service variables

| Variable | Description | Example |
|---|---|---|
| `$SERVICEDESC$` | Service name | `CPU load` |
| `$SERVICESTATE$` | Service state | `OK`, `WARNING`, `CRITICAL`, `UNKNOWN` |
| `$SERVICEOUTPUT$` | Plugin output including value and thresholds | `CRITICAL - Load 95% (warn/crit at 80%/90%)` |
| `$SERVICEPERFDATA$` | Raw performance data | |
| `$SERVICEDOWNTIME$` | Number of active downtimes | |

### Acknowledgement variables

| Variable | Description |
|---|---|
| `$NOTIFICATIONAUTHOR$` | Who acknowledged |
| `$NOTIFICATIONCOMMENT$` | Acknowledgement comment |

## Example Templates

**Host (default):**
```
$NOTIFICATIONTYPE$: $HOSTNAME$ $HOSTSTATE$ $HOSTOUTPUT$
```
→ `PROBLEM: srv-web-01 DOWN PING timeout`

**Service (default):**
```
$NOTIFICATIONTYPE$: $HOSTNAME$ $SERVICEDESC$ $SERVICESTATE$ $SERVICEOUTPUT$
```
→ `PROBLEM: srv-web-01 CPU load CRITICAL Load 95% (warn/crit at 80%/90%)`

**Compact with timestamp:**
```
$SHORTDATETIME$ $NOTIFICATIONTYPE$ $HOSTNAME$ $SERVICESTATE$ $SERVICEDESC$
```

**Acknowledgement:**
```
ACK $HOSTNAME$ $SERVICEDESC$ by $NOTIFICATIONAUTHOR$: $NOTIFICATIONCOMMENT$
```

## Links

- [F24 eCall HTTP/HTTPS API documentation](https://ecall-messaging.com/schnittstellen-und-dokumente/http-https/)
- [Checkmk Notifications](https://docs.checkmk.com/latest/en/notifications.html)
- [Checkmk notification context variables](https://docs.checkmk.com/latest/en/notifications.html#environment_variables)

## License

GNU GPL v2
