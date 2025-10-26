from unittest                                                                      import TestCase
from osbot_utils.testing.__                                                        import __
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.utils.Objects                                                     import base_classes
from osbot_utils.type_safe.primitives.core.Safe_Float                              import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Transformation__Result import Schema__HTML__Transformation__Result
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode

class test_Schema__HTML__Transformation__Result(TestCase):

    def test__init__(self):                                                         # Test auto-initialization
        with Schema__HTML__Transformation__Result() as _:
            assert type(_)                        is Schema__HTML__Transformation__Result
            assert base_classes(_)                == [Type_Safe, object]
            assert _.transformed_html             == ""
            assert _.transformation_mode          is None
            assert _.content_type                 == ""
            assert _.cache_hit                    is False
            assert type(_.transformation_time_ms) is Safe_Float
            assert _.transformation_time_ms       == 0.0

    def test__init__with_cache_hit(self):                                           # Test initialization with cache hit
        html = "<html>cached</html>"

        with Schema__HTML__Transformation__Result(transformed_html    = html                                   ,
                                                   transformation_mode = Enum__HTML__Transformation_Mode.HASHES ,
                                                   content_type        = "text/html"                            ,
                                                   cache_hit           = True                                   ) as _:
            assert _.transformed_html       == html
            assert _.transformation_mode    == Enum__HTML__Transformation_Mode.HASHES
            assert _.cache_hit              is True
            assert _.transformation_time_ms == 0.0                                  # Cache hits have 0 time

    def test__init__with_cache_miss(self):                                          # Test initialization with cache miss
        html = "<html>fresh</html>"

        with Schema__HTML__Transformation__Result(transformed_html       = html                                   ,
                                                   transformation_mode    = Enum__HTML__Transformation_Mode.XXX    ,
                                                   content_type           = "text/html"                            ,
                                                   cache_hit              = False                                  ,
                                                   transformation_time_ms = Safe_Float(125.5)                      ) as _:
            assert _.transformed_html       == html
            assert _.cache_hit              is False
            assert _.transformation_time_ms == 125.5

    def test_was_cached(self):                                                      # Test was_cached method
        with Schema__HTML__Transformation__Result(cache_hit=True) as _:
            assert _.was_cached() is True

        with Schema__HTML__Transformation__Result(cache_hit=False) as _:
            assert _.was_cached() is False

    def test_to_headers(self):                                                      # Test HTTP headers generation
        with Schema__HTML__Transformation__Result(transformed_html       = "<html>test</html>"                  ,
                                                   transformation_mode    = Enum__HTML__Transformation_Mode.HASHES,
                                                   content_type           = "text/html"                           ,
                                                   cache_hit              = True                                  ,
                                                   transformation_time_ms = Safe_Float(50.0)                      ) as _:
            headers = _.to_headers()

            assert type(headers) is dict
            assert headers["x-proxy-transformation"] == "hashes"
            assert headers["x-proxy-cache"]          == "hit"
            assert headers["x-html-service-time"]    == "50.0ms"
            assert headers["content-type"]           == "text/html"

    def test_to_headers__cache_miss(self):                                          # Test headers with cache miss
        with Schema__HTML__Transformation__Result(transformation_mode    = Enum__HTML__Transformation_Mode.DICT,
                                                   content_type           = "text/plain"                         ,
                                                   cache_hit              = False                                ,
                                                   transformation_time_ms = Safe_Float(234.7)                    ) as _:
            headers = _.to_headers()

            assert headers["x-proxy-transformation"] == "dict"
            assert headers["x-proxy-cache"]          == "miss"
            assert headers["x-html-service-time"]    == "234.7ms"
            assert headers["content-type"]           == "text/plain"

    def test_to_headers__different_modes(self):                                     # Test headers for all transformation modes
        modes_and_content_types = [
            (Enum__HTML__Transformation_Mode.OFF      , "text/html"  ),
            (Enum__HTML__Transformation_Mode.DICT     , "text/plain" ),
            (Enum__HTML__Transformation_Mode.XXX      , "text/html"  ),
            (Enum__HTML__Transformation_Mode.HASHES   , "text/html"  ),
            (Enum__HTML__Transformation_Mode.ROUNDTRIP, "text/html"  ),
        ]

        for mode, content_type in modes_and_content_types:
            with Schema__HTML__Transformation__Result(transformation_mode = mode        ,
                                                       content_type        = content_type) as _:
                headers = _.to_headers()

                assert headers["x-proxy-transformation"] == mode.value
                assert headers["content-type"]           == content_type

    def test__transformation_time_auto_conversion(self):                            # Test transformation time auto-conversion
        with Schema__HTML__Transformation__Result(transformation_time_ms=100) as _:
            assert type(_.transformation_time_ms) is Safe_Float
            assert _.transformation_time_ms       == 100.0

        with Schema__HTML__Transformation__Result(transformation_time_ms=12.345) as _:
            assert type(_.transformation_time_ms) is Safe_Float
            assert _.transformation_time_ms       == 12.345

    def test__obj__comparison(self):                                                # Test .obj() method for comprehensive comparison
        html = "<html>transformed</html>"

        with Schema__HTML__Transformation__Result(transformed_html       = html                                   ,
                                                   transformation_mode    = Enum__HTML__Transformation_Mode.XXX    ,
                                                   content_type           = "text/html"                            ,
                                                   cache_hit              = False                                  ,
                                                   transformation_time_ms = Safe_Float(75.5)                       ) as _:
            assert _.obj() == __(transformed_html       = html                                   ,
                                 transformation_mode    = Enum__HTML__Transformation_Mode.XXX    ,
                                 content_type           = "text/html"                            ,
                                 cache_hit              = False                                  ,
                                 transformation_time_ms = Safe_Float(75.5)                       )