"""Test the Inception alarm control panel entity."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityDescription,
)
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
    AlarmControlPanelState,
    CodeFormat,
)

from custom_components.inception.alarm_control_panel import (
    InceptionAlarm,
    InceptionAlarmDescription,
)
from custom_components.inception.entity import InceptionEntity
from custom_components.inception.pyinception.schemas.area import AreaPublicState


class TestInceptionAlarm:
    """Test InceptionAlarm entity."""

    def test_alarm_class_exists(self) -> None:
        """Test that alarm class exists and has expected structure."""
        assert hasattr(InceptionAlarm, "__init__")
        assert hasattr(InceptionAlarm, "async_alarm_arm_away")
        assert hasattr(InceptionAlarm, "async_alarm_arm_home")
        assert hasattr(InceptionAlarm, "async_alarm_arm_night")
        assert hasattr(InceptionAlarm, "async_alarm_disarm")
        assert hasattr(InceptionAlarm, "_alarm_control")
        assert isinstance(InceptionAlarm, type)

    def test_alarm_inheritance(self) -> None:
        """Test alarm entity inheritance."""
        assert issubclass(InceptionAlarm, AlarmControlPanelEntity)
        assert issubclass(InceptionAlarm, InceptionEntity)

    def test_entity_description_class(self) -> None:
        """Test entity description class exists."""
        assert hasattr(InceptionAlarmDescription, "__init__")
        assert issubclass(InceptionAlarmDescription, AlarmControlPanelEntityDescription)

    def test_alarm_attributes(self) -> None:
        """Test alarm entity attributes."""
        # Create a dummy instance to check attributes that are set in __init__
        mock_coordinator = Mock()
        mock_area_data = Mock()
        mock_area_data.entity_info.id = "test_id"
        mock_area_data.entity_info.name = "Test"
        mock_area_data.arm_info.multi_mode_arm_enabled = True
        mock_area_data.public_state = AreaPublicState.DISARMED

        description = InceptionAlarmDescription(key="test", name="Test")
        alarm = InceptionAlarm(
            coordinator=mock_coordinator,
            entity_description=description,
            data=mock_area_data,
        )

        # Check that the code format and arm requirement are properly set
        assert alarm._attr_code_arm_required is True
        assert alarm._attr_code_format == CodeFormat.NUMBER

    @pytest.fixture
    def mock_coordinator(self) -> Mock:
        """Create a mock coordinator."""
        coordinator = Mock()
        coordinator.api = Mock()
        coordinator.api.request = AsyncMock()
        return coordinator

    @pytest.fixture
    def mock_area_data(self) -> Mock:
        """Create mock area data."""
        area_data = Mock()
        area_data.entity_info.id = "area_123"
        area_data.entity_info.name = "Test Area"
        area_data.arm_info.multi_mode_arm_enabled = True
        area_data.public_state = AreaPublicState.DISARMED
        return area_data

    @pytest.fixture
    def alarm_entity(
        self, mock_coordinator: Mock, mock_area_data: Mock
    ) -> InceptionAlarm:
        """Create an alarm entity for testing."""
        description = InceptionAlarmDescription(
            key="area_123",
            name="Test Area",
        )
        return InceptionAlarm(
            coordinator=mock_coordinator,
            entity_description=description,
            data=mock_area_data,
        )

    def test_alarm_init(self, alarm_entity: InceptionAlarm) -> None:
        """Test alarm entity initialization."""
        assert alarm_entity.entity_description.key == "area_123"
        assert alarm_entity.entity_description.name == "Test Area"
        assert alarm_entity.data.entity_info.id == "area_123"

    def test_supported_features_multi_mode(
        self, mock_coordinator: Mock, mock_area_data: Mock
    ) -> None:
        """Test supported features with multi-mode enabled."""
        mock_area_data.arm_info.multi_mode_arm_enabled = True
        description = InceptionAlarmDescription(key="area_123", name="Test Area")
        alarm = InceptionAlarm(
            coordinator=mock_coordinator,
            entity_description=description,
            data=mock_area_data,
        )

        expected_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.ARM_HOME
            | AlarmControlPanelEntityFeature.ARM_NIGHT
            | AlarmControlPanelEntityFeature.TRIGGER
        )
        assert alarm._attr_supported_features == expected_features

    def test_supported_features_single_mode(
        self, mock_coordinator: Mock, mock_area_data: Mock
    ) -> None:
        """Test supported features with multi-mode disabled."""
        mock_area_data.arm_info.multi_mode_arm_enabled = False
        description = InceptionAlarmDescription(key="area_123", name="Test Area")
        alarm = InceptionAlarm(
            coordinator=mock_coordinator,
            entity_description=description,
            data=mock_area_data,
        )

        expected_features = (
            AlarmControlPanelEntityFeature.ARM_AWAY
            | AlarmControlPanelEntityFeature.TRIGGER
        )
        assert alarm._attr_supported_features == expected_features

    @pytest.mark.parametrize(
        ("area_state", "expected_alarm_state"),
        [
            (AreaPublicState.ALARM, AlarmControlPanelState.TRIGGERED),
            (AreaPublicState.ENTRY_DELAY, AlarmControlPanelState.PENDING),
            (AreaPublicState.EXIT_DELAY, AlarmControlPanelState.PENDING),
            (AreaPublicState.ARM_WARNING, AlarmControlPanelState.ARMING),
            (AreaPublicState.STAY_ARM, AlarmControlPanelState.ARMED_HOME),
            (AreaPublicState.SLEEP_ARM, AlarmControlPanelState.ARMED_NIGHT),
            (AreaPublicState.AWAY_ARM, AlarmControlPanelState.ARMED_AWAY),
            (AreaPublicState.ARMED, AlarmControlPanelState.ARMED_AWAY),
            (AreaPublicState.DISARMED, AlarmControlPanelState.DISARMED),
        ],
    )
    def test_alarm_state_mapping(
        self,
        alarm_entity: InceptionAlarm,
        area_state: AreaPublicState,
        expected_alarm_state: AlarmControlPanelState,
    ) -> None:
        """Test alarm state mapping from area states."""
        alarm_entity.data.public_state = area_state
        assert alarm_entity.alarm_state == expected_alarm_state

    def test_alarm_state_none_when_no_public_state(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test alarm state returns None when no public state."""
        # Use mock to bypass type checking
        with patch.object(alarm_entity.data, "public_state", None):
            assert alarm_entity.alarm_state is None

    @pytest.mark.asyncio
    async def test_alarm_control_with_code(self, alarm_entity: InceptionAlarm) -> None:
        """Test _alarm_control method with code."""
        code = "1234"
        control_type = "Arm"

        await alarm_entity._alarm_control(control_type, code)

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": control_type,
            "ExecuteAsOtherUser": "true",
            "OtherUserPIN": code,
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_alarm_control_without_code_logs_warning(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test _alarm_control method without code logs warning."""
        control_type = "Arm"

        with patch(
            "custom_components.inception.alarm_control_panel.LOGGER"
        ) as mock_logger:
            await alarm_entity._alarm_control(control_type, None)

            mock_logger.warning.assert_called_once_with("No alarm code provided")

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": control_type,
            "ExecuteAsOtherUser": "true",
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_async_alarm_arm_away(self, alarm_entity: InceptionAlarm) -> None:
        """Test async_alarm_arm_away method."""
        code = "1234"

        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.async_alarm_arm_away(code)
            mock_control.assert_called_once_with("Arm", code)

    @pytest.mark.asyncio
    async def test_async_alarm_arm_home(self, alarm_entity: InceptionAlarm) -> None:
        """Test async_alarm_arm_home method."""
        code = "1234"

        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.async_alarm_arm_home(code)
            mock_control.assert_called_once_with("ArmStay", code)

    @pytest.mark.asyncio
    async def test_async_alarm_arm_night(self, alarm_entity: InceptionAlarm) -> None:
        """Test async_alarm_arm_night method."""
        code = "1234"

        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.async_alarm_arm_night(code)
            mock_control.assert_called_once_with("ArmSleep", code)

    @pytest.mark.asyncio
    async def test_async_alarm_disarm(self, alarm_entity: InceptionAlarm) -> None:
        """Test async_alarm_disarm method."""
        code = "1234"

        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.async_alarm_disarm(code)
            mock_control.assert_called_once_with("Disarm", code)

    @pytest.mark.asyncio
    async def test_all_alarm_methods_without_code(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test all alarm methods work without code parameter."""
        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.async_alarm_arm_away()
            await alarm_entity.async_alarm_arm_home()
            await alarm_entity.async_alarm_arm_night()
            await alarm_entity.async_alarm_disarm()

            expected_calls = [
                (("Arm", None), {}),
                (("ArmStay", None), {}),
                (("ArmSleep", None), {}),
                (("Disarm", None), {}),
            ]

            assert mock_control.call_count == 4
            for i, expected_call in enumerate(expected_calls):
                assert mock_control.call_args_list[i] == expected_call


class TestInceptionAlarmAreaArmService:
    """Test area_arm service for alarm control panel."""

    @pytest.fixture
    def mock_coordinator(self) -> Mock:
        """Create a mock coordinator."""
        coordinator = Mock()
        coordinator.api = Mock()
        coordinator.api.request = AsyncMock()
        return coordinator

    @pytest.fixture
    def mock_area_data(self) -> Mock:
        """Create mock area data."""
        area_data = Mock()
        area_data.entity_info.id = "area_123"
        area_data.entity_info.name = "Test Area"
        area_data.arm_info.multi_mode_arm_enabled = True
        area_data.public_state = AreaPublicState.DISARMED
        return area_data

    @pytest.fixture
    def alarm_entity(
        self, mock_coordinator: Mock, mock_area_data: Mock
    ) -> InceptionAlarm:
        """Create an alarm entity for testing."""
        description = InceptionAlarmDescription(
            key="area_123",
            name="Test Area",
        )
        return InceptionAlarm(
            coordinator=mock_coordinator,
            entity_description=description,
            data=mock_area_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_with_both_params(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test area_arm service with both exit_delay and seal_check provided."""
        code = "1234"
        exit_delay = True
        seal_check = False

        await alarm_entity.area_arm_service(
            exit_delay=exit_delay, seal_check=seal_check, code=code
        )

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": "Arm",
            "ExecuteAsOtherUser": "true",
            "OtherUserPIN": code,
            "ExitDelay": "true",
            "SealCheck": "false",
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_with_only_exit_delay(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test area_arm service with only exit_delay provided."""
        code = "1234"
        exit_delay = False

        await alarm_entity.area_arm_service(exit_delay=exit_delay, code=code)

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": "Arm",
            "ExecuteAsOtherUser": "true",
            "OtherUserPIN": code,
            "ExitDelay": "false",
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_with_only_seal_check(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test area_arm service with only seal_check provided."""
        code = "1234"
        seal_check = True

        await alarm_entity.area_arm_service(seal_check=seal_check, code=code)

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": "Arm",
            "ExecuteAsOtherUser": "true",
            "OtherUserPIN": code,
            "SealCheck": "true",
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_with_no_optional_params(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test area_arm service with neither exit_delay nor seal_check provided."""
        code = "1234"

        await alarm_entity.area_arm_service(code=code)

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": "Arm",
            "ExecuteAsOtherUser": "true",
            "OtherUserPIN": code,
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_without_code(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test area_arm service without code (should log warning)."""
        exit_delay = True
        seal_check = False

        with patch(
            "custom_components.inception.alarm_control_panel.LOGGER"
        ) as mock_logger:
            await alarm_entity.area_arm_service(
                exit_delay=exit_delay, seal_check=seal_check
            )

            mock_logger.warning.assert_called_once_with("No alarm code provided")

        expected_data = {
            "Type": "ControlArea",
            "AreaControlType": "Arm",
            "ExecuteAsOtherUser": "true",
            "ExitDelay": "true",
            "SealCheck": "false",
        }

        alarm_entity.coordinator.api.request.assert_called_once_with(  # type: ignore[attr-defined]
            method="post",
            path="/control/area/area_123/activity",
            data=expected_data,
        )

    @pytest.mark.asyncio
    async def test_area_arm_service_calls_alarm_control(
        self, alarm_entity: InceptionAlarm
    ) -> None:
        """Test that area_arm_service calls _alarm_control with correct parameters."""
        code = "1234"
        exit_delay = True
        seal_check = False

        with patch.object(alarm_entity, "_alarm_control") as mock_control:
            await alarm_entity.area_arm_service(
                exit_delay=exit_delay, seal_check=seal_check, code=code
            )
            mock_control.assert_called_once_with(
                "Arm", code, exit_delay=exit_delay, seal_check=seal_check
            )
