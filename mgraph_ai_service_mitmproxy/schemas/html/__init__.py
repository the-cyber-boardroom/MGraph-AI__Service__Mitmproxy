from unittest                                                                      import TestCase
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode

class test_Enum__HTML__Transformation_Mode(TestCase):

    def test__enum_values(self):                                                    # Test all enum values exist
        assert Enum__HTML__Transformation_Mode.OFF.value        == "off"
        assert Enum__HTML__Transformation_Mode.DICT.value       == "dict"
        assert Enum__HTML__Transformation_Mode.XXX.value        == "xxx"
        assert Enum__HTML__Transformation_Mode.HASHES.value     == "hashes"
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.value  == "roundtrip"

    def test_from_cookie_value(self):                                               # Test cookie value parsing
        assert Enum__HTML__Transformation_Mode.from_cookie_value("off")        == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value("dict")       == Enum__HTML__Transformation_Mode.DICT
        assert Enum__HTML__Transformation_Mode.from_cookie_value("xxx")        == Enum__HTML__Transformation_Mode.XXX
        assert Enum__HTML__Transformation_Mode.from_cookie_value("hashes")     == Enum__HTML__Transformation_Mode.HASHES
        assert Enum__HTML__Transformation_Mode.from_cookie_value("roundtrip")  == Enum__HTML__Transformation_Mode.ROUNDTRIP

    def test_from_cookie_value__case_insensitive(self):                             # Test case insensitive parsing
        assert Enum__HTML__Transformation_Mode.from_cookie_value("OFF")        == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value("DICT")       == Enum__HTML__Transformation_Mode.DICT
        assert Enum__HTML__Transformation_Mode.from_cookie_value("Xxx")        == Enum__HTML__Transformation_Mode.XXX
        assert Enum__HTML__Transformation_Mode.from_cookie_value("HaShEs")     == Enum__HTML__Transformation_Mode.HASHES
        assert Enum__HTML__Transformation_Mode.from_cookie_value("RoundTrip")  == Enum__HTML__Transformation_Mode.ROUNDTRIP

    def test_from_cookie_value__with_whitespace(self):                              # Test parsing with whitespace
        assert Enum__HTML__Transformation_Mode.from_cookie_value("  off  ")    == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value(" dict ")     == Enum__HTML__Transformation_Mode.DICT
        assert Enum__HTML__Transformation_Mode.from_cookie_value("xxx\t")      == Enum__HTML__Transformation_Mode.XXX

    def test_from_cookie_value__empty_or_invalid(self):                             # Test empty or invalid values default to OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value("")           == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value(None)         == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value("invalid")    == Enum__HTML__Transformation_Mode.OFF
        assert Enum__HTML__Transformation_Mode.from_cookie_value("unknown")    == Enum__HTML__Transformation_Mode.OFF

    def test_is_active(self):                                                       # Test is_active method
        assert Enum__HTML__Transformation_Mode.OFF.is_active()       is False      # OFF is not active
        assert Enum__HTML__Transformation_Mode.DICT.is_active()      is True       # All others are active
        assert Enum__HTML__Transformation_Mode.XXX.is_active()       is True
        assert Enum__HTML__Transformation_Mode.HASHES.is_active()    is True
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.is_active() is True

    def test_requires_caching(self):                                                # Test caching requirement
        assert Enum__HTML__Transformation_Mode.OFF.requires_caching()       is False
        assert Enum__HTML__Transformation_Mode.DICT.requires_caching()      is True
        assert Enum__HTML__Transformation_Mode.XXX.requires_caching()       is True
        assert Enum__HTML__Transformation_Mode.HASHES.requires_caching()    is True
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.requires_caching() is True

    def test_to_endpoint_path(self):                                                # Test endpoint path generation
        assert Enum__HTML__Transformation_Mode.OFF.to_endpoint_path()       == ""
        assert Enum__HTML__Transformation_Mode.DICT.to_endpoint_path()      == "/html/to/tree/view"
        assert Enum__HTML__Transformation_Mode.XXX.to_endpoint_path()       == "/html/to/html/xxx"
        assert Enum__HTML__Transformation_Mode.HASHES.to_endpoint_path()    == "/html/to/html/hashes"
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.to_endpoint_path() == "/html/to/html"

    def test_to_content_type(self):                                                 # Test content type generation
        assert Enum__HTML__Transformation_Mode.OFF.to_content_type()       == "text/html"
        assert Enum__HTML__Transformation_Mode.DICT.to_content_type()      == "text/plain"    # Tree view is plain text
        assert Enum__HTML__Transformation_Mode.XXX.to_content_type()       == "text/html"
        assert Enum__HTML__Transformation_Mode.HASHES.to_content_type()    == "text/html"
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.to_content_type() == "text/html"

    def test_to_cache_data_key(self):                                               # Test cache data key generation
        assert Enum__HTML__Transformation_Mode.OFF.to_cache_data_key()       == ""
        assert Enum__HTML__Transformation_Mode.DICT.to_cache_data_key()      == "transformations/html-dict"
        assert Enum__HTML__Transformation_Mode.XXX.to_cache_data_key()       == "transformations/html-xxx"
        assert Enum__HTML__Transformation_Mode.HASHES.to_cache_data_key()    == "transformations/html-hashes"
        assert Enum__HTML__Transformation_Mode.ROUNDTRIP.to_cache_data_key() == "transformations/html-roundtrip"

    def test__all_modes_complete(self):                                             # Test all modes have complete configuration
        for mode in Enum__HTML__Transformation_Mode:
            if mode.is_active():
                assert mode.to_endpoint_path()   != ""                              # Active modes must have endpoint
                assert mode.to_content_type()    != ""                              # Active modes must have content type
                assert mode.to_cache_data_key()  != ""                              # Active modes must have cache key
            else:
                assert mode == Enum__HTML__Transformation_Mode.OFF                  # Only OFF should be inactive