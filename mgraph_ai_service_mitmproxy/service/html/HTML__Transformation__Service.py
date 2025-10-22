# mgraph_ai_service_mitmproxy/service/html/HTML__Transformation__Service.py

import time
from typing                                                                         import Optional
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                               import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode       import Enum__HTML__Transformation_Mode
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request        import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Transformation__Result  import Schema__HTML__Transformation__Result
from mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client                 import HTML__Service__Client
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service                import Proxy__Cache__Service

class HTML__Transformation__Service(Type_Safe):                                     # Orchestrates HTML transformations with caching
    html_service_client : HTML__Service__Client  = None                             # HTML Service HTTP client
    cache_service       : Proxy__Cache__Service  = None                             # Cache service integration

    def setup(self) -> 'HTML__Transformation__Service':                             # Initialize service dependencies
        """Setup service with dependencies"""
        self.html_service_client = HTML__Service__Client().setup()
        self.cache_service       = Proxy__Cache__Service().setup()
        return self

    def transform_html(self, source_html   : str,                                   # Source HTML content
                             target_url    : str,                                   # Original URL (for cache key)
                             mode          : Enum__HTML__Transformation_Mode        # Transformation mode
                       ) -> Schema__HTML__Transformation__Result:                   # Transformation result
        """Transform HTML content with specified mode, using cache when possible"""

        if not mode.is_active():                                                    # No transformation needed
            return Schema__HTML__Transformation__Result(
                transformed_html       = source_html       ,
                transformation_mode    = mode              ,
                content_type           = "text/html"       ,
                cache_hit              = False             ,
                transformation_time_ms = Safe_Float(0.0)
            )

        cached_result = self._get_cached_transformation(target_url, mode)           # Try to get from cache
        if cached_result:
            return cached_result

        transformation_result = self._transform_via_service(source_html, mode)      # Cache miss - call HTML Service

        if transformation_result.transformed_html:                                   # Store successful transformation in cache
            self._store_transformation_in_cache(target_url, mode, transformation_result)

        return transformation_result

    # todo: remove the _ from the name
    def _get_cached_transformation(self, target_url : str,                                # Target URL for cache lookup
                                         mode       : Enum__HTML__Transformation_Mode     # Transformation mode
                                    ) -> Optional[Schema__HTML__Transformation__Result]:  # Cached result or None
        """Try to retrieve transformation from cache"""
        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return None

        if not mode.requires_caching():
            return None

        try:
            page_refs = self.cache_service.get_or_create_page_entry(target_url)     # Get cache_id for this URL
            cache_id  = page_refs.cache_id
            data_key  = mode.to_cache_data_key()
            data_file_id = f'transformation-{mode}'              # todo: refactor into separate method
            cached_html = self.cache_service.cache_client.data().retrieve().data__string__with__id_and_key(
                cache_id     = cache_id        ,
                data_key     = data_key        ,
                data_file_id = data_file_id    ,
                namespace    = self.namespace())

            if cached_html:
                self.cache_service.increment_cache_hit()
                print(f"         >>> Cache HIT for {mode.value}: {target_url}")

                return Schema__HTML__Transformation__Result(
                    transformed_html       = cached_html              ,
                    transformation_mode    = mode                     ,
                    content_type           = mode.to_content_type()   ,
                    cache_hit              = True                     ,
                    transformation_time_ms = Safe_Float(0.0)
                )
            else:
                self.cache_service.increment_cache_miss()
                return None

        except Exception as e:
            print(f"⚠️  Cache retrieval error (non-fatal): {e}")
            return None

    def _transform_via_service(self, source_html : str,                             # Source HTML to transform
                                     mode        : Enum__HTML__Transformation_Mode  # Transformation mode
                                ) -> Schema__HTML__Transformation__Result:          # Transformation result
        """Call HTML Service to perform transformation"""
        start_time = time.time()

        request = Schema__HTML__Service__Request(
            html                = source_html ,
            transformation_mode = mode
        )

        response = self.html_service_client.transform_html(request)

        call_duration_ms = (time.time() - start_time) * 1000

        if response.is_successful():
            print(f"       HTML Service took {call_duration_ms/1000:.2f}s for {mode.value}")

            return Schema__HTML__Transformation__Result(
                transformed_html       = response.body                ,
                transformation_mode    = mode                         ,
                content_type           = response.content_type        ,
                cache_hit              = False                        ,
                transformation_time_ms = Safe_Float(call_duration_ms)
            )
        else:
            print(f"⚠️  HTML Service error: {response.error_message}")

            return Schema__HTML__Transformation__Result(                            # Return original HTML on error
                transformed_html       = source_html              ,
                transformation_mode    = mode                     ,
                content_type           = "text/html"              ,
                cache_hit              = False                    ,
                transformation_time_ms = Safe_Float(call_duration_ms)
            )

    def _store_transformation_in_cache(self, target_url   : str,                    # Target URL for cache key
                                             mode         : Enum__HTML__Transformation_Mode,  # Transformation mode
                                             result       : Schema__HTML__Transformation__Result  # Result to cache
                                        ) -> None:                                  # No return value
        """Store transformation result in cache"""
        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return

        if not mode.requires_caching():
            return

        try:
            page_refs    = self.cache_service.get_or_create_page_entry(target_url)
            cache_id     = page_refs.cache_id
            data_key     = mode.to_cache_data_key()
            data_file_id = f'transformation-{mode}'              # todo: refactor into separate method
            self.cache_service.cache_client.data_store().data__store_string__with__id_and_key(
                body         = result.transformed_html ,
                cache_id     = cache_id                ,
                data_file_id = data_file_id            ,
                data_key     = data_key                ,
                namespace    = self.namespace()        )

            print(f"         >>> Cached {mode.value} transformation for {target_url}")

        except Exception as e:
            print(f"⚠️  Cache storage error (non-fatal): {e}")

    def store_original_html(self, target_url   : str,                               # Target URL for cache key
                                  original_html: str                                # Original HTML to store
                             ) -> None:                                             # No return value
        """Store original HTML in cache for provenance"""
        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return

        try:
            page_refs    = self.cache_service.get_or_create_page_entry(target_url)
            cache_id     = page_refs.cache_id
            data_file_id = 'original-html'              # todo: refactor into const
            self.cache_service.cache_client.data_store().data__store_string__with__id_and_key(
                body         = original_html            ,
                cache_id     = cache_id                 ,
                data_key     = "transformations/html"   ,
                data_file_id = data_file_id             ,
                namespace    = self.namespace()         )

            print(f"         >>> Stored original HTML for {target_url}")

        except Exception as e:
            print(f"⚠️  Original HTML storage error (non-fatal): {e}")

    def namespace(self):
        return self.cache_service.cache_config.namespace