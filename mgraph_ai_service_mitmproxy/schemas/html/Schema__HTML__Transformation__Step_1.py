from typing                                                                         import Dict
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.html.safe_dict.Safe_Dict__Hash__To__Text   import Safe_Dict__Hash__To__Text


class Schema__HTML__Transformation__Step_1(Type_Safe):
    html_dict    : Dict                                                 # dict of html (this is one of the few cases where we are (from a performance point of view) keep the data in a dict, since the html can be quite large
    hash_mapping : Safe_Dict__Hash__To__Text                            # dict of hash mappings
