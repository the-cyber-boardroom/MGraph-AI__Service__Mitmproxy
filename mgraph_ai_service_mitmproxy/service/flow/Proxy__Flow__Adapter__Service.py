from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Application_Result  import Schema__Flow__Application_Result
from mgraph_ai_service_mitmproxy.schemas.flow.Schema__Flow__Extraction_Result   import Schema__Flow__Extraction_Result
from mgraph_ai_service_mitmproxy.service.flow.Proxy__Flow__Applicator__Service  import Proxy__Flow__Applicator__Service
from mgraph_ai_service_mitmproxy.service.flow.Proxy__Flow__Extractor__Service   import Proxy__Flow__Extractor__Service
from mgraph_ai_service_mitmproxy.service.proxy.Proxy__Response__Service         import Proxy__Response__Service
from typing                                                                     import Any, Tuple

class Proxy__Flow__Adapter__Service(Type_Safe):                  # Complete flow adapter orchestrator
    extractor_service : Proxy__Flow__Extractor__Service          # Extract data from flow
    applicator_service: Proxy__Flow__Applicator__Service         # Apply results to flow
    response_service  : Proxy__Response__Service                 # Process response data

    def process_flow(self, flow: Any                            # Main entry point: process complete flow
                    ) -> Tuple[Schema__Flow__Extraction_Result,
                              Schema__Flow__Application_Result]:  # Extraction and application results
        """
        Main entry point: Complete flow processing

        This is the single method that should be called from mitmproxy addon.
        It handles:
        1. Extracting data from flow
        2. Processing response (debug, stats, CORS, etc.)
        3. Applying results back to flow

        Returns tuple of (extraction_result, application_result)
        """
        # Step 1: Extract data from flow
        extraction_result = self.extractor_service.extract_from_flow(flow)

        # Check for extraction errors
        if extraction_result.has_error():
            # Apply error response to flow
            application_result = self.applicator_service.apply_error_response(
                flow,
                extraction_result.extraction_error,
                status_code=500
            )
            return (extraction_result, application_result)

        # Step 2: Process response data
        try:
            processing_result = self.response_service.process_response(
                extraction_result.response_data
            )

            # Check for processing errors
            if processing_result.has_error():
                # Apply error response
                application_result = self.applicator_service.apply_error_response(
                    flow,
                    processing_result.processing_error,
                    status_code=500
                )
                return (extraction_result, application_result)

        except Exception as e:
            # Apply error response
            application_result = self.applicator_service.apply_error_response(
                flow,
                f"Response processing failed: {str(e)}",
                status_code=500
            )
            return (extraction_result, application_result)

        # Step 3: Apply results to flow
        application_result = self.applicator_service.apply_to_flow(flow, processing_result)

        return (extraction_result, application_result)

    def should_process_flow(self, flow: Any                     # Check if flow should be processed
                           ) -> bool:                            # Should process
        """
        Quick check if flow should be processed

        Can be used in request() hook to decide early if processing needed
        """
        return self.extractor_service.has_debug_commands(flow)

    def extract_only(self, flow: Any                            # Extract data without processing
                    ) -> Schema__Flow__Extraction_Result:       # Extraction result
        """
        Extract data from flow without processing

        Useful for inspecting request data before response is available
        """
        return self.extractor_service.extract_from_flow(flow)

    def get_processing_summary(self,                            # Get summary of processing
                              extraction_result  : Schema__Flow__Extraction_Result,
                              application_result : Schema__Flow__Application_Result
                              ) -> dict:                         # Summary dict
        """Get a complete summary of flow processing"""
        return {
            'extraction': extraction_result.get_summary(),
            'application': application_result.get_summary(),
            'flow_id': extraction_result.flow_id or application_result.flow_id,
            'overall_success': (extraction_result.extraction_success and
                              application_result.application_success)
        }