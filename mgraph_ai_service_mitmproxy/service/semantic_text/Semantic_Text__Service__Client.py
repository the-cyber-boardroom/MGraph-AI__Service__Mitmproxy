import requests
from typing                                                                                                     import Dict
from osbot_utils.decorators.methods.cache_on_self                                                               import cache_on_self
from osbot_utils.type_safe.Type_Safe                                                                            import Type_Safe
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Name                        import Safe_Str__Http__Header__Name
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Header__Value                       import Safe_Str__Http__Header__Value
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id                                 import Safe_Str__Id
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                                  import type_safe
from osbot_utils.utils.Env                                                                                      import get_env
from osbot_utils.utils.Http                                                                                     import url_join_safe
from osbot_utils.utils.Json import json_dumps

from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Response   import Schema__Semantic_Text__Transformation__Response
from mgraph_ai_service_mitmproxy.schemas.semantic_text.client.Schema__Semantic_Text__Transformation__Request    import Schema__Semantic_Text__Transformation__Request
from mgraph_ai_service_mitmproxy.schemas.semantic_text.const__semantic_text                                     import ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__BASE_URL, ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__KEY_NAME, ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__KEY_VALUE


class Semantic_Text__Service__Client(Type_Safe):                                                       # HTTP client for Semantic Text Service API

    @cache_on_self
    def server_base_url(self):
        base_url_env  = get_env(ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__BASE_URL)
        return base_url_env

    @cache_on_self
    def headers(self) -> Dict[Safe_Str__Http__Header__Name, Safe_Str__Http__Header__Value]:                                    # Get authentication headers from environment
        key_name  = get_env(ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__KEY_NAME)
        key_value = get_env(ENV_VAR__AUTH__TARGET_SERVER__SEMANTIC_TEXT_SERVICE__KEY_VALUE)
        
        headers = { "content-type" : "application/json" }
        
        if key_name and key_value:
            headers[Safe_Str__Id(key_name)] = Safe_Str__Id(key_value)
        
        return headers

    @type_safe
    def transform_text(self, request  : Schema__Semantic_Text__Transformation__Request  # Transform text using Semantic Text Service
                       ) -> Schema__Semantic_Text__Transformation__Response:                                           # Transformation response

        endpoint_path = "/text-transformation/transform"
        server        = self.server_base_url()
        if not server:
            raise ValueError("in transform_text, the target server was not be set")

        url           = url_join_safe(self.server_base_url(), endpoint_path)
        post_headers  = self.headers()
        post_json     = request.json()
        # print()
        # print()
        # print(json_dumps(post_json))
        # print()
        # print()
        response = requests.post(url     = url          ,
                                 headers = post_headers ,
                                 json    = post_json    )

        return Schema__Semantic_Text__Transformation__Response.from_json(response.json())