from enum import Enum

# todo: remove legacy url-* when the html-* are working (and the semantic-text is wired up)
class Enum__Cache__Transformation_Type(str, Enum):
    # Existing (legacy - to be deprecated)
    URL_TO_HTML          = "url-to-html"                                            # ❌ Legacy: Re-fetches URL
    URL_TO_LINES         = "url-to-lines"                                           # ❌ Legacy: Text extraction
    URL_TO_RATINGS       = "url-to-ratings"                                         # 📝 Keep for now
    URL_TO_HTML_FILTERED = "url-to-html-min-rating"                                 # 📝 Keep for now
    
    # New HTML Service transformations (Phase 1)
    HTML_TO_DICT         = "html-to-dict"                                           # ✅ Tree structure view
    HTML_TO_XXX          = "html-to-xxx"                                            # ✅ Privacy masked
    HTML_TO_HASHES       = "html-to-hashes"                                         # ✅ Hash display
    HTML_TO_ROUNDTRIP    = "html-to-roundtrip"                                      # ✅ Validation test
    
    # Future HTML Service transformations (Phase 2+)
    HTML_TO_TEXT_NODES   = "html-to-text-nodes"                                     # 📝 Future: Text extraction with metadata
    HTML_TO_TEXT_HASHES  = "html-to-text-hashes"                                    # 📝 Future: Lightweight hash mapping

    # todo: refactor out of Type_Safe clasls
    def to_data_key(self) -> str:                                                   # Convert to cache data_key path
        """Convert transformation type to cache storage data_key"""
        mapping = {
            # Legacy transformations
            "url-to-html"           : "transformations/html"          ,
            "url-to-lines"          : "transformations/text"          ,
            "url-to-ratings"        : "transformations/ratings"       ,
            "url-to-html-min-rating": "transformations/html-filtered" ,
            
            # New HTML Service transformations
            "html-to-dict"          : "transformations/html-dict"     ,
            "html-to-xxx"           : "transformations/html-xxx"      ,
            "html-to-hashes"        : "transformations/html-hashes"   ,
            "html-to-roundtrip"     : "transformations/html-roundtrip",
            
            # Future transformations
            "html-to-text-nodes"    : "transformations/text-nodes"    ,
            "html-to-text-hashes"   : "transformations/text-hashes"
        }
        return mapping.get(self.value, f"transformations/{self.value}")
    
    def is_legacy_transformation(self) -> bool:                                      # Check if legacy transformation
        """Check if this is a legacy transformation that should be deprecated"""
        legacy_types = {
            Enum__Cache__Transformation_Type.URL_TO_HTML          ,
            Enum__Cache__Transformation_Type.URL_TO_LINES         ,
            Enum__Cache__Transformation_Type.URL_TO_RATINGS       ,
            Enum__Cache__Transformation_Type.URL_TO_HTML_FILTERED
        }
        return self in legacy_types
    
    def is_html_service_transformation(self) -> bool:                                # Check if HTML Service transformation
        """Check if this is a new HTML Service transformation"""
        html_service_types = {
            Enum__Cache__Transformation_Type.HTML_TO_DICT       ,
            Enum__Cache__Transformation_Type.HTML_TO_XXX        ,
            Enum__Cache__Transformation_Type.HTML_TO_HASHES     ,
            Enum__Cache__Transformation_Type.HTML_TO_ROUNDTRIP  ,
            Enum__Cache__Transformation_Type.HTML_TO_TEXT_NODES ,
            Enum__Cache__Transformation_Type.HTML_TO_TEXT_HASHES
        }
        return self in html_service_types