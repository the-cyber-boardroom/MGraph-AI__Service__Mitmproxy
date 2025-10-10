from unittest                                                                           import TestCase
from memory_fs.storage_fs.providers.Storage_FS__Memory                                  import Storage_FS__Memory
from mgraph_ai_service_cache.fast_api.Service__Fast_API                                 import Service__Fast_API
from mgraph_ai_service_cache.service.cache.Cache__Config                                import Cache__Config
from mgraph_ai_service_cache.service.cache.Cache__Service                               import Cache__Service
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client           import Service__Fast_API__Client
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client__Config   import Service__Fast_API__Client__Config
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Storage_Mode       import Enum__Cache__Storage_Mode
from osbot_fast_api.utils.Fast_API_Server                                               import Fast_API_Server
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API__Config                    import Serverless__Fast_API__Config
from osbot_utils.helpers.duration.decorators.capture_duration                           import capture_duration
from osbot_utils.utils.Http                                                             import GET_json
from osbot_utils.utils.Json                                                             import str_to_json
from osbot_utils.utils.Misc                                                             import list_set
from osbot_utils.utils.Objects                                                          import obj
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service                    import Proxy__Cache__Service
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Config            import Schema__Cache__Config
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Stats             import Schema__Cache__Stats

class test_Proxy__Cache__Service(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        with capture_duration() as duration:
            cache_config = Cache__Config(storage_mode=Enum__Cache__Storage_Mode.MEMORY)

            cls.serverless_config       = Serverless__Fast_API__Config(enable_api_key=False)
            cls.cache_service__fast_api = Service__Fast_API(config=cls.serverless_config,
                                                            cache_service=Cache__Service(cache_config=cache_config))  # Inject configured service

            cls.fast_api_server         = Fast_API_Server(app=cls.cache_service__fast_api.app())
            cls.server_url              = cls.fast_api_server.url().rstrip("/")                              # note: the trailing / was causing issues with the auto-generated request code


            cls.server_config           = Service__Fast_API__Client__Config(base_url=cls.server_url, verify_ssl=False)
            cls.fast_api_client         = Service__Fast_API__Client        (config=cls.server_config)

            cls.cache_service__fast_api.setup()
            cls.fast_api_server        .start()

            cls.client_config = Service__Fast_API__Client__Config(base_url = cls.server_url   )
            cls.cache_client  = Service__Fast_API__Client        (config   = cls.client_config)
            cls.cache_config = Schema__Cache__Config             (enabled  = True                ,
                                                                  base_url  = cls.server_url     ,
                                                                  namespace = "proxy-cache-tests",
                                                                  timeout   = 30)
            # Create cache service instance
            cls.cache_service = Proxy__Cache__Service(cache_client = cls.cache_client,
                                                      cache_config = cls.cache_config,
                                                      stats        = Schema__Cache__Stats())

        assert duration.seconds < 5               # server setup and start should not take more than 0.5 (locally takes about 0.25)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api_server.stop()


    def test__setUpClass(self):
        with self.cache_service as _:
            assert type(_) is Proxy__Cache__Service

            # Check OpenAPI spec
            open_api_json = obj(GET_json(self.server_url + '/openapi.json'))
            assert open_api_json.info.title == 'Service__Fast_API'
            assert '/{namespace}/retrieve/{cache_id}' in list_set(open_api_json.paths)                  # confirm the routes have been wired

            storage_info = GET_json(self.server_url + '/server/storage/info')                           # Verify we're using MEMORY storage mode
            assert storage_info == { 'storage_mode': 'memory',   'ttl_hours': 24 }

            assert self.cache_service__fast_api.cache_service.cache_config.storage_mode == Enum__Cache__Storage_Mode.MEMORY # Additional verification - check the actual cache service configuration

            storage_backend = self.cache_service__fast_api.cache_service.storage_backend()              # Verify storage backend type
            assert isinstance(storage_backend, Storage_FS__Memory)


    def test__url_to_cache_key(self):                          # Test URL to cache_key conversion
        with self.cache_service as _:
            # Basic URL
            cache_key = _.url_to_cache_key("https://example.com/articles/hello-world")
            assert cache_key == "sites/example.com/pages/articles/hello-world"

            # With query params (should be ignored)
            cache_key = _.url_to_cache_key("https://example.com/article?id=123&ref=twitter")
            assert cache_key == "sites/example.com/pages/article"

            # Homepage
            cache_key = _.url_to_cache_key("https://example.com")
            assert cache_key == "sites/example.com/pages/index"

            # With subdomain
            cache_key = _.url_to_cache_key("https://blog.example.com/post/2024/january")
            assert cache_key == "sites/blog.example.com/pages/post/2024/january"

            # With special characters (should be sanitized)
            cache_key = _.url_to_cache_key("https://example.com/articles/hello-world!@#$%")
            assert cache_key == "sites/example.com/pages/articles/hello-world-"

    def test__sanitize_url_path(self):                         # Test URL path sanitization
        with self.cache_service as _:
            # Basic alphanumeric
            assert _._sanitize_url_path("hello-world") == "hello-world"

            # With special characters
            assert _._sanitize_url_path("hello@world!test") == "hello-world-test"

            # With multiple consecutive special chars
            assert _._sanitize_url_path("hello!!!world") == "hello-world"

            # With forward slashes (should be preserved)
            assert _._sanitize_url_path("articles/2024/january") == "articles/2024/january"

    def test__get_or_create_page_entry(self):                  # Test page entry creation with KEY_BASED strategy
        with self.cache_service as _:
            url = "https://example.com/an-entry"
            # First call - creates page entry
            cache_id_1 = _.get_or_create_page_entry(url)
            assert cache_id_1 is not None
            assert len(cache_id_1) > 0

            # Verify in-memory mapping
            cache_key = _.url_to_cache_key(url)
            assert cache_key in _.cache_key_to_id
            assert _.cache_key_to_id[cache_key] == cache_id_1

            # Second call - returns same cache_id
            cache_id_2 = _.get_or_create_page_entry(url)
            assert cache_id_2 == cache_id_1

            # Stats should show one page cached
            assert _.stats.total_pages_cached >= 1

    def test__store_transformation(self):                      # Test storing WCF transformation as child data
        with self.cache_service as _:
            url = "https://example.com/test-page-2"
            wcf_command = "url-to-html"
            content = "<html><body><h1>Test Page</h1></body></html>"
            metadata = {
                "status_code": 200,
                "content_type": "text/html",
                "wcf_response_time_ms": 1234.5,
                "cached_at": "2024-10-10T12:00:00Z"
            }

            # Store transformation
            cache_id = _.store_transformation(
                target_url=url,
                wcf_command=wcf_command,
                content=content,
                metadata=metadata
            )

            assert cache_id is not None
            assert len(cache_id) > 0

    def test__get_cached_transformation(self):                 # Test retrieving cached transformation
        with self.cache_service as _:
            url = "https://example.com/test-page-3"
            wcf_command = "url-to-html"
            expected_content = "<html><body><h1>Cached Content</h1></body></html>"

            # First, store a transformation
            _.store_transformation(
                target_url=url,
                wcf_command=wcf_command,
                content=expected_content,
                metadata={"test": "metadata"}
            )

            # Then retrieve it
            cached_content = _.get_cached_transformation(url, wcf_command)

            assert cached_content is not None
            assert cached_content == expected_content

    def test__cache_miss(self):                                # Test cache miss scenario
        with self.cache_service as _:
            url = "https://example.com/non-existent-page"
            wcf_command = "url-to-html"

            # Try to get non-existent transformation
            cached_content = _.get_cached_transformation(url, wcf_command)

            assert cached_content is None

    def test__has_cached_transformation(self):                 # Test checking if transformation exists
        with self.cache_service as _:
            url = "https://example.com/test-page-6"
            wcf_command = "url-to-text"
            content = "Plain text content"

            # Before storing
            assert _.has_cached_transformation(url, wcf_command) == False

            # Store transformation
            _.store_transformation(url, wcf_command, content, {})

            # After storing
            assert _.has_cached_transformation(url, wcf_command) == True

    def test__multiple_transformations_per_page(self):         # Test multiple transformation types for same page
        with self.cache_service as _:
            url = "https://example.com/test-page-5"

            # Store HTML transformation
            html_content = "<html><body><h1>Test</h1></body></html>"
            _.store_transformation(url, "url-to-html", html_content, {})

            # Store text transformation
            text_content = "Test heading"
            _.store_transformation(url, "url-to-text", text_content, {})

            # Store ratings transformation
            ratings_content = '{"rating": "safe", "score": 0.95}'
            _.store_transformation(url, "url-to-ratings", ratings_content, {})

            # Retrieve all transformations
            html = _.get_cached_transformation(url, "url-to-html")
            text = _.get_cached_transformation(url, "url-to-text")
            ratings = _.get_cached_transformation(url, "url-to-ratings")

            assert html == html_content
            assert text == text_content
            assert ratings == str_to_json(ratings_content)

    def test__wcf_command_to_data_key(self):                   # Test WCF command to data_key conversion
        with self.cache_service as _:
            assert _._wcf_command_to_data_key("url-to-html") == "transformations/html"
            assert _._wcf_command_to_data_key("url-to-text") == "transformations/text"
            assert _._wcf_command_to_data_key("url-to-ratings") == "transformations/ratings"
            assert _._wcf_command_to_data_key("url-to-html-min-rating") == "transformations/html-filtered"

            # Unknown command - should use generic path
            assert _._wcf_command_to_data_key("unknown-command") == "transformations/unknown_command"

    def test__cache_statistics(self):                          # Test cache statistics tracking
        with self.cache_service as _:
            url = "https://example.com/test-page-6"
            wcf_command = "url-to-html"
            content = "<html><body>Test</body></html>"

            # Store transformation
            _.store_transformation(url, wcf_command, content, {})

            # First retrieval - cache hit
            _.get_cached_transformation(url, wcf_command)
            _.increment_cache_hit()

            # Check for non-existent transformation - cache miss
            _.get_cached_transformation("https://example.com/missing", wcf_command)
            _.increment_cache_miss()

            # Get statistics
            stats = _.get_cache_stats()

            assert stats["enabled"] == True
            assert stats["cache_hits"] > 0
            assert stats["cache_misses"] > 0
            assert stats["hit_rate"] > 0.0
            assert stats["wcf_calls_saved"] > 0

    def test__end_to_end_caching_flow(self):                   # Test complete caching flow (simulating WCF integration)
        with self.cache_service as _:
            url = "https://example.com/articles/end-to-end-test"
            wcf_command = "url-to-html"

            # Initial cache miss
            cached = _.get_cached_transformation(url, wcf_command)
            assert cached is None
            _.increment_cache_miss()

            # Simulate WCF call and cache result
            wcf_response = "<html><body><h1>Article Title</h1><p>Content...</p></body></html>"
            metadata = {
                "status_code": 200,
                "content_type": "text/html",
                "wcf_response_time_ms": 2345.6
            }

            _.store_transformation(url, wcf_command, wcf_response, metadata)

            # Subsequent request - cache hit
            cached = _.get_cached_transformation(url, wcf_command)
            assert cached is not None
            assert cached == wcf_response
            _.increment_cache_hit()

            # Verify statistics
            stats = _.get_cache_stats()
            assert stats["cache_misses"] >= 1
            assert stats["cache_hits"] >= 1


class test_Schema__Cache__Config(TestCase):

    def test__init__(self):                                     # Test cache config initialization
        with Schema__Cache__Config() as _:
            assert _.enabled == True
            assert _.base_url == "https://cache.dev.mgraph.ai"
            assert _.namespace == "wcf-results"
            assert _.timeout == 30
            assert _.strategy.value == "key_based"              # Verify KEY_BASED strategy
            assert _.data_file_id == "latest"
            assert _.cache_metadata == True
            assert _.track_stats == True


