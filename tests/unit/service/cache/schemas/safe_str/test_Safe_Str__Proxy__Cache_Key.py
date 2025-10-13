import re
import pytest
from unittest                                                                                   import TestCase
from osbot_utils.testing.__                                                                     import __
from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.utils.Objects                                                                  import base_types
from osbot_utils.type_safe.Type_Safe__Primitive                                                 import Type_Safe__Primitive
from osbot_utils.type_safe.primitives.core.Safe_Str                                             import Safe_Str
from osbot_utils.type_safe.primitives.core.enums.Enum__Safe_Str__Regex_Mode                     import Enum__Safe_Str__Regex_Mode
from mgraph_ai_service_mitmproxy.service.cache.schemas.safe_str.Safe_Str__Proxy__Cache_Key      import Safe_Str__Proxy__Cache_Key, TYPE_SAFE_STR__URL__MAX_LENGTH


class test_Safe_Str__Proxy__Cache_Key(TestCase):

    def test__init__(self):                                      # Test basic initialization and configuration
        with Safe_Str__Proxy__Cache_Key() as _:
            assert type(_)                is Safe_Str__Proxy__Cache_Key
            assert _.regex.pattern        == r'[^a-zA-Z0-9_.\-/]'
            assert _.regex_mode           == Enum__Safe_Str__Regex_Mode.REPLACE  # Default mode
            assert _.max_length           == TYPE_SAFE_STR__URL__MAX_LENGTH
            assert _.max_length           == 1024
            assert _.trim_whitespace      is True
            assert _.replacement_char     == '_'                 # Default Safe_Str replacement
            assert _.strict_validation    is False               # Default - allows replacement
            assert _.allow_empty          is True                # Default Safe_Str behavior

            # Empty initialization should be empty string
            assert str(_) == ''

    def test_valid_characters(self):                            # Test characters that pass through unchanged
        # Alphanumeric characters
        assert str(Safe_Str__Proxy__Cache_Key('abc123'        )) == 'abc123'
        assert str(Safe_Str__Proxy__Cache_Key('ABC123'        )) == 'ABC123'
        assert str(Safe_Str__Proxy__Cache_Key('AbC123XyZ'     )) == 'AbC123XyZ'
        assert str(Safe_Str__Proxy__Cache_Key('0123456789'    )) == '0123456789'

        # Allowed special characters: _ . - /
        assert str(Safe_Str__Proxy__Cache_Key('file_name'     )) == 'file_name'
        assert str(Safe_Str__Proxy__Cache_Key('file.txt'      )) == 'file.txt'
        assert str(Safe_Str__Proxy__Cache_Key('file-name'     )) == 'file-name'
        assert str(Safe_Str__Proxy__Cache_Key('path/to/file'  )) == 'path/to/file'

        # Combinations
        assert str(Safe_Str__Proxy__Cache_Key('api/v1/users_list.json'     )) == 'api/v1/users_list.json'
        assert str(Safe_Str__Proxy__Cache_Key('cache-key-123.data'         )) == 'cache-key-123.data'
        assert str(Safe_Str__Proxy__Cache_Key('proxy_cache/2024.01.15'     )) == 'proxy_cache/2024.01.15'
        assert str(Safe_Str__Proxy__Cache_Key('user-123/session_abc.json'  )) == 'user-123/session_abc.json'

    def test_invalid_character_replacement(self):              # Test REPLACE mode sanitization
        # Spaces replaced with underscore
        assert str(Safe_Str__Proxy__Cache_Key('hello world'           )) == 'hello_world'
        assert str(Safe_Str__Proxy__Cache_Key('cache key value'       )) == 'cache_key_value'

        # Special characters replaced
        assert str(Safe_Str__Proxy__Cache_Key('user@domain.com'       )) == 'user_domain.com'
        assert str(Safe_Str__Proxy__Cache_Key('key!value'             )) == 'key_value'
        assert str(Safe_Str__Proxy__Cache_Key('path\\to\\file'        )) == 'path_to_file'
        assert str(Safe_Str__Proxy__Cache_Key('data:value'            )) == 'data_value'
        assert str(Safe_Str__Proxy__Cache_Key('key=value'             )) == 'key_value'
        assert str(Safe_Str__Proxy__Cache_Key('key&value'             )) == 'key_value'
        assert str(Safe_Str__Proxy__Cache_Key('key?query'             )) == 'key_query'
        assert str(Safe_Str__Proxy__Cache_Key('key#fragment'          )) == 'key_fragment'
        assert str(Safe_Str__Proxy__Cache_Key('key[index]'            )) == 'key_index_'
        assert str(Safe_Str__Proxy__Cache_Key('key{value}'            )) == 'key_value_'
        assert str(Safe_Str__Proxy__Cache_Key('key<tag>'              )) == 'key_tag_'
        assert str(Safe_Str__Proxy__Cache_Key('key>value'             )) == 'key_value'

        # Multiple special characters
        assert str(Safe_Str__Proxy__Cache_Key('user@example!com'      )) == 'user_example_com'
        assert str(Safe_Str__Proxy__Cache_Key('path/to\\file:data'    )) == 'path/to_file_data'
        assert str(Safe_Str__Proxy__Cache_Key('key(value){data}'      )) == 'key_value__data_'

        # Unicode characters replaced
        assert str(Safe_Str__Proxy__Cache_Key('café'                  )) == 'caf_'
        assert str(Safe_Str__Proxy__Cache_Key('日本語'                   )) == '___'
        assert str(Safe_Str__Proxy__Cache_Key('emoji😀test'            )) == 'emoji_test'

    def test_proxy_cache_patterns(self):                        # Test realistic proxy cache key patterns
        # URL-like patterns (common in proxy caching)
        assert str(Safe_Str__Proxy__Cache_Key('api.example.com/v1/users'           )) == 'api.example.com/v1/users'
        assert str(Safe_Str__Proxy__Cache_Key('cdn.example.com/images/logo.png'    )) == 'cdn.example.com/images/logo.png'
        assert str(Safe_Str__Proxy__Cache_Key('api/users/123/profile'              )) == 'api/users/123/profile'

        # HTTP-like cache keys (with problematic chars replaced)
        assert str(Safe_Str__Proxy__Cache_Key('GET:api.example.com/users'          )) == 'GET_api.example.com/users'
        assert str(Safe_Str__Proxy__Cache_Key('POST:api.example.com/users?id=123'  )) == 'POST_api.example.com/users_id_123'
        assert str(Safe_Str__Proxy__Cache_Key('https://api.example.com/v1'         )) == 'https_//api.example.com/v1'

        # File-like cache keys
        assert str(Safe_Str__Proxy__Cache_Key('cache/user-123/session.json'        )) == 'cache/user-123/session.json'
        assert str(Safe_Str__Proxy__Cache_Key('temp/response_abc123.data'          )) == 'temp/response_abc123.data'
        assert str(Safe_Str__Proxy__Cache_Key('proxy_cache/2024-01-15/request.bin' )) == 'proxy_cache/2024-01-15/request.bin'

        # Versioned keys
        assert str(Safe_Str__Proxy__Cache_Key('api/v1.2.3/endpoint'                )) == 'api/v1.2.3/endpoint'
        assert str(Safe_Str__Proxy__Cache_Key('cache_v2/user_data.json'            )) == 'cache_v2/user_data.json'

    def test_whitespace_trimming(self):                         # Test whitespace trimming behavior
        # Leading/trailing whitespace trimmed
        assert str(Safe_Str__Proxy__Cache_Key('  cache-key  '      )) == 'cache-key'
        assert str(Safe_Str__Proxy__Cache_Key('\tcache-key\t'      )) == 'cache-key'
        assert str(Safe_Str__Proxy__Cache_Key('\ncache-key\n'      )) == 'cache-key'
        assert str(Safe_Str__Proxy__Cache_Key('  \t cache-key \n ' )) == 'cache-key'

        # Internal whitespace replaced
        assert str(Safe_Str__Proxy__Cache_Key('  cache key value  ')) == 'cache_key_value'
        assert str(Safe_Str__Proxy__Cache_Key('\tapi\tpath\t'      )) == 'api_path'

        # Multiple spaces collapsed to single underscore
        assert str(Safe_Str__Proxy__Cache_Key('cache    key'       )) == 'cache____key'
        assert str(Safe_Str__Proxy__Cache_Key('a  b   c    d'      )) == 'a__b___c____d'

    def test_max_length_enforcement(self):                      # Test max length constraint
        # At max length (1024) - should work
        key_at_max = 'a' * 1024
        result = Safe_Str__Proxy__Cache_Key(key_at_max)
        assert len(result) == 1024
        assert str(result) == key_at_max

        # Just under max length - should work
        key_under_max = 'a' * 1023
        result = Safe_Str__Proxy__Cache_Key(key_under_max)
        assert len(result) == 1023

        # Over max length - should raise exception
        error_message_1 = "in Safe_Str__Proxy__Cache_Key, value exceeds maximum length of 1024 characters (was 1025)"
        key_over_max = 'a' * 1025
        with pytest.raises(ValueError, match=re.escape(error_message_1)):
            Safe_Str__Proxy__Cache_Key(key_over_max)


        # Way over max length
        error_message_2 = "in Safe_Str__Proxy__Cache_Key, value exceeds maximum length of 1024 characters (was 2048)"
        key_way_over = 'a' * 2048
        with pytest.raises(ValueError, match=re.escape(error_message_2)):
            Safe_Str__Proxy__Cache_Key(key_way_over)


        # Max length with path structure
        error_message_3 = "in Safe_Str__Proxy__Cache_Key, value exceeds maximum length of 1024 characters (was 1415)"
        long_path = 'cache/' + 'subdir/' * 200 + 'file.json'
        with pytest.raises(ValueError, match=re.escape(error_message_3)):
            Safe_Str__Proxy__Cache_Key(long_path)

    def test_edge_cases(self):                                  # Test edge cases
        # Empty string
        assert str(Safe_Str__Proxy__Cache_Key('')   ) == ''
        assert str(Safe_Str__Proxy__Cache_Key(None) ) == ''

        # Whitespace only (trimmed to empty)
        assert str(Safe_Str__Proxy__Cache_Key('   ') ) == ''
        assert str(Safe_Str__Proxy__Cache_Key('\t\n')) == ''

        # All special characters (replaced)
        assert str(Safe_Str__Proxy__Cache_Key('!@#$%^&*()'   )) == '__________'
        assert str(Safe_Str__Proxy__Cache_Key('[]{}<>|\\"\';')) == '___________'

        # Only valid characters
        assert str(Safe_Str__Proxy__Cache_Key('abc123_.-/'   )) == 'abc123_.-/'

        # Single character
        assert str(Safe_Str__Proxy__Cache_Key('a'    )) == 'a'
        assert str(Safe_Str__Proxy__Cache_Key('_'    )) == '_'
        assert str(Safe_Str__Proxy__Cache_Key('.'    )) == '.'
        assert str(Safe_Str__Proxy__Cache_Key('-'    )) == '-'
        assert str(Safe_Str__Proxy__Cache_Key('/'    )) == '/'
        assert str(Safe_Str__Proxy__Cache_Key('@'    )) == '_'

        # Repeated characters
        assert str(Safe_Str__Proxy__Cache_Key('______'       )) == '______'
        assert str(Safe_Str__Proxy__Cache_Key('......'       )) == '......'
        assert str(Safe_Str__Proxy__Cache_Key('------'       )) == '------'
        assert str(Safe_Str__Proxy__Cache_Key('//////'       )) == '//////'

    def test_type_conversion(self):                             # Test conversion from other types
        # From integer
        assert str(Safe_Str__Proxy__Cache_Key(123           )) == '123'
        assert str(Safe_Str__Proxy__Cache_Key(0             )) == '0'
        assert str(Safe_Str__Proxy__Cache_Key(999999        )) == '999999'

        # From float (decimal point is valid)
        assert str(Safe_Str__Proxy__Cache_Key(123.45        )) == '123.45'
        assert str(Safe_Str__Proxy__Cache_Key(0.5           )) == '0.5'

        # From boolean
        assert str(Safe_Str__Proxy__Cache_Key(True          )) == 'True'
        assert str(Safe_Str__Proxy__Cache_Key(False         )) == 'False'

        # From another Safe_Str
        other = Safe_Str('cache-key')
        assert str(other)                                      == 'cache_key'       # Safe_Str will convert - to _
        assert str(Safe_Str__Proxy__Cache_Key(other         )) == 'cache_key'

    def test_in_type_safe_schema(self):                         # Test usage in Type_Safe classes
        class Schema__Proxy__Cache(Type_Safe):
            primary_key   : Safe_Str__Proxy__Cache_Key
            secondary_key : Safe_Str__Proxy__Cache_Key = None
            lookup_key    : Safe_Str__Proxy__Cache_Key

        with Schema__Proxy__Cache() as _:
            # Auto-initialization to empty string
            assert type(_.primary_key) is Safe_Str__Proxy__Cache_Key
            assert type(_.lookup_key ) is Safe_Str__Proxy__Cache_Key
            assert _.primary_key      == ''
            assert _.lookup_key       == ''
            assert _.secondary_key    is None

            # Setting with raw strings (auto-sanitization)
            _.primary_key = 'api/users/123'
            assert _.primary_key == 'api/users/123'

            # Setting with problematic characters (auto-replaced)
            _.lookup_key = 'GET:api.example.com/users?id=123'
            assert _.lookup_key == 'GET_api.example.com/users_id_123'

            # Setting nullable field
            _.secondary_key = 'cache/backup-key.json'
            assert _.secondary_key == 'cache/backup-key.json'

            # Verify .obj() comparison
            assert _.obj() == __(primary_key   = 'api/users/123'                        ,
                                 secondary_key = 'cache/backup-key.json'                ,
                                 lookup_key    = 'GET_api.example.com/users_id_123'    )

    def test_json_serialization(self):                          # Test JSON round-trip
        class Schema__Cache__Config(Type_Safe):
            cache_key : Safe_Str__Proxy__Cache_Key
            path      : Safe_Str__Proxy__Cache_Key

        with Schema__Cache__Config() as _:
            _.cache_key = 'api/v1/users'
            _.path      = 'cache/data/response.json'

            # JSON serialization
            json_data = _.json()
            assert json_data == { 'cache_key': 'api/v1/users'          ,
                                  'path'     : 'cache/data/response.json' }

            # Round trip
            restored = Schema__Cache__Config.from_json(json_data)
            assert restored.obj() == _.obj()
            assert type(restored.cache_key) is Safe_Str__Proxy__Cache_Key
            assert type(restored.path)      is Safe_Str__Proxy__Cache_Key

    def test_inheritance(self):                                 # Test Safe_Str inheritance
        key = Safe_Str__Proxy__Cache_Key('api/cache-key')

        # Should inherit from Safe_Str
        assert isinstance(key, Safe_Str__Proxy__Cache_Key)
        assert isinstance(key, Safe_Str)
        assert isinstance(key, str)

        # Check base types
        assert base_types(key) == [Safe_Str, Type_Safe__Primitive, str, object, object]

        # Should have Safe_Str attributes
        assert hasattr(key, 'regex')
        assert hasattr(key, 'regex_mode')
        assert hasattr(key, 'max_length')
        assert hasattr(key, 'trim_whitespace')

    def test_string_operations(self):                           # Test string behavior
        key = Safe_Str__Proxy__Cache_Key('api/users')

        # String concatenation
        result = key + '/123'
        assert type(result) is Safe_Str__Proxy__Cache_Key       # Type preserved
        assert str(result)  == 'api/users/123'

        # Concatenation with special chars (get replaced)
        result = key + '?id=456'
        assert str(result) == 'api/users_id_456'

        # String formatting
        assert f"Key: {key}"         == "Key: api/users"
        assert "Key: {}".format(key) == "Key: api/users"

        # Length
        assert len(key) == 9

        # Indexing
        assert key[0] == 'a'
        assert key[4] == 'u'

        # Slicing
        assert key[:3]  == 'api'
        assert key[4:]  == 'users'

    def test_comparison_operations(self):                       # Test comparisons
        key1 = Safe_Str__Proxy__Cache_Key('api/users')
        key2 = Safe_Str__Proxy__Cache_Key('api/users')
        key3 = Safe_Str__Proxy__Cache_Key('api/posts')

        # Equality
        assert key1 == key2
        assert key1 == 'api/users'
        assert 'api/users' == key1

        # Inequality
        assert key1 != key3
        assert key1 != 'api/posts'

        # Ordering (lexicographic)
        assert key3 < key1                                      # 'posts' < 'users'
        assert key1 > key3
        assert key1 <= key2
        assert key1 >= key2

    def test_repr_and_str(self):                                # Test string representations
        key = Safe_Str__Proxy__Cache_Key('api/cache-key')

        assert str(key)  == 'api/cache-key'
        assert repr(key) == "Safe_Str__Proxy__Cache_Key('api/cache-key')"

        # Empty key
        empty = Safe_Str__Proxy__Cache_Key('')
        assert str(empty)  == ''
        assert repr(empty) == "Safe_Str__Proxy__Cache_Key('')"

        # Key with sanitized characters
        sanitized = Safe_Str__Proxy__Cache_Key('key with spaces')
        assert str(sanitized)  == 'key_with_spaces'
        assert repr(sanitized) == "Safe_Str__Proxy__Cache_Key('key_with_spaces')"

    def test_use_as_dict_key(self):                             # Test hashability for dict keys
        key1 = Safe_Str__Proxy__Cache_Key('api/users')
        key2 = Safe_Str__Proxy__Cache_Key('api/posts')

        # Should work as dict keys
        cache_map = {
            key1: 'users_data',
            key2: 'posts_data'
        }

        assert cache_map[key1] == 'users_data'
        assert cache_map[key2] == 'posts_data'
        assert len(cache_map)  == 2

        # Same value should map to same key
        key3 = Safe_Str__Proxy__Cache_Key('api/users')
        cache_map[key3] = 'updated_users_data'
        assert len(cache_map)   == 2                            # Still 2, not 3
        assert cache_map[key1]  == 'updated_users_data'         # Overwritten

    def test_regex_mode_replace(self):                          # Test REPLACE mode specifically
        # REPLACE mode transforms input by replacing invalid chars
        assert Safe_Str__Proxy__Cache_Key.regex_mode == Enum__Safe_Str__Regex_Mode.REPLACE

        # Verify replacement happens, not validation error
        key = Safe_Str__Proxy__Cache_Key('hello@world')
        assert str(key) == 'hello_world'                        # Replaced, not error

        # Multiple replacements
        key = Safe_Str__Proxy__Cache_Key('user@example.com/data')
        assert str(key) == 'user_example.com/data'

        # This differs from MATCH mode which would raise ValueError
        # REPLACE mode is safer for proxy cache keys where we want
        # to sanitize arbitrary input rather than reject it

    def test_path_like_patterns(self):                          # Test file/URL path patterns
        # Unix-style paths
        assert str(Safe_Str__Proxy__Cache_Key('/var/cache/proxy'                )) == '/var/cache/proxy'
        assert str(Safe_Str__Proxy__Cache_Key('cache/user/session'              )) == 'cache/user/session'
        assert str(Safe_Str__Proxy__Cache_Key('./relative/path'                 )) == './relative/path'
        assert str(Safe_Str__Proxy__Cache_Key('../parent/path'                  )) == '../parent/path'

        # URL-style paths
        assert str(Safe_Str__Proxy__Cache_Key('api.example.com/v1/resource'     )) == 'api.example.com/v1/resource'
        assert str(Safe_Str__Proxy__Cache_Key('cdn.example.com/static/image.jpg')) == 'cdn.example.com/static/image.jpg'

        # Mixed separators (backslash replaced)
        assert str(Safe_Str__Proxy__Cache_Key('path\\to\\file'                  )) == 'path_to_file'
        assert str(Safe_Str__Proxy__Cache_Key('C:\\Windows\\System32'           )) == 'C__Windows_System32'

        # Query strings (special chars replaced)
        assert str(Safe_Str__Proxy__Cache_Key('api/users?id=123&name=test'      )) == 'api/users_id_123_name_test'
        assert str(Safe_Str__Proxy__Cache_Key('search?q=hello+world'            )) == 'search_q_hello_world'

    def test_realistic_proxy_scenarios(self):                   # Test real-world proxy cache use cases
        # HTTP method + URL pattern
        get_users = 'GET_api.example.com/users'
        assert str(Safe_Str__Proxy__Cache_Key(get_users)) == get_users

        # With query params (sanitized)
        get_user = Safe_Str__Proxy__Cache_Key('GET:api.example.com/users?id=123')
        assert str(get_user) == 'GET_api.example.com/users_id_123'

        # POST with body hash
        post_create = 'POST_api.example.com/users_body_abc123def456'
        assert str(Safe_Str__Proxy__Cache_Key(post_create)) == post_create

        # CDN cache keys
        cdn_image = 'cdn.example.com/images/user-avatar-123.png'
        assert str(Safe_Str__Proxy__Cache_Key(cdn_image)) == cdn_image

        # Versioned API endpoints
        api_v1 = 'api/v1.2.3/users/profile'
        assert str(Safe_Str__Proxy__Cache_Key(api_v1)) == api_v1

        # Cache with timestamp
        timed_cache = 'cache/2024-01-15/user-123/session.data'
        assert str(Safe_Str__Proxy__Cache_Key(timed_cache)) == timed_cache

        # Nested resource paths
        nested = 'api/organizations/123/projects/456/issues/789'
        assert str(Safe_Str__Proxy__Cache_Key(nested)) == nested

    def test_allowed_special_chars_explicitly(self):            # Test each allowed special char individually
        # Underscore
        assert str(Safe_Str__Proxy__Cache_Key('hello_world'     )) == 'hello_world'
        assert str(Safe_Str__Proxy__Cache_Key('___'             )) == '___'

        # Period/Dot
        assert str(Safe_Str__Proxy__Cache_Key('file.txt'        )) == 'file.txt'
        assert str(Safe_Str__Proxy__Cache_Key('...'             )) == '...'
        assert str(Safe_Str__Proxy__Cache_Key('api.v1.users'    )) == 'api.v1.users'

        # Hyphen/Dash
        assert str(Safe_Str__Proxy__Cache_Key('cache-key'       )) == 'cache-key'
        assert str(Safe_Str__Proxy__Cache_Key('---'             )) == '---'
        assert str(Safe_Str__Proxy__Cache_Key('user-id-123'     )) == 'user-id-123'

        # Forward slash
        assert str(Safe_Str__Proxy__Cache_Key('path/to/file'    )) == 'path/to/file'
        assert str(Safe_Str__Proxy__Cache_Key('///'             )) == '///'
        assert str(Safe_Str__Proxy__Cache_Key('/api/v1/users/'  )) == '/api/v1/users/'

        # All together
        assert str(Safe_Str__Proxy__Cache_Key('api_v1.users/cache-key')) == 'api_v1.users/cache-key'