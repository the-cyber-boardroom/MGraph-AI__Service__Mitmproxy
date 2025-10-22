# mgraph_ai_service_mitmproxy/schemas/html/Schema__HTML__Service__Request.py

from osbot_utils.type_safe.Type_Safe                                                      import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                       import Safe_Str
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode              import Enum__HTML__Transformation_Mode

class Schema__HTML__Service__Request(Type_Safe):                                    # HTML Service API request
    html                : str                                                       # Source HTML content
    transformation_mode : Enum__HTML__Transformation_Mode                           # Transformation mode to apply

    # todo: review why we need this? since the Type_Safe .json() should work ok here
    def to_json_payload(self) -> dict:                                              # Convert to JSON payload
        """Convert to JSON payload for HTML Service API"""
        return {"html": self.html}