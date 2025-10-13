from unittest                                                                           import TestCase

import pytest
from mgraph_ai_service_cache.fast_api.Cache_Service__Fast_API                           import Cache_Service__Fast_API
from mgraph_ai_service_cache.service.cache.Cache__Config                                import Cache__Config
from mgraph_ai_service_cache.service.cache.Cache__Service                               import Cache__Service
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client           import Service__Fast_API__Client
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client__Config   import Service__Fast_API__Client__Config
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Storage_Mode       import Enum__Cache__Storage_Mode
from osbot_fast_api.utils.Fast_API_Server                                               import Fast_API_Server
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                    import Serverless__Fast_API__Config
from osbot_utils.helpers.duration.decorators.capture_duration                           import capture_duration
from osbot_utils.testing.__                                                             import __
from osbot_utils.type_safe.primitives.core.Safe_UInt                                    import Safe_UInt
from osbot_utils.utils.Http                                                             import GET_json
from osbot_utils.utils.Misc                                                             import list_set
from osbot_utils.utils.Objects                                                          import obj
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service                    import Proxy__Cache__Service
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Config            import Schema__Cache__Config
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Stats             import Schema__Cache__Stats
from osbot_utils.utils.Dev import pprint

# todo: refactor most of these methods into the cache_service tests, since they are not testing Routes__Cache methods
class test_Routes__Cache(TestCase):

    @classmethod
    def setUpClass(cls) -> None:                                                                # Setup cache service and test infrastructure
        pytest.skip("write tests to use setup__testing__cache_service__with__test_data and to actually hit the Routes__Cache")
        with capture_duration() as duration:
            cache_config = Cache__Config(storage_mode=Enum__Cache__Storage_Mode.MEMORY)         # Setup cache service backend
            cls.serverless_config = Serverless__Fast_API__Config(enable_api_key=False)
            cls.cache_service__fast_api = Cache_Service__Fast_API(config=cls.serverless_config,
                                                                  cache_service=Cache__Service(cache_config=cache_config))

            cls.fast_api_server = Fast_API_Server(app=cls.cache_service__fast_api.app())
            cls.server_url      = cls.fast_api_server.url().rstrip("/")

            cls.cache_service__fast_api.setup()
            cls.fast_api_server.start()

            cls.client_config = Service__Fast_API__Client__Config(base_url=cls.server_url)          # Setup cache client
            cls.cache_client = Service__Fast_API__Client(config=cls.client_config)

            cls.cache_config = Schema__Cache__Config(enabled    = True               ,              # Setup proxy cache service
                                                     base_url   = cls.server_url     ,
                                                     namespace  = "test-cache-routes",
                                                     timeout    = 2                  )

            cls.cache_service = Proxy__Cache__Service(cache_client=cls.cache_client,
                                                      cache_config=cls.cache_config,
                                                      stats=Schema__Cache__Stats())

            cls._populate_test_cache()                                                              # Populate test data

        assert duration.seconds < 1.5

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api_server.stop()

    @classmethod
    def _populate_test_cache(cls):                                              # Populate cache with test data
        test_urls = [ "https://example.com/"                ,                   # Add some test pages with transformations
                      "https://docs.diniscruz/ai"           ,
                      "https://docs.diniscruz/ai/about.html"]

        for url in test_urls:
            cls.cache_service.store_transformation(target_url   = url               ,       # Store HTML transformation
                                                   wcf_command  = "url-to-html"     ,
                                                   content      = f"<html><body><h1>Test content for {url}</h1></body></html>",
                                                   metadata     = {"status_code": 200, "content_type": "text/html"})

            # Store text transformation
            cls.cache_service.store_transformation(target_url   = url                                               ,
                                                   wcf_command  = "url-to-lines"                                    ,
                                                   content      = f"Test text content for {url}"                    ,
                                                   metadata     = {"status_code": 200, "content_type": "text/plain"})

    def test__routes_wired_to_fast_api(self):
        #print(self.server_url)
        #response = GET_json(self.server_url + '/cache/health')

        #pprint(response)

        #open_api = GET_json(self.server_url + '/openapi.json')
        #pprint(list_set(open_api.get('paths')))
        # todo: fix this test to use the mitmproxy service not the cache service
        #assert 'status' in response
        pass


    def test__get_health(self):
        """Test /cache/health endpoint logic"""
        # Test enabled cache
        # health_data = {
        #     "status": "ok",
        #     "enabled": True,
        #     "base_url": str(self.cache_service.cache_config.base_url),
        #     "namespace": str(self.cache_service.cache_config.namespace)
        # }
        #
        # assert health_data["status"] == "ok"
        # assert health_data["enabled"] is True
        # assert "base_url" in health_data
        # assert "namespace" in health_data
        # todo: redo this test since the test above is not actually testing the /cache/health endpoint

    def test__get_stats(self):              # Test /cache/stats endpoint logic
        # todo: add check to call /cache/stats
        stats = self.cache_service.get_cache_stats()

        assert obj(stats) == __(enabled                     = True             ,
                                hit_rate                    = 0.0              ,
                                cache_hits                  = Safe_UInt(0)     ,
                                cache_misses                = Safe_UInt(0)     ,
                                wcf_calls_saved             = Safe_UInt(0)     ,
                                total_pages_cached          = Safe_UInt(3)     ,
                                avg_cache_hit_time_ms       = 0.0              ,
                                avg_cache_miss_time_ms      = 0.0              ,
                                avg_wcf_call_time_ms        = 0.0              ,
                                estimated_time_saved_seconds= 0.0              )

    def test__get_config(self):                     # Test /cache/config endpoint logic
        # todo: add check to call /cache/config
        config = self.cache_service.cache_config

        config_data = {
            "enabled": config.enabled,
            "base_url": str(config.base_url),
            "namespace": str(config.namespace),
            "timeout": int(config.timeout),
            "strategy": config.strategy.value,
            "data_file_id": config.data_file_id,
            "cache_metadata": config.cache_metadata,
            "track_stats": config.track_stats
        }

        assert config_data["enabled"] is True
        assert config_data["namespace"] == "test-cache-routes"
        assert config_data["strategy"] == "key_based"
        assert config_data["data_file_id"] == "latest"









