"""
Inception API Message Categories.

This module contains the message type mappings from the Inception API documentation.
These provide human-readable descriptions for MessageID values in review events.
"""

from __future__ import annotations

# Message ID to description mapping from Inception API documentation
MESSAGE_DESCRIPTIONS: dict[int, tuple[str, str]] = {
    # Format: message_id: (string_value, description)
    # System Messages
    0: ("Unknown", "Unknown"),
    1: ("System_Started", "System Started"),
    2: ("System_AppVersion", "System Application Version"),
    3: ("System_FWVersion", "System Firmware Version"),
    4: ("System_SerialNumber", "System Serial Number"),
    5: ("System_ProductVariant", "System Product Variant"),
    21: ("System_ServiceModeEnabled", "Service Mode Enabled"),
    22: ("System_ServiceModeUpdated", "Service Mode Updated"),
    23: ("System_ServiceModeDisabled", "Service Mode Disabled"),
    24: ("System_ServiceModeDisableAfterTime", "Service Mode Will Disable After Time"),
    25: ("System_ServiceModeExpired", "Service Mode Expired"),
    41: ("System_EthernetConnected", "Ethernet Network Connected"),
    42: ("System_EthernetDisconnected", "Ethernet Network Disconnected"),
    43: ("System_EthernetDHCPMode", "Ethernet set to DHCP mode"),
    44: ("System_EthernetStaticMode", "Ethernet set to Static Address mode"),
    61: ("System_SkyTunnelConnected", "Direct Ethernet SkyTunnel Connected"),
    62: ("System_SkyTunnelDisconnected", "Direct Ethernet SkyTunnel Disconnected"),
    63: ("System_SkyTunnelWebAccessEnabled", "SkyTunnel Web Access Enabled"),
    64: ("System_SkyTunnelWebAccessDisabled", "SkyTunnel Web Access Disabled"),
    65: ("System_SkyTunnelReportingEnabled", "SkyTunnel Reporting Enabled"),
    66: ("System_SkyTunnelReportingDisabled", "SkyTunnel Reporting Disabled"),
    67: (
        "System_SkyTunnelUnableReconnect",
        "Direct Ethernet SkyTunnel Unable to Connect",
    ),
    68: (
        "System_SkyTunnelFailedInitialization",
        "Direct Ethernet SkyTunnel Disconnected, Failed Initialization",
    ),
    69: ("System_SkyTunnelPathEstablished", "SkyTunnel Path Established"),
    70: ("System_SkyTunnelPathLost", "SkyTunnel Path Lost"),
    91: ("System_WiFiAPEnabled", "WiFi Access Point Enabled"),
    92: ("System_WiFiAPDisabled", "WiFi Access Point Disabled"),
    93: ("System_WiFiLocalNetworkConnected", "WiFi Local Network Connected"),
    94: (
        "System_WiFiLocalNetworkConnectFailed",
        "WiFi Local Network Connection Failed",
    ),
    95: ("System_WiFiLocalNetworkDisconnected", "WiFi Local Network Disconnected"),
    96: ("System_WiFiDisabled", "WiFi Disabled"),
    97: ("System_WiFiConfiguredForAP", "WiFi Configured for Access Point Mode"),
    98: (
        "System_WiFiConfiguredForPersonal",
        "WiFi Configured for Personal Network Mode",
    ),
    99: (
        "System_WiFiConfiguredForEnterprize",
        "WiFi Configured for Enterprise Network Mode",
    ),
    100: ("System_WiFiDetailedStatusChange", "WiFi Status Change"),
    121: ("System_DateTimeChangeDetected", "Date and Time Change Detected"),
    122: ("System_DateTimeManuallyChanged", "Date and Time Manually Updated"),
    123: ("System_DateTimeTimezoneChanged", "System Timezone Changed"),
    124: ("System_DateTimeNTPChanged", "NTP Server Change Detected"),
    141: ("System_WebLoginSuccessful", "Web Login was Successful by User"),
    142: (
        "System_WebLoginFailedUserUnknown",
        "Web Login Failed because Username was Unknown",
    ),
    143: (
        "System_WebLoginFailedCredentialsInvalid",
        "Web Login Failed because Credentials were Invalid",
    ),
    144: (
        "System_WebLoginFailedNoPermission",
        "Web Login Failed because User does not have Permission",
    ),
    145: ("System_WebLogoutSuccessful", "Web Logout was Successful by User"),
    146: (
        "System_WebLoginFailedLockout",
        "Web Login Failed, subsequent login attempts will be blocked for a short time",
    ),
    147: (
        "System_WebLoginFailedUserExpired",
        "Web Login Failed because User is Expired",
    ),
    148: (
        "System_WebLoginFailedL3UserNotAllowed",
        "Web Login Failed because Level 3 User Access is not allowed",
    ),
    149: ("System_WebLoginTimedOut", "Web Login Session Timed Out from Inactivity"),
    150: (
        "System_WebLoginFailedInvalid2FACode",
        "Web Login Failed because 2FA Code was Invalid",
    ),
    151: ("System_WebLoginTwoFactorBackupCodeUsed", "User 2FA Backup Code was used"),
    152: ("System_WebLoginLockoutForgiven", "Web Login Lockout Forgiven"),
    153: (
        "System_WebLoginLockoutAllUsersForgiven",
        "Web Login Lockout All Users Forgiven",
    ),
    154: (
        "System_WebLoginFailedInterventionLockout",
        "Web Login Failed, login attempts will be blocked until administrator intervention",  # noqa: E501
    ),
    # Audit Messages
    1500: ("Audit_ItemCreated", "Item Created"),
    1501: ("Audit_ItemChanged", "Item Changed"),
    1502: ("Audit_ItemDeleted", "Item Deleted"),
    1503: ("Audit_CustomItemImported", "Custom Item Imported"),
    1504: ("Audit_CustomItemImportFailed", "Custom Item Import Failed"),
    1505: ("Audit_Lvl3CreatedLvl2", "Level 3 User Created Level 2 User"),
    1506: ("Audit_Lvl3DeletedLvl2", "Level 3 User Deleted Level 2 User"),
    1507: ("Audit_WebLoginTwoFactorEnrolled", "User Enrolled a User for 2FA Login"),
    1508: (
        "Audit_WebLoginTwoFactorUnenrolled",
        "User Unenrolled a User from 2FA Login",
    ),
    1509: ("Audit_UserPINRevealed", "User Revealed a User PIN"),
    1510: ("Audit_UserPINSent", "User PIN Sent to User"),
    1511: ("Audit_EntityPasswordRevealed", "User Revealed an Entity Password"),
    1550: ("Audit_ReportGenerated", "Report Generated"),
    # Access Messages - Door Events
    2000: ("Access_DoorUnlocked", "Door Unlocked"),
    2001: ("Access_DoorLocked", "Door Locked"),
    2002: ("Access_DoorOpened", "Door Opened (unsecured)"),
    2003: ("Access_DoorClosed", "Door Closed"),
    2004: ("Access_DoorOpenTooLong", "Door Held Open Too Long"),
    2005: (
        "Access_DoorClosedAfterOpenTooLong",
        "Door Closed After Being Held Open Too Long",
    ),
    2006: ("Access_DoorUserAccessGranted", "Door Access Granted for User"),
    2007: (
        "Access_DoorUserAccessDeniedPermission",
        "Door User Access Denied because No Permission",
    ),
    2008: (
        "Access_DoorUserAccessDeniedLockOut",
        "Door User Access Denied because Door Locked Out",
    ),
    2009: (
        "OBSOLETE_Access_DoorUserPINValidSecondCredential",
        "User PIN Valid, Waiting for Card",
    ),
    2010: (
        "Access_DoorUserCardValidSecondCredential",
        "User Credential Valid, Waiting for Other Credential",
    ),
    2011: (
        "Access_DoorAccessButtonAccessGranted",
        "Door Access Granted from Access Button",
    ),
    2012: (
        "Access_DoorAccessButtonAccessDeniedLockout",
        "Door Access Denied from Access Button because Door Locked Out",
    ),
    2013: ("Access_DoorAutomationAccessGranted", "Door Access Granted from Automation"),
    2014: (
        "Access_DoorAutomationAccessDeniedLockout",
        "Door Access Denied from Automation because Door Locked Out",
    ),
    2015: (
        "Access_DoorUserControlDeniedPermission",
        "Door Control by User Denied because No Permission",
    ),
    2016: ("Access_DoorOverrideSetToLock", "Door State Override set to Lock"),
    2017: ("Access_DoorOverrideSetToUnlock", "Door State Override set to Unlock"),
    2018: ("Access_DoorOverrideSetToLockOut", "Door State Override set to Lock out"),
    2019: ("Access_DoorOverrideCleared", "Door State Override Cleared"),
    2020: ("Access_DoorBreakglassBroken", "Door Breakglass Broken"),
    2021: ("Access_DoorBreakglassRestored", "Door Breakglass Restored"),
    2022: (
        "Access_DoorUserAccessDeniedAreaArmed",
        "Door User Access Denied because Area Armed",
    ),
    2023: ("Access_DoorAccessFailedNoDoor", "Door Access Failed, No Door Assigned"),
    2024: (
        "Access_DoorOpenTooLongFailServiceMode",
        "Door Held Open Too Long Failed, Service Mode is Enabled",
    ),
    2025: (
        "Access_DoorUserCredentialRejectedAccessMode",
        "User Credential Type Rejected due to Access Mode",
    ),
    2026: (
        "Access_DoorUserAccessDeniedUserExpired",
        "Door User Access Denied because User Expired",
    ),
    2027: ("Access_DoorHeldResponseMuted", "Door Held Open Response Muted"),
    2028: ("Access_AccessRequestsCancelled", "Door Grant Access Requests Cancelled"),
    2029: ("Access_DoorForceSuppressed", "Door Forced Suppressed"),
    2030: ("Access_DoorForceSuppressExpired", "Door Forced Suppress Expired"),
    2031: ("Access_RfDoorManuallyOpened", "RF Door Manually Opened"),
    2032: (
        "Access_RfDoorUnlockedOfflineCachedCard",
        "RF Door Unlocked While Offline by Cached Card",
    ),
    2033: (
        "Access_DoorUserCredentialMismatch",
        "Multi Credential Failed Due To Mismatched Credential",
    ),
    2034: (
        "Access_DoorUserCredentialTimeout",
        "Multi Credential Failed Due To Timeout",
    ),
    # Access Messages - Card/Credential Events
    3001: ("Access_CardReadSuccessful", "Credential Read Successful"),
    3002: (
        "Access_CardFailedUnknownReader",
        "Credential Read Failed because Reader was Unknown",
    ),
    3003: (
        "Access_CardFailedUnknownCard",
        "Credential Read Failed because Credential was Unknown",
    ),
    3004: (
        "Access_CardFailedParityFailed",
        "Credential Read Failed because Parity Check Failed",
    ),
    3005: (
        "Access_CardFailedUnknownSiteCode",
        "Credential Read Failed because Site Code was Unknown",
    ),
    3006: (
        "Access_CardFailedCardUnassigned",
        "Credential Read Failed because Credential is Unassigned",
    ),
    3007: ("Access_Card3BadgeDetected", "Card 3-Badge Action Detected"),
    3008: (
        "Access_CardFailedReaderLockedOut",
        "Credential Read Failed because Reader is Locked Out",
    ),
    3009: (
        "Access_UserCancelledFirstCardUsed",
        "User Cancelled because First Credential Use",
    ),
    3010: (
        "Access_CardFailedWiringIssue",
        "Credential Read Failed, Potentially Incorrect D1/D0 Wiring",
    ),
    3011: (
        "Access_CardFailedCardStateInactive",
        "Credential Read Failed because Credential State was Inactive",
    ),
    3012: (
        "Access_CardFailedTemplateUnknown",
        "Credential Read Failed because Credential Template was Unknown",
    ),
    3013: ("Access_Card2BadgeDetected", "Card 2-Badge Action Detected"),
    # Access Messages - PIN Events
    3501: ("Access_PINValid", "PIN Valid"),
    3502: (
        "Access_PINFailedKeypadInvalid",
        "PIN Failed because Keypad Type is Invalid",
    ),
    3503: ("Access_PINFailedUnknownUser", "Invalid PIN Entered"),
    3504: (
        "Access_PINFailedReaderLockedOut",
        "PIN Failed because Reader is Locked Out",
    ),
    3505: ("Access_UserCancelledFirstPINUsed", "User Cancelled because First PIN Use"),
    # Security Messages - Area Events
    5000: ("Security_AreaArmedByUser", "Area Armed by User"),
    5001: ("Security_AreaArmedByUserWithExit", "Area Armed With Exit Delay by User"),
    5002: ("Security_AreaArmedByTimePeriod", "Area Armed by Time Period"),
    5003: ("Security_AreaArmedByInactivity", "Area Armed by Inactivity"),
    5004: ("Security_AreaArmedByAutomation", "Area Armed by Automation"),
    5005: ("Security_AreaArmedBySystem", "Area Armed by System"),
    5006: ("Security_AreaArmWarningStarted", "Area Arm Warning Started"),
    5007: (
        "Security_AreaArmFailNoPermission",
        "Area Arm Failed because User does not have Permission",
    ),
    5008: (
        "Security_AreaArmFailUnsealedInputs",
        "Area Arm Failed due to Unsealed Inputs",
    ),
    5009: (
        "Security_AreaArmUnnecessary",
        "Area Arm Unnecessary because Area is Already Armed",
    ),
    5010: (
        "Security_AreaArmFailModuleHealth",
        "Area Arm Failed due to Module Health Issues",
    ),
    5011: (
        "Security_AreaArmFailReportingPath",
        "Area Arm Failed due to Reporting Path Issues",
    ),
    5012: (
        "Security_AreaArmFailNotComplete",
        "Area Arm Failed because Arm Proceedure Not Completed",
    ),
    5013: (
        "Security_AreaExitCancelledModuleHealth",
        "Area Arm Cancelled because Module Issue",
    ),
    5014: (
        "Security_AreaExitCancelledInputEvent",
        "Area Arm Cancelled because Input Alarm",
    ),
    5015: (
        "Security_AreaArmFailUnackedMessages",
        "Area Arm Failed because Unacknowledged Messages",
    ),
    5016: (
        "Security_AreaArmWarningCancelledDueToActivity",
        "Area Arm Warning Cancelled by System due to Activity",
    ),
    5201: ("Security_AreaDisarmedByUser", "Area Disarmed by User"),
    5202: ("Security_AreaDeferDisarmedByUser", "Area Time Disarmed by User"),
    5203: ("Security_AreaDisarmedByTimePeriod", "Area Disarmed by Time Period"),
    5204: ("Security_AreaDisarmedByAutomation", "Area Disarmed by Automation"),
    5205: ("Security_AreaDisarmedBySystem", "Area Disarmed by System"),
    5206: ("Security_AreaEntryDelayStarted", "Area Entry Delay Started"),
    5207: (
        "Security_AreaDisarmFailNoPermission",
        "Area Disarm Failed because User does not have Permission",
    ),
    5208: (
        "Security_AreaDisarmUnnecessary",
        "Area Disarm Unnecessary because Area is Already Disarmed",
    ),
    # Security Messages - Input Events
    5401: ("Security_InputDeisolatedByUser", "Input De-Isolated by User"),
    5402: ("Security_InputDeisolatedByAutomation", "Input De-Isolated by Automation"),
    5403: ("Security_InputDeisolatedBySystem", "Input De-Isolated by System"),
    5404: ("Security_InputIsolatedByUser", "Input Isolated by User"),
    5405: ("Security_InputIsolatedByAutomation", "Input Isolated by Automation"),
    5406: ("Security_InputIsolatedBySystem", "Input Isolated by System"),
    5407: (
        "Security_InputIsolatedTemporarilyByUser",
        "Input Temporarily Isolated by User",
    ),
    5408: (
        "Security_InputIsolatedTemporarilyBySystem",
        "Input Temporarily Isolated by System",
    ),
    # Hardware Messages
    10000: ("Hardware_LanModuleDiscovered", "LAN Module Discovered"),
    10001: ("Hardware_LanModuleConnected", "LAN Module Connected"),
    10002: ("Hardware_LanModuleDisconnected", "LAN Module Disconnected"),
    10003: ("Hardware_LanModuleFWUpdateStarted", "LAN Module Firmware Update Started"),
    10004: ("Hardware_LanModuleFWUpdateFailed", "LAN Module Firmware Update Failed"),
    10005: (
        "Hardware_LanModuleFWUpdateCompleted",
        "LAN Module Firmware Update Completed",
    ),
    10006: ("Hardware_LanModuleFWVersion", "LAN Module Current Firmware"),
    10007: ("Hardware_LanModuleFWVersionUpdated", "LAN Module F/W Version Detected"),
    10008: ("Hardware_LANSecureRequested", "LAN Secure Requested"),
    10009: (
        "Hardware_LANModuleSubstitutionDetected",
        "LAN Module Substitution Detected",
    ),
    10010: (
        "Hardware_LANModuleSubstitutionRestored",
        "LAN Module Substitution Restored",
    ),
    10011: ("Hardware_LANSecureDisabled", "LAN Secure Detection Disabled"),
    10012: (
        "Hardware_LANModuleImpersonationDetected",
        "LAN Module Impersonation Detected",
    ),
}


def get_message_info(message_id: int | None) -> tuple[str, str] | None:
    """
    Get message information for a given message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        Tuple of (string_value, description) or None if not found

    """
    if message_id is None:
        return None
    return MESSAGE_DESCRIPTIONS.get(message_id)


def get_message_description(message_id: int | None) -> str | None:
    """
    Get human-readable description for a message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        Human-readable description or None if not found

    """
    info = get_message_info(message_id)
    return info[1] if info else None


def get_message_string_value(message_id: int | None) -> str | None:
    """
    Get string value for a message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        String value or None if not found

    """
    info = get_message_info(message_id)
    return info[0] if info else None
