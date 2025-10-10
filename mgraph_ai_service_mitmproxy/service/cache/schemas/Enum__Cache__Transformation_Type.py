from enum import Enum

class Enum__Cache__Transformation_Type(str, Enum):              # WCF transformation command types
    URL_TO_HTML          = "url-to-html"                        # Convert URL to HTML
    URL_TO_TEXT          = "url-to-text"                        # Extract text from URL
    URL_TO_RATINGS       = "url-to-ratings"                     # Get content ratings
    URL_TO_HTML_FILTERED = "url-to-html-min-rating"             # HTML with rating filter

    def __str__(self):
        return self.value

    # todo move this logic to the class file that implements this logic
    def to_data_key(self) -> str:                               # Convert to data_key path for child data storage
        """Convert to data_key path for child data storage"""
        mapping = { "url-to-html"           : "transformations/html"          ,
                    "url-to-text"           : "transformations/text"          ,
                    "url-to-ratings"        : "transformations/ratings"       ,
                    "url-to-html-min-rating": "transformations/html-filtered" }
        return mapping.get(self.value, f"transformations/{self.value.replace('-', '_')}")