# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Setup**: `scripts/setup` - Install dependencies and set up development environment
- **Lint**: `scripts/lint` - Format code with ruff and run linting checks
- **Test**: `scripts/tests` - Run pytest with verbose output 
- **Development**: `scripts/develop` - Start Home Assistant in development mode with debug logging

## Repository Architecture

This is a Home Assistant custom integration for InnerRange Inception security systems. The integration follows the standard Home Assistant custom component structure:

### Core Structure

- `custom_components/inception/` - Main integration code
  - `__init__.py` - Entry point with platform setup (alarm_control_panel, binary_sensor, lock, number, select, switch)
  - `coordinator.py` - DataUpdateCoordinator for managing API data fetching
  - `config_flow.py` - Configuration flow for Home Assistant UI setup
  - `entity.py` - Base entity class with common functionality
  - Platform-specific files: `alarm_control_panel.py`, `binary_sensor.py`, `lock.py`, `number.py`, `select.py`, `switch.py`

### PyInception Library

- `custom_components/inception/pyinception/` - Embedded API client library
  - `api.py` - Main API client for InnerRange Inception systems
  - `data.py` - Data structures and models
  - `schemas/` - Pydantic schemas for API responses (door, area, input, output, etc.)

### Development Environment

The project uses a containerized development environment with:
- Home Assistant 2025.9.0 as the base
- Configuration in `config/configuration.yaml` with debug logging enabled for the inception component
- Custom component loaded via PYTHONPATH modification in `scripts/develop`

### Key Integration Points

- **Data Coordinator**: Single coordinator manages all API calls and data updates
- **Entity Platforms**: Each platform (lock, alarm, etc.) creates entities based on user permissions from Inception system
- **Real-time Updates**: Uses local push notifications from Inception system (iot_class: "local_push")

### Testing

Tests should be placed in `tests/` directory. The project uses pytest with Home Assistant test framework integration via `pytest-homeassistant-custom-component`.

### Code Standards

- Uses ruff for formatting and linting with strict rule set (target Python 3.13)
- Black code style enforced
- Type hints required throughout codebase
- Follows Home Assistant integration patterns and conventions