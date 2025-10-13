import uuid
from typing                                                                          import Dict
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Response__Processing_Result   import Schema__Response__Processing_Result
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Debug__Service                 import Proxy__Debug__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                 import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__CORS__Service                  import Proxy__CORS__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Headers__Service               import Proxy__Headers__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service                import Proxy__Cookie__Service



class Proxy__Response__Service(Type_Safe):                       # Main response processing orchestrator
    debug_service   : Proxy__Debug__Service         = None       # Debug command processing
    stats_service   : Proxy__Stats__Service                      # Statistics tracking
    cors_service    : Proxy__CORS__Service                       # CORS header management
    headers_service : Proxy__Headers__Service                    # Standard headers
    cookie_service  : Proxy__Cookie__Service                     # Cookie-based control

    def setup(self):
        self.debug_service = Proxy__Debug__Service().setup()
        return self

    def generate_request_id(self) -> str:                        # Generate unique request ID
        """Generate a unique request ID"""
        return f"req-{uuid.uuid4().hex[:12]}"

    def process_response(self, response_data : Schema__Proxy__Response_Data        # Main entry point for response processing
                          ) -> Schema__Response__Processing_Result:           # Complete processing result
        try:
            request_id       = self.generate_request_id()                                                 # todo: review if we should not be setting this request id in get_standard_headers (since that is the only place this value is used)
            body_size        = len(response_data.response.get("body", ""))                                 # Update statistics
            modifications    = Schema__Proxy__Modifications()                                          # Create modifications object
            request_headers  = response_data.request.get('headers', {})                              # Extract request headers (includes Cookie header)
            debug_params     = self.cookie_service.convert_to_debug_params(request_headers)             # Parse cookie-based debug params from request headers, The interceptor sends request headers in response_data.request['headers']
            standard_headers = self.headers_service.get_standard_headers(response_data,request_id)  # Add standard headers
            #status_code = response_data.response.get("status_code", 200)                            # todo: review this value, since it is not currently used in this method

            self.stats_service.increment_response(bytes_processed = body_size)
            modifications.headers_to_add.update(standard_headers)

            if self.cookie_service.has_any_proxy_cookies(request_headers):                          # Add cookie summary header if any proxy cookies present
                cookie_summary = self.cookie_service.get_cookie_summary(request_headers)
                modifications.headers_to_add["x-proxy-cookie-summary"] = str(cookie_summary)
            self.debug_service.process_debug_commands(debug_params  = debug_params ,                # Process debug commands (this may override response)
                                                      response_data = response_data,
                                                      modifications = modifications)

            if modifications.override_response:                                                     # Check if debug command overrode the response
                return self.finalize_overridden_response(response_data=response_data ,                             # For overridden responses, finalize and return
                                                         modifications=modifications )

            if modifications.modified_body:                                                         # Check if content was modified (but not overridden)
                self.stats_service.increment_content_modification()

            # todo: review if we need to have this CORS capabilities in this part of the proxy workflow
            cors_headers = self.cors_service.get_cors_headers_for_request(response_data)            # Add CORS headers
            modifications.headers_to_add.update(cors_headers)

            if self.cors_service.is_preflight_request(response_data):                               # Handle CORS preflight requests
                return self.finalize_preflight_response(response_data, modifications)

            return self._finalize_regular_response(response_data,                                   # Finalize regular response
                                                   modifications,
                                                   request_id   )

        except Exception as e:
            # print('Error:' , e)
            # import traceback
            # traceback.print_exc()
            return self._create_error_result( response_data, str(e))        # Handle any processing errors

    def finalize_overridden_response(self, response_data  : Schema__Proxy__Response_Data,
                                           modifications  : Schema__Proxy__Modifications,
                                      ) -> Schema__Response__Processing_Result:             # Finalize a response that was overridden by debug command
        final_body = modifications.modified_body or ""

        final_headers = self.build_final_headers(response_data                      ,       # Get final headers
                                                 modifications                      ,
                                                 modifications.override_content_type,
                                                 len(final_body.encode('utf-8'))    )

        return Schema__Response__Processing_Result( modifications        = modifications                      ,
                                                    final_status_code    = modifications.override_status      ,
                                                    final_content_type   = modifications.override_content_type,
                                                    final_body           = final_body                         ,
                                                    final_headers        = final_headers                      ,
                                                    content_was_modified = True                               ,
                                                    response_overridden  = True                               )

    # todo: review this method and see if it should be called 'preflight'
    def finalize_preflight_response(self, response_data  : Schema__Proxy__Response_Data,  # Finalize CORS preflight response
                                          modifications  : Schema__Proxy__Modifications,
                                     ) -> Schema__Response__Processing_Result:
        preflight_headers = self.cors_service.handle_preflight_request(response_data)               # Get preflight-specific headers
        modifications.headers_to_add.update(preflight_headers)

        final_headers = modifications.headers_to_add.copy()

        return Schema__Response__Processing_Result(modifications        = modifications,
                                                   final_status_code    = 204,  # No Content for preflight
                                                   final_content_type   = "text/plain",
                                                   final_body           = "",
                                                   final_headers        = final_headers,
                                                   content_was_modified = False,
                                                   response_overridden  = False)

    def _finalize_regular_response(self,                         # Finalize regular response
                                  response_data  : Schema__Proxy__Response_Data,
                                  modifications  : Schema__Proxy__Modifications,
                                  request_id     : str
                                  ) -> Schema__Response__Processing_Result:
        """Finalize a regular (non-overridden, non-preflight) response"""
        # Determine final body
        if modifications.modified_body:
            final_body = modifications.modified_body
        else:
            final_body = response_data.response.get("body", "")

        # Determine final content type
        final_content_type = response_data.response.get("content_type", "text/plain")

        # Determine final status
        final_status = response_data.response.get("status_code", 200)

        # Build final headers
        final_headers = self.build_final_headers(
            response_data,
            modifications,
            final_content_type,
            len(final_body.encode('utf-8'))
        )

        return Schema__Response__Processing_Result( modifications        = modifications                    ,
                                                    final_status_code    = final_status                     ,
                                                    final_content_type   = final_content_type               ,
                                                    final_body           = final_body                       ,
                                                    final_headers        = final_headers                    ,
                                                    content_was_modified = bool(modifications.modified_body),
                                                    response_overridden  = False                            )

    def build_final_headers(self, response_data   : Schema__Proxy__Response_Data,  # Build the complete set of final headers
                                  modifications   : Schema__Proxy__Modifications,
                                  content_type    : str,
                                  content_length  : int
                             ) -> Dict[str, str]:                 # Final headers

        final_headers   = response_data.response.get("headers", {}).copy()                            # Start with original response headers
        content_headers = self.headers_service.get_content_headers(content_type, content_length)    # Add content headers
        final_headers.update(content_headers)

        # Add all headers from modifications (includes standard, debug, CORS)
        final_headers.update(modifications.headers_to_add)

        # Remove headers that should be removed
        for header_to_remove in modifications.headers_to_remove:
            final_headers.pop(header_to_remove, None)

        return final_headers

    def _create_error_result(self,                               # Create error result
                            response_data : Schema__Proxy__Response_Data,
                            error_message : str
                            ) -> Schema__Response__Processing_Result:
        """Create an error result when processing fails"""
        error_body = f"Response processing error: {error_message}"

        return Schema__Response__Processing_Result(
            modifications        = Schema__Proxy__Modifications(),
            final_status_code    = 500,
            final_content_type   = "text/plain",
            final_body          = error_body,
            final_headers       = { "content-type": "text/plain"            ,
                                    "content-length": str(len(error_body))  ,
                                    "X-Processing-Error": "true"            },
            content_was_modified = False,
            response_overridden  = False,
            processing_error    = error_message
        )