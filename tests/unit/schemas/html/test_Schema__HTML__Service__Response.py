from unittest                                                                      import TestCase
from osbot_utils.testing.__                                                        import __
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.utils.Objects                                                     import base_classes
from osbot_utils.type_safe.primitives.core.Safe_UInt                               import Safe_UInt
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Response      import Schema__HTML__Service__Response

class test_Schema__HTML__Service__Response(TestCase):

    def test__init__(self):                                                         # Test auto-initialization
        with Schema__HTML__Service__Response() as _:
            assert type(_)         is Schema__HTML__Service__Response
            assert base_classes(_) == [Type_Safe, object]
            assert type(_.status_code)   is Safe_UInt
            assert _.status_code         == 0
            assert _.content_type        == ""
            assert _.body                == ""
            assert _.headers             == {}
            assert _.success             is False
            assert _.error_message       is None

    def test__init__with_success_response(self):                                    # Test successful response initialization
        headers = {"content-type": "text/html", "content-length": "1234"}
        body    = "<html><body>Transformed</body></html>"

        with Schema__HTML__Service__Response(status_code   = 200            ,
                                             content_type  = "text/html"    ,
                                             body          = body           ,
                                             headers       = headers        ,
                                             success       = True           ) as _:
            assert _.status_code    == 200
            assert _.content_type   == "text/html"
            assert _.body           == body
            assert _.headers        == headers
            assert _.success        is True
            assert _.error_message  is None

    def test__init__with_error_response(self):                                      # Test error response initialization
        error_msg = "HTML Service timeout after 30s"

        with Schema__HTML__Service__Response(status_code   = 504                ,
                                             content_type  = "text/plain"       ,
                                             body          = ""                 ,
                                             headers       = {}                 ,
                                             success       = False              ,
                                             error_message = error_msg          ) as _:
            assert _.status_code    == 504
            assert _.success        is False
            assert _.error_message  == error_msg

    def test__init__with_status_code_auto_conversion(self):                         # Test status code auto-conversion to Safe_UInt
        with Schema__HTML__Service__Response(status_code=200) as _:
            assert type(_.status_code) is Safe_UInt
            assert _.status_code       == 200

    def test_is_successful(self):                                                   # Test is_successful method
        # Successful response - status 200 and success True
        with Schema__HTML__Service__Response(status_code = 200 ,
                                             success     = True) as _:
            assert _.is_successful() is True

        # Failed response - status 200 but success False
        with Schema__HTML__Service__Response(status_code = 200  ,
                                             success     = False) as _:
            assert _.is_successful() is False

        # Failed response - success True but status 500
        with Schema__HTML__Service__Response(status_code = 500 ,
                                             success     = True) as _:
            assert _.is_successful() is False

        # Failed response - both False and error status
        with Schema__HTML__Service__Response(status_code = 404  ,
                                             success     = False) as _:
            assert _.is_successful() is False

    def test_is_successful__edge_cases(self):                                       # Test is_successful with edge case status codes
        # 2xx success codes
        with Schema__HTML__Service__Response(status_code = 200,
                                             success     = True) as _:
            assert _.is_successful() is True

        # Non-200 2xx codes will return False
        with Schema__HTML__Service__Response(status_code = 201  ,
                                             success     = False) as _:
            assert _.is_successful() is False

    def test__obj__comparison(self):                                                # Test .obj() method for comprehensive comparison
        body    = "<html>test</html>"
        headers = {"content-type": "text/html"}

        with Schema__HTML__Service__Response(status_code   = 200         ,
                                             content_type  = "text/html" ,
                                             body          = body        ,
                                             headers       = headers     ,
                                             success       = True        ) as _:

            assert _.obj() == __(status_code   = 200                         ,
                                 content_type  = "text/html"                 ,
                                 body          = body                        ,
                                 headers       = __(content_type='text/html'),
                                 success       = True                        ,
                                 error_message = None                        )

    def test__response_with_different_content_types(self):                          # Test different content types
        content_types = ["text/html", "text/plain", "application/json"]

        for content_type in content_types:
            with Schema__HTML__Service__Response(status_code  = 200          ,
                                                 content_type = content_type ,
                                                 success      = True         ) as _:
                assert _.content_type == content_type
                assert _.is_successful() is True