from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.Safe_UInt__HTTP__Status                     import Safe_UInt__HTTP__Status
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Content_Type               import Enum__WCF__Content_Type
from typing                                                                          import Optional, Dict

class Schema__WCF__Response(Type_Safe):                      # WCF service response data
    status_code   : Safe_UInt__HTTP__Status                   # HTTP status code from WCF
    content_type  : Enum__WCF__Content_Type                  # Content type of response
    body          : str                                      # Response body content
    headers       : Dict[str, str]                           # Response headers
    success       : bool            = False                  # Whether request succeeded
    error_message : Optional[str]   = None                   # Error message if failed

    def is_html(self) -> bool:                               # Check if response is HTML
        """Check if response content type is HTML"""
        return self.content_type == Enum__WCF__Content_Type.text_html

    def is_json(self) -> bool:                               # Check if response is JSON
        """Check if response content type is JSON"""
        return self.content_type == Enum__WCF__Content_Type.application_json

    def is_plain_text(self) -> bool:                         # Check if response is plain text
        """Check if response content type is plain text"""
        return self.content_type == Enum__WCF__Content_Type.text_plain

    def can_override_response(self) -> bool:                 # Check if response can override proxy response
        """Check if this response should override the proxy response"""
        return self.success and self.status_code == 200 and self.body != ""