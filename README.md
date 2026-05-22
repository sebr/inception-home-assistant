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
`switch` | A switch for each Siren or Strobe, switches to control custom inputs (activate/deactivate), and switches to control review event monitoring.

## Supported Inception Entities

### Doors

For each door that the authenticated user has permission to access, the following entities are created:

* A `lock` entity to lock and unlock the door. By default, the `lock.unlock` action will permanently unlock the door.
* A `select` entity to choose the unlock operation of the door. The options are `Unlock` or `Timed Unlock`.
* A `number` entity to set the duration of a timed unlock operation. The duration is in seconds and the default value is **5 seconds**.
* `binary_sensor` entities which indicate: Open, Forced, Held Open to Long, Reader Tamper

### Areas

For each area that the authenticated user has permission to access, the following entities are created:

* An `alarm_control_panel` entity to arm and disarm the area. If multi-mode area arming is enabled, Night and Perimeter modes are also available. PIN code requirements can be configured in the integration options (see [Configure alarm code options](#3-configure-alarm-code-options-optional)).

### Inputs

For each input that the authenticated user has permission to access, the following entities are created:

* A `binary_sensor` entity to indicate the state of the input. Calculated inputs such as forced and held open are disabled by default. The device class is inferred from the input's name.
* A `switch` entity to control if the input has been Isolated

#### Custom Inputs

Custom inputs created in the Inception system have additional functionality:

* An **Active** switch to control the activation state of the custom input
  - Allows you to programmatically activate or deactivate custom inputs from Home Assistant
  - Useful for triggering automation macros configured in the Inception system
  - The switch state reflects whether the custom input is currently active

Custom inputs can be used to integrate Home Assistant automations with Inception system logic. For example, you could create a custom input in Inception that triggers specific actions (unlocking multiple doors, changing area modes, etc.) and then activate it from Home Assistant based on any trigger or condition.

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

### inception.badge_credential

Virtually badges a user credential at a door reader, as though the card had been physically presented. The Inception controller carries out the resulting access attempt (grant / deny / review-event emission) exactly as it would for a real swipe.

**Parameters:**
- `reader_id` (required): ID of the reader to badge at. Discover reader IDs via the [`inception.get_attached_readers`](#inceptionget_attached_readers) service.
- `credential_template` (required): The Credential Template ID of the user credential. Available from the user's `PhysicalCredentials[]` entry in the Inception API.
- `card_number` (required): The card number (Credential `Data` value) of the user credential.
- `entry_id` (optional): Select which configured Inception hub to target. Only required when multiple hubs are configured.

**Response:** A service response containing `activity_id` — the controller's `ActivityID` for the submitted activity, useful for cross-referencing review events.

**Example:**
```yaml
service: inception.badge_credential
data:
  reader_id: "5a1b8b27-3d0c-4d52-9f72-3f0e5b9d4a52"
  credential_template: "0f8c5e94-5cb7-4f3f-9b66-2e2e3c0a5d33"
  card_number: "0000123"
response_variable: result
```

### inception.send_pin

Virtually presents a User PIN at a door reader, as though it had been physically entered on the keypad.

**Parameters:**
- `reader_id` (required): ID of the reader to present the PIN at. Discover reader IDs via the [`inception.get_attached_readers`](#inceptionget_attached_readers) service.
- `pin` (required): The User PIN to present. PINs cannot be retrieved from the Inception API (they are write-only for security), so the caller must know the value.
- `entry_id` (optional): Select which configured Inception hub to target. Only required when multiple hubs are configured.

**Response:** A service response containing `activity_id` — the controller's `ActivityID` for the submitted activity.

**Example:**
```yaml
service: inception.send_pin
data:
  reader_id: "5a1b8b27-3d0c-4d52-9f72-3f0e5b9d4a52"
  pin: "1234"
response_variable: result
```

### inception.get_attached_readers

Returns the readers attached to a door. Use the resulting reader IDs with [`inception.badge_credential`](#inceptionbadge_credential) and [`inception.send_pin`](#inceptionsend_pin). Reader IDs are stable, so you typically only need to call this once per automation while wiring it up.

**Parameters:**
- `door_id` (required): The Inception ID of the door to list readers for. Available as the `unique_id` of the door's lock entity in Home Assistant.
- `entry_id` (optional): Select which configured Inception hub to query. Only required when multiple hubs are configured.

**Response:** A service response containing `readers` (the list of reader objects, each with `ID` and `Name`) and `count`.

**Example:**
```yaml
service: inception.get_attached_readers
data:
  door_id: "fbec7c22-500d-4f3b-b94e-4c19ff501f9f"
response_variable: result
```

### inception.get_review_events

Queries historical review events from the Inception controller. Returns matching events as a service response.

**Parameters:** All optional. Leave them empty to fetch the most recent events.
- `limit`: Maximum number of events to return (default 100, max 1000).
- `offset`: Skip this many events before returning results. Use with `limit` for pagination.
- `direction`: `asc` (oldest first, default) or `desc` (newest first).
- `start` / `end`: Earliest / latest event timestamp to include.
- `category_filter`: One or more of `System`, `Audit`, `Access`, `Security`, `Hardware`.
- `message_type_id_filter`: A list of numeric `MessageID` values to match.
- `involved_entity_id_filter`: A list of UUID strings — events whose `WhoID`, `WhatID`, or `WhereID` matches will be returned.
- `reference_id` / `reference_time`: Anchor pagination around a specific event (the event's ID and its `WhenTicks` value).
- `entry_id`: Select which configured Inception hub to query. Only required when multiple hubs are configured.

**Response:** A service response containing `events` (the list of event records) and `count`.

**Example:**
```yaml
service: inception.get_review_events
data:
  limit: 50
  direction: desc
  category_filter: [Access, Security]
response_variable: result
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

### Inception trigger platform

For easier discovery in the visual automation editor, the integration also registers an `inception` trigger type. Pick **Inception** → **Review event received** from the trigger type dropdown and choose any optional filters (category, message ID, who/what/where IDs). Multiple values per field are OR-ed together; multiple fields are AND-ed.

YAML equivalent:

```yaml
automation:
  - alias: "Alert on Door Forced Open"
    trigger:
      platform: inception
      message_value: [5505] # Input forced
      where_id: ["abc123"]
    action:
      - service: notify.mobile_app
        data:
          message: "{{ trigger.event.data.description }}"
```


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

### 3. Configure alarm code options (optional)

After adding the integration, you can configure how the alarm control panel handles PIN codes:

1. Navigate to Home Assistant Settings > Devices & Services
2. Find the Inception integration and click `Configure`
3. Adjust the following options:

Option | Description | Default
-- | -- | --
**Require pin code** | When enabled, a code is required for area arming/disarming. If disabled, area operations will be performed as the user which is associated with the configured API token. | Enabled
**Require code to arm** | When enabled, a valid code must be entered to arm the alarm. When disabled, a code is only required for disarming. | Disabled

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
