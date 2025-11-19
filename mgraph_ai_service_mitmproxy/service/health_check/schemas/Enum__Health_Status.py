from enum import Enum


class Enum__Health_Status(str, Enum):                               # Health check status levels
    HEALTHY   = "healthy"     # All systems operational
    DEGRADED  = "degraded"    # Some issues but functional
    UNHEALTHY = "unhealthy"   # Critical issues
    UNKNOWN   = "unknown"     # Unable to determine