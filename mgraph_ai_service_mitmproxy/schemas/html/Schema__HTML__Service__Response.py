from typing                                                                              import Dict, Optional
from osbot_utils.type_safe.Type_Safe                                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                     import Safe_UInt
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Text             import Safe_Str__Text
from osbot_utils.type_safe.primitives.domains.http.safe_str.Safe_Str__Http__Content_Type import Safe_Str__Http__Content_Type
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Html                import Safe_Str__Html


class Schema__HTML__Service__Response(Type_Safe):                                   # HTML Service API response
    status_code   : Safe_UInt                                                       # HTTP status code
    content_type  : Safe_Str__Http__Content_Type                                    # Response content type
    body          : Safe_Str__Html                                                  # Response body (transformed HTML or tree view)
    # todo: we should be using Safe_Str* schema classes for the headers
    headers       : Dict[str, str]                                                  # Response headers
    success       : bool                                                            # Whether request was successful
    # todo: see if Safe_Str__Text works for these error messages
    error_message : Optional[Safe_Str__Text]          = None                        # Error message if failed

    # todo: review why we need this, and if so, move it out of this Schema file
    def is_successful(self) -> bool:                                                # Check if response is successful
        return self.success and self.status_code == 200