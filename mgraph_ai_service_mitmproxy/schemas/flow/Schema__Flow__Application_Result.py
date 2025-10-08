from osbot_utils.type_safe.Type_Safe     import Type_Safe
from typing                              import Optional, List

class Schema__Flow__Application_Result(Type_Safe):               # Flow application result
    application_success : bool                  = True           # Whether application succeeded
    application_error   : Optional[str]         = None           # Error message if failed
    flow_id             : Optional[str]         = None           # Flow identifier
    status_applied      : bool                  = False          # Whether status was applied
    headers_applied     : bool                  = False          # Whether headers were applied
    body_applied        : bool                  = False          # Whether body was applied
    headers_count       : int                   = 0              # Number of headers applied
    body_size           : int                   = 0              # Size of body applied
    modifications_made  : List[str]                              # List of modifications made

    def has_error(self) -> bool:                                 # Check if application failed
        """Check if application encountered an error"""
        return self.application_error is not None

    def add_modification(self, modification: str):               # Track a modification
        """Track a modification that was made"""
        self.modifications_made.append(modification)

    def get_summary(self) -> dict:                               # Get application summary
        """Get summary of application"""
        return {
            'success': self.application_success,
            'error': self.application_error,
            'flow_id': self.flow_id,
            'status_applied': self.status_applied,
            'headers_applied': self.headers_applied,
            'body_applied': self.body_applied,
            'headers_count': self.headers_count,
            'body_size': self.body_size,
            'modifications': self.modifications_made
        }