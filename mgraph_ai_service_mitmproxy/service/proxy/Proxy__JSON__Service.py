import json
from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from datetime                                                                        import datetime
from typing                                                                          import Dict, Optional

class Proxy__JSON__Service(Type_Safe):                           # JSON content manipulation service

    def inject_debug_fields(self,
                           json_content  : str,                  # Original JSON content
                           debug_params  : Dict[str, str]        # Debug parameters to inject
                           ) -> Optional[str]:                   # Modified JSON or None
        """Inject debug information into JSON content"""
        try:
            # Parse JSON
            json_data = json.loads(json_content)

            # Add debug fields
            json_data["_debug_params"] = debug_params
            json_data["_debug_timestamp"] = datetime.utcnow().isoformat()
            json_data["_debug_injected"] = True

            # Return formatted JSON
            return json.dumps(json_data, indent=2)

        except json.JSONDecodeError:
            # If JSON parsing fails, return None
            return None
        except Exception:
            return None

    def create_debug_json_response(self,
                                   response_data : Dict           # Response data to show
                                   ) -> str:                      # JSON string
        """Create a JSON response with debug information"""
        return json.dumps(response_data, indent=2)