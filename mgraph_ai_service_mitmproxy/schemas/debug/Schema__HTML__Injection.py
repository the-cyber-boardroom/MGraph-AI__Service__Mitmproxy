from osbot_utils.type_safe.Type_Safe                                                 import Type_Safe
from typing                                                                          import Dict, Optional

class Schema__HTML__Injection(Type_Safe):                        # HTML content injection configuration
    inject_banner     : bool            = False                  # Whether to inject debug banner
    inject_panel      : bool            = False                  # Whether to inject debug panel
    banner_content    : Optional[str]   = None                   # HTML content for banner
    panel_content     : Optional[str]   = None                   # HTML content for panel
    injection_applied : bool            = False                  # Whether injection was successful

    def has_injections(self) -> bool:                            # Check if any injections configured
        """Check if any HTML injections are configured"""
        return self.inject_banner or self.inject_panel

    def get_injections_summary(self) -> Dict[str, bool]:         # Get summary of injections
        """Get a summary of what injections were applied"""
        return {
            'banner_injected': self.inject_banner and self.injection_applied,
            'panel_injected': self.inject_panel and self.injection_applied
        }