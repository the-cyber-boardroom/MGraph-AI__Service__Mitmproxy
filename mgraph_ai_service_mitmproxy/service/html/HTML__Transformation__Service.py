import time
from typing                                                                         import Optional

from mgraph_ai_service_html.html__fast_api.schemas.html.Schema__Html__To__Dict__Hashes__Request import Schema__Html__To__Dict__Hashes__Request
from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Float                               import Safe_Float
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode       import Enum__HTML__Transformation_Mode
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request        import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Transformation__Result  import Schema__HTML__Transformation__Result
from mgraph_ai_service_mitmproxy.schemas.html.Schema__Hashes__To__Html__Request import Schema__Hashes__To__Html__Request
from mgraph_ai_service_mitmproxy.service.html.HTML__Service__Client                 import HTML__Service__Client
from mgraph_ai_service_mitmproxy.service.cache.Proxy__Cache__Service                import Proxy__Cache__Service
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url            import Safe_Str__Url
from mgraph_ai_service_mitmproxy.service.html.HTML__Transformation__Service__Local  import HTML__Transformation__Service__Local


class HTML__Transformation__Service(Type_Safe):                                              # Orchestrates HTML transformations with caching
    html_service_client      : HTML__Service__Client  = None                                      # HTML Service HTTP client
    cache_service            : Proxy__Cache__Service  = None                                      # Cache service integration
    local_transformation_svc : HTML__Transformation__Service__Local

    def setup(self) -> 'HTML__Transformation__Service':                                      # Initialize service dependencies
        self.html_service_client = HTML__Service__Client().setup()
        self.cache_service       = Proxy__Cache__Service().setup()
        return self

    def transform_html(self, source_html   : str                                  ,          # Source HTML content
                             target_url    : str                                  ,          # Original URL (for cache key)
                             mode          : Enum__HTML__Transformation_Mode                 # Transformation mode
                       ) -> Schema__HTML__Transformation__Result:                            # Transformation result
        if not mode.is_active():                                                              # No transformation needed
            return Schema__HTML__Transformation__Result(transformed_html       = source_html       ,
                                                        transformation_mode    = mode              ,
                                                        content_type           = "text/html"       ,
                                                        cache_hit              = False             ,
                                                        transformation_time_ms = Safe_Float(0.0)   )
        if mode.is_local_transformation():
            return self._transform_locally(source_html, mode)

        cached_result = self.get_cached_transformation(target_url, mode)                    # Try to get from cache

        if cached_result:
            return cached_result

        transformation_result = self._transform_via_service(source_html, mode)               # Cache miss - call HTML Service

        if transformation_result.transformed_html:                                           # Store successful transformation in cache
            self._store_transformation_in_cache(target_url, mode, transformation_result)

        return transformation_result

    def get_cached_transformation(self, target_url : Safe_Str__Url                  ,       # Target URL for cache lookup
                                        mode       : Enum__HTML__Transformation_Mode        # Transformation mode
                                  )  -> Optional[Schema__HTML__Transformation__Result]:     # Cached result or None

        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return None

        if not mode.requires_caching():
            return None


        page_refs     = self.cache_service.get_or_create_page_entry(target_url)         # Get cache_id for this URL
        cache_id      = page_refs.cache_id
        data_key      = mode.to_cache_data_key()
        data_file_id  = f'transformation-{mode}'                                        # todo: refactor into separate method
        retrieve      = self.cache_service.cache_client.data().retrieve()
        cached_html   = retrieve.data__string__with__id_and_key(cache_id     = cache_id        ,
                                                                data_key     = data_key        ,
                                                                data_file_id = data_file_id    ,
                                                                namespace    = self.namespace())
        if cached_html:
            self.cache_service.increment_cache_hit()
            # print(f"         >>> Cache HIT for {mode.value}: {target_url}")              # todo: remove this print

            return Schema__HTML__Transformation__Result(transformed_html       = cached_html            ,
                                                        transformation_mode    = mode                   ,
                                                        content_type           = mode.to_content_type() ,
                                                        cache_hit              = True                   ,
                                                        transformation_time_ms = Safe_Float(0.0)        )
        else:
            self.cache_service.increment_cache_miss()
            return None

    def _transform_via_service(self, source_html : str                                  ,     # Source HTML to transform
                                     mode        : Enum__HTML__Transformation_Mode            # Transformation mode
                                ) -> Schema__HTML__Transformation__Result:                   # Transformation result
        start_time = time.time()

        request = Schema__HTML__Service__Request(html                = source_html ,
                                                 transformation_mode = mode        )

        response = self.html_service_client.transform_html(request)

        call_duration_ms = (time.time() - start_time) * 1000

        if response.is_successful():
            #print(f"       HTML Service took {call_duration_ms/1000:.2f}s for {mode.value}")                     # todo: remove this print

            return Schema__HTML__Transformation__Result(transformed_html       = response.body         ,
                                                        transformation_mode    = mode                  ,
                                                        content_type           = response.content_type ,
                                                        cache_hit              = False                 ,
                                                        transformation_time_ms = Safe_Float(call_duration_ms) )
        else:
            #print(f"\u26a0\ufe0f  HTML Service error: {response.error_message}")         # todo: remove this print

            return Schema__HTML__Transformation__Result(transformed_html       = source_html           ,
                                                        transformation_mode    = mode                  ,
                                                        content_type           = "text/html"           ,
                                                        cache_hit              = False                 ,
                                                        transformation_time_ms = Safe_Float(call_duration_ms) )

    def _store_transformation_in_cache(self, target_url : str                                           ,  # Target URL for cache key
                                             mode       : Enum__HTML__Transformation_Mode               ,  # Transformation mode
                                             result     : Schema__HTML__Transformation__Result             # Result to cache
                                        ) -> None:                                                       # No return value
        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return

        if not mode.requires_caching():
            return


        page_refs    = self.cache_service.get_or_create_page_entry(target_url)
        cache_id     = page_refs.cache_id
        data_key     = mode.to_cache_data_key()
        data_file_id = f'transformation-{mode}'                                         # todo: refactor into separate method
        self.cache_service.cache_client.data_store().data__store_string__with__id_and_key(body         = result.transformed_html ,
                                                                                          cache_id     = cache_id                ,
                                                                                          data_file_id = data_file_id            ,
                                                                                          data_key     = data_key                ,
                                                                                          namespace    = self.namespace()         )

        #print(f"         >>> Cached {mode.value} transformation for {target_url}")  # todo: remove this print

    def store_original_html(self, target_url    : str                               ,          # Target URL for cache key
                                  original_html : str                                          # Original HTML to store
                             ) -> None:                                                       # No return value

        if not self.cache_service or not self.cache_service.cache_config.enabled:
            return

        page_refs    = self.cache_service.get_or_create_page_entry(target_url)
        cache_id     = page_refs.cache_id
        data_file_id = 'original-html'                                                   # todo: refactor into const
        self.cache_service.cache_client.data_store().data__store_string__with__id_and_key(body         = original_html            ,
                                                                                          cache_id     = cache_id                 ,
                                                                                          data_key     = "transformations/html"   ,
                                                                                          data_file_id = data_file_id             ,
                                                                                          namespace    = self.namespace()          )

        #print(f"         >>> Stored original HTML for {target_url}")             # todo: remove this print


    def namespace(self):                                                                  # Return cache namespace
        return self.cache_service.cache_config.namespace

    def _transform_locally(self, source_html : str,
                                  mode        : Enum__HTML__Transformation_Mode
                      ) -> Schema__HTML__Transformation__Result:
        """Process transformations locally without calling HTML Service"""
        import time
        start_time = time.time()

        if mode == Enum__HTML__Transformation_Mode.XXX_RANDOM:
            # Step 1: Get hash mapping from HTML Service
            dict_hashes_request = Schema__Html__To__Dict__Hashes__Request(html=source_html)
            dict_hashes_response = self.html_service_client.get_dict_hashes(dict_hashes_request)

            if not dict_hashes_response.is_successful():
                return None
                #return self._error_result(source_html, mode)

            # Extract html_dict and hash_mapping from response
            html_dict = dict_hashes_response.html_dict
            hash_mapping = dict_hashes_response.hash_mapping

            # Step 2: Randomly mask some hashes (LOCAL)
            modified_mapping = self.local_transformation_svc.transform_xxx_random_via_hashes(
                html_dict,
                hash_mapping
            )

            # Step 3: Reconstruct HTML with masked hashes
            reconstruct_request = Schema__Hashes__To__Html__Request(html_dict=html_dict,
                                                                    hash_mapping=modified_mapping)
            reconstruct_response = self.html_service_client.reconstruct_from_hashes(reconstruct_request)

            if not reconstruct_response.is_successful():
                return None
                #return self._error_result(source_html, mode)

            transformed = reconstruct_response.body
        else:
            transformed = source_html

        call_duration_ms = (time.time() - start_time) * 1000

        return Schema__HTML__Transformation__Result(
            transformed_html       = transformed,
            transformation_mode    = mode,
            content_type           = "text/html",
            cache_hit              = False,
            transformation_time_ms = Safe_Float(call_duration_ms))


    def _error_result(self,
                 source_html : str,
                 mode        : Enum__HTML__Transformation_Mode,
                 start_time  : float
                ) -> Schema__HTML__Transformation__Result:
        """Helper to create error result (returns original HTML)"""
        call_duration_ms = (time.time() - start_time) * 1000

        return Schema__HTML__Transformation__Result(
            transformed_html       = source_html,  # Return original on error
            transformation_mode    = mode,
            content_type           = "text/html",
            cache_hit              = False,
            transformation_time_ms = Safe_Float(call_duration_ms)
        )
