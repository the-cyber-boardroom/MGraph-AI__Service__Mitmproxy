from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from typing                                                                          import Optional

class Schema__Flow__Extraction_Result(Type_Safe):                # Flow extraction result
    response_data      : Schema__Proxy__Response_Data            # Extracted response data
    extraction_success : bool                   = True           # Whether extraction succeeded
    extraction_error   : Optional[str]          = None           # Error message if failed
    flow_id            : Optional[str]          = None           # Flow identifier

    def has_error(self) -> bool:                                 # Check if extraction failed
        """Check if extraction encountered an error"""
        return self.extraction_error is not None

    def get_summary(self) -> dict:                               # Get extraction summary
        """Get summary of extraction"""
        return {
            'success': self.extraction_success,
            'error': self.extraction_error,
            'flow_id': self.flow_id,
            'has_debug_params': bool(self.response_data.debug_params),
            'request_method': self.response_data.request.get('method'),
            'request_host': self.response_data.request.get('host')
        }