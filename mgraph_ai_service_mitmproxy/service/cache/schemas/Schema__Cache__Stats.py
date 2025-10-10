from osbot_utils.type_safe.Type_Safe                                                            import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_UInt                                           import Safe_UInt

class Schema__Cache__Stats(Type_Safe):                          # Cache statistics for monitoring
    enabled                  : bool      = True                 # Whether cache is enabled
    cache_hits               : Safe_UInt = Safe_UInt(0)         # Number of cache hits
    cache_misses             : Safe_UInt = Safe_UInt(0)         # Number of cache misses
    wcf_calls_saved          : Safe_UInt = Safe_UInt(0)         # Number of WCF calls avoided
    total_pages_cached       : Safe_UInt = Safe_UInt(0)         # Total unique pages cached

    # Performance metrics (in milliseconds)
    avg_cache_hit_time_ms    : float = 0.0                      # Average cache hit latency
    avg_cache_miss_time_ms   : float = 0.0                      # Average cache miss latency
    avg_wcf_call_time_ms     : float = 0.0                      # Average WCF call time

    def hit_rate(self) -> float:                                # Calculate cache hit rate (0.0 to 1.0)
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return float(self.cache_hits) / float(total)

    # todo: see if we really need this feature (and stats)
    def estimated_time_saved_seconds(self) -> float:            # Estimate total time saved by cache hits
        if self.cache_hits == 0:
            return 0.0
        return (float(self.cache_hits) * 2.0) - (float(self.cache_hits) * (self.avg_cache_hit_time_ms / 1000.0)) # Assume average WCF call is 2 seconds