import requests
from unittest                                                                               import TestCase
from unittest.mock                                                                          import Mock, patch
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id             import Safe_Str__Id
from osbot_utils.utils.Objects                                                              import base_classes
from osbot_utils.testing.__                                                                 import __, __SKIP__
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url                    import Safe_Str__Url
from osbot_utils.type_safe.primitives.core.Safe_Float                                       import Safe_Float
from mgraph_ai_service_mitmproxy.service.health_check.Cache__Health_Check__Service          import Cache__Health_Check__Service
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Enum__Health_Status           import Enum__Health_Status
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Schema__Cache_Service_Info    import Schema__Cache_Service_Info
from mgraph_ai_service_mitmproxy.service.health_check.schemas.Schema__Health_Check_Result   import Schema__Health_Check_Result


class test_Cache__Health_Check__Service(TestCase):

    @classmethod
    def setUpClass(cls):                                                            # Setup shared test objects once
        cls.base_url    = "https://cache-service.example.com"
        cls.api_key     = "test-api-key-12345"
        cls.timeout     = 10.0
        cls.service     = Cache__Health_Check__Service(base_url        = cls.base_url,
                                                        timeout        = cls.timeout ,
                                                        api_key        = cls.api_key ,
                                                        api_key_header = "X-API-Key" )

    def test__init__(self):                                                         # Test auto-initialization of service
        with Cache__Health_Check__Service() as _:
            assert type(_)                   is Cache__Health_Check__Service
            assert base_classes(_)           == [Cache__Health_Check__Service.__bases__[0], object]
            assert type(_.base_url)          is Safe_Str__Url
            assert type(_.timeout)           is Safe_Float
            assert type(_.api_key_header)    is Safe_Str__Id

            assert _.obj() == __(base_url       = ''             ,                  # Empty URL default
                                 timeout        = 5.0            ,                  # Default timeout
                                 api_key        = None           ,                  # Optional API key
                                 api_key_header = "X-API-Key"   )                  # Default header name

    def test__init__with_values(self):                                              # Test initialization with explicit values
        with Cache__Health_Check__Service(base_url = self.base_url,
                                          timeout  = 15.0) as _:
            assert _.base_url == self.base_url
            assert _.timeout  == 15.0
            assert _.api_key  is None

    def test__type_conversion(self):                                                # Test Type_Safe auto-conversion
        with Cache__Health_Check__Service() as _:
            _.base_url = "http://example.com"                                       # String to Safe_Str__Url
            assert type(_.base_url) is Safe_Str__Url
            assert _.base_url       == "http://example.com"

            _.timeout = 7.5                                                         # Float to Safe_Float
            assert type(_.timeout)  is Safe_Float
            assert _.timeout        == 7.5

            _.api_key = "raw-key-string"                                            # String to Safe_Str__Text
            assert type(_.api_key)  is Safe_Str__Id
            assert _.api_key        == "raw-key-string"

    def test_get_headers(self):                                                     # Test header generation without API key
        with Cache__Health_Check__Service(base_url = self.base_url) as _:
            headers = _.get_headers()
            assert headers == {}                                                    # No headers when no API key

    def test_get_headers__with_api_key(self):                                       # Test header generation with API key
        with Cache__Health_Check__Service(base_url    = self.base_url,
                                          api_key     = self.api_key,
                                          api_key_header = "X-Custom-Key") as _:
            headers = _.get_headers()
            assert headers == {Safe_Str__Id("X-Custom-Key"): self.api_key}

    @patch('requests.get')
    def test_check_connectivity__success(self, mock_get):                           # Test successful connectivity check
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_get.return_value     = mock_response

        result = self.service.check_connectivity()

        assert type(result)                    is Schema__Health_Check_Result
        assert result.obj()                    == __( status        = 'healthy'                                                  ,
                                                      message       = 'Cache service reachable at https://cache-service.example.com',
                                                      checks_passed = ['connectivity']                                           ,
                                                      checks_failed = []                                                          ,
                                                      details       = __(response_time_ms = __SKIP__ ,
                                                                          status_code      = 200     )                           ,
                                                      checked_at    = __SKIP__                                                    ,
                                                      duration_ms   = __SKIP__                      )
        assert result.status                  == Enum__Health_Status.HEALTHY
        assert "Cache service reachable"      in result.message
        assert result.duration_ms             > 0
        assert "connectivity"                 in result.checks_passed
        assert result.details["status_code"]  == 200

    @patch('requests.get')
    def test_check_connectivity__root_404(self, mock_get):                          # Test connectivity with 404 on root
        mock_response             = Mock()
        mock_response.status_code = 404
        mock_get.return_value     = mock_response

        result = self.service.check_connectivity()

        assert result.status                  == Enum__Health_Status.HEALTHY        # 404 is acceptable for root
        assert "reachable"                    in result.message
        assert "connectivity"                 in result.checks_passed

    @patch('requests.get')
    def test_check_connectivity__unexpected_status(self, mock_get):                 # Test connectivity with unexpected status
        mock_response             = Mock()
        mock_response.status_code = 500
        mock_get.return_value     = mock_response

        result = self.service.check_connectivity()

        assert result.obj() == __( status        = 'degraded'                               ,
                                   message       = 'Cache service returned unexpected status: 500',
                                   checks_passed = []                                        ,
                                   checks_failed = ['connectivity: Status 500']              ,
                                   details       = __()                                      ,
                                   checked_at    = __SKIP__                                  ,
                                   duration_ms   = __SKIP__                                  )
        assert result.status                  == Enum__Health_Status.DEGRADED
        assert "unexpected status: 500"       in result.message
        assert "connectivity: Status 500"     in result.checks_failed

    @patch('requests.get')
    def test_check_connectivity__connection_error(self, mock_get):                  # Test connectivity with connection error
        error_message = "Connection refused"
        mock_get.side_effect = requests.exceptions.ConnectionError(error_message)

        result = self.service.check_connectivity()

        assert result.status                        == Enum__Health_Status.UNHEALTHY
        assert "Cannot connect"                     in result.message
        assert "connectivity: Connection refused"   in result.checks_failed
        assert result.details["error"]              == error_message

    @patch('requests.get')
    def test_check_connectivity__timeout(self, mock_get):                           # Test connectivity with timeout
        mock_get.side_effect = requests.exceptions.Timeout()

        result = self.service.check_connectivity()

        assert result.status                  == Enum__Health_Status.UNHEALTHY
        assert "timeout"                      in result.message.lower()
        assert "connectivity: Timeout"        in result.checks_failed

    @patch('requests.get')
    def test_check_connectivity__unexpected_error(self, mock_get):                  # Test connectivity with unexpected error
        error_message = "Unexpected network error"
        mock_get.side_effect = Exception(error_message)

        result = self.service.check_connectivity()

        assert result.status                    == Enum__Health_Status.UNKNOWN
        assert "Unexpected error"               in result.message
        assert f"connectivity: {error_message}" in result.checks_failed

    @patch('requests.get')
    def test_check_storage_info__success(self, mock_get):                           # Test successful storage info check
        storage_data = { "storage_mode" : "s3"          ,
                         "ttl_hours"    : 24            ,
                         "s3_bucket"    : "test-bucket" }
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.json        = Mock(return_value=storage_data)
        mock_get.return_value     = mock_response

        result = self.service.check_storage_info()

        assert result.status                        == Enum__Health_Status.HEALTHY
        assert "Storage backend: s3"                in result.message
        assert "storage_info"                       in result.checks_passed
        assert "storage_mode_present"               in result.checks_passed
        assert result.details["storage_info"]       == storage_data
        assert result.duration_ms                   > 0

    @patch('requests.get')
    def test_check_storage_info__missing_storage_mode(self, mock_get):              # Test storage info with missing storage_mode
        storage_data = {"ttl_hours": 24}                                            # Missing storage_mode
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.json        = Mock(return_value=storage_data)
        mock_get.return_value     = mock_response

        result = self.service.check_storage_info()
        assert result.obj()                                  ==  __( status        = 'degraded'                                     ,
                                                                     message       = 'Storage backend: unknown'                     ,
                                                                     checks_passed = ['storage_info']                               ,
                                                                     checks_failed = ['storage_mode_present: Missing storage_mode'] ,
                                                                     details       = __( storage_info     = __(ttl_hours = 24) ,
                                                                                         response_time_ms = __SKIP__           )   ,
                                                                     checked_at    = __SKIP__                                       ,
                                                                     duration_ms   = __SKIP__                                       )
        assert result.status                                 == Enum__Health_Status.DEGRADED
        assert 'storage_mode_present: Missing storage_mode'  in result.checks_failed

    @patch('requests.get')
    def test_check_storage_info__endpoint_error(self, mock_get):                    # Test storage info with endpoint error
        mock_response             = Mock()
        mock_response.status_code = 404
        mock_get.return_value     = mock_response

        result = self.service.check_storage_info()
        assert result.obj()                  == __( status        = 'degraded'                          ,
                                                    message       = 'Storage info endpoint returned 404',
                                                    checks_passed = []                                  ,
                                                    checks_failed = ['storage_info: Status 404']        ,
                                                    details       = __()                                ,
                                                    checked_at    = __SKIP__                            ,
                                                    duration_ms   = __SKIP__                            )
        assert result.status                        == Enum__Health_Status.DEGRADED
        assert "endpoint returned 404"              in result.message
        assert "storage_info: Status 404"           in result.checks_failed

    @patch('requests.get')
    def test_check_storage_info__exception(self, mock_get):                         # Test storage info with exception
        error_message = "Network error"
        mock_get.side_effect = Exception(error_message)

        result = self.service.check_storage_info()
        assert result.status                     == Enum__Health_Status.UNHEALTHY
        assert "Cannot retrieve storage info"    in result.message
        assert f"storage_info: {error_message}"  in result.checks_failed
        assert result.details                    == {'error':'Network error'}

    @patch('requests.get')
    def test_check_api_endpoints__all_healthy(self, mock_get):                      # Test all endpoints are healthy
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_get.return_value     = mock_response

        result = self.service.check_api_endpoints()

        assert result.status                        == Enum__Health_Status.HEALTHY
        assert "All 3 API endpoints operational"    in result.message
        assert result.details["endpoints_checked"]  == 3
        assert result.details["endpoints_passed"]   == 3
        assert result.details["endpoints_failed"]   == 0

    @patch('requests.get')
    def test_check_api_endpoints__partial_failure(self, mock_get):                  # Test some endpoints fail
        def side_effect(*args, **kwargs):
            if "storage/info" in args[0]:
                return Mock(status_code=200)
            else:
                return Mock(status_code=500)

        mock_get.side_effect = side_effect

        result = self.service.check_api_endpoints()
        assert result.obj()            == __( status        = 'unhealthy'                            ,
                                              message       = 'Only 1/3 endpoints working'           ,
                                              checks_passed = ['endpoint_/server/storage/info']       ,
                                              checks_failed = [ 'endpoint_/info/health: Status 500'  ,
                                                                'endpoint_/info/server: Status 500'] ,
                                              details       = __( endpoints_checked = 3 ,
                                                                  endpoints_passed  = 1 ,
                                                                  endpoints_failed  = 2 )            ,
                                              checked_at    = __SKIP__                                ,
                                              duration_ms   = __SKIP__                                )
        assert result.status           == Enum__Health_Status.UNHEALTHY
        assert "1/3 endpoints working" in result.message

    @patch('requests.get')
    def test_check_api_endpoints__majority_fail(self, mock_get):                    # Test majority of endpoints fail
        mock_response             = Mock()
        mock_response.status_code = 500
        mock_get.return_value     = mock_response

        result = self.service.check_api_endpoints()

        assert result.status                        == Enum__Health_Status.UNHEALTHY
        assert "Only 0/3 endpoints working"         in result.message
        assert result.details["endpoints_passed"]   == 0
        assert result.details["endpoints_failed"]   == 3

    @patch('requests.get')
    def test_check_api_endpoints__with_exceptions(self, mock_get):                  # Test endpoints with exceptions
        def side_effect(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Connection failed")

        mock_get.side_effect = side_effect

        result = self.service.check_api_endpoints()

        assert result.status                        == Enum__Health_Status.UNHEALTHY
        assert result.details["endpoints_failed"]   == 3

    @patch('requests.get')
    def test_get_service_info__success(self, mock_get):                             # Test successful service info retrieval
        storage_data = { "storage_mode": "s3",
                         "ttl_hours": 48,
                         "s3_bucket": "production-bucket"   }
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.json        = Mock(return_value=storage_data)
        mock_get.return_value     = mock_response

        result = self.service.get_service_info()

        assert result.obj()         == __( storage_mode  = 's3'                                  ,
                                           ttl_hours     = 48                                    ,
                                           s3_bucket     = 'production-bucket'                  ,
                                           version       = None                                 ,
                                           is_reachable  = True                                 ,
                                           base_url      = 'https://cache-service.example.com'  )

        assert type(result)         is Schema__Cache_Service_Info
        assert result.base_url      == self.base_url
        assert result.storage_mode  == "s3"
        assert result.ttl_hours     == 48
        assert result.s3_bucket     == "production-bucket"
        assert result.is_reachable  is True

    @patch('requests.get')
    def test_get_service_info__endpoint_error(self, mock_get):                      # Test service info with endpoint error
        mock_response             = Mock()
        mock_response.status_code = 500
        mock_get.return_value     = mock_response

        result = self.service.get_service_info()

        assert result is None

    @patch('requests.get')
    def test_get_service_info__exception(self, mock_get):                           # Test service info with exception
        mock_get.side_effect = Exception("Network error")

        result = self.service.get_service_info()

        assert type(result)         is Schema__Cache_Service_Info
        assert result.base_url      == self.base_url
        assert result.is_reachable  is False

    @patch('requests.get')
    def test_perform_comprehensive_check__all_healthy(self, mock_get):              # Test comprehensive check with all systems healthy
        storage_data = { "storage_mode": "s3",
                         "ttl_hours": 24,
                         "s3_bucket": "test-bucket" }
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.json        = Mock(return_value=storage_data)
        mock_get.return_value     = mock_response

        result = self.service.perform_comprehensive_check()

        assert result["overall_status"]             == Enum__Health_Status.HEALTHY.value
        assert result["overall_message"]            == "All systems operational"
        assert result["total_duration_ms"]          > 0
        assert "timestamp"                          in result
        assert result["summary"]["total_checks"]    == 3
        assert result["summary"]["healthy"]         == 3
        assert result["summary"]["degraded"]        == 0
        assert result["summary"]["unhealthy"]       == 0
        assert "connectivity"                       in result["checks"]
        assert "storage"                            in result["checks"]
        assert "endpoints"                          in result["checks"]

    @patch('requests.get')
    def test_perform_comprehensive_check__with_unhealthy(self, mock_get):           # Test comprehensive check with unhealthy services
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = self.service.perform_comprehensive_check()

        assert result["overall_status"]             == Enum__Health_Status.UNHEALTHY.value
        assert "critical issues detected"           in result["overall_message"]
        assert result["summary"]["unhealthy"]       > 0

    @patch('requests.get')
    def test_perform_comprehensive_check__with_degraded(self, mock_get):            # Test comprehensive check with degraded services
        def side_effect(*args, **kwargs):
            if "storage/info" in args[0]:
                response = Mock()
                response.status_code = 200
                response.json = Mock(return_value={"ttl_hours": 24})                # Missing storage_mode
                return response
            else:
                response = Mock()
                response.status_code = 200
                return response

        mock_get.side_effect = side_effect

        result = self.service.perform_comprehensive_check()

        assert result["overall_status"]             == Enum__Health_Status.DEGRADED.value
        assert "Some issues detected"               in result["overall_message"]

    @patch('requests.get')
    def test_perform_comprehensive_check__service_info_present(self, mock_get):     # Test comprehensive check includes service info
        storage_data = {
            "storage_mode": "s3",
            "ttl_hours": 24,
            "s3_bucket": "test-bucket"
        }
        mock_response             = Mock()
        mock_response.status_code = 200
        mock_response.json        = Mock(return_value=storage_data)
        mock_get.return_value     = mock_response

        result = self.service.perform_comprehensive_check()

        assert result["service_info"] is not None
        service_info = result["service_info"]
        assert "base_url"     in service_info
        assert "storage_mode" in service_info
        assert "is_reachable" in service_info

    def test__serialization_round_trip(self):                                       # Test JSON serialization preserves types
        with Cache__Health_Check__Service(base_url = self.base_url,
                                          timeout  = 15.0,
                                          api_key  = self.api_key) as original:
            json_data = original.json()

            with Cache__Health_Check__Service.from_json(json_data) as restored:
                assert restored.base_url     == original.base_url
                assert restored.timeout      == original.timeout
                assert restored.api_key      == original.api_key

                assert type(restored.base_url)  is Safe_Str__Url                    # Types preserved
                assert type(restored.timeout)   is Safe_Float
                assert type(restored.api_key)   is Safe_Str__Id