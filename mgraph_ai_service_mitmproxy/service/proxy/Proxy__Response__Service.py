from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Response__Processing_Result   import Schema__Response__Processing_Result
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Debug__Service                 import Proxy__Debug__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Stats__Service                 import Proxy__Stats__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__CORS__Service                  import Proxy__CORS__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Headers__Service               import Proxy__Headers__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Cookie__Service                import Proxy__Cookie__Service
from typing                                                                          import Dict
import uuid

class Proxy__Response__Service(Type_Safe):                       # Main response processing orchestrator
    debug_service   : Proxy__Debug__Service                      # Debug command processing
    stats_service   : Proxy__Stats__Service                      # Statistics tracking
    cors_service    : Proxy__CORS__Service                       # CORS header management
    headers_service : Proxy__Headers__Service                    # Standard headers
    cookie_service  : Proxy__Cookie__Service                     # Cookie-based control

    def generate_request_id(self) -> str:                        # Generate unique request ID
        """Generate a unique request ID"""
        return f"req-{uuid.uuid4().hex[:12]}"

    def process_response(self,                                   # Main entry point for response processing
                        response_data : Schema__Proxy__Response_Data
                        ) -> Schema__Response__Processing_Result:  # Complete processing result
        """
        Main entry point: Process a proxy response completely

        This orchestrates all response processing:
        1. Update statistics
        2. Create modifications object
        3. Add standard headers
        4. Extract cookies from request headers and merge with debug_params
        5. Process debug commands (may override)
        6. Add CORS headers
        7. Finalize response
        """
        try:
            # Generate request ID
            request_id = self.generate_request_id()

            # Update statistics
            body_size = len(response_data.response.get("body", ""))
            status_code = response_data.response.get("status_code", 200)

            self.stats_service.increment_response(bytes_processed = body_size)

            # Create modifications object
            modifications = Schema__Proxy__Modifications()

            # Extract request headers (includes Cookie header)
            request_headers = response_data.request.get('headers', {})

            # Parse cookie-based debug params from request headers
            # The interceptor sends request headers in response_data.request['headers']
            cookie_debug_params = self.cookie_service.convert_to_debug_params(request_headers)

            # Combine: cookies take precedence over query params
            combined_debug_params = {**response_data.debug_params, **cookie_debug_params}

            # Update response_data with combined debug params
            response_data.debug_params = combined_debug_params

            # Add standard headers
            standard_headers = self.headers_service.get_standard_headers(
                response_data,
                request_id
            )
            modifications.headers_to_add.update(standard_headers)

            # Add cookie summary header if any proxy cookies present
            print('has cookies', self.cookie_service.has_any_proxy_cookies(request_headers))
            if self.cookie_service.has_any_proxy_cookies(request_headers):
                cookie_summary = self.cookie_service.get_cookie_summary(request_headers)
                modifications.headers_to_add["X-Proxy-Cookie-Summary"] = str(cookie_summary)

            # Add debug headers if debug mode (from cookies or query params)
            if response_data.debug_params:
                debug_headers = self.headers_service.get_debug_headers(response_data)
                modifications.headers_to_add.update(debug_headers)

            # Process debug commands (this may override response)
            self.debug_service.process_debug_commands(response_data, modifications)

            # Check if debug command overrode the response
            if modifications.override_response:
                return self._finalize_overridden_response(response_data ,                # For overridden responses, finalize and return
                                                          modifications ,
                                                          request_id    )

            # Check if content was modified (but not overridden)
            if modifications.modified_body:
                self.stats_service.increment_content_modification()

            # Add CORS headers
            cors_headers = self.cors_service.get_cors_headers_for_request(response_data)
            modifications.headers_to_add.update(cors_headers)

            # Handle CORS preflight requests
            if self.cors_service.is_preflight_request(response_data):
                return self._finalize_preflight_response(
                    response_data,
                    modifications,
                    request_id
                )

            # Finalize regular response
            return self._finalize_regular_response(
                response_data,
                modifications,
                request_id
            )

        except Exception as e:
            # Handle any processing errors
            return self._create_error_result(
                response_data,
                str(e)
            )

    def _finalize_overridden_response(self,                      # Finalize debug-overridden response
                                     response_data  : Schema__Proxy__Response_Data,
                                     modifications  : Schema__Proxy__Modifications,
                                     request_id     : str
                                     ) -> Schema__Response__Processing_Result:
        """Finalize a response that was overridden by debug command"""
        final_body = modifications.modified_body or ""

        # Get final headers
        final_headers = self.build_final_headers(
            response_data,
            modifications,
            modifications.override_content_type,
            len(final_body.encode('utf-8'))
        )

        return Schema__Response__Processing_Result(
            modifications        = modifications,
            final_status_code    = modifications.override_status,
            final_content_type   = modifications.override_content_type,
            final_body          = final_body,
            final_headers       = final_headers,
            debug_mode_active   = bool(response_data.debug_params),
            content_was_modified = True,
            response_overridden  = True
        )

    def _finalize_preflight_response(self,                       # Finalize CORS preflight response
                                    response_data  : Schema__Proxy__Response_Data,
                                    modifications  : Schema__Proxy__Modifications,
                                    request_id     : str
                                    ) -> Schema__Response__Processing_Result:
        """Finalize a CORS preflight OPTIONS request"""
        # Get preflight-specific headers
        preflight_headers = self.cors_service.handle_preflight_request(response_data)
        modifications.headers_to_add.update(preflight_headers)

        final_headers = modifications.headers_to_add.copy()

        return Schema__Response__Processing_Result(
            modifications        = modifications,
            final_status_code    = 204,  # No Content for preflight
            final_content_type   = "text/plain",
            final_body          = "",
            final_headers       = final_headers,
            debug_mode_active   = False,
            content_was_modified = False,
            response_overridden  = False
        )

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

        return Schema__Response__Processing_Result(
            modifications        = modifications,
            final_status_code    = final_status,
            final_content_type   = final_content_type,
            final_body          = final_body,
            final_headers       = final_headers,
            debug_mode_active   = bool(response_data.debug_params),
            content_was_modified = bool(modifications.modified_body),
            response_overridden  = False
        )

    def build_final_headers(self, response_data   : Schema__Proxy__Response_Data,  # Build the complete set of final headers
                                  modifications   : Schema__Proxy__Modifications,
                                  content_type    : str,
                                  content_length  : int
                             ) -> Dict[str, str]:                 # Final headers

        final_headers   = response_data.response.get("headers", {}).copy()                            # Start with original response headers
        content_headers = self.headers_service.get_content_headers(content_type, content_length)    # Add content headers
        final_headers.update(content_headers)

        # Add cache headers (no-cache for debug mode)
        if response_data.debug_params:
            cache_headers = self.headers_service.get_cache_headers(no_cache=True)
            final_headers.update(cache_headers)

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
            final_headers       = {
                "Content-Type": "text/plain",
                "Content-Length": str(len(error_body)),
                "X-Processing-Error": "true"
            },
            debug_mode_active   = False,
            content_was_modified = False,
            response_overridden  = False,
            processing_error    = error_message
        )