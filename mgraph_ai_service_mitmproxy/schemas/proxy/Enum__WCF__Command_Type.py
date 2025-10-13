from enum import Enum

# todo: refactor this with Enum__Cache__Transformation_Type since this is a duplicate of these mappings
class Enum__WCF__Command_Type(Enum):            # Types of WCF commands that can be executed
    url_to_html                  = 'url-to-html'
    url_to_html_dict             = 'url-to-html-dict'
    url_to_html_xxx              = 'url-to-html-xxx'
    url_to_html_min_rating       = 'url-to-html-min-rating'
    url_to_html_hashes           = 'url-to-html-hashes'
    url_to_ratings               = 'url-to-ratings'
    url_to_text_nodes            = 'url-to-text-nodes'
    url_to_lines                 = 'url-to-lines'
    url_to_text                  = 'url-to-text'

    @classmethod
    def from_show_param(cls, show_value: str):              # Convert show parameter to enum
        """Convert a show parameter value to WCF command type"""
        # Handle special cases like 'url-to-html-min-rating:0.5'
        if show_value.startswith('url-to-html-min-rating'):
            return cls.url_to_html_min_rating

        # Direct mapping
        for command_type in cls:
            if command_type.value == show_value:
                return command_type

        return None

    @classmethod
    def is_wcf_command(cls, show_value: str) -> bool:       # Check if show param is WCF command
        """Check if a show parameter is a WCF command"""
        return show_value.startswith('url-to')