# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Bootstrap**: `scripts/bootstrap` - Create `./.venv` with uv on the host (no dev container needed)
- **Setup**: `scripts/setup` - Dev container setup; installs system packages, then runs `scripts/bootstrap`
- **Lint**: `scripts/lint` - Format code with ruff and run linting checks
- **Test**: `scripts/tests` - Run pytest with verbose output
- **Development**: `scripts/develop` - Start Home Assistant in development mode with debug logging
  - `portree up` - Run Home Assistant on a port portree picks for this worktree; `portree ls --json` gives the `direct_url`
  - `HA_PORT=8124 scripts/develop` - Run on a fixed port by hand
  - `scripts/develop --watch` - Restart Home Assistant when files under `custom_components/` change (needs watchexec)
- **Worktree**: `scripts/worktree <branch>` - Create a sibling git worktree that shares this `.venv`, seeded with this checkout's HA state

Scripts use `./.venv` when it exists, otherwise whatever is on `PATH`. They call the venv directly rather than `uv run`, because `uv sync` would remove the Home Assistant component requirements that `scripts/bootstrap` installs for `--skip-pip`.

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

### API Reference

- `docs/inception-api/` - Inner Range's "Inception REST API Sample Usage" document (prose originally written for protocol v8, extended against the `Inception_RestApi.postman_collection.json` shipped for API version 16). Converted to Markdown and split into topic files. Consult these when working on `pyinception/`. Start with `docs/inception-api/README.md` for the index; topic files cover `getting-started.md` (auth: password / hashed / 2FA / API token, logout, SkyTunnel, protocol-version), `entities.md` (Areas, Doors, Inputs, Outputs, Lift Floors, Storage Units, Users), `activities.md` (virtual badge / PIN / user duress + activity state/updates/cancel), `user-management.md` (User CRUD + photos + PIN generation + by-PIN lookup + SkyCommand), `configuration.md` (permission groups and template/profile catalogues), `review-events.md` (event queries), `long-polling.md` (real-time monitoring via `api/v1/monitor-updates` — entity states, activity progress, recent user info, live review events, data changes), and `system.md` (protocol version, system-info). The canonical live docs are served by the controller itself at `http://[inception-address]/ApiDoc` (or `https://skytunnel.com.au/Inception/API_SAMPLE/ApiDoc`).

### Development Environment

Development runs on the host from `./.venv` (see `scripts/bootstrap`); the dev container still works and runs the same script. In both:
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