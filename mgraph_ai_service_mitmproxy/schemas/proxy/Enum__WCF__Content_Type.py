from enum import Enum

class Enum__WCF__Content_Type(Enum):
    """Content types returned by WCF service"""
    text_html        = 'text/html; charset=utf-8'
    text_plain       = 'text/plain; charset=utf-8'
    application_json = 'application/json'
    unknown          = 'unknown'

    @classmethod
    def from_header(cls, content_type_header: str):          # Parse content type from header
        """Parse content type from HTTP header"""
        if not content_type_header:
            return cls.unknown

        # Normalize the header
        content_type = content_type_header.lower().strip()

        # Match against known types
        if 'text/html' in content_type:
            return cls.text_html
        elif 'text/plain' in content_type:
            return cls.text_plain
        elif 'application/json' in content_type:
            return cls.application_json
        else:
            return cls.unknown