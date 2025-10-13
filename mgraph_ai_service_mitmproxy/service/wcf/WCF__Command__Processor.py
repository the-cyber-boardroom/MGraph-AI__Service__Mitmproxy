from typing                                                                 import Optional
from osbot_utils.type_safe.Type_Safe                                        import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type      import Enum__WCF__Command_Type

class WCF__Command__Processor(Type_Safe):                                   # Processes WCF show commands with special parameter handling

    def parse_show_command(self, show_value: str                            # Parse show command value and extract special parameters
                           ) -> Optional[tuple]:                            # Returns (command_type, rating, model_to_use, modified_url_suffix) or None
        if not Enum__WCF__Command_Type.is_wcf_command(show_value):
            return None

        command_type = Enum__WCF__Command_Type.from_show_param(show_value)
        if not command_type:
            return None

        rating               = None
        model_to_use         = None
        modified_url_suffix  = ""

        if show_value.startswith('url-to-html-min-rating'):                 # Handle rating parameter
            if ':' in show_value:
                try:
                    rating = float(show_value.split(':')[1])
                except:
                    rating = 0.5
            else:
                rating = 0.5
            modified_url_suffix = f"&rating={rating}"

        if show_value == 'url-to-ratings':                                  # Handle special model override
            model_to_use = "google/gemini-2.0-flash-lite-001"               # todo: move to const

        return (command_type, rating, model_to_use, modified_url_suffix)    # todo: this should return a Type_Safe class





