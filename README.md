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
`switch` | A switch for each Siren or Strobe.

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
