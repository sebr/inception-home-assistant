# InnerRange Inception

_Integration to integrate with [Inner Range Inception](https://www.innerrange.com/products/controllers/996300) security systems._

If this integration has been useful to you, please consider chipping in and buying me a coffee!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/sebr)

**This integration will set up the following platforms:**

Platform | Description
-- | --
`lock` | A lock for each configured Door.
`number` | A number input which is used to define the duration of a timed unlock operation for each Door.
`select` | A select which is used to choose the unlock operation of each door (i.e. Unlock or Timed Unlock).
`alarm_control_panel` | For each Area that can be armed or disarmed.
`binary_sensor` | For each Input and for Door attributes such as Open or Isolated states.
`sensor` | Diagnostic sensor for the last received review event.
`switch` | A switch for each Siren or Strobe, plus switches to control review event monitoring.

## Supported Inception Entities

### Doors

For each door that the authenticated user has permission to access, the following entities are created:

* A `lock` entity to lock and unlock the door. By default, the `lock.unlock` action will permanently unlock the door.
* A `select` entity to choose the unlock operation of the door. The options are `Unlock` or `Timed Unlock`.
* A `number` entity to set the duration of a timed unlock operation. The duration is in seconds and the default value is **5 seconds**.
* `binary_sensor` entities which indicate: Open, Forced, Held Open to Long, Reader Tamper

### Areas

For each area that the authenticated user has permission to access, the following entities are created:

* An `alarm_control_panel` entity to arm and disarm the area. If multi-mode area arming is enabled, Night and Perimiter modes are also available.

### Inputs

For each input that the authenticated user has permission to access, the following entities are created:

* A `binary_sensor` entity to indicate the state of the input. Calculated inputs such as forced and held open are disabled by default. The device class is inferred from the input's name.
* A `switch` entity to control if the input has been Isolated

### Outputs

For each output that the authenticated user has permission to access, the following entities are created:

* A `switch` entity to control the output. Typically a siren or strobe.

### Diagnostic Sensors

The integration provides diagnostic sensors for monitoring and troubleshooting:

* **Last Review Event Sensor**: A diagnostic sensor that displays the message description of the most recently received review event. All event data is available as entity attributes including event ID, timestamps, who/what/where information, and message details. This sensor is automatically disabled when review event monitoring is turned off and is useful for debugging event reception and creating dashboards showing recent security activity.

### Review Event Controls

The integration includes configuration switches to control review event monitoring:

* **Global Review Events Switch**: Master switch to enable/disable all review event monitoring
* **Category Switches**: Individual switches for each event category (System, Audit, Access, Security, Hardware) allowing fine-grained control over which types of events are monitored

## Services

The integration provides custom services for advanced control of Inception entities.

### inception.unlock

Unlocks a door with optional timed unlock functionality.

**Target:** Lock entities (`lock` domain)

**Parameters:**
- `time_secs` (optional): Number of seconds to grant access. If provided, performs a timed unlock. If omitted, performs a permanent unlock.
  - Type: Integer
  - Default: Permanent unlock (no time limit)

**Example:**
```yaml
# Permanent unlock
service: inception.unlock
target:
  entity_id: lock.front_door

# Timed unlock for 30 seconds
service: inception.unlock
target:
  entity_id: lock.front_door
data:
  time_secs: 30
```

### inception.area_arm

Arms an area with custom exit delay and seal check settings. This service provides fine-grained control over the arming process beyond the standard alarm panel controls.

**Target:** Alarm control panel entities (`alarm_control_panel` domain)

**Parameters:**
- `exit_delay` (optional): Enable exit delay when arming. When enabled, provides time to exit the premises before the system fully activates.
  - Type: Boolean
  - Default: System default

- `seal_check` (optional): Check if all inputs are sealed (inactive/closed) before arming. When enabled, arming will fail if any inputs are unsealed.
  - Type: Boolean
  - Default: System default

- `code` (optional): PIN code for arming the area.
  - Type: String
  - Default: None (If omitted, defaults to the user which is associated with the integration's configured API token.)

**Example:**
```yaml
# Arm with default system behavior
service: inception.area_arm
target:
  entity_id: alarm_control_panel.main_area
data:
  code: "1234"

# Arm without exit delay (instant arm)
service: inception.area_arm
target:
  entity_id: alarm_control_panel.main_area
data:
  exit_delay: false
  code: "1234"

# Force arm without checking if inputs are sealed
service: inception.area_arm
target:
  entity_id: alarm_control_panel.main_area
data:
  seal_check: false
  code: "1234"

# Instant arm and bypass seal check
service: inception.area_arm
target:
  entity_id: alarm_control_panel.main_area
data:
  exit_delay: false
  seal_check: false
  code: "1234"
```

## Events

The integration emits Home Assistant events for real-time security notifications:

### Review Events

The integration automatically monitors and emits `inception_review_event` events for security activities such as:

* Door access attempts (card access, PIN entry)
* Area arming/disarming activities
* Input state changes (motion detection, door sensors)
* System events (tamper alerts, communication errors)

**Event Data Structure:**
```json
{
  "event_id": "evt_123",
  "description": "Card access granted",
  "message_category": "Access",
  "message_value": "2011",
  "message_description": "Door Access Granted from Access Button",
  "when": "2025-09-14T21:48:41.3832147+10:00",
  "who": "John Doe",
  "what": "Front Door",
  "where": "Main Entrance",
  "when_ticks": 1701432600
}
```

**Event Fields:**
- `event_id`: Unique identifier for the event
- `description`: Human-readable description from the system
- `message_category`: Category of the message (e.g., "Access", "Security")
- `message_value`: Category of the message (e.g., 2001, 5000)
- `message_description`: Detailed description based on the MessageID (automatically added by integration)
- `when`: Timestamp in ISO 6801 format
- `reference_time`: The timestamp of the event in UTC ticks in string form, used as a reference point to query for newer events
- `who`: The name of the Inception User or entity that triggered this event, if applicable
- `who_id`: The Inception ID of the entity who triggered this event
- `what`: The name of the Inception entity that was affected by this event, if applicable
- `what_id`: The Inception ID of the entity who was affected by this event
- `where`: The name of the area or location where the event occurred, if applicable
- `where_id`: The Inception ID of the entity where the event was triggered

**Using in Automations:**
```yaml
automation:
  - alias: "Log Security Events"
    trigger:
      platform: event
      event_type: inception_review_event
      event_data:
        message_category: "Access"
    action:
      - service: logbook.log
        data:
          name: "Security System"
          message: "{{ trigger.event.data.description }} - {{ trigger.event.data.who }} at {{ trigger.event.data.where }}"

  - alias: "Alert on Security Breach"
    trigger:
      platform: event
      event_type: inception_review_event
      event_data:
        message_value: 5501 # Input Event Created
    action:
      - service: notify.mobile_app
        data:
          message: "Security Alert: {{ trigger.event.data.description }}"

  - alias: "Door Access Notification"
    trigger:
      platform: event
      event_type: inception_review_event
      event_data:
        message_category: "Access"
    action:
      - service: notify.mobile_app
        data:
          title: "Door Access"
          message: "{{ trigger.event.data.message_description }} - {{ trigger.event.data.who }} at {{ trigger.event.data.what }}"
```

**Note:** Review events are only available if your Inception user account has permission to access the review/audit logs. If you see 404 errors in the logs, contact your system administrator to enable review event permissions.

## Installation

Recommended installation is via the [Home Assistant Community Store (HACS)](https://hacs.xyz/). [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

### 1. Install via HACS

If you do not wish to use HACS, then please download the latest version from the [releases page](https://github.com/sebr/inception-home-assistant/releases) and proceed to Step 2.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sebr&repository=inception-home-assistant&category=integration)

1. Navigate to the HACS add-on
2. Search for the `Inception` integration and install it
3. Restart Home Assistant

### 2. Configure via Home Assistant

1. Navigate to Home Assistant Settings > Devices & Services
2. Click `+ Add Integration`
3. Search for `Inception`
4. Complete the guided configuration

### Create a user in Inception

I strongly recommend creating a new user in Inception for Home Assistant to use.

Create a new user
<img width="1420" alt="Screenshot 2024-12-09 at 7 18 42 pm" src="https://github.com/user-attachments/assets/0b3b33e6-d65e-43af-8d59-ba07f4d3d551">

Grant the user permission to access required entities
<img width="1420" alt="Screenshot 2024-12-09 at 7 18 11 pm" src="https://github.com/user-attachments/assets/ced17288-39ed-400b-8f67-04f5ecdf5426">

Grant the user `REST Web API User` web page profile and create a `User API Token`
<img width="1420" alt="Screenshot 2024-12-09 at 7 19 04 pm" src="https://github.com/user-attachments/assets/254eeda4-3451-445e-a466-eac2fd9297a7">

## Contributions are welcome

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Acknowledgements

This integration is a custom component Home Assistant port of the excellent [inception-mqtt](https://github.com/matthew-larner/inception-mqtt/) project by @matthew-larner.
