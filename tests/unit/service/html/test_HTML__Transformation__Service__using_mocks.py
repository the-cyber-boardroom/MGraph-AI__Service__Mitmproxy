# from unittest                                                                      import TestCase
# from unittest.mock                                                                 import patch, Mock, MagicMock
# from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
# from osbot_utils.utils.Objects                                                     import base_classes
# from mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service        import HTML__Transformation__Service
# from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode
# from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Transformation__Result import Schema__HTML__Transformation__Result
#
# class test_HTML__Transformation__Service__using_mocks(TestCase):
#
#     def test__init__(self):                                                         # Test auto-initialization
#         with HTML__Transformation__Service() as _:
#             assert type(_)         is HTML__Transformation__Service
#             assert base_classes(_) == [Type_Safe, object]
#             assert _.html_service_client is None
#             assert _.cache_service       is None
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_setup(self, mock_cache_service, mock_html_client):                     # Test setup method
#         mock_client_instance = Mock()
#         mock_client_instance.setup.return_value = mock_client_instance
#         mock_html_client.return_value = mock_client_instance
#
#         mock_cache_instance = Mock()
#         mock_cache_instance.setup.return_value = mock_cache_instance
#         mock_cache_service.return_value = mock_cache_instance
#
#         with HTML__Transformation__Service() as _:
#             result = _.setup()
#
#             assert result is _                                                      # Setup returns self
#             assert _.html_service_client is not None
#             assert _.cache_service       is not None
#
#     def test_transform_html__mode_off(self):                                        # Test transformation with OFF mode (passthrough)
#         with HTML__Transformation__Service() as _:
#             source_html = "<html><body>Original</body></html>"
#
#             result = _.transform_html(
#                 source_html = source_html                              ,
#                 target_url  = "https://example.com"                    ,
#                 mode        = Enum__HTML__Transformation_Mode.OFF
#             )
#
#             assert type(result)               is Schema__HTML__Transformation__Result
#             assert result.transformed_html    == source_html                        # Unchanged
#             assert result.transformation_mode == Enum__HTML__Transformation_Mode.OFF
#             assert result.cache_hit           is False
#             assert result.transformation_time_ms == 0.0
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_transform_html__cache_hit(self, mock_cache_service, mock_html_client): # Test transformation with cache hit
#         # Setup mocks
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = True
#
#         mock_page_refs          = Mock()
#         mock_page_refs.cache_id = "test-cache-id-123"
#         mock_cache_instance.get_or_create_page_entry.return_value = mock_page_refs
#
#         mock_cache_client = Mock()
#         cached_html       = "<html>cached content</html>"
#         mock_cache_client.data().retrieve().data__string__with__id_and_key.return_value = cached_html
#         mock_cache_instance.cache_client = mock_cache_client
#         mock_cache_service.return_value  = mock_cache_instance
#
#         mock_client_instance = Mock()
#         mock_client_instance.setup.return_value = mock_client_instance
#         mock_html_client.return_value = mock_client_instance
#
#         with HTML__Transformation__Service() as _:
#             _.setup()
#             _.cache_service = mock_cache_instance
#
#             result = _.transform_html(
#                 source_html = "<html>original</html>"                  ,
#                 target_url  = "https://example.com/page"               ,
#                 mode        = Enum__HTML__Transformation_Mode.HASHES
#             )
#
#             assert result.transformed_html    == cached_html
#             assert result.cache_hit           is True
#             assert result.transformation_mode == Enum__HTML__Transformation_Mode.HASHES
#             assert result.transformation_time_ms == 0.0                             # Cache hits have 0 time
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_transform_html__cache_miss(self, mock_cache_service, mock_html_client): # Test transformation with cache miss
#         # Setup cache mock (cache miss)
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = True
#
#         mock_page_refs          = Mock()
#         mock_page_refs.cache_id = "test-cache-id-456"
#         mock_cache_instance.get_or_create_page_entry.return_value = mock_page_refs
#
#         mock_cache_client = Mock()
#         mock_cache_client.data().retrieve().data__string__with__id_and_key.return_value = None  # Cache miss
#         mock_cache_instance.cache_client = mock_cache_client
#         mock_cache_service.return_value  = mock_cache_instance
#
#         # Setup HTML service mock (successful transformation)
#         transformed_html     = "<html>transformed content</html>"
#         mock_service_response = Mock()
#         mock_service_response.is_successful.return_value = True
#         mock_service_response.body         = transformed_html
#         mock_service_response.content_type = "text/html"
#
#         mock_client_instance = Mock()
#         mock_client_instance.setup.return_value        = mock_client_instance
#         mock_client_instance.transform_html.return_value = mock_service_response
#         mock_html_client.return_value = mock_client_instance
#
#         with HTML__Transformation__Service() as _:
#             _.setup()
#             _.cache_service = mock_cache_instance
#
#             result = _.transform_html(
#                 source_html = "<html>original</html>"                  ,
#                 target_url  = "https://example.com/page"               ,
#                 mode        = Enum__HTML__Transformation_Mode.XXX
#             )
#
#             assert result.transformed_html    == transformed_html
#             assert result.cache_hit           is False
#             assert result.transformation_mode == Enum__HTML__Transformation_Mode.XXX
#             assert result.transformation_time_ms > 0                                # Should have some time
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_transform_html__service_error_returns_original(self, mock_cache_service, mock_html_client): # Test HTML Service error returns original HTML
#         # Setup cache mock (cache miss)
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = True
#         mock_cache_instance.get_or_create_page_entry.return_value.cache_id = "test-id"
#         mock_cache_instance.cache_client.data().retrieve().data__string__with__id_and_key.return_value = None
#         mock_cache_service.return_value = mock_cache_instance
#
#         # Setup HTML service mock (error)
#         mock_service_response = Mock()
#         mock_service_response.is_successful.return_value = False
#         mock_service_response.error_message = "HTML Service timeout"
#
#         mock_client_instance = Mock()
#         mock_client_instance.setup.return_value        = mock_client_instance
#         mock_client_instance.transform_html.return_value = mock_service_response
#         mock_html_client.return_value = mock_client_instance
#
#         with HTML__Transformation__Service() as _:
#             _.setup()
#             _.cache_service = mock_cache_instance
#
#             source_html = "<html>original</html>"
#
#             result = _.transform_html(
#                 source_html = source_html                              ,
#                 target_url  = "https://example.com/page"               ,
#                 mode        = Enum__HTML__Transformation_Mode.HASHES
#             )
#
#             assert result.transformed_html == source_html                           # Returns original on error
#             assert result.cache_hit        is False
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_store_original_html(self, mock_cache_service, mock_html_client):       # Test original HTML storage
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = True
#
#         mock_page_refs          = Mock()
#         mock_page_refs.cache_id = "original-cache-id"
#         mock_cache_instance.get_or_create_page_entry.return_value = mock_page_refs
#
#         mock_cache_client = Mock()
#         mock_cache_instance.cache_client = mock_cache_client
#         mock_cache_service.return_value  = mock_cache_instance
#
#         with HTML__Transformation__Service() as _:
#             _.cache_service = mock_cache_instance
#
#             original_html = "<html><body>Original</body></html>"
#
#             _.store_original_html(
#                 target_url    = "https://example.com/page"  ,
#                 original_html = original_html
#             )
#
#             # Verify cache storage was called with correct parameters
#             mock_cache_client.data_store().data__store_string__with__id_and_key.assert_called_once_with(
#                 cache_id = "original-cache-id"        ,
#                 data_key = "transformations/html"     ,
#                 content  = original_html
#             )
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_store_original_html__cache_disabled(self, mock_cache_service, mock_html_client): # Test original HTML storage with cache disabled
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = False
#         mock_cache_service.return_value = mock_cache_instance
#
#         with HTML__Transformation__Service() as _:
#             _.cache_service = mock_cache_instance
#
#             _.store_original_html(
#                 target_url    = "https://example.com/page"  ,
#                 original_html = "<html>test</html>"
#             )
#
#             # Should not attempt to store when cache is disabled
#             mock_cache_instance.get_or_create_page_entry.assert_not_called()
#
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.HTML__Service__Client')
#     @patch('mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service.Proxy__Cache__Service')
#     def test_transform_html__cache_error_non_fatal(self, mock_cache_service, mock_html_client): # Test cache errors are non-fatal
#         # Setup cache that raises exception
#         mock_cache_instance = Mock()
#         mock_cache_instance.cache_config.enabled = True
#         mock_cache_instance.get_or_create_page_entry.side_effect = Exception("Cache error")
#         mock_cache_service.return_value = mock_cache_instance
#
#         # Setup successful HTML service
#         mock_service_response = Mock()
#         mock_service_response.is_successful.return_value = True
#         mock_service_response.body         = "<html>transformed</html>"
#         mock_service_response.content_type = "text/html"
#
#         mock_client_instance = Mock()
#         mock_client_instance.setup.return_value        = mock_client_instance
#         mock_client_instance.transform_html.return_value = mock_service_response
#         mock_html_client.return_value = mock_client_instance
#
#         with HTML__Transformation__Service() as _:
#             _.setup()
#             _.cache_service = mock_cache_instance
#
#             result = _.transform_html(
#                 source_html = "<html>original</html>"                  ,
#                 target_url  = "https://example.com/page"               ,
#                 mode        = Enum__HTML__Transformation_Mode.DICT
#             )
#
#             # Should still succeed despite cache error
#             assert result.transformed_html == "<html>transformed</html>"
#             assert result.cache_hit        is False