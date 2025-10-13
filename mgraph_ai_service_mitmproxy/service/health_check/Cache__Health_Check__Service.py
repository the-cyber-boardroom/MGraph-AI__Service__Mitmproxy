import requests
import time
from typing                                                                                                   import Dict, Any, Optional, List
from datetime                                                                                                 import datetime
from osbot_utils.type_safe.Type_Safe                                                                          import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                import type_safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                                         import Safe_Float
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                               import Safe_Str__Id
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                                      import Safe_Str__Url
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Enum__Health_Status                             import Enum__Health_Status
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Schema__Cache_Service_Info                      import Schema__Cache_Service_Info
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Schema__Health_Check_Result                     import Schema__Health_Check_Result


class Cache__Health_Check__Service(Type_Safe):                                  # Health check service for cache endpoints
    base_url        : Safe_Str__Url                                             # Cache service base URL
    timeout         : Safe_Float        = 5.0                                   # Request timeout in seconds
    api_key         : Safe_Str__Id      = None                                  # Optional API key
    api_key_header  : Safe_Str__Id      = "X-API-Key"                           # API key header name

    @type_safe
    def get_headers(self) -> Dict[Safe_Str__Id, Safe_Str__Id]:                                       # Get headers for requests
        headers = {}
        if self.api_key:
            headers[self.api_key_header] = self.api_key
        return headers

    @type_safe
    def check_connectivity(self) -> Schema__Health_Check_Result:                   # Check basic connectivity to cache service
        start_time = time.time()
        result     = Schema__Health_Check_Result()

        try:
            response    = requests.get(f"{self.base_url}/",
                                      headers = self.get_headers(),
                                      timeout = float(self.timeout))

            duration_ms        = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms

            if response.status_code in [200, 404]:                                 # 404 is ok for root endpoint
                result.status                       = Enum__Health_Status.HEALTHY
                result.message                      = f"Cache service reachable at {self.base_url}"
                result.details["response_time_ms"]  = duration_ms
                result.details["status_code"]       = response.status_code
                result.add_passed_check("connectivity")
            else:
                result.status  = Enum__Health_Status.DEGRADED
                result.message = f"Cache service returned unexpected status: {response.status_code}"
                result.add_failed_check("connectivity", f"Status {response.status_code}")

        except requests.exceptions.ConnectionError as e:
            result.status         = Enum__Health_Status.UNHEALTHY
            result.message        = f"Cannot connect to cache service: {str(e)}"
            result.details["error"] = str(e)
            result.add_failed_check("connectivity", "Connection refused")

        except requests.exceptions.Timeout:
            result.status  = Enum__Health_Status.UNHEALTHY
            result.message = f"Cache service timeout after {self.timeout}s"
            result.add_failed_check("connectivity", "Timeout")

        except Exception as e:
            result.status  = Enum__Health_Status.UNKNOWN
            result.message = f"Unexpected error: {str(e)}"
            result.add_failed_check("connectivity", str(e))

        return result

    @type_safe
    def check_storage_info(self) -> Schema__Health_Check_Result:                   # Check storage backend information
        start_time = time.time()
        result     = Schema__Health_Check_Result()

        try:
            url      = f"{self.base_url}/server/storage/info"
            response = requests.get(url,
                                   headers = self.get_headers(),
                                   timeout = float(self.timeout))

            duration_ms        = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms

            if response.status_code == 200:
                storage_info = response.json()

                result.status                       = Enum__Health_Status.HEALTHY
                result.message                      = f"Storage backend: {storage_info.get('storage_mode', 'unknown')}"
                result.details["storage_info"]      = storage_info
                result.details["response_time_ms"]  = duration_ms
                result.add_passed_check("storage_info")

                if "storage_mode" in storage_info:                                 # Validate storage info structure
                    result.add_passed_check("storage_mode_present")
                else:
                    result.status = Enum__Health_Status.DEGRADED
                    result.add_failed_check("storage_mode_present", "Missing storage_mode")

            else:
                result.status  = Enum__Health_Status.DEGRADED
                result.message = f"Storage info endpoint returned {response.status_code}"
                result.add_failed_check("storage_info", f"Status {response.status_code}")

        except Exception as e:
            result.status         = Enum__Health_Status.UNHEALTHY
            result.message        = f"Cannot retrieve storage info: {str(e)}"
            result.details["error"] = str(e)
            result.add_failed_check("storage_info", str(e))

        return result

    @type_safe
    def check_api_endpoints(self) -> Schema__Health_Check_Result:                  # Check availability of key API endpoints
        result = Schema__Health_Check_Result()

        endpoints_to_check = [                                                     # Endpoints to check with expected status codes
            ("/server/storage/info", [200]),
            ("/info/health"        , [200]),
            ("/info/server"        , [200]),
        ]

        passed_count = 0
        failed_count = 0

        for endpoint_path, expected_statuses in endpoints_to_check:
            try:
                url      = f"{self.base_url}{endpoint_path}"
                response = requests.get(url,
                                       headers = self.get_headers(),
                                       timeout = float(self.timeout))

                if response.status_code in expected_statuses:
                    result.add_passed_check(f"endpoint_{endpoint_path}")
                    passed_count += 1
                else:
                    result.add_failed_check(f"endpoint_{endpoint_path}",
                                          f"Status {response.status_code}")
                    failed_count += 1

            except Exception as e:
                result.add_failed_check(f"endpoint_{endpoint_path}", str(e))
                failed_count += 1

        if failed_count == 0:                                                      # Determine overall status
            result.status  = Enum__Health_Status.HEALTHY
            result.message = f"All {passed_count} API endpoints operational"
        elif passed_count > failed_count:
            result.status  = Enum__Health_Status.DEGRADED
            result.message = f"{passed_count}/{passed_count + failed_count} endpoints working"
        else:
            result.status  = Enum__Health_Status.UNHEALTHY
            result.message = f"Only {passed_count}/{passed_count + failed_count} endpoints working"

        result.details["endpoints_checked"] = passed_count + failed_count
        result.details["endpoints_passed"]  = passed_count
        result.details["endpoints_failed"]  = failed_count

        return result

    @type_safe
    def get_service_info(self) -> Optional[Schema__Cache_Service_Info]:            # Get comprehensive service information
        try:
            storage_response = requests.get(url     = f"{self.base_url}/server/storage/info",
                                            headers = self.get_headers(),
                                            timeout = float(self.timeout))

            if storage_response.status_code != 200:
                return None

            storage_data = storage_response.json()

            return Schema__Cache_Service_Info(base_url     = str(self.base_url)                      ,
                                              storage_mode = storage_data.get("storage_mode", "unknown"),
                                              ttl_hours    = storage_data.get("ttl_hours", 0)          ,
                                              s3_bucket    = storage_data.get("s3_bucket")             ,
                                              is_reachable = True                                      )

        except Exception:
            return Schema__Cache_Service_Info(base_url     = str(self.base_url),
                                              is_reachable = False              )

    @type_safe
    def perform_comprehensive_check(self) -> Dict[str, Any]:                       # Perform all health checks and return comprehensive report
        start_time = time.time()

        connectivity_check = self.check_connectivity()                            # Run all checks
        storage_check      = self.check_storage_info()
        endpoints_check    = self.check_api_endpoints()
        service_info       = self.get_service_info()

        all_checks = [connectivity_check, storage_check, endpoints_check]

        healthy_count   = sum(1 for check in all_checks if check.is_healthy())    # Determine overall health
        unhealthy_count = sum(1 for check in all_checks
                             if check.status == Enum__Health_Status.UNHEALTHY)

        if unhealthy_count > 0:
            overall_status  = Enum__Health_Status.UNHEALTHY
            overall_message = f"{unhealthy_count} critical issues detected"
        elif healthy_count == len(all_checks):
            overall_status  = Enum__Health_Status.HEALTHY
            overall_message = "All systems operational"
        else:
            overall_status  = Enum__Health_Status.DEGRADED
            overall_message = "Some issues detected but service functional"

        total_duration_ms = (time.time() - start_time) * 1000

        return {
            "overall_status"    : overall_status.value,
            "overall_message"   : overall_message,
            "timestamp"         : datetime.utcnow().isoformat() + "Z",
            "total_duration_ms" : total_duration_ms,
            "service_info"      : service_info.json() if service_info else None,
            "checks"            : {
                "connectivity" : connectivity_check.json(),
                "storage"      : storage_check.json(),
                "endpoints"    : endpoints_check.json()
            },
            "summary"           : {
                "total_checks" : len(all_checks),
                "healthy"      : healthy_count,
                "degraded"     : len(all_checks) - healthy_count - unhealthy_count,
                "unhealthy"    : unhealthy_count
            }
        }