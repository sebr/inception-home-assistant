"""Mock API response fixtures for testing."""

from __future__ import annotations

from typing import Any

# Mock door summary responses
MOCK_DOOR_SUMMARIES: dict[str, Any] = {
    "Doors": {
        "1": {
            "Id": 1,
            "EntityInfo": {
                "Id": 1,
                "Name": "Front Door",
                "Description": "Main entrance door",
            },
        },
        "2": {
            "Id": 2,
            "EntityInfo": {
                "Id": 2,
                "Name": "Back Door",
                "Description": "Rear entrance door",
            },
        },
        "3": {
            "Id": 3,
            "EntityInfo": {
                "Id": 3,
                "Name": "Garage Door",
                "Description": "Vehicle entrance",
            },
        },
    },
}

# Mock door state responses
MOCK_DOOR_STATES: list[dict[str, Any]] = [
    {
        "id": 1,
        "locked": True,
        "open": False,
        "forced": False,
        "heldOpen": False,
        "readerTamper": False,
    },
    {
        "id": 2,
        "locked": False,
        "open": True,
        "forced": False,
        "heldOpen": False,
        "readerTamper": False,
    },
    {
        "id": 3,
        "locked": True,
        "open": False,
        "forced": True,
        "heldOpen": False,
        "readerTamper": False,
    },
]

# Mock area summary responses
MOCK_AREA_SUMMARIES: dict[str, Any] = {
    "Areas": {
        "1": {
            "Id": 1,
            "EntityInfo": {
                "Id": 1,
                "Name": "Main Area",
                "Description": "Primary security area",
            },
        },
        "2": {
            "Id": 2,
            "EntityInfo": {
                "Id": 2,
                "Name": "Perimeter",
                "Description": "Outdoor security zone",
            },
        },
    },
}

# Mock area state responses
MOCK_AREA_STATES: list[dict[str, Any]] = [
    {
        "id": 1,
        "armed": False,
        "mode": "disarmed",
        "partArmed": False,
    },
    {
        "id": 2,
        "armed": True,
        "mode": "armed",
        "partArmed": False,
    },
]

# Mock input summary responses
MOCK_INPUT_SUMMARIES: dict[str, Any] = {
    "Inputs": {
        "1": {
            "Id": 1,
            "EntityInfo": {
                "Id": 1,
                "Name": "Motion Sensor",
                "Description": "PIR motion detector",
            },
        },
        "2": {
            "Id": 2,
            "EntityInfo": {
                "Id": 2,
                "Name": "Door Contact",
                "Description": "Magnetic door sensor",
            },
        },
        "3": {
            "Id": 3,
            "EntityInfo": {
                "Id": 3,
                "Name": "Glass Break",
                "Description": "Acoustic glass break detector",
            },
        },
    },
}

# Mock input state responses
MOCK_INPUT_STATES: list[dict[str, Any]] = [
    {
        "id": 1,
        "active": False,
        "isolated": False,
    },
    {
        "id": 2,
        "active": True,
        "isolated": False,
    },
    {
        "id": 3,
        "active": False,
        "isolated": True,
    },
]

# Mock output summary responses
MOCK_OUTPUT_SUMMARIES: dict[str, Any] = {
    "Outputs": {
        "1": {
            "Id": 1,
            "EntityInfo": {
                "Id": 1,
                "Name": "Siren",
                "Description": "Main alarm siren",
            },
        },
        "2": {
            "Id": 2,
            "EntityInfo": {
                "Id": 2,
                "Name": "Strobe",
                "Description": "Visual alarm indicator",
            },
        },
    },
}

# Mock output state responses
MOCK_OUTPUT_STATES: list[dict[str, Any]] = [
    {
        "id": 1,
        "active": False,
    },
    {
        "id": 2,
        "active": True,
    },
]

# Complete API response mock
MOCK_API_RESPONSE: dict[str, Any] = {
    "doors": MOCK_DOOR_SUMMARIES,
    "areas": MOCK_AREA_SUMMARIES,
    "inputs": MOCK_INPUT_SUMMARIES,
    "outputs": MOCK_OUTPUT_SUMMARIES,
}

# Update monitor response mock
MOCK_UPDATE_MONITOR_RESPONSE: dict[str, Any] = {
    "doors": [
        {"id": 1, **MOCK_DOOR_STATES[0]},
        {"id": 2, **MOCK_DOOR_STATES[1]},
    ],
    "areas": [
        {"id": 1, **MOCK_AREA_STATES[0]},
    ],
    "inputs": [
        {"id": 1, **MOCK_INPUT_STATES[0]},
        {"id": 2, **MOCK_INPUT_STATES[1]},
    ],
    "outputs": [
        {"id": 1, **MOCK_OUTPUT_STATES[0]},
    ],
}

# Error responses
MOCK_AUTH_ERROR_RESPONSE: dict[str, Any] = {
    "error": "Unauthorized",
    "message": "Invalid token",
}

MOCK_SERVER_ERROR_RESPONSE: dict[str, Any] = {
    "error": "Internal Server Error",
    "message": "Server encountered an error",
}
