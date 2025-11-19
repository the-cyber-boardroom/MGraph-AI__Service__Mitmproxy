from typing                                                                         import List, Dict, Any
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.utils.Misc                                                         import datetime_now
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Enum__Health_Status   import Enum__Health_Status


class Schema__Health_Check_Result(Type_Safe):               # Result of a health check operation"""
    status          : Enum__Health_Status                   # Overall health status
    message         : str                                   # Human-readable status message
    checks_passed   : List[str]                             # List of passed checks
    checks_failed   : List[str]                             # List of failed checks
    details         : Dict[str, Any]                        # Additional details
    checked_at      : str                                   # ISO timestamp of check
    duration_ms     : float                                 # Time taken for check

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.checked_at:
            self.checked_at = datetime_now()

    def is_healthy(self) -> bool:
        """Check if status is healthy"""
        return self.status == Enum__Health_Status.HEALTHY

    def add_passed_check(self, check_name: str):
        """Add a passed check"""
        self.checks_passed.append(check_name)

    def add_failed_check(self, check_name: str, reason: str = ""):
        """Add a failed check"""
        failure = f"{check_name}: {reason}" if reason else check_name
        self.checks_failed.append(failure)
