# from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
# from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Extraction_Result  import Schema__Flow__Extraction_Result
# from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data    import Schema__Proxy__Response_Data
# from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Request__Service         import Proxy__Request__Service
# from typing                                                                    import Any, Dict
#
# class Proxy__Flow__Extractor__Service(Type_Safe):                # Extract data from mitmproxy flow
#     request_service : Proxy__Request__Service                    # Request parsing service
#     service_version : str = "1.0.0"                              # Service version
#
#     def extract_request_data(self, flow: Any                     # Extract request from flow
#                             ) -> Dict:                           # Request data dict
#         """Extract request data from mitmproxy flow.request"""
#         try:
#             # Get query string
#             query_string = None
#             if hasattr(flow.request, 'query_string') and flow.request.query_string:
#                 query_string = flow.request.query_string.decode('utf-8', errors='ignore')
#
#             # Use request service to extract
#             return self.request_service.extract_request_data(method       = flow.request.method,
#                                                              host         = flow.request.host,
#                                                              port         = flow.request.port,
#                                                              path         = flow.request.path,
#                                                              scheme       = flow.request.scheme,
#                                                              headers      = dict(flow.request.headers),
#                                                              query_string = query_string              )
#         except Exception as e:
#             # Return minimal data on error
#             return {
#                 'method': 'GET',
#                 'host': 'unknown',
#                 'port': 443,
#                 'path': '/',
#                 'url': 'https://unknown/',
#                 'scheme': 'https',
#                 'headers': {},
#                 'query_params': {}
#             }
#
#     def extract_debug_params(self, flow: Any                     # Extract debug params from flow
#                             ) -> Dict[str, str]:                 # Debug params dict
#         """Extract debug parameters from mitmproxy flow.request"""
#         try:
#             # Get query string
#             query_string = None
#             if hasattr(flow.request, 'query_string') and flow.request.query_string:
#                 query_string = flow.request.query_string.decode('utf-8', errors='ignore')
#
#             # Use request service to extract debug params
#             return self.request_service.extract_debug_params(
#                 method       = flow.request.method,
#                 host         = flow.request.host,
#                 port         = flow.request.port,
#                 path         = flow.request.path,
#                 scheme       = flow.request.scheme,
#                 headers      = dict(flow.request.headers),
#                 query_string = query_string
#             )
#         except Exception:
#             return {}
#
#     def extract_response_data(self, flow: Any                    # Extract response from flow
#                              ) -> Dict:                          # Response data dict
#         """Extract response data from mitmproxy flow.response"""
#         try:
#             # Get content type
#             content_type = 'text/plain'
#             if hasattr(flow.response, 'headers') and 'content-type' in flow.response.headers:
#                 content_type = flow.response.headers.get('content-type', 'text/plain')
#
#             # Get body
#             body = ''
#             if hasattr(flow.response, 'content') and flow.response.content:
#                 body = flow.response.content.decode('utf-8', errors='ignore')
#
#             # Get headers
#             headers = {}
#             if hasattr(flow.response, 'headers'):
#                 headers = dict(flow.response.headers)
#
#             # Get status code
#             status_code = 200
#             if hasattr(flow.response, 'status_code'):
#                 status_code = flow.response.status_code
#
#             return {
#                 'status_code': status_code,
#                 'content_type': content_type,
#                 'body': body,
#                 'headers': headers,
#                 'body_size': len(body.encode('utf-8')) if body else 0
#             }
#         except Exception:
#             return {
#                 'status_code': 500,
#                 'content_type': 'text/plain',
#                 'body': '',
#                 'headers': {},
#                 'body_size': 0
#             }
#
#     def extract_from_flow(self, flow: Any                        # Main entry point: extract complete data
#                          ) -> Schema__Flow__Extraction_Result:   # Extraction result
#         """
#         Main entry point: Extract complete data from mitmproxy flow
#
#         Returns Schema__Flow__Extraction_Result with Schema__Proxy__Response_Data
#         """
#         try:
#             # Extract request data
#             request_data = self.extract_request_data(flow)
#
#             # Extract debug parameters
#             debug_params = self.extract_debug_params(flow)
#
#             # Extract response data
#             response_data = self.extract_response_data(flow)
#
#             # Get flow ID if available
#             flow_id = None
#             if hasattr(flow, 'id'):
#                 flow_id = str(flow.id)
#
#             # Create Schema__Proxy__Response_Data
#             proxy_response_data = Schema__Proxy__Response_Data(
#                 request      = request_data,
#                 debug_params = debug_params,
#                 response     = response_data,
#                 stats        = {},
#                 version      = self.service_version
#             )
#
#             # Create extraction result
#             return Schema__Flow__Extraction_Result(response_data      = proxy_response_data,
#                                                    extraction_success = True               ,
#                                                    flow_id            = flow_id            )
#
#         except Exception as e:
#             # Create error result with minimal data
#             minimal_response_data = Schema__Proxy__Response_Data(
#                 request      = {
#                     'method': 'GET',
#                     'host': 'unknown',
#                     'port': 443,
#                     'path': '/',
#                     'url': 'https://unknown/',
#                     'scheme': 'https',
#                     'headers': {},
#                     'query_params': {}
#                 },
#                 debug_params = {},
#                 response     = {
#                     'status_code': 500,
#                     'content_type': 'text/plain',
#                     'body': '',
#                     'headers': {}
#                 },
#                 stats        = {},
#                 version      = self.service_version
#             )
#
#             return Schema__Flow__Extraction_Result(
#                 response_data      = minimal_response_data,
#                 extraction_success = False,
#                 extraction_error   = f"Flow extraction failed: {str(e)}"
#             )
#
#     def has_debug_commands(self, flow: Any                       # Quick check for debug commands
#                           ) -> bool:                             # Has debug commands
#         """Quick check if flow has debug commands"""
#         try:
#             if hasattr(flow.request, 'query_string') and flow.request.query_string:
#                 query_string = flow.request.query_string.decode('utf-8', errors='ignore')
#                 return self.request_service.should_process_debug_commands(query_string)
#         except Exception:
#             pass
#         return False