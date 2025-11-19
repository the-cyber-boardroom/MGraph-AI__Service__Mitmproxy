from unittest                                                               import TestCase
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Stats import Schema__Cache__Stats


class test_Schema__Cache__Stats(TestCase):

    def test__init__(self):                                     # Test cache stats initialization
        with Schema__Cache__Stats() as _:
            assert _.enabled == True
            assert _.cache_hits == 0
            assert _.cache_misses == 0
            assert _.wcf_calls_saved == 0
            assert _.total_pages_cached == 0


    def test__hit_rate(self):                                   # Test hit rate calculation
        with Schema__Cache__Stats() as _:
            # No hits or misses - should return 0.0
            assert _.hit_rate() == 0.0

            # 80% hit rate
            _.cache_hits = 80
            _.cache_misses = 20
            assert _.hit_rate() == 0.8

            # 100% hit rate
            _.cache_hits = 100
            _.cache_misses = 0
            assert _.hit_rate() == 1.0

    def test__estimated_time_saved_seconds(self):               # Test time saved estimation
        with Schema__Cache__Stats() as _:
            # No cache hits - should return 0.0
            assert _.estimated_time_saved_seconds() == 0.0

            # With cache hits
            _.cache_hits = 100
            _.avg_cache_hit_time_ms = 50.0                      # 50ms average cache hit time

            saved = _.estimated_time_saved_seconds()
            assert saved > 0.0
            # Assuming average WCF call is 2 seconds:
            # (100 hits * 2s) - (100 hits * 0.05s) = 200s - 5s = 195s
            assert abs(saved - 195.0) < 1.0                     # Allow small floating point difference