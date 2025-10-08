from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.schemas.Safe_UInt__HTTP_Status                      import Safe_UInt__HTTP_Status
from typing                                                                          import Dict, Optional

class Schema__Response__Processing_Result(Type_Safe):            # Complete response processing result
    modifications       : Schema__Proxy__Modifications           # Content modifications
    final_status_code   : Safe_UInt__HTTP_Status                 # Final HTTP status
    final_content_type  : str                                    # Final content type
    final_body          : str                                    # Final response body
    final_headers       : Dict[str, str]                         # Final response headers
    debug_mode_active   : bool            = False                # Whether debug mode was active
    content_was_modified: bool            = False                # Whether content was modified
    response_overridden : bool            = False                # Whether response was overridden
    processing_error    : Optional[str]   = None                 # Error message if processing failed

    def has_error(self) -> bool:                                 # Check if processing had error
        """Check if response processing encountered an error"""
        return self.processing_error is not None

    def get_summary(self) -> Dict:                               # Get processing summary
        """Get a summary of response processing"""
        return {
            'status_code': int(self.final_status_code),
            'content_type': self.final_content_type,
            'body_size': len(self.final_body),
            'headers_added': len(self.modifications.headers_to_add),
            'debug_mode': self.debug_mode_active,
            'modified': self.content_was_modified,
            'overridden': self.response_overridden,
            'error': self.processing_error
        }