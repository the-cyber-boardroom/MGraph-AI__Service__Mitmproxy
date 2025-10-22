from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                                    import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode            import Enum__HTML__Transformation_Mode
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                import Safe_Str__Html


# todo: move the logic/code below into a helper class
# todo: renamed HTML to Html
class Schema__HTML__Transformation__Result(Type_Safe):                # Result of HTML transformation operation
    transformed_html       : Safe_Str__Html                           # Transformed HTML content
    transformation_mode    : Enum__HTML__Transformation_Mode          # Mode that was applied
    content_type           : Safe_Str__Http__Content_Type             # Content type of result
    cache_hit              : bool                                     # Whether result came from cache
    transformation_time_ms : Safe_Float                      = None    # Time taken for transformation (ms)

    def was_cached(self) -> bool:                                                   # Check if result was from cache
        return self.cache_hit

    def to_headers(self) -> dict:                                                   # Convert transformation metadata to HTTP headers
        return { "x-proxy-transformation"  : self.transformation_mode.value      ,
                  "x-proxy-cache"          : "hit" if self.cache_hit else "miss" ,
                  "x-html-service-time"    : f"{self.transformation_time_ms}ms"  ,
                  "content-type"           : self.content_type                   }