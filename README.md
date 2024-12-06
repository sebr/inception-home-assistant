# InnerRange Inception

_Integration to integrate with [Inner Range Inception](https://www.innerrange.com/products/controllers/996300) security systems._

If this integration has been useful to you, please consider chipping in and buying me a coffee!

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/sebr)

**This integration will set up the following platforms.**

Platform | Description
-- | --
`lock` | A lock for each configured Door.
`alarm_control_panel` | For each Area that can be armed or disarmed.
`binary_sensor` | For each Input and for metadata of each Door.
`switch` | A switch for each Siren or Strobe.

## Installation

Recommended installation is via the [Home Assistant Community Store (HACS)](https://hacs.xyz/). [![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

### 1. Install via HACS

If you do not wish to use HACS, then please download the latest version from the [releases page](https://github.com/sebr/inception-home-assistant/releases) and proceed to Step 2.

1. Navigate to the HACS add-on
2. Search for the `Inception` integration and install it
3. Restart Home Assistant


### 2. Configure via Home Assistant

1. Navigate to Home Assistant Settings > Devices & Services
2. Click `+ Add Integration`
3. Search for `Inception`
4. Complete the guided configuration

## Configuration is done in the UI

1. Navigate to your Inception controller
2. Create a user and assign it the appropriate permissions
3. Create a token for the user

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Acknowledgements

This integration is a custom component Home Assistant port of the excellent [inception-mqtt](https://github.com/matthew-larner/inception-mqtt/) project by @matthew-larner.
