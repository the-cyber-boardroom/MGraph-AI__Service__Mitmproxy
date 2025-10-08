import re
import json
from typing                                                            import Dict, Optional
from osbot_utils.type_safe.Type_Safe                                   import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.debug.Schema__HTML__Injection import Schema__HTML__Injection


class Proxy__HTML__Service(Type_Safe):                           # HTML content manipulation service

    def create_debug_banner(self,
                           debug_params : Dict[str, str],        # Debug parameters to display
                           request_path : str                    # Request path
                           ) -> str:                             # HTML for debug banner
        """Create HTML debug banner"""
        banner_html = f"""
        <div style="position:fixed;top:0;left:0;right:0;background:#ff0;color:#000;padding:10px;z-index:999999;font-family:monospace;border-bottom:2px solid #f00">
            🔧 DEBUG MODE | Params: {json.dumps(debug_params)} | Path: {request_path}
        </div>
        """
        return banner_html

    def create_debug_panel(self,
                          request_info  : Dict,                  # Request information
                          response_info : Dict,                  # Response information
                          debug_params  : Dict[str, str]         # Debug parameters
                          ) -> str:                              # HTML for debug panel
        """Create HTML debug panel"""
        panel_html = f"""
        <div id="debug-panel" style="position:fixed;bottom:0;left:0;right:0;background:#222;color:#0f0;padding:20px;max-height:300px;overflow:auto;font-family:monospace;z-index:999999">
            <h3 style="color:#0f0;margin:0 0 10px 0">🔧 Debug Panel</h3>
            <details>
                <summary>Request Info</summary>
                <pre style="color:#0f0">{json.dumps(request_info, indent=2)}</pre>
            </details>
            <details>
                <summary>Response Headers</summary>
                <pre style="color:#0f0">{json.dumps(response_info.get("headers", {}), indent=2)}</pre>
            </details>
            <details>
                <summary>Debug Params</summary>
                <pre style="color:#0f0">{json.dumps(debug_params, indent=2)}</pre>
            </details>
            <button onclick="document.getElementById('debug-panel').style.display='none'" style="position:absolute;top:10px;right:10px">X</button>
        </div>
        """
        return panel_html

    def inject_into_html(self,
                        html_content : str,                      # Original HTML content
                        injection    : Schema__HTML__Injection   # Injection configuration
                        ) -> Optional[str]:                      # Modified HTML or None
        """Inject debug content into HTML"""
        if not injection.has_injections():
            return None

        modified_html = html_content
        injected = False

        # Inject debug banner
        if injection.inject_banner and injection.banner_content:
            # Try to inject after <body> tag
            if "<body" in modified_html:
                modified_html = re.sub(
                    r'(<body[^>]*>)',
                    r'\1' + injection.banner_content,
                    modified_html,
                    count=1
                )
                injected = True
            # Fallback: inject before </body>
            elif "</body>" in modified_html:
                modified_html = modified_html.replace(
                    "</body>",
                    f"{injection.banner_content}</body>",
                    1
                )
                injected = True

        # Inject debug panel
        if injection.inject_panel and injection.panel_content:
            # Try to inject before </body>
            if "</body>" in modified_html:
                modified_html = modified_html.replace(
                    "</body>",
                    f"{injection.panel_content}</body>",
                    1
                )
                injected = True

        if injected:
            injection.injection_applied = True
            return modified_html

        return None

    def apply_text_replacement(self,
                              content      : str,                # Content to modify
                              old_text     : str,                # Text to replace
                              new_text     : str                 # Replacement text
                              ) -> Optional[str]:                # Modified content or None
        """Apply text replacement to content"""
        if old_text not in content:
            return None

        # Wrap new text in markers for visibility
        marked_new_text = f'[{new_text}]'
        modified_content = content.replace(old_text, marked_new_text)

        return modified_content

    def is_html_content(self, content_type: str) -> bool:        # Check if content is HTML
        """Check if content type is HTML"""
        if not content_type:
            return False
        return "text/html" in content_type.lower()

    def is_json_content(self, content_type: str) -> bool:        # Check if content is JSON
        """Check if content type is JSON"""
        if not content_type:
            return False
        return "application/json" in content_type.lower()

    def is_text_content(self, content_type: str) -> bool:        # Check if content is plain text
        """Check if content type is plain text"""
        if not content_type:
            return False
        return "text/plain" in content_type.lower()