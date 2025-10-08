from unittest                                                                    import TestCase
from osbot_utils.utils.Objects                                                      import base_classes, __
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service               import Proxy__Cookie__Service
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type              import Enum__WCF__Command_Type


class test_Proxy__Cookie__Service(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cookie_service = Proxy__Cookie__Service()                                          # Reusable service instance

        cls.test_headers_basic = {                                                             # Test data: basic cookies
            'cookie': 'mitm-show=url-to-html; mitm-debug=true'
        }

        cls.test_headers_full = {                                                              # Test data: all cookie types
            'cookie': 'mitm-show=url-to-html-xxx; mitm-inject=debug-panel; mitm-replace=Hello:Hi; mitm-debug=true; mitm-rating=0.5; mitm-model=gpt-4; mitm-cache=true'
        }

        cls.test_headers_wcf = {                                                               # Test data: WCF commands
            'cookie': 'mitm-show=url-to-html-min-rating; mitm-rating=0.7'
        }

        cls.test_headers_empty = {}                                                            # Test data: no cookies

        cls.test_headers_non_proxy = {                                                         # Test data: non-proxy cookies
            'cookie': 'session=abc123; user=john; theme=dark'
        }

    def test__init__(self):                                                                    # Test auto-initialization of Proxy__Cookie__Service
        with Proxy__Cookie__Service() as _:
            assert type(_)         is Proxy__Cookie__Service
            assert base_classes(_) == [Proxy__Cookie__Service.__bases__[0], object]

            assert _.obj() == __(COOKIE_PREFIX = 'mitm-'             ,
                                COOKIE_SHOW    = 'mitm-show'         ,
                                COOKIE_INJECT  = 'mitm-inject'       ,
                                COOKIE_REPLACE = 'mitm-replace'      ,
                                COOKIE_DEBUG   = 'mitm-debug'        ,
                                COOKIE_RATING  = 'mitm-rating'       ,
                                COOKIE_MODEL   = 'mitm-model'        ,
                                COOKIE_CACHE   = 'mitm-cache'        )

    def test_parse_cookies(self):                                                             # Test basic cookie parsing
        with self.cookie_service as _:
            cookies = _.parse_cookies(self.test_headers_basic)

            assert type(cookies)       is dict
            assert len(cookies)        == 2
            assert cookies['mitm-show']  == 'url-to-html'
            assert cookies['mitm-debug'] == 'true'

    def test_parse_cookies__empty_headers(self):                                              # Test parsing with no cookie header
        with self.cookie_service as _:
            cookies = _.parse_cookies(self.test_headers_empty)

            assert cookies == {}
            assert len(cookies) == 0

    def test_parse_cookies__case_insensitive(self):                                           # Test cookie header case insensitivity
        with self.cookie_service as _:
            headers_upper = {'Cookie': 'mitm-show=url-to-text'}                              # Uppercase Cookie header
            headers_lower = {'cookie': 'mitm-show=url-to-text'}                              # Lowercase cookie header

            cookies_upper = _.parse_cookies(headers_upper)
            cookies_lower = _.parse_cookies(headers_lower)

            assert cookies_upper == cookies_lower
            assert cookies_upper['mitm-show'] == 'url-to-text'

    def test_get_proxy_cookies(self):                                                         # Test filtering for mitm-* cookies only
        with self.cookie_service as _:
            mixed_headers = {
                'cookie': 'mitm-show=url-to-html; session=xyz; mitm-debug=true; user=john; mitm-cache=true'
            }

            proxy_cookies = _.get_proxy_cookies(mixed_headers)

            assert len(proxy_cookies) == 3
            assert 'mitm-show'  in proxy_cookies
            assert 'mitm-debug' in proxy_cookies
            assert 'mitm-cache' in proxy_cookies
            assert 'session'    not in proxy_cookies                                          # Non-proxy cookie filtered out
            assert 'user'       not in proxy_cookies                                          # Non-proxy cookie filtered out

    def test_get_proxy_cookies__only_non_proxy(self):                                         # Test when only non-proxy cookies present
        with self.cookie_service as _:
            proxy_cookies = _.get_proxy_cookies(self.test_headers_non_proxy)

            assert proxy_cookies == {}
            assert len(proxy_cookies) == 0

    def test_get_show_command(self):                                                          # Test extracting show command
        with self.cookie_service as _:
            show_cmd = _.get_show_command(self.test_headers_basic)

            assert show_cmd == 'url-to-html'
            assert type(show_cmd) is str

    def test_get_show_command__not_present(self):                                             # Test when show command absent
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-debug=true'}
            show_cmd = _.get_show_command(headers)

            assert show_cmd is None

    def test_get_inject_command(self):                                                        # Test extracting inject command
        with self.cookie_service as _:
            inject_cmd = _.get_inject_command(self.test_headers_full)

            assert inject_cmd == 'debug-panel'

    def test_get_inject_command__not_present(self):                                           # Test when inject command absent
        with self.cookie_service as _:
            inject_cmd = _.get_inject_command(self.test_headers_basic)

            assert inject_cmd is None

    def test_get_replace_command(self):                                                       # Test extracting replace command
        with self.cookie_service as _:
            replace_cmd = _.get_replace_command(self.test_headers_full)

            assert replace_cmd == 'Hello:Hi'

    def test_get_replace_command__not_present(self):                                          # Test when replace command absent
        with self.cookie_service as _:
            replace_cmd = _.get_replace_command(self.test_headers_basic)

            assert replace_cmd is None

    def test_is_debug_enabled(self):                                                          # Test debug mode detection
        with self.cookie_service as _:
            assert _.is_debug_enabled(self.test_headers_basic) is True
            assert _.is_debug_enabled(self.test_headers_empty) is False

    def test_is_debug_enabled__various_true_values(self):                                     # Test different ways to enable debug
        with self.cookie_service as _:
            test_cases = [
                ('true',  True ),
                ('1',     True ),
                ('yes',   True ),
                ('on',    True ),
                ('True',  True ),                                                              # Uppercase
                ('TRUE',  True ),                                                              # All caps
                ('false', False),
                ('0',     False),
                ('no',    False),
                ('off',   False),
            ]

            for value, expected in test_cases:
                headers = {'cookie': f'mitm-debug={value}'}
                result = _.is_debug_enabled(headers)
                assert result is expected, f"Failed for value: {value}"

    def test_get_rating(self):                                                                # Test rating extraction
        with self.cookie_service as _:
            rating = _.get_rating(self.test_headers_full)

            assert rating == 0.5
            assert type(rating) is float

    def test_get_rating__not_present(self):                                                   # Test when rating absent
        with self.cookie_service as _:
            rating = _.get_rating(self.test_headers_basic)

            assert rating is None

    def test_get_rating__invalid_format(self):                                                # Test invalid rating format
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-rating=not-a-number'}
            rating = _.get_rating(headers)

            assert rating is None                                                              # Returns None for invalid

    def test_get_rating__various_formats(self):                                               # Test different rating formats
        with self.cookie_service as _:
            test_cases = [
                ('0.5',   0.5  ),
                ('0.75',  0.75 ),
                ('1.0',   1.0  ),
                ('0',     0.0  ),
                ('1',     1.0  ),
                ('.5',    0.5  ),
                ('0.999', 0.999),
            ]

            for value, expected in test_cases:
                headers = {'cookie': f'mitm-rating={value}'}
                result = _.get_rating(headers)
                assert result == expected, f"Failed for value: {value}"

    def test_get_model_override(self):                                                        # Test model override extraction
        with self.cookie_service as _:
            model = _.get_model_override(self.test_headers_full)

            assert model == 'gpt-4'
            assert type(model) is str

    def test_get_model_override__not_present(self):                                           # Test when model override absent
        with self.cookie_service as _:
            model = _.get_model_override(self.test_headers_basic)

            assert model is None

    def test_is_cache_enabled(self):                                                          # Test cache detection
        with self.cookie_service as _:
            assert _.is_cache_enabled(self.test_headers_full)  is True
            assert _.is_cache_enabled(self.test_headers_basic) is False

    def test_is_cache_enabled__various_values(self):                                          # Test different cache enable values
        with self.cookie_service as _:
            true_values  = ['true', '1', 'yes', 'on', 'True', 'TRUE']
            false_values = ['false', '0', 'no', 'off', '', 'invalid']

            for value in true_values:
                headers = {'cookie': f'mitm-cache={value}'}
                assert _.is_cache_enabled(headers) is True, f"Failed for: {value}"

            for value in false_values:
                headers = {'cookie': f'mitm-cache={value}'}
                assert _.is_cache_enabled(headers) is False, f"Failed for: {value}"

    def test_is_wcf_show_command(self):                                                       # Test WCF command detection
        with self.cookie_service as _:
            assert _.is_wcf_show_command(self.test_headers_basic) is True                    # url-to-html is WCF
            assert _.is_wcf_show_command(self.test_headers_empty) is False                   # No command

    def test_is_wcf_show_command__all_wcf_types(self):                                        # Test all WCF command types
        with self.cookie_service as _:
            wcf_commands = [
                'url-to-html',
                'url-to-html-xxx',
                'url-to-html-min-rating',
                'url-to-ratings',
                'url-to-text-nodes',
                'url-to-lines',
                'url-to-text',
            ]

            for command in wcf_commands:
                headers = {'cookie': f'mitm-show={command}'}
                result = _.is_wcf_show_command(headers)
                assert result is True, f"Failed to detect WCF command: {command}"

    def test_is_wcf_show_command__non_wcf(self):                                              # Test non-WCF commands
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=response-data'}
            result = _.is_wcf_show_command(headers)

            assert result is False                                                             # response-data is not WCF

    def test_get_wcf_command_type(self):                                                      # Test WCF command type parsing
        with self.cookie_service as _:
            cmd_type = _.get_wcf_command_type(self.test_headers_basic)

            assert cmd_type == Enum__WCF__Command_Type.url_to_html
            assert type(cmd_type).__name__ == 'Enum__WCF__Command_Type'

    def test_get_wcf_command_type__all_types(self):                                           # Test parsing all WCF command types
        with self.cookie_service as _:
            test_cases = [
                ('url-to-html',            Enum__WCF__Command_Type.url_to_html           ),
                ('url-to-html-xxx',        Enum__WCF__Command_Type.url_to_html_xxx       ),
                ('url-to-html-min-rating', Enum__WCF__Command_Type.url_to_html_min_rating),
                ('url-to-ratings',         Enum__WCF__Command_Type.url_to_ratings        ),
                ('url-to-text-nodes',      Enum__WCF__Command_Type.url_to_text_nodes     ),
                ('url-to-lines',           Enum__WCF__Command_Type.url_to_lines          ),
                ('url-to-text',            Enum__WCF__Command_Type.url_to_text           ),
            ]

            for command, expected_type in test_cases:
                headers = {'cookie': f'mitm-show={command}'}
                result = _.get_wcf_command_type(headers)
                assert result == expected_type, f"Failed for command: {command}"

    def test_get_wcf_command_type__not_wcf(self):                                             # Test non-WCF command returns None
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=response-data'}
            cmd_type = _.get_wcf_command_type(headers)

            assert cmd_type is None

    def test_convert_to_debug_params(self):                                                   # Test conversion to debug_params format
        with self.cookie_service as _:
            debug_params = _.convert_to_debug_params(self.test_headers_full)

            assert debug_params == {'show'   : 'url-to-html-xxx',
                                   'inject' : 'debug-panel'      ,
                                   'replace': 'Hello:Hi'         ,
                                   'debug'  : 'true'             }

    def test_convert_to_debug_params__partial(self):                                          # Test conversion with only some cookies
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=url-to-text; mitm-cache=true'}
            debug_params = _.convert_to_debug_params(headers)

            assert debug_params == {'show': 'url-to-text'}                                    # Only show in debug_params
            assert 'cache'  not in debug_params                                                # cache not a debug param
            assert 'inject' not in debug_params
            assert 'debug'  not in debug_params

    def test_convert_to_debug_params__empty(self):                                            # Test conversion with no cookies
        with self.cookie_service as _:
            debug_params = _.convert_to_debug_params(self.test_headers_empty)

            assert debug_params == {}
            assert len(debug_params) == 0

    def test_get_cookie_summary(self):                                                        # Test comprehensive cookie summary
        with self.cookie_service as _:
            summary = _.get_cookie_summary(self.test_headers_full)

            assert type(summary) is dict
            assert summary['show_command']    == 'url-to-html-xxx'
            assert summary['inject_command']  == 'debug-panel'
            assert summary['replace_command'] == 'Hello:Hi'
            assert summary['debug_enabled']   is True
            assert summary['rating']          == 0.5
            assert summary['model_override']  == 'gpt-4'
            assert summary['cache_enabled']   is True
            assert summary['is_wcf_command']  is True
            assert len(summary['all_proxy_cookies']) == 7

    def test_get_cookie_summary__minimal(self):                                               # Test summary with minimal cookies
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=response-data'}
            summary = _.get_cookie_summary(headers)

            assert summary['show_command']    == 'response-data'
            assert summary['inject_command']  is None
            assert summary['replace_command'] is None
            assert summary['debug_enabled']   is False
            assert summary['rating']          is None
            assert summary['model_override']  is None
            assert summary['cache_enabled']   is False
            assert summary['is_wcf_command']  is False
            assert len(summary['all_proxy_cookies']) == 1

    def test_has_any_proxy_cookies(self):                                                     # Test detection of any proxy cookies
        with self.cookie_service as _:
            assert _.has_any_proxy_cookies(self.test_headers_basic)     is True
            assert _.has_any_proxy_cookies(self.test_headers_empty)     is False
            assert _.has_any_proxy_cookies(self.test_headers_non_proxy) is False

    def test_has_any_proxy_cookies__mixed(self):                                              # Test with mixed proxy and non-proxy cookies
        with self.cookie_service as _:
            headers = {'cookie': 'session=xyz; mitm-show=url-to-html; user=john'}
            result = _.has_any_proxy_cookies(headers)

            assert result is True                                                              # Has at least one proxy cookie

    def test_validate_show_command__valid_wcf(self):                                          # Test validation of valid WCF commands
        with self.cookie_service as _:
            wcf_commands = [
                'url-to-html',
                'url-to-html-xxx',
                'url-to-html-min-rating',
                'url-to-ratings',
                'url-to-text-nodes',
                'url-to-lines',
                'url-to-text',
            ]

            for command in wcf_commands:
                is_valid, error = _.validate_show_command(command)
                assert is_valid is True, f"Failed for: {command}"
                assert error is None, f"Unexpected error for: {command}"

    def test_validate_show_command__valid_response_data(self):                                # Test validation of response-data command
        with self.cookie_service as _:
            is_valid, error = _.validate_show_command('response-data')

            assert is_valid is True
            assert error is None

    def test_validate_show_command__invalid(self):                                            # Test validation of invalid commands
        with self.cookie_service as _:
            is_valid, error = _.validate_show_command('invalid-command')

            assert is_valid is False
            assert error == "Unknown show command: invalid-command"

    def test_validate_show_command__empty(self):                                              # Test validation of empty command
        with self.cookie_service as _:
            is_valid, error = _.validate_show_command('')

            assert is_valid is False
            assert error == "Show command cannot be empty"

    def test_create_cookie_header(self):                                                      # Test Set-Cookie header creation
        with self.cookie_service as _:
            cookie_header = _.create_cookie_header(
                cookie_name  = 'mitm-show',
                cookie_value = 'url-to-html',
                max_age      = 3600,
                path         = '/'
            )

            assert 'mitm-show=url-to-html' in cookie_header
            assert 'Max-Age=3600'          in cookie_header
            assert 'Path=/'                in cookie_header
            assert 'SameSite=Lax'          in cookie_header

    def test_create_cookie_header__custom_values(self):                                       # Test Set-Cookie with different parameters
        with self.cookie_service as _:
            cookie_header = _.create_cookie_header(
                cookie_name  = 'mitm-debug',
                cookie_value = 'true',
                max_age      = 7200,
                path         = '/api'
            )

            assert 'mitm-debug=true' in cookie_header
            assert 'Max-Age=7200'    in cookie_header
            assert 'Path=/api'       in cookie_header

    def test__cookie_priority_over_query_params(self):                                        # Test cookies take precedence over query params
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=url-to-html'}

            query_debug_params = {'show': 'url-to-text'}                                      # Different value in query
            cookie_debug_params = _.convert_to_debug_params(headers)

            combined = {**query_debug_params, **cookie_debug_params}                          # Merge with cookie last

            assert combined['show'] == 'url-to-html'                                           # Cookie value wins
            assert combined['show'] != 'url-to-text'                                           # Query value lost

    def test__multiple_cookies_same_name(self):                                                # Test behavior with duplicate cookie names
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-show=first; mitm-show=second'}                        # Duplicate cookie name
            cookies = _.parse_cookies(headers)

            assert 'mitm-show' in cookies
            assert cookies['mitm-show'] in ['first', 'second']                                # One of them is kept

    def test__special_characters_in_cookie_values(self):                                       # Test cookie values with special chars
        with self.cookie_service as _:
            headers = {'cookie': 'mitm-replace=Hello:Hi%20There'}
            replace_cmd = _.get_replace_command(headers)

            assert replace_cmd == 'Hello:Hi%20There'                                          # Value preserved

    def test__wcf_command_with_rating(self):                                                   # Test WCF command combined with rating
        with self.cookie_service as _:
            show_cmd = _.get_show_command(self.test_headers_wcf)
            rating = _.get_rating(self.test_headers_wcf)
            is_wcf = _.is_wcf_show_command(self.test_headers_wcf)

            assert show_cmd == 'url-to-html-min-rating'
            assert rating == 0.7
            assert is_wcf is True

    def test__all_cookies_together(self):                                                      # Test all cookie types working together
        with self.cookie_service as _:
            headers = {
                'cookie': 'mitm-show=url-to-html; mitm-inject=debug-panel; mitm-replace=A:B; '
                         'mitm-debug=true; mitm-rating=0.9; mitm-model=claude-3; mitm-cache=true; '
                         'session=xyz; user=john'                                              # Non-proxy cookies mixed in
            }

            show    = _.get_show_command(headers)
            inject  = _.get_inject_command(headers)
            replace = _.get_replace_command(headers)
            debug   = _.is_debug_enabled(headers)
            rating  = _.get_rating(headers)
            model   = _.get_model_override(headers)
            cache   = _.is_cache_enabled(headers)
            proxy   = _.get_proxy_cookies(headers)

            assert show    == 'url-to-html'
            assert inject  == 'debug-panel'
            assert replace == 'A:B'
            assert debug   is True
            assert rating  == 0.9
            assert model   == 'claude-3'
            assert cache   is True
            assert len(proxy) == 7                                                             # Only proxy cookies
            assert 'session' not in proxy
            assert 'user' not in proxy