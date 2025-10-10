import re
import time
from datetime                                                                           import datetime
from urllib.parse                                                                       import urlparse
from typing                                                                             import Optional, Dict
from mgraph_ai_service_cache_client.client_contract.Service__Fast_API__Client           import Service__Fast_API__Client
from mgraph_ai_service_cache_client.schemas.cache.enums.Enum__Cache__Store__Strategy    import Enum__Cache__Store__Strategy
from osbot_utils.type_safe.Type_Safe                                                    import Type_Safe
from mgraph_ai_service_mitmproxy.service.cache.schemas.Enum__Cache__Transformation_Type import Enum__Cache__Transformation_Type
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Config            import Schema__Cache__Config
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Page_Entry        import Schema__Cache__Page_Entry
from mgraph_ai_service_mitmproxy.service.cache.schemas.Schema__Cache__Stats             import Schema__Cache__Stats

DEFAULT__TEXT__CACHE_NOT_FOUND = 'Not found'

class Proxy__Cache__Service(Type_Safe):                         # Cache service for WCF transformations
    cache_client      : Service__Fast_API__Client               # Cache service client (Service__Fast_API__Client)
    cache_config      : Schema__Cache__Config                   # Configuration
    stats             : Schema__Cache__Stats                    # Cache statistics
    cache_key_to_id   : Dict[str, str]                          # Map cache_key to cache_id for quick lookups

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'cache_key_to_id') or self.cache_key_to_id is None:
            self.cache_key_to_id = {}                           # Initialize mapping dictionary

    def url_to_cache_key(self, target_url : str                 # Convert URL to hierarchical cache_key
                          ) -> str:                             # Hierarchical cache_key
        """
        Convert URL to hierarchical cache_key.

        Examples:
            https://example.com/articles/hello-world
            → sites/example.com/pages/articles/hello-world

            https://example.com/blog/post-123?utm_source=twitter
            → sites/example.com/pages/blog/post-123
        """
        parsed = urlparse(target_url)

        # Extract domain (including subdomain)
        domain = parsed.netloc

        # Extract path (remove leading/trailing slashes, ignore query/fragment)
        path = parsed.path.strip('/')

        # Handle empty path (homepage)
        if not path:
            path = "index"

        # Sanitize path (replace problematic characters)
        path = self._sanitize_url_path(path)

        # Construct hierarchical cache_key
        cache_key = f"sites/{domain}/pages/{path}"

        return cache_key

    def _sanitize_url_path(self, path : str                     # Sanitize URL path for use in cache_key
                            ) -> str:                           # Sanitized path
        """
        Sanitize URL path for use in cache_key.

        - Keep alphanumeric, hyphens, underscores, forward slashes
        - Replace other characters with hyphens
        """
        # Keep: a-z A-Z 0-9 - _ /
        sanitized = re.sub(r'[^a-zA-Z0-9\-_/]', '-', path)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        return sanitized

    def get_or_create_page_entry(self, target_url : str         # Get existing page cache_id or create new page entry
                                  ) -> str:                     # cache_id for the page
        """
        Get existing page cache_id or create new page entry.

        Uses KEY_BASED strategy with semantic cache_key.
        Returns: cache_id for the page (used for child data storage)
        """
        cache_key = self.url_to_cache_key(target_url)

        # Check if we already have this cache_id in memory
        if cache_key in self.cache_key_to_id:
            return self.cache_key_to_id[cache_key]

        # Try to retrieve existing page by cache_key
        # NOTE: There's no direct retrieve__cache_key method, so we attempt storage
        # which returns existing cache_id if content already exists (content-addressable)

        parsed = urlparse(target_url)

        page_entry = Schema__Cache__Page_Entry( url           = target_url,
                                                cache_key     = cache_key,
                                                domain        = parsed.netloc,
                                                path          = parsed.path,
                                                created_at    = datetime.utcnow().isoformat(),
                                                last_accessed = datetime.utcnow().isoformat(),
                                                access_count  = 1)

        try:
            # Store with KEY_BASED strategy using semantic cache_key
            result = self.cache_client.store().store__json__cache_key(namespace = self.cache_config.namespace,
                                                                      strategy  = Enum__Cache__Store__Strategy.KEY_BASED,
                                                                      cache_key = cache_key,
                                                                      file_id   = "page-entry",                       # Fixed file_id for page entries
                                                                      body      = page_entry.json()
            )

            cache_id = result["cache_id"]

            # Store mapping for quick future lookups
            self.cache_key_to_id[cache_key] = cache_id

            # Update stats (only if this is a new page)
            if self.cache_config.track_stats:
                self.stats.total_pages_cached += 1

            return cache_id

        except Exception as e:
            # If storage fails, we can't proceed
            print(f"⚠️  Cache error storing page entry: {e}")
            raise

    def page_exists(self, target_url : str                      # Check if page exists in cache
                     ) -> bool:                                 # Page exists
        """Check if page exists in cache"""
        cache_key = self.url_to_cache_key(target_url)

        # Check in-memory mapping first
        if cache_key in self.cache_key_to_id:
            return True

        # Try to get cache_id (which will create if not exists)
        # This is not ideal for "exists" check, but without retrieve__cache_key
        # we don't have a better option
        try:
            self.get_or_create_page_entry(target_url)
            return True
        except Exception:
            return False

    def get_cached_transformation(self, target_url  : str       ,  # Get cached WCF transformation
                                        wcf_command : str
                                   ) -> Optional[str]:          # Cached content or None
        """
        Retrieve cached WCF transformation.

        Returns: Cached content string, or None if not cached
        """
        if not self.cache_config.enabled:
            return None

        start_time = time.time()
        cache_key  = self.url_to_cache_key(target_url)          # todo:  see why this is not being used

        # Get page cache_id (from mapping or by creating entry)
        try:
            cache_id = self.get_or_create_page_entry(target_url)
        except Exception as e:
            # Can't get cache_id, treat as cache miss
            return None

        # Get transformation data
        data_key = self._wcf_command_to_data_key(wcf_command)

        try:
            transformation = self.cache_client.data().retrieve().data__string__with__id_and_key(
                cache_id     = cache_id,
                namespace    = self.cache_config.namespace,
                data_key     = data_key,
                data_file_id = self.cache_config.data_file_id
            )
            if transformation == DEFAULT__TEXT__CACHE_NOT_FOUND:            # check if we got a Not found (aka 404) error
                return None
            # Update stats
            duration_ms = (time.time() - start_time) * 1000
            self._update_cache_hit_stats(duration_ms)

            return transformation
        except Exception as e:
            print(e)
            # Transformation not cached
            return None

    def store_transformation(self, target_url  : str            ,  # Store WCF transformation result
                                   wcf_command : str            ,
                                   content     : str            ,
                                   metadata    : dict
                              ) -> str:                         # cache_id of the page entry
        """
        Store WCF transformation result as child data.

        Args:
            target_url: Original URL that was transformed
            wcf_command: WCF command type (e.g., "url-to-html")
            content: Transformed content (HTML, text, etc.)
            metadata: WCF call metadata (response time, status, etc.)

        Returns: cache_id of the page entry
        """
        if not self.cache_config.enabled:
            return ""

        # Ensure page entry exists
        cache_id = self.get_or_create_page_entry(target_url)

        # Convert WCF command to data_key
        data_key = self._wcf_command_to_data_key(wcf_command)

        # Store transformation content as child data
        self.cache_client.data_store().data__store_string__with__id_and_key(
            cache_id     = cache_id,
            namespace    = self.cache_config.namespace,
            data_key     = data_key,
            data_file_id = self.cache_config.data_file_id,
            body         = content
        )

        # Store metadata (optional, if enabled)
        if self.cache_config.cache_metadata:
            metadata_key = f"{data_key}/metadata"

            self.cache_client.data_store().data__store_json__with__id_and_key(
                cache_id     = cache_id,
                namespace    = self.cache_config.namespace,
                data_key     = metadata_key,
                data_file_id = self.cache_config.data_file_id,
                body         = metadata
            )

        return cache_id

    def has_cached_transformation(self, target_url  : str       ,  # Check if transformation is cached
                                        wcf_command : str
                                   ) -> bool:                   # Is cached
        if not self.cache_config.enabled:
            return False

        cached = self.get_cached_transformation(target_url, wcf_command)

        return cached is not None

    def increment_cache_hit(self):                              # Record cache hit
        """Record cache hit"""
        if self.cache_config.track_stats:
            self.stats.cache_hits       += 1
            self.stats.wcf_calls_saved  += 1

    def increment_cache_miss(self):                             # Record cache miss
        """Record cache miss"""
        if self.cache_config.track_stats:
            self.stats.cache_misses += 1

    def get_cache_stats(self) -> dict:                          # Get cache statistics
        """Get cache statistics"""
        return {
            "enabled"                      : self.cache_config.enabled,
            "hit_rate"                     : self.stats.hit_rate(),
            "cache_hits"                   : self.stats.cache_hits,
            "cache_misses"                 : self.stats.cache_misses,
            "wcf_calls_saved"              : self.stats.wcf_calls_saved,
            "total_pages_cached"           : self.stats.total_pages_cached,
            "avg_cache_hit_time_ms"        : self.stats.avg_cache_hit_time_ms,
            "avg_cache_miss_time_ms"       : self.stats.avg_cache_miss_time_ms,
            "avg_wcf_call_time_ms"         : self.stats.avg_wcf_call_time_ms,
            "estimated_time_saved_seconds" : self.stats.estimated_time_saved_seconds()
        }

    def _wcf_command_to_data_key(self, wcf_command : str        # Convert WCF command to data_key path
                                   ) -> str:                    # data_key path
        """
        Convert WCF command to data_key path for child data storage.

        Examples:
            url-to-html          → transformations/html
            url-to-text          → transformations/text
            url-to-ratings       → transformations/ratings
        """
        try:
            command_type = Enum__Cache__Transformation_Type(wcf_command)
            return command_type.to_data_key()
        except ValueError:
            # Unknown command - use generic path
            return f"transformations/{wcf_command.replace('-', '_')}"

    def _update_cache_hit_stats(self, duration_ms : float       # Update cache hit statistics
                                 ) -> None:                     # No return
        """Update cache hit statistics"""
        if not self.cache_config.track_stats:
            return

        # Update running average
        total_hits = float(self.stats.cache_hits)
        if total_hits == 0:
            self.stats.avg_cache_hit_time_ms = duration_ms
        else:
            current_avg = self.stats.avg_cache_hit_time_ms
            self.stats.avg_cache_hit_time_ms = ((current_avg * total_hits) + duration_ms) / (total_hits + 1)