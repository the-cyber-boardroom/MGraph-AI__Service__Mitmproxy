from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__Debug__Command                import Schema__Debug__Command
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__HTML__Injection               import Schema__HTML__Injection
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Response_Data          import Schema__Proxy__Response_Data
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Modifications          import Schema__Proxy__Modifications
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__HTML__Service                  import Proxy__HTML__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__JSON__Service                  import Proxy__JSON__Service
from typing                                                                          import Dict, List, Optional
from mgraph_ai_service_mitmproxy.service.wcf.Proxy__WCF__Service                     import Proxy__WCF__Service


class Proxy__Debug__Service(Type_Safe):                          # Debug command processing service
    wcf_service  : Proxy__WCF__Service      = None               # WCF service integration
    html_service : Proxy__HTML__Service                          # HTML manipulation
    json_service : Proxy__JSON__Service                          # JSON manipulation

    def setup(self):
        self.wcf_service = Proxy__WCF__Service().setup()
        return self

    def parse_debug_commands(self,debug_params : Dict[str, str]        # Debug parameters
                             ) -> List[Schema__Debug__Command]:   # List of debug commands
        """Parse debug parameters into command objects"""
        return Schema__Debug__Command.from_debug_params(debug_params)

    def process_show_command(self, command       : Schema__Debug__Command      ,    # Show command to process
                                   response_data : Schema__Proxy__Response_Data     # Response data
                              ) -> Optional[Schema__Proxy__Modifications]:          # Modifications or None

        if command.is_wcf_show_command():                                           # Handle WCF commands (url-to-*)
            target_url = response_data.request.get('url')
            wcf_response = self.wcf_service.process_show_command(show_value = command.command_value,
                                                                 target_url = target_url )

            if wcf_response and wcf_response.can_override_response():
                modifications                                   = Schema__Proxy__Modifications()
                modifications.override_response                 = True
                modifications.override_status                   = wcf_response.status_code
                modifications.override_content_type             = wcf_response.content_type.value
                modifications.modified_body                     = wcf_response.body
                modifications.headers_to_add["x-debug-show"]    = command.command_value
                modifications.headers_to_add["x-wcf-processed"] = "true"

                return modifications

        # Handle response-data show command
        if command.is_response_data_show_command():
            modifications = Schema__Proxy__Modifications()

            response_json = self.json_service.create_debug_json_response(response_data.json())  # Create JSON response with all response data

            modifications.override_response              = True
            modifications.override_status                = 200
            modifications.override_content_type          = "application/json"
            modifications.modified_body                  = response_json
            modifications.headers_to_add["x-debug-show"] = "response-data"

            return modifications

        return None

    def process_inject_command(self, command       : Schema__Debug__Command     ,  # Inject command
                                     debug_params  : dict                       ,
                                     response_data : Schema__Proxy__Response_Data  # Response data
                              ) -> Optional[Schema__HTML__Injection]:  # Injection config or None
        """Process an 'inject' debug command"""
        injection = Schema__HTML__Injection()

        # Inject debug panel
        if command.command_value == 'debug-panel':
            injection.inject_panel = True
            injection.panel_content = self.html_service.create_debug_panel(debug_params  = debug_params          ,
                                                                           request_info  = response_data.request ,
                                                                           response_info = response_data.response)
            return injection

        return None

    def process_debug_mode(self,  debug_params  : Dict                        ,
                                  response_data : Schema__Proxy__Response_Data      # Process debug mode (inject banner)
                             ) -> Optional[Schema__HTML__Injection]:
        injection = Schema__HTML__Injection()
        injection.inject_banner = True
        injection.banner_content = self.html_service.create_debug_banner(debug_params = debug_params                           ,
                                                                         request_path = response_data.request.get('path', '/') )
        return injection

    def process_replace_command(self,
                               command : Schema__Debug__Command  # Replace command
                               ) -> Optional[tuple]:             # (old_text, new_text) or None
        """Process a 'replace' debug command"""
        # Parse replace value (format: old:new)
        if ':' in command.command_value:
            old_text, new_text = command.command_value.split(':', 1)
            return old_text, new_text

        return None

    def process_debug_commands(self, debug_params   : Dict                        ,             # Main entry point: process all debug commands
                                     response_data  : Schema__Proxy__Response_Data,             # the response data received from the proxy
                                     modifications  : Schema__Proxy__Modifications,             # Modifications to update
                                ) -> None:                                                        # Updates modifications are in the modifications object # todo: review this pattern


        # Parse commands
        commands = self.parse_debug_commands(debug_params)
        # Process show commands first (they override everything)
        for command in commands:
            if command.is_show_command():


                if command.is_wcf_show_command():                                           #  Only process WCF commands for HTML responses
                    content_type = response_data.response.get("content_type", "")           # todo: move this logic to a better place

                    if not self.html_service.is_html_content(content_type):                 # Skip if not HTML content
                        modifications.headers_to_add["x-wcf-skipped"] = "non-html-content"  # Add header to indicate why it was skipped
                        continue  # Skip this command

                show_mods = self.process_show_command(command, response_data)
                if show_mods and show_mods.override_response:
                    # Show command wants to override - apply and return
                    modifications.override_response = show_mods.override_response
                    modifications.override_status = show_mods.override_status
                    modifications.override_content_type = show_mods.override_content_type
                    modifications.modified_body = show_mods.modified_body
                    modifications.headers_to_add.update(show_mods.headers_to_add)
                    return  # Early return - show commands take precedence

        # Get response content info
        content_type = response_data.response.get("content_type", "")
        body_content = response_data.response.get("body", "")

        if not body_content:
            return

        # Process HTML content modifications
        if self.html_service.is_html_content(content_type):
            modified_body = body_content

            # Collect all HTML injections
            injections = []

            # Check for inject commands
            for command in commands:
                if command.is_inject_command():
                    injection = self.process_inject_command(command       = command      ,
                                                            debug_params  = debug_params ,
                                                            response_data = response_data)
                    if injection:
                        injections.append(injection)

            # Check for debug mode (inject_debug or debug params)
            if (debug_params.get('inject_debug') == 'true' or
                debug_params.get('debug') == 'true'):
                injection = self.process_debug_mode(debug_params=debug_params, response_data=response_data)
                if injection:
                    injections.append(injection)

            # Apply all injections
            for injection in injections:
                result = self.html_service.inject_into_html(modified_body, injection)
                if result:
                    modified_body = result

                    # Add headers for tracking
                    if injection.inject_banner:
                        modifications.headers_to_add["x-debug-banner-injected"] = "true"
                    if injection.inject_panel:
                        modifications.headers_to_add["x-debug-panel-injected"] = "true"

            # Process replace commands
            for command in commands:
                if command.is_replace_command():
                    replace_tuple = self.process_replace_command(command)
                    if replace_tuple:
                        old_text, new_text = replace_tuple
                        result = self.html_service.apply_text_replacement(
                            modified_body, old_text, new_text
                        )
                        if result:
                            modified_body = result
                            modifications.headers_to_add["X-Debug-Replace"] = f"{old_text} -> {new_text}"

            # If body was modified, update it
            if modified_body != body_content:
                modifications.modified_body = modified_body

        # Process JSON content modifications
        elif self.html_service.is_json_content(content_type):
            if debug_params.get('inject_debug') == 'true':
                modified_json = self.json_service.inject_debug_fields(
                    body_content, debug_params
                )
                if modified_json:
                    modifications.modified_body = modified_json

        # Process plain text content modifications
        elif self.html_service.is_text_content(content_type):
            if debug_params.get('debug') == 'true':
                modified_text = f"[DEBUG MODE - Params: {debug_params}]\n\n{body_content}\n\n[END DEBUG]"
                modifications.modified_body = modified_text