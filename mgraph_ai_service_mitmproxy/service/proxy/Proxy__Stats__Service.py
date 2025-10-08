from typing                                                         import Dict, Any, List
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.proxy.Schema__Proxy__Stats import Schema__Proxy__Stats


class Proxy__Stats__Service(Type_Safe):                              # Statistics tracking service
    stats : Schema__Proxy__Stats                                     # Current statistics

    def increment_request(self, host : str ,                         # Record new request
                                path : str
                          ) -> None:
        self.stats.total_requests += 1
        # self.stats.hosts_seen.add(host)
        # self.stats.paths_seen.add(path)

    def increment_response(self, bytes_processed : int               # Record new response
                           ) -> None:
        self.stats.total_responses       += 1
        self.stats.total_bytes_processed += bytes_processed

    def increment_content_modification(self) -> None:                # Record content modification
        self.stats.content_modifications += 1

    def get_stats(self) -> Dict[str, Any]:                           # Get current statistics
        return {
            "total_requests"       : self.stats.total_requests        ,
            "total_responses"      : self.stats.total_responses       ,
            # "unique_hosts"         : list(self.stats.hosts_seen)      ,
            # "unique_paths"         : list(self.stats.paths_seen)      ,
            # "hosts_count"          : len(self.stats.hosts_seen)       ,
            # "paths_count"          : len(self.stats.paths_seen)       ,
            "total_bytes_processed": self.stats.total_bytes_processed ,
            "content_modifications": self.stats.content_modifications
        }

    def reset_stats(self) -> Dict[str, Any]:                         # Reset statistics
        old_stats = self.get_stats()

        self.stats = Schema__Proxy__Stats()                          # Create fresh stats

        return {
            "message"        : "Stats reset successfully" ,
            "previous_stats" : old_stats
        }