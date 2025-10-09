# from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
# from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Application_Result       import Schema__Flow__Application_Result
# from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Response__Processing_Result   import Schema__Response__Processing_Result
# from typing                                                                          import Any
#
# class Proxy__Flow__Applicator__Service(Type_Safe):               # Apply results to mitmproxy flow
#
#     def apply_status_code(self, flow: Any,                      # Apply status code to flow
#                                 status_code: int                        # Status code to apply
#                            ) -> bool:                              # Success
#         """Apply status code to mitmproxy flow.response"""
#         try:
#             flow.response.status_code = status_code
#             return True
#         except Exception:
#             return False
#
#     def apply_headers(self, flow: Any,                          # Apply headers to flow
#                      headers: dict                               # Headers to apply
#                      ) -> int:                                   # Number of headers applied
#         """Apply headers to mitmproxy flow.response"""
#         try:
#             # Clear existing headers
#             flow.response.headers.clear()
#
#             # Apply new headers
#             count = 0
#             for key, value in headers.items():
#                 flow.response.headers[key] = value
#                 count += 1
#
#             return count
#         except Exception:
#             return 0
#
#     def apply_body(self, flow: Any,                             # Apply body to flow
#                   body: str                                      # Body content to apply
#                   ) -> int:                                      # Body size applied
#         """Apply body content to mitmproxy flow.response"""
#         try:
#             # Encode body to bytes
#             body_bytes = body.encode('utf-8')
#
#             # Apply to flow
#             flow.response.content = body_bytes
#
#             return len(body_bytes)
#         except Exception:
#             return 0
#
#     def apply_to_flow(self, flow: Any,                          # Main entry point: apply result to flow
#                             result: Schema__Response__Processing_Result  # Processing result to apply
#                        ) -> Schema__Flow__Application_Result:      # Application result
#         """
#         Main entry point: Apply processing result to mitmproxy flow
#
#         Returns Schema__Flow__Application_Result with details of what was applied
#         """
#         try:
#             # Get flow ID if available
#             flow_id = None
#             if hasattr(flow, 'id'):
#                 flow_id = str(flow.id)
#
#             # Create application result
#             app_result = Schema__Flow__Application_Result(
#                 application_success = True,
#                 flow_id             = flow_id
#             )
#
#             # Apply status code
#             if self.apply_status_code(flow, int(result.final_status_code)):
#                 app_result.status_applied = True
#                 app_result.add_modification(f"status: {result.final_status_code}")
#
#             # Apply headers
#             headers_count = self.apply_headers(flow, result.final_headers)
#             if headers_count > 0:
#                 app_result.headers_applied = True
#                 app_result.headers_count = headers_count
#                 app_result.add_modification(f"headers: {headers_count} applied")
#
#             # Apply body
#             body_size = self.apply_body(flow, result.final_body)
#             if body_size > 0:
#                 app_result.body_applied = True
#                 app_result.body_size = body_size
#                 app_result.add_modification(f"body: {body_size} bytes")
#
#             # Track if content was modified or overridden
#             if result.response_overridden:
#                 app_result.add_modification("response: overridden")
#             elif result.content_was_modified:
#                 app_result.add_modification("content: modified")
#
#             # Track debug mode
#             if result.debug_mode_active:
#                 app_result.add_modification("debug: active")
#
#             return app_result
#
#         except Exception as e:
#             # Create error result
#             return Schema__Flow__Application_Result(
#                 application_success = False,
#                 application_error   = f"Flow application failed: {str(e)}",
#                 flow_id             = flow_id if 'flow_id' in locals() else None
#             )
#
#     def apply_error_response(self, flow: Any,                   # Apply error response to flow
#                             error_message: str,                  # Error message
#                             status_code: int = 500               # Error status code
#                             ) -> Schema__Flow__Application_Result:  # Application result
#         """Apply an error response to the flow"""
#         try:
#             # Get flow ID
#             flow_id = None
#             if hasattr(flow, 'id'):
#                 flow_id = str(flow.id)
#
#             # Apply error status
#             flow.response.status_code = status_code
#
#             # Apply error body
#             error_body = f"Proxy Error: {error_message}"
#             flow.response.content = error_body.encode('utf-8')
#
#             # Apply error headers
#             flow.response.headers.clear()
#             flow.response.headers['content-type'] = 'text/plain'
#             flow.response.headers['content-length'] = str(len(error_body))
#             flow.response.headers['X-Proxy-Error'] = 'true'
#
#             return Schema__Flow__Application_Result(
#                 application_success = True,
#                 flow_id             = flow_id,
#                 status_applied      = True,
#                 headers_applied     = True,
#                 body_applied        = True,
#                 headers_count       = 3,
#                 body_size           = len(error_body),
#                 modifications_made  = ['error_response']
#             )
#
#         except Exception as e:
#             return Schema__Flow__Application_Result(
#                 application_success = False,
#                 application_error   = f"Error response application failed: {str(e)}"
#             )