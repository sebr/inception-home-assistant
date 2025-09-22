"""
Inception API Message Categories.

This module contains the message type mappings from the Inception API documentation.
These provide human-readable descriptions for MessageID values in review events.
"""

from __future__ import annotations

# Message ID to description mapping from Inception API documentation
MESSAGE_DESCRIPTIONS: dict[int, tuple[str, str]] = {
    # Format: message_id: (string_value, description)
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
    181: ("System_FWUpdateRequested", "System Firmware Update Requested"),
    182: ("System_FWUpdateSucceeded", "System Firmware Update Succeeded"),
    183: ("System_FWUpdateFailed", "System Firmware Update Failed"),
    184: (
        "System_FWUpdateDefaultRequired",
        "System Firmware Update Requires Factory Default",
    ),
    185: (
        "System_FWUpdateDefaultApproved",
        "System Firmware Update Factory Default Approved",
    ),
    186: ("System_FWDownloadRequested", "Firmware Download via SkyTunnel Requested"),
    187: ("System_FWDownloadStarted", "Firmware Download via SkyTunnel Started"),
    188: ("System_FWDownloadCompleted", "Firmware Download via SkyTunnel Completed"),
    189: ("System_FWDownloadCancelled", "Firmware Download via SkyTunnel Cancelled"),
    190: (
        "System_FWDownloadFailedNoConnection",
        "Firmware Download via SkyTunnel Unable to Start, No Connection",
    ),
    191: (
        "System_FWDownloadFailedLostConnection",
        "Firmware Download via SkyTunnel Failed, Lost Connection",
    ),
    192: (
        "System_FWDownloadFailedAlreadyInProgress",
        "Firmware Download via SkyTunnel Unable to Start, Download Already in Progress",
    ),
    193: (
        "System_FWDownloadFailedValidation",
        "Firmware Download via SkyTunnel Failed Validation",
    ),
    241: ("System_DBBackupRequested", "Database Backup Requested"),
    242: ("System_DBRestoreRequested", "Database Restore Requested"),
    243: (
        "System_DBRestoreFailedInvalidFile",
        "Database Restore Failed because the File was Invalid",
    ),
    244: (
        "System_DBBackupFailedUSBError",
        "Database Backup Failed due to USB Drive error",
    ),
    245: ("System_DBBackupCompleted", "Database Backup Completed"),
    261: ("System_FactoryDefaultRequested", "Factory Reset Requested"),
    262: (
        "System_Level3UserAccessEnabledByUser",
        "Level 3 User Access Enabled By User",
    ),
    263: (
        "System_Level3UserAccessDisabledByUser",
        "Level 3 User Access Disabled By User",
    ),
    264: ("System_EULAAcceptedByUser", "EULA Accepted By User"),
    265: ("System_InitialConfigurationPerformed", "Initial Configuration Performed"),
    361: ("System_TimePeriodActive", "Time Period went Active"),
    362: ("System_TimePeriodInactive", "Time Period went Inactive"),
    381: ("System_AutomatedActionTrue", "Automated Action Changed State to True"),
    382: ("System_AutomatedActionFalse", "Automated Action Changed State to False"),
    401: ("System_NotificationCreated", "Notification Event Created"),
    402: (
        "System_NotificationFailedExpiredUser",
        "Notification Failed, User is Expired / Cancelled",
    ),
    403: (
        "System_NotificationFailedServiceMode",
        "Notification Failed, Service Mode is Enabled",
    ),
    451: ("System_EmailFailedNoServer", "Email Failed, No Server Configured"),
    452: (
        "System_EmailFailedUnableToContactServer",
        "Email Failed, Unable to Connect to Server",
    ),
    453: (
        "System_EmailFailedNoUserEmailAddress",
        "Email Failed, No User Email Address",
    ),
    454: ("System_EmailFailedUnknownError", "Email Failed, Unknown Error"),
    455: ("System_EmailTestEmailPrepared", "Test Email Preparing to Send"),
    456: ("System_EmailTestEmailSent", "Test Email Sent"),
    457: ("System_EmailCreatedPreparingToSend", "Email Created, Preparing to Send"),
    458: ("System_EmailQueuedRateLimiting", "Email Queued due to Rate Limiting"),
    459: ("System_EmailAppended", "Email Appended to Existing Message"),
    460: ("System_EmailSent", "Email Message Sent"),
    501: (
        "System_PermissionDeniedExpiredUser",
        "Permission Denied for Expired / Cancelled User attempting to control Item",
    ),
    521: (
        "System_SkyCommandRequestFailUnknownUser",
        "SkyCommand Request Failed because Unknown User",
    ),
    522: (
        "System_SkyCommandRequestFailedUnknownItem",
        "SkyCommand Request Failed because Unknown Item",
    ),
    523: ("System_SkyCommandControlRequest", "SkyCommand Control Request Received"),
    524: ("System_SkyCommandListRequest", "SkyCommand List Request Received"),
    525: (
        "System_SkyCommandUserAssociated",
        "SkyCommand User Associated to Inception User",
    ),
    526: (
        "System_SkyCommandUserAssociationRemoved",
        "SkyCommand User Association Removed",
    ),
    527: (
        "System_SkyCommandUserAssociationRemovedForAnotherUser",
        "SkyCommand User Association Removed for Another User",
    ),
    528: (
        "System_SkyCommandNotificationFailedNoUser",
        "SkyCommand Notification Failed, No SkyCommand User",
    ),
    529: (
        "System_SkyCommandNotificationFailedNoSkyTunnel",
        "SkyCommand Notification Failed, No SkyTunnel Connection",
    ),
    530: (
        "System_SkyCommandNotificationFailedTimedOut",
        "SkyCommand Notification Failed, Connection Timed Out",
    ),
    531: (
        "System_SkyCommandNotificationFailedSubscriptionRequired",
        "SkyCommand Notification Failed, Subscription Required",
    ),
    532: (
        "System_SkyCommandNotificationFailedSkyCommandUserMissing",
        "SkyCommand Notification Failed, SkyCommand User Not Found",
    ),
    533: (
        "System_SkyCommandNotificationFailedUnknownError",
        "SkyCommand Notification Failed, Unknown Error",
    ),
    534: (
        "System_SkyCommandNotificationPrepared",
        "SkyCommand Notification Created, Preparing to Send",
    ),
    535: ("System_SkyCommandNotificationSent", "SkyCommand Notification Message Sent"),
    536: ("System_SkyCommandNotificationExpired", "SkyCommand Notification(s) Expired"),
    537: ("System_SkyCommandAppLogin", "SkyCommand App Login"),
    601: ("System_ConnectionConnected", "Connection Connected"),
    602: ("System_ConnectionDisconnected", "Connection Disconnected"),
    603: ("System_ConnectionFailed", "Connection Failed to Connect"),
    604: ("System_ConnectionReceivedMessage", "Connection Received Message"),
    605: ("System_ConnectionSentMessage", "Connection Sent Message"),
    606: (
        "System_ConnectionDiscardedTextIncorrectFraming",
        "Connection Discarded Text because Incorrect Framing",
    ),
    607: (
        "System_ConnectionDiscardedTextBufferFull",
        "Connection Discarded Text because Buffer Full",
    ),
    608: (
        "System_ConnectionDiscardedMessageSendRetryTimeout",
        "Connection Discarded Message Because Send Retry Timeout",
    ),
    609: (
        "System_ConnectionHttpMessageFailedNoResponse",
        "HTTP Connection Failed Because No Response",
    ),
    610: (
        "System_ConnectionHttpMessageFailedClientError",
        "HTTP Connection Failed Because Client Error",
    ),
    611: (
        "System_ConnectionHttpMessageFailedServerError",
        "HTTP Connection Failed Because Server Error",
    ),
    612: (
        "System_ConnectionDiscardedMessageQueueFull",
        "Connection Discarded Message Because Queue Is Full",
    ),
    651: ("System_ScheduledTaskStarted", "Scheduled Task Started"),
    652: ("System_ScheduledTaskSucceeded", "Scheduled Task Succeeded"),
    653: ("System_ScheduledTaskFailed", "Scheduled Task Failed"),
    654: ("System_RestApiRequestReceived", "REST API Request Received"),
    655: ("System_RestApiRequestCompleted", "REST API Request Completed"),
    656: (
        "System_RestApiRequestFailureUnauthorized",
        "REST API Request Failed because User not Authorized",
    ),
    657: (
        "System_RestApiRequestFailureInternalServerError",
        "REST API Request Failed due to Internal Server Error",
    ),
    658: (
        "System_RestApiUserLookupViaPinRequested",
        "REST API User Lookup by PIN Requested",
    ),
    659: (
        "System_RestApiRequestFailureInvalidApiToken",
        "REST API Request Failed due to invalid API Token",
    ),
    660: ("System_DuimFileImportSuccess", "DUIM User File Import Successful"),
    661: ("System_DuimFileImportFailure", "DUIM User File Import Failed"),
    662: ("System_DuimNetworkShareAccessFailure", "DUIM Network Share Access Failed"),
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
    2501: ("Access_AntiPassbackViolation", "Anti-Passback Violation by User"),
    2502: (
        "Access_AntiPassbackTimedViolation",
        "Anti-Passback Timed Violation by User",
    ),
    2503: (
        "Access_AntiPassbackAutoForgiveness",
        "Anti-Passback Automatic Forgiveness to User",
    ),
    2504: (
        "Access_AntiPassbackManualForgiveness",
        "Anti-Passback Manual Forgiveness to User",
    ),
    2505: (
        "Access_AntiPassbackForgivenessAllUsers",
        "Anti-Passback Forgiveness to All Users",
    ),
    2506: (
        "Access_AntiPassbackForgivenessUsersWithViolations",
        "Anti-Passback Forgiveness to All Users with Violations",
    ),
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
    3801: ("Access_UserAreaUpdated", "User Location Updated"),
    4001: ("Access_FloorFreeAccess", "Floor Free Access"),
    4002: ("Access_FloorSecured", "Floor Secured"),
    4003: (
        "Access_FloorUserControlDeniedPermission",
        "Floor Control by User Denied because No Permission",
    ),
    4004: (
        "Access_FloorOverrideSetToFreeAccess",
        "Floor State Override set to Free Access",
    ),
    4005: ("Access_FloorOverrideSetToSecure", "Floor State Override set to Secure"),
    4006: ("Access_FloorOverrideSetToLockOut", "Floor State Override set to Lock out"),
    4007: ("Access_FloorOverrideCleared", "Floor State Override Cleared"),
    4008: (
        "Access_FloorFreeAccessDeniedAreaArmed",
        "Floor Control by User Denied because Area Armed",
    ),
    4201: (
        "Access_LiftCarButtonDeniedAreaArmed",
        "Lift Car Floor Access Denied because Area Armed",
    ),
    4202: (
        "Access_LiftCarAccessFailedNoFloors",
        "Lift Car Access Failed, no Floors Programmed",
    ),
    4203: (
        "Access_LiftCarButtonDeniedNoPermission",
        "Lift Car Denied because No Permission",
    ),
    4204: ("Access_LiftCarAccessGranted", "Lift Car Access Granted"),
    4205: ("Access_LiftFloorSelected", "Lift Floor Selected by User"),
    4206: (
        "Access_LiftCarButtonDeniedFloorLockout",
        "Lift Car Floor Access Denied because Floor Lockout",
    ),
    4207: (
        "Access_LiftCarButtonDeniedUserExpired",
        "Lift Car Denied because User Expired",
    ),
    4251: ("Access_StorageBlockAccessRequested", "Storage Block Access Requested"),
    4252: ("Access_StorageBlockExitRequested", "Storage Block Exit Requested"),
    4253: (
        "Access_StorageBlockAccessFailedNoUnits",
        "Storage Block Access Failed, no Units Programmed",
    ),
    4254: (
        "Access_StorageBlockAccessFailedNoPermission",
        "Storage Block Access Failed, no Unit Permissions",
    ),
    4255: (
        "Access_StorageBlockDeniedUserExpired",
        "Storage Block Denied because User Expired",
    ),
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
    5301: ("Security_AreaWalkTestStarted", "Area Walk Test Started"),
    5302: ("Security_AreaWalkTestCompleted", "Area Walk Test Completed"),
    5303: ("Security_AreaWalkTestCancelled", "Area Walk Test Cancelled"),
    5304: ("Security_AreaWalkTestFailedAreaArmed", "Area Walk Test Failed, Area Armed"),
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
    5409: ("Security_InputSoakTestStartedByUser", "Input Soak Test Started by User"),
    5410: ("Security_InputSoakTestCompletedBySystem", "Input Soak Test Completed"),
    5411: ("Security_InputSoakTestFailed", "Input Soak Test Failed"),
    5412: (
        "Security_InputSoakTestCancelledByUser",
        "Input Soak Test Cancelled by User",
    ),
    5413: (
        "Security_InputSoakTestCancelledBySystem",
        "Input Soak Test Cancelled by System",
    ),
    5414: ("Security_InputPulseDetected", "Input Pulse Detected"),
    5501: ("Security_InputEventCreated", "Input Event Created"),
    5502: ("Security_InputEventTransmitted", "Input Event Successfully Transmitted"),
    5503: ("Security_HardwareEventCreated", "Hardware Event Created"),
    5504: (
        "Security_HardwareEventTransmitted",
        "Hardware Event Successfully Transmitted",
    ),
    5505: ("Security_AreaEventCreated", "Area Event Created"),
    5506: ("Security_AreaEventTransmitted", "Area Event Successfully Transmitted"),
    5507: ("Security_ResetEventCreated", "System Reset Event Created"),
    5508: ("Security_ResetEventTransmitted", "System Reset Successfully Transmitted"),
    5509: (
        "Security_TestReportTransmitted",
        "Test Report Event Successfully Transmitted",
    ),
    5510: ("Security_CommsFailEventCreated", "Comms Failure Event Created"),
    5511: (
        "Security_CommsFailEventTransmitted",
        "Comms Failure Successfully Transmitted",
    ),
    5512: ("Security_UserDuressEventCreated", "User Duress Event Created"),
    5513: (
        "Security_UserDuressEventTransmitted",
        "User Duress Successfully Transmitted",
    ),
    5514: ("Security_TechOnSiteEventCreated", "Tech On Site Event Created"),
    5515: (
        "Security_TechOnSiteEventTransmitted",
        "Tech On Site Event Successfully Transmitted",
    ),
    5516: ("Security_ConfirmationEventCreated", "Confirmation Event Created"),
    5517: (
        "Security_ConfirmationEventTransmitted",
        "Confirmation Event Successfully Transmitted",
    ),
    5518: ("Security_SwingerEventCreated", "Swinger Shutdown Event Created"),
    5519: (
        "Security_SwingerEventTransmitted",
        "Swinger Shutdown Event Successfully Transmitted",
    ),
    5520: ("Security_AlarmCancelledBySystem", "Alarm Cancelled by System"),
    5521: ("Security_AlarmCancelledByUser", "Alarm Cancelled by User"),
    5801: (
        "Security_ReportingPathFailNoPathsConfigured",
        "Alarm Event Failed to Send, No Paths Configured",
    ),
    5802: (
        "Security_ReportingPathFailNoPathsAvailable",
        "Alarm Event Failed to Send because No Paths Available. Retrying to Send",
    ),
    5803: (
        "Security_ReportingPathFailServiceMode",
        "Alarm Event Failed to Send, Service Mode is Enabled",
    ),
    5804: (
        "Security_ReportingPathDiscardedTimeout",
        "Alarm Event Failed, Event Discarded due to Timeout",
    ),
    5805: (
        "Security_ReportingPathDiscardedQueueLimit",
        "Alarm Event Failed, Past Event Discarded due to Too Many Events Queued",
    ),
    5806: (
        "Security_ReportingPathDiscardedUnknownError",
        "Alarm Event Failed, Event Discarded due to Unknown Error",
    ),
    5807: ("PlaceholderUnused", "Placeholder"),
    5808: (
        "Security_ReportingPathFailSpecificPathNotEnabled",
        "Alarm Event Failed to Send, Specified Path Not Enabled",
    ),
    5809: (
        "Security_ReportingPathFailSoakTestActive",
        "Alarm Event Failed to Send, Soak Test is Active",
    ),
    5810: (
        "Security_ReportingPathFailSwingerActive",
        "Alarm Event Failed, Swinger Shutdown Active",
    ),
    6001: (
        "Security_ReportingPathSkyTunnelEnabled",
        "SkyTunnel Alarm Reporting Path Enabled",
    ),
    6002: (
        "Security_ReportingPathSkyTunnelFailed",
        "SkyTunnel Alarm Reporting Path Comms Failure",
    ),
    6003: (
        "Security_ReportingPathSkyTunnelReesetablished",
        "SkyTunnel Alarm Reporting Path Comms Re-established",
    ),
    6004: (
        "Security_ReportingPathSkyTunnelDisabled",
        "SkyTunnel Alarm Reporting Path Disabled",
    ),
    6005: (
        "Security_ReportingPathSkyTunnelTestReport",
        "SkyTunnel Alarm Test Report Sent",
    ),
    6006: ("Security_ReportingPathT4000Enabled", "Alarm Device Reporting Path Enabled"),
    6007: (
        "Security_ReportingPathT4000Failed",
        "Alarm Device Reporting Path Comms Failure",
    ),
    6008: (
        "Security_ReportingPathT4000Reestablished",
        "Alarm Device Reporting Path Comms Re-established",
    ),
    6009: (
        "Security_ReportingPathT4000Disabled",
        "Alarm Device Reporting Path Disabled",
    ),
    6010: ("Security_ReportingPathT4000TestReport", "Alarm Device Test Report Sent"),
    6011: (
        "OBSOLETE_Security_ReportingPathDialerEnabled",
        "Dialer Alarm Reporting Path Enabled",
    ),
    6012: (
        "OBSOLETE_Security_ReportingPathDialerFailed",
        "Dialer Alarm Reporting Path Comms Failure",
    ),
    6013: (
        "OBSOLETE_Security_ReportingPathDialerReestablished",
        "Dialer Alarm Reporting Path Comms Re-established",
    ),
    6014: (
        "OBSOLETE_Security_ReportingPathDialerDisabled",
        "Dialer Alarm Reporting Path Disabled",
    ),
    6015: (
        "OBSOLETE_Security_ReportingPathDialerTestReport",
        "Dialer Alarm Test Report Sent",
    ),
    6016: ("Security_ReportingPathManualTestReport", "Manual Test Report Sent"),
    6017: (
        "Security_ReportingPathAlarmQueueClearedByUser",
        "Alarm Queue Cleared By User",
    ),
    6018: (
        "Security_ReportingPathAllAlarmsGenerated",
        "All Possible Alarms Generated By User",
    ),
    6019: (
        "Security_ReportingPathTempIsolateUser",
        "Alarm Comms Issues Temporarily Isolated by User",
    ),
    6020: (
        "Security_ReportingPathTempIsolateSystem",
        "Alarm Comms Issues Temporarily Isolated by System",
    ),
    6021: (
        "Security_ReportingPathDeIsolateUser",
        "Alarm Comms Issues De-Isolated by User",
    ),
    6022: (
        "Security_ReportingPathDeIsolateSystem",
        "Alarm Comms Issues De-Isolated by System",
    ),
    6023: ("Security_ReportingPathSIAIPEnabled", "SIA IP Alarm Reporting Path Enabled"),
    6024: (
        "Security_ReportingPathSIAIPFailed",
        "SIA IP Alarm Reporting Path Comms Failure",
    ),
    6025: (
        "Security_ReportingPathSIAIPReestablished",
        "SIA IP Alarm Reporting Path Comms Re-established",
    ),
    6026: (
        "Security_ReportingPathSIAIPDisabled",
        "SIA IP Alarm Reporting Path Disabled",
    ),
    6027: ("Security_ReportingPathSIAIPTestReport", "SIA IP Alarm Test Report Sent"),
    6201: ("Security_SirensTestStartedByUser", "Siren Testing Started by User"),
    6202: ("Security_SirensTestStoppedByUser", "Siren Testing Stopped by User"),
    6203: ("Security_SirensActivatedInArea", "Sirens Activated in Area"),
    6204: ("Security_SirensStoppedInArea", "Sirens Stopped in Area"),
    6205: (
        "Security_SirensFailServiceMode",
        "Siren Failed to Sound, Service Mode is Enabled",
    ),
    6206: (
        "Security_SirensFailLimitReached",
        "Siren Failed to Sound, Activation Limit",
    ),
    6207: (
        "Security_SirensFailRetriggerNotAllowed",
        "Siren Failed to Sound, Retrigger Not Allowed",
    ),
    6208: (
        "Security_SirenResponseSuppressedServiceMode",
        "Siren Response Suppressed, Service Mode is Enabled",
    ),
    6301: ("Security_StrobeActivatedInArea", "Strobe Activated in Area"),
    6302: ("Security_StrobeStoppedInArea", "Strobe Stopped in Area"),
    6303: ("Security_StrobeTestStartedByUser", "Strobe Testing Started by User"),
    6304: ("Security_StrobeTestStoppedByUser", "Strobe Testing Stopped by User"),
    6401: ("Security_HardwareDeIsolatedByUser", "Hardware De-Isolated by User"),
    6402: ("Security_HardwareDeIsolatedBySystem", "Hardware De-Isolated by System"),
    6403: ("Security_HardwareIsolatedByUser", "Hardware Isolated by User"),
    6404: (
        "Security_HardwareTempIsolatedByUser",
        "Hardware Temporarily Isolated by User",
    ),
    6405: (
        "Security_HardwareTempIsolatedBySystem",
        "Hardware Temporarily Isolated by System",
    ),
    6501: (
        "Security_AnticodePermissionGrantedToUser",
        "Anti-code Permission Granted to User",
    ),
    6601: ("Security_GSMAlarmCommsConnected", "Alarm Comms Device Connected"),
    6602: ("Security_GSMAlarmCommsDisconnected", "Alarm Comms Device Disconnected"),
    6603: (
        "Security_GSMAlarmCommsUnableReconnect",
        "Alarm Comms Device Unable to Reconnect",
    ),
    6604: (
        "Security_GSMAlarmCommsConnectedDepricated",
        "Alarm Comms Device Connected ",
    ),
    6605: (
        "Security_GSMAlarmCommsDisconnectedDepricated",
        "Alarm Comms Device Disconnected ",
    ),
    6606: (
        "Security_GSMAlarmCommsUnableReconnectDepricated",
        "Alarm Comms Device Unable to Reconnect ",
    ),
    6607: (
        "Security_GSMAlarmCommsPathsUnavailable",
        "Alarm Comms Device No Paths Available",
    ),
    6608: ("Security_GSMAlarmCommsPathsRestored", "Alarm Comms Device Paths Available"),
    6701: (
        "Security_UnconfirmedIntruderDetected",
        "Unconfirmed Intruder Condition Detected",
    ),
    6702: ("Security_IntruderReinstated", "Intruder Condition Reinstated"),
    6703: (
        "Security_ConfirmedIntruderDetected",
        "Confirmed Intruder Condition Detected",
    ),
    6704: (
        "Security_UnconfirmedDuressDetected",
        "Unconfirmed Duress Condition Detected",
    ),
    6705: ("Security_DuressReinstated", "Duress Condition Reinstated"),
    6706: ("Security_ConfirmedDuressDetected", "Confirmed Duress Condition Detected"),
    6707: (
        "Security_IntruderConfirmationTimerExtended",
        "Intruder Confirmation Timer Extended",
    ),
    6708: (
        "Security_DuressConfirmationTimerExtended",
        "Duress Confirmation Timer Extended",
    ),
    6801: ("Security_UnitUnlocked", "Storage Unit Unlocked"),
    6802: ("Security_UnitSecured", "Storage Unit Secured"),
    6804: ("Security_UnitSecuredByReSecure", "Storage Unit Secured by Re-secure Time"),
    6805: ("Security_UnitVacant", "Storage Unit Marked as Vacant"),
    6806: ("Security_UnitVacancyCleared", "Storage Unit Vacancy Cleared"),
    6808: ("Security_UnitAlarmDetected", "Storage Unit Alarm Detected"),
    6809: ("Security_UnitAlarmRestored", "Storage Unit Alarm Restored"),
    6810: ("Security_UnitDoorOpened", "Storage Unit Door Opened"),
    6811: ("Security_UnitDoorClosed", "Storage Unit Door Closed"),
    6812: ("Security_UnitUnlockedTooLong", "Storage Unit Unlocked Too Long"),
    6813: ("Security_UnitTamperDetected", "Storage Unit Tamper Detected"),
    6814: ("Security_UnitTamperRestored", "Storage Unit Tamper Restored"),
    6815: (
        "Security_UnitSecureDeniedNoPermission",
        "Storage Unit Secure by User Denied because No Permission",
    ),
    6816: (
        "Security_UnitUnlockDeniedNoPermission",
        "Storage Unit Unlock by User Denied because No Permission",
    ),
    6817: (
        "Security_UnitVacantDeniedNoPermission",
        "Storage Unit Make Vacant by User Denied because No Permission",
    ),
    6818: (
        "Security_UnitVacancyClearDeniedNoPermission",
        "Storage Unit Clear Vacancy by User Denied because No Permission",
    ),
    6819: (
        "Security_UnitSecurePending",
        "Storage Unit Moved to Secure Pending State due to Active Inputs",
    ),
    6820: ("Security_UnitAlarmClearedByUser", "Storage Unit Alarm Cleared by User"),
    6821: (
        "Security_UnitAlarmClearDeniedNoPermission",
        "Failed to Clear Alarms on Storage Unit due to No Permission",
    ),
    6822: (
        "Security_UnitAlarmClearDeniedActiveInputs",
        "Failed to Clear Alarms on Storage Unit due to Active Inputs",
    ),
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
    10501: ("Hardware_OSDPReaderDiscovered", "SIFER/OSDP Reader Discovered"),
    10502: ("Hardware_OSDPReaderConnected", "SIFER/OSDP Reader Connected"),
    10503: (
        "Hardware_OSDPReaderConnectedAndMoved",
        "SIFER/OSDP Reader Connected and Moved",
    ),
    10504: ("Hardware_OSDPReaderDisconnected", "SIFER/OSDP Reader Disconnected"),
    10505: (
        "Hardware_OSDPReaderFWUpdateStarted",
        "SIFER/OSDP Reader Firmware Update Started",
    ),
    10506: (
        "Hardware_OSDPReaderFWUpdateFailed",
        "SIFER/OSDP Reader Firmware Update Failed",
    ),
    10507: (
        "Hardware_OSDPReaderFWUpdateCompleted",
        "SIFER/OSDP Reader Firmware Update Completed",
    ),
    10508: ("Hardware_OSDPReaderFWVersion", "SIFER/OSDP Reader Current Firmware"),
    10509: (
        "Hardware_OSDPReaderFWVersionUpdated",
        "SIFER/OSDP Reader F/W Version Detected",
    ),
    10510: ("Hardware_OSDPReaderFeedbackUpdated", "SIFER/OSDP Feedback Updated"),
    10511: ("Hardware_OSDPReaderFeedbackStopped", "SIFER/OSDP Feedback Stopped"),
    10512: (
        "Hardware_OSDPReaderAddressChangeCommand",
        "OSDP Reader Address Change Command Sent",
    ),
    10701: ("Hardware_UnibusDiscovered", "Unibus Expander Discovered"),
    10702: ("Hardware_UnibusConnected", "Unibus Expander Connected"),
    10703: ("Hardware_UnibusConnectedAndMoved", "Unibus Expander Connected and Moved"),
    10704: ("Hardware_UnibusDisconnected", "Unibus Expander Disconnected"),
    10705: (
        "Hardware_UnibusFWUpdateStarted",
        "Unibus Expander Firmware Update Started",
    ),
    10706: ("Hardware_UnibusFWUpdateFailed", "Unibus Expander Firmware Update Failed"),
    10707: (
        "Hardware_UnibusFWUpdateCompleted",
        "Unibus Expander Firmware Update Completed",
    ),
    10708: ("Hardware_UnibusFWVersion", "Unibus Expander Current Firmware"),
    10709: ("Hardware_UnibusFWVersionUpdated", "Unibus Expander F/W Version Detected"),
    10801: ("OBSOLETEHardware_EthernetPlugonDiscovered", "Ethernet Plugon Discovered"),
    10802: ("OBSOLETEHardware_EthernetPlugonConnected", "Ethernet Plugon Connected"),
    10803: (
        "OBSOLETEHardware_EthernetPlugonConnectedAndMoved",
        "Ethernet Plugon Connected and Moved",
    ),
    10804: (
        "OBSOLETEHardware_EthernetPlugonDisconnected",
        "Ethernet Plugon Disconnected",
    ),
    10805: (
        "OBSOLETEHardware_EthernetPlugonFWUpdateStarted",
        "Ethernet Plugon Firmware Update Started",
    ),
    10806: (
        "OBSOLETEHardware_EthernetPlugonFWUpdateFailed",
        "Ethernet Plugon Firmware Update Failed",
    ),
    10807: (
        "OBSOLETEHardware_EthernetPlugonFWUpdateCompleted",
        "Ethernet Plugon Firmware Update Completed",
    ),
    10808: (
        "OBSOLETEHardware_EthernetPlugonFWVersion",
        "Ethernet Plugon Current Firmware",
    ),
    10809: (
        "OBSOLETEHardware_EthernetPlugonFWVersionUpdated",
        "Ethernet Plugon F/W Version Detected",
    ),
    11001: ("Hardware_InputChangeToUnknown", "Input Changed State to Unknown"),
    11002: ("Hardware_InputChangeToSealed", "Input Changed State to Sealed"),
    11003: ("Hardware_InputChangeToAlarm", "Input Changed State to Alarm"),
    11004: ("Hardware_InputChangeToTampered", "Input Changed State to Tampered"),
    11005: ("Hardware_InputChangeToOn", "Input Changed State to On"),
    11006: ("Hardware_InputChangeToOff", "Input Changed State to Off"),
    11007: ("Hardware_InputChangeToActive", "Input Changed State to Active"),
    11008: ("Hardware_InputChangeToInactive", "Input Changed State to Inactive"),
    11009: ("Hardware_InputChangeToMask", "Input Changed State to Mask"),
    11010: ("Hardware_InputChangeToAlarmMask", "Input Changed State to Alarm + Mask"),
    11011: ("Hardware_InputStateChange", "Input State Changed"),
    11201: ("Hardware_OutputChangeToUnknown", "Output Changed State to Unknown"),
    11202: ("Hardware_OutputChangeToOn", "Output Changed State to On"),
    11203: ("Hardware_OutputChangeToOff", "Output Changed State to Off"),
    11204: (
        "Hardware_OutputControlFailNotControllable",
        "Output Control Failed because Not User Controllable",
    ),
    11205: (
        "Hardware_OutputControlFailNoPermission",
        "Output Control Failed because No Permission",
    ),
    11206: ("Hardware_OutputControlUserTurnOn", "Output Turned On by User"),
    11207: ("Hardware_OutputControlUserTurnOff", "Output Turned Off by User"),
    11208: (
        "Hardware_OutputControlUserTurnOnTimed",
        "Output Turned On for Time by User",
    ),
    11209: (
        "Hardware_OutputControlUserTurnOffTimed",
        "Output Turned Off for Time by User",
    ),
    11210: ("Hardware_OutputControlAutomationTurnOn", "Output Turned On by Automation"),
    11211: (
        "Hardware_OutputControlAutomationTurnOff",
        "Output Turned Off by Automation",
    ),
    11212: (
        "Hardware_OutputControlAutomationTurnOnTimed",
        "Output Turned On for Time by Automation",
    ),
    11213: (
        "Hardware_OutputControlAutomationTurnOffTimed",
        "Output Turned Off for Time by Automation",
    ),
    11401: ("Hardware_SirenToneStarted", "Siren Tone Started"),
    11402: ("Hardware_SirenToneStopped", "Siren Tone Stopped"),
    11403: ("Hardware_SirenSquawkActivated", "Siren Squawk Activated"),
    11404: (
        "Hardware_SirenSquawkIgnored",
        "Siren Squawk Ignored, Tone Already Playing",
    ),
    12501: ("Hardware_USBWiFiModuleConnected", "WiFi Module Connected"),
    12502: ("Hardware_USBWiFiModuleDisconnected", "WiFi Module Disconnected"),
    13001: ("Hardware_TerminalLoginSuccess", "Terminal Login was Successful by User"),
    13002: (
        "Hardware_TerminalLoginFailedPINUnknown",
        "Terminal Login Failed because PIN was Unknown",
    ),
    13003: (
        "Hardware_TerminalLoginFailedNoPermission",
        "Terminal Login Failed because User does not have Permission",
    ),
    13004: (
        "Hardware_TerminalLogoutSuccessful",
        "Terminal Logout was Successful by User",
    ),
    13005: (
        "Hardware_TerminalLockedOut",
        "Terminal Locked Out, Too Many Failed Attempts",
    ),
    13006: (
        "Hardware_TerminalLoginFailedUserExpired",
        "Terminal Login Failed because User is Expired",
    ),
    13007: (
        "Hardware_TerminalLoginFailedAreaArmed",
        "Terminal Login Failed because one or more Areas were Armed",
    ),
    13008: (
        "Hardware_TerminalLoginFailedCredentialInactive",
        "Terminal Login Failed because User's Credential was Inactive",
    ),
    13501: ("Hardware_RemoteFobButtonUnknownFob", "Remote Fob Button from Unknown Fob"),
    13502: (
        "Hardware_RemoteFobButtonFromUser",
        "Remote Fob Button press received from User",
    ),
    13503: (
        "Hardware_RemoteFobButtonDuplicate",
        "Remote Fob Button press received (duplicate)",
    ),
    13504: (
        "Hardware_RemoteFobButtonMissingTemplate",
        "Remote Fob Button press received for missing Template",
    ),
    13505: (
        "Hardware_RemoteFobButtonNoAction",
        "Remote Fob Button press received but no Action assigned",
    ),
    13506: ("Hardware_RfDetectorDiscovered", "Rf Device Learn Button Pressed"),
    13507: ("Hardware_RfSignalStrength", "Rf Input Signal Strength Update"),
    13508: (
        "Hardware_RemoteFobButtonFromExpiredUser",
        "Remote Fob Button press received from Expired / Cancelled User",
    ),
    13509: ("Hardware_RemoteFobBatteryLow", "Remote Fob Low Battery Detected"),
    13510: ("Hardware_RemoteFobBatteryOk", "Remote Fob Low Battery Restored"),
    14001: ("Hardware_BatteryTestQueued", "Battery Test Queued"),
    14002: ("Hardware_BatteryTestManuallyRequested", "Battery Test Manually Requested"),
    14003: ("Hardware_BatteryTestStarted", "Battery Test Started"),
    14004: ("Hardware_BatteryTestUnableToStart", "Battery Test Unable to Start"),
    14005: ("Hardware_BatteryTestPassed", "Battery Test Passed"),
    14006: ("Hardware_BatteryTestFailed", "Battery Test Failed"),
    14007: ("Hardware_BatteryTestAborted", "Battery Test Aborted"),
    14201: (
        "Hardware_ReaderAreaFailedNoDoor",
        "Keypad Reader Area Control Failed, No Door",
    ),
    14202: (
        "Hardware_ReaderAreaFailedNoArea",
        "Keypad Reader Area Control Failed, No Area",
    ),
    14203: ("Hardware_ReaderLockedOut", "Reader Locked Out, Too Many Failed Attempts"),
    14301: ("Hardware_ILAMStartedOfflineSync", "ILAM Started Synchronising Offline DB"),
    14302: (
        "Hardware_ILAMFinishedOfflineSync",
        "ILAM Finished Synchronising Offline DB",
    ),
    20000: ("Integration_IntegratedConnectionOnline", "Integrated Connection Online"),
    20001: ("Integration_IntegratedConnectionOffline", "Integrated Connection Offline"),
    20002: ("Integration_IntegratedConnectionError", "Integrated Connection Error"),
    20003: ("Integration_DeviceStateOnline", "Integrated Device Online"),
    20004: ("Integration_DeviceStateOffline", "Integrated Device Offline"),
    20005: ("Integration_AnalyticsEventDetected", "Integration Analytics Detected"),
    20006: ("Integration_AnalyticsEventRestored", "Integration Analytics Restored"),
    20007: (
        "Integration_ThirdPartyDeviceConfigurationErrorDetected",
        "3rd Party Device Configuration Error Detected",
    ),
    20008: (
        "Integration_ThirdPartyDeviceConfigurationErrorRestored",
        "3rd Party Device Configuration Error Restored",
    ),
    20009: ("Integration_VideoSignalErrorDetected", "Video Signal Error Detected"),
    20010: ("Integration_VideoSignalErrorRestored", "Video Signal Error Restored"),
    20011: ("Integration_ThirdPartyDiskErrorDetected", "3rd Party Disk Error Detected"),
    20012: ("Integration_ThirdPartyDiskErrorRestored", "3rd Party Disk Error Restored"),
    20013: ("Integration_CommandActivity", "Integration Command Activity"),
}


def get_message_info(message_id: int) -> tuple[str, str] | None:
    """
    Get message information for a given message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        Tuple of (string_value, description) or None if not found

    """
    return MESSAGE_DESCRIPTIONS.get(message_id)


def get_message_description(message_id: int) -> str | None:
    """
    Get human-readable description for a message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        Human-readable description or None if not found

    """
    info = get_message_info(message_id)
    return info[1] if info else None


def get_message_string_value(message_id: int) -> str | None:
    """
    Get string value for a message ID.

    Args:
        message_id: The MessageID from the review event

    Returns:
        String value or None if not found

    """
    info = get_message_info(message_id)
    return info[0] if info else None
