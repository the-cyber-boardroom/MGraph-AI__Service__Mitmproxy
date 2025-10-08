from osbot_utils.decorators.methods.cache_on_self                        import cache_on_self
from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url
from osbot_utils.utils.Env                                               import get_env, load_dotenv
from mgraph_ai_service_mitmproxy.schemas.proxy.Enum__WCF__Command_Type   import Enum__WCF__Command_Type
from typing                                                              import Dict, Optional
from mgraph_ai_service_mitmproxy.service.consts.consts__proxy            import ENV_VAR__WCF_SERVICE__AUTH__API_KEY__NAME, ENV_VAR__WCF_SERVICE__AUTH__API_KEY__VALUE


class Schema__WCF__Request(Type_Safe):                       # WCF service request data
    command_type    : Enum__WCF__Command_Type                # Type of WCF command to execute
    target_url      : Safe_Str__Url                          # URL to process with WCF
    rating          : Optional[float] = None                 # Optional rating parameter (e.g., min-rating)
    model_to_use    : Optional[str]   = None                 # Optional model override
    # auth_header_name : str            = ""                   # Auth header name from env
    # auth_header_value: str            = ""                   # Auth header value from env
    wcf_base_url    : str             = "https://dev.web-content-filtering.mgraph.ai"  # WCF service base URL

    def construct_wcf_url(self) -> str:                      # Build complete WCF URL
        """Construct the complete WCF service URL"""
        # Base path for html-graphs endpoint
        endpoint = f"{self.wcf_base_url}/html-graphs/{self.command_type.value}/"

        # Add target URL as parameter
        url = f"{endpoint}?url={self.target_url}"

        # Add optional rating parameter
        if self.rating is not None:
            url += f"&rating={self.rating}"

        # Add optional model parameter
        if self.model_to_use:
            url += f"&model_to_use={self.model_to_use}"

        return url

    @cache_on_self
    def get_auth_headers(self) -> Dict[str, str]:            # Get headers for WCF service authentication
        load_dotenv()
        auth_header_name   = get_env(ENV_VAR__WCF_SERVICE__AUTH__API_KEY__NAME )
        auth_header_value  = get_env(ENV_VAR__WCF_SERVICE__AUTH__API_KEY__VALUE )
        if auth_header_name and auth_header_name:
            return {auth_header_name:auth_header_value}
        return {}