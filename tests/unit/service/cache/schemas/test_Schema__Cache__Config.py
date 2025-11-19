from unittest                                                                import TestCase
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Config import Schema__Cache__Config


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
