from enum import Enum

# todo: move the logic/code below into a helper class
# todo: renamed HTML to Html
class Enum__HTML__Transformation_Mode(str, Enum):                                  # HTML transformation mode types
    OFF        = "off"                                                              # No transformation (passthrough)
    DICT       = "dict"                                                             # Tree structure view
    XXX        = "xxx"                                                              # Privacy mask (all text → 'x')
    HASHES     = "hashes"                                                           # Hash display mode
    ROUNDTRIP  = "roundtrip"                                                        # Validation test (html→dict→html)

    @classmethod
    def from_cookie_value(cls, cookie_value: str                                    # Parse cookie value to mode
                         ) -> 'Enum__HTML__Transformation_Mode':                    # Transformation mode or OFF
        """Parse mitm-mode cookie value to transformation mode"""
        if not cookie_value:
            return cls.OFF

        cookie_value_lower = cookie_value.lower().strip()

        for mode in cls:
            if mode.value == cookie_value_lower:
                return mode

        return cls.OFF                                                              # Default to OFF for unknown values

    def is_active(self) -> bool:                                                    # Check if mode requires transformation
        """Check if this mode requires transformation (not OFF)"""
        return self != Enum__HTML__Transformation_Mode.OFF

    def requires_caching(self) -> bool:                                             # Check if mode should be cached
        """Check if this transformation should be cached"""
        return self.is_active()                                                     # All active modes are cacheable

    def to_endpoint_path(self) -> str:                                              # Convert mode to HTML Service endpoint path"""
        mapping = {
            Enum__HTML__Transformation_Mode.DICT      : "/html/to/tree/view"       , # BUG this should be to html/to/dict and we should add new TREE_VIEW mode which would be the one that points to /html/to/tree/view
            Enum__HTML__Transformation_Mode.XXX       : "/html/to/html/xxx"        ,
            Enum__HTML__Transformation_Mode.HASHES    : "/html/to/html/hashes"     ,
            Enum__HTML__Transformation_Mode.ROUNDTRIP : "/html/to/html"
        }
        return mapping.get(self, "")

    def to_content_type(self) -> str:                                               # Get response content type
        """Get content type for this transformation mode"""
        if self == Enum__HTML__Transformation_Mode.DICT:
            return "text/plain"                                                     # Tree view is plain text
        else:
            return "text/html"                                                      # All other modes return HTML

    def to_cache_data_key(self) -> str:                                             # Get cache storage key
        """Get cache data key for this transformation mode"""
        mapping = {
            Enum__HTML__Transformation_Mode.DICT      : "transformations/html-dict"    ,
            Enum__HTML__Transformation_Mode.XXX       : "transformations/html-xxx"     ,
            Enum__HTML__Transformation_Mode.HASHES    : "transformations/html-hashes"  ,
            Enum__HTML__Transformation_Mode.ROUNDTRIP : "transformations/html-roundtrip"
        }
        return mapping.get(self, "")

    def str(self):
        return self.value