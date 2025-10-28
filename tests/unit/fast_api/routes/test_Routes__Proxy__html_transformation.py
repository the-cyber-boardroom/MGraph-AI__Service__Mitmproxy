import pytest
from unittest                                                                        import TestCase
from osbot_utils.testing.__                                                          import __, __SKIP__
from osbot_utils.testing.Temp_Env_Vars                                               import Temp_Env_Vars
from osbot_utils.utils.Http                                                          import GET_json
from osbot_utils.utils.Misc                                                          import list_set
from mgraph_ai_service_mitmproxy.fast_api.routes.Routes__Proxy                       import Routes__Proxy
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from tests.unit.Mitmproxy_Service__Fast_API__Test_Objs                               import (get__cache_service__fast_api_server,
                                                                                              get__html_service__fast_api_server  )


class test_Routes__Proxy__html_transformation(TestCase):                       # Test HTML transformation workflow via Routes__Proxy

    @classmethod
    def setUpClass(cls):                                                        # ONE-TIME setup: start HTML and Cache services
        pytest.skip("wire up tests")
        with get__html_service__fast_api_server() as _:
            cls.html_service_server   = _.fast_api_server
            cls.html_service_base_url = _.server_url

        with get__cache_service__fast_api_server() as _:
            cls.cache_service_server   = _.fast_api_server
            cls.cache_service_base_url = _.server_url

        cls.html_service_server .start()
        cls.cache_service_server.start()

        env_vars = { 'AUTH__TARGET_SERVER__HTML_SERVICE__BASE_URL' : cls.html_service_base_url  ,
                     'AUTH__TARGET_SERVER__CACHE_SERVICE__BASE_URL': cls.cache_service_base_url }
        cls.temp_env_vars = Temp_Env_Vars(env_vars=env_vars).set_vars()
        cls.routes        = Routes__Proxy()

    @classmethod
    def tearDownClass(cls):                                                     # Stop both servers
        cls.html_service_server .stop()
        cls.cache_service_server.stop()
        cls.temp_env_vars.restore_vars()

    def test__fast_api__servers(self):                                          # Verify both servers running
        assert GET_json(self.html_service_base_url  + '/info/health') == {'status': 'ok'}
        assert GET_json(self.cache_service_base_url + '/info/health') == {'status': 'ok'}

    def test__init__(self):                                                     # Test Routes__Proxy initialization
        with self.routes as _:
            assert type(_)                is Routes__Proxy
            assert _.tag                  == 'proxy'
            assert _.proxy_service        is not None
            assert _.proxy_service.response_service                        is not None
            assert _.proxy_service.response_service.html_transformation_service is not None

    def test__process_response__no_html_transformation(self):                  # Test response processing WITHOUT mitm-mode cookie
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/test'                                              ,
                                       'headers' : {}                                                   }  # No mitm-mode cookie
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body>Original content</body></html>'     }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)      is Schema__Proxy__Modifications
            assert modifications.modified_body is None                          # No transformation applied

            #assert 'x-mgraph-proxy'         in modifications.headers_to_add     # Standard headers added
            #assert 'x-response-id'          in modifications.headers_to_add

            assert modifications.obj() == __( block_request        = False                                       ,
                                              block_status         = 403                                         ,
                                              block_message        = 'Blocked by proxy'                         ,
                                              include_stats        = False                                       ,
                                              modified_body        = None                                        ,
                                              override_response    = False                                       ,
                                              override_status      = None                                        ,
                                              override_content_type= None                                        ,
                                              headers_to_add       = __( x_proxy_service               = 'mgraph-proxy'                           ,
                                                                         x_proxy_version               = '1.0.0'                                  ,
                                                                         x_request_id                  = __SKIP__                                ,
                                                                         x_processed_at                = __SKIP__                                ,
                                                                         x_original_host               = 'example.com'                           ,
                                                                         x_original_path               = '/test'                                 ,
                                                                         access_control_allow_origin   = '*'                                      ,
                                                                         access_control_allow_methods  = 'GET, POST, PUT, DELETE, OPTIONS'        ,
                                                                         access_control_allow_headers  = '*'                                      ,
                                                                         access_control_expose_headers = 'content-length, content-type'          ,
                                                                         access_control_allow_credentials = 'true'                               ,
                                                                         access_control_max_age        = '3600'                                  ) ,
                                              headers_to_remove    = []                                          ,
                                              cached_response      = __()                                        ,
                                              stats                = __()                                        )

            assert list_set(modifications.headers_to_add) == [ 'access-control-allow-credentials'     ,
                                                               'access-control-allow-headers'         ,
                                                               'access-control-allow-methods'         ,
                                                               'access-control-allow-origin'          ,
                                                               'access-control-expose-headers'        ,
                                                               'access-control-max-age'               ,
                                                               'x-original-host'                      ,
                                                               'x-original-path'                      ,
                                                               'x-processed-at'                       ,
                                                               'x-proxy-service'                      ,
                                                               'x-proxy-version'                      ,
                                                               'x-request-id'                         ]


    def test__process_response__with_mode_off(self):                           # Test response processing with mitm-mode=off
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/test'                                              ,
                                       'headers' : {'cookie': 'mitm-mode=off'}                          }  # Explicit OFF mode
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body>Content</body></html>'              }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is None                          # OFF mode = no transformation
            assert 'x-mgraph-proxy'            in modifications.headers_to_add

    def test__process_response__with_mode_hashes(self):                        # Test HTML transformation with mitm-mode=hashes
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/test'                                              ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }  # HASHES mode
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Test content</p></body></html>'  }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is not None                      # Transformation applied
            assert '<html>'                    in modifications.modified_body   # Still HTML
            assert 'Test content'              not in modifications.modified_body  # Original text replaced with hash
            assert len(modifications.modified_body) > 0                         # Has content
            assert 'x-html-transformation-mode' in modifications.headers_to_add # Transformation headers added
            assert modifications.headers_to_add['x-html-transformation-mode'] == 'hashes'

    def test__process_response__with_mode_xxx(self):                           # Test HTML transformation with mitm-mode=xxx
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/secret'                                            ,
                                       'headers' : {'cookie': 'mitm-mode=xxx'}                          }  # XXX mode
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Secret text here</p></body></html>' }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is not None
            assert '<html>'                    in modifications.modified_body   # HTML structure preserved
            assert 'Secret text'               not in modifications.modified_body  # Text replaced with xxx
            assert 'xxx'                       in modifications.modified_body   # Contains xxx replacement
            assert 'x-html-transformation-mode' in modifications.headers_to_add
            assert modifications.headers_to_add['x-html-transformation-mode'] == 'xxx'

    def test__process_response__with_mode_ratings(self):                       # Test HTML transformation with mitm-mode=ratings
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/content'                                           ,
                                       'headers' : {'cookie': 'mitm-mode=ratings'}                      }  # RATINGS mode
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Content for rating</p></body></html>' }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is not None
            assert '<html>'                    in modifications.modified_body
            assert 'x-html-transformation-mode' in modifications.headers_to_add
            assert modifications.headers_to_add['x-html-transformation-mode'] == 'ratings'

    def test__process_response__non_html_content(self):                        # Test that non-HTML content is NOT transformed
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/api/data'                                          ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }  # Mode enabled
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'application/json'}             ,  # JSON, not HTML
                                       'body'        : '{"data": "value"}'                              }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is None                          # JSON not transformed
            assert 'x-html-transformation-mode' not in modifications.headers_to_add  # No transformation headers

    def test__process_response__empty_body(self):                              # Test handling of empty response body
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/empty'                                             ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }
            response_data.response = { 'status_code' : 204                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : ''                                               }  # Empty body
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert type(modifications)         is Schema__Proxy__Modifications
            assert modifications.modified_body is None                          # Empty body not transformed
            assert 'x-html-transformation-mode' not in modifications.headers_to_add

    def test__process_response__transformation_headers(self):                  # Test transformation result headers are properly added
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/test'                                              ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Test</p></body></html>'          }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert 'x-html-transformation-mode'    in modifications.headers_to_add
            assert 'x-html-transformation-cache'   in modifications.headers_to_add
            assert 'x-html-content-type'           in modifications.headers_to_add

            assert modifications.headers_to_add['x-html-transformation-mode']  == 'hashes'
            assert modifications.headers_to_add['x-html-transformation-cache'] in ['hit', 'miss']
            assert modifications.headers_to_add['x-html-content-type']        == 'text/html; charset=utf-8'

    def test__process_response__with_multiple_cookies(self):                   # Test HTML transformation works with other cookies present
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                                        ,
                                       'host'    : 'example.com'                                                                ,
                                       'path'    : '/test'                                                                      ,
                                       'headers' : {'cookie': 'mitm-mode=hashes; mitm-debug=true; session=abc123'}             }  # Multiple cookies
            response_data.response = { 'status_code' : 200                                                                      ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}                             ,
                                       'body'        : '<html><body><p>Content</p></body></html>'                               }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            assert modifications.modified_body is not None                      # Transformation still works
            assert 'x-html-transformation-mode' in modifications.headers_to_add
            assert 'x-proxy-cookie-summary'     in modifications.headers_to_add # Cookie summary includes mitm-mode

    def test__process_response__cache_behavior(self):                          # Test cache hit/miss on repeated transformations
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/cached-test'                                       ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Cache test</p></body></html>'    }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            # First call - cache miss
            modifications_1 = self.routes.process_response(response_data)
            assert modifications_1.headers_to_add['x-html-transformation-cache'] == 'miss'

            # Second call - cache hit
            modifications_2 = self.routes.process_response(response_data)
            assert modifications_2.headers_to_add['x-html-transformation-cache'] == 'hit'
            assert modifications_2.modified_body == modifications_1.modified_body   # Same transformed content

    def test__process_response__original_html_stored(self):                    # Test that original HTML is stored for provenance
        with Schema__Proxy__Response_Data() as response_data:
            original_html = '<html><body><p>Original content for provenance</p></body></html>'

            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/provenance-test'                                   ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : original_html                                    }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            modifications = self.routes.process_response(response_data)

            # Verify transformation occurred
            assert modifications.modified_body is not None
            assert modifications.modified_body != original_html

            # Original should be stored in cache (this is tested via the cache service)
            # Here we just verify the transformation workflow completed

    def test__process_response__stats_updated(self):                           # Test that proxy stats are updated correctly
        with Schema__Proxy__Response_Data() as response_data:
            response_data.request  = { 'method'  : 'GET'                                                ,
                                       'host'    : 'example.com'                                        ,
                                       'path'    : '/stats-test'                                        ,
                                       'headers' : {'cookie': 'mitm-mode=hashes'}                       }
            response_data.response = { 'status_code' : 200                                              ,
                                       'headers'     : {'content-type': 'text/html; charset=utf-8'}     ,
                                       'body'        : '<html><body><p>Stats test</p></body></html>'    }
            response_data.stats    = {}
            response_data.version  = 'v1.0.0'

            initial_stats = self.routes.get_proxy_stats()
            initial_modifications = initial_stats['content_modifications']

            self.routes.process_response(response_data)                         # Process with transformation

            final_stats = self.routes.get_proxy_stats()
            final_modifications = final_stats['content_modifications']

            assert final_modifications > initial_modifications                  # Stats incremented