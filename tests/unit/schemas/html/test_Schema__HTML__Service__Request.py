from unittest                                                                      import TestCase

from osbot_utils.testing.__                                                        import __
from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.utils.Objects                                                     import base_classes
from mgraph_ai_service_mitmproxy.schemas.html.Schema__HTML__Service__Request       import Schema__HTML__Service__Request
from mgraph_ai_service_mitmproxy.schemas.html.Enum__HTML__Transformation_Mode      import Enum__HTML__Transformation_Mode

class test_Schema__HTML__Service__Request(TestCase):

    def test__init__(self):                                                         # Test auto-initialization
        with Schema__HTML__Service__Request() as _:
            assert type(_)         is Schema__HTML__Service__Request
            assert base_classes(_) == [Type_Safe, object]
            assert _.html          == ""                                            # Empty string default
            assert _.transformation_mode       is None                              # defaults to None

    def test__init__with_values(self):                                              # Test initialization with values
        html_content = "<html><body>Test</body></html>"
        mode         = Enum__HTML__Transformation_Mode.HASHES

        with Schema__HTML__Service__Request(html=html_content, transformation_mode=mode) as _:
            assert _.html                == html_content
            assert _.transformation_mode == mode

    def test__init__with_mode_auto_conversion(self):                                # Test mode enum auto-conversion from string
        with Schema__HTML__Service__Request(transformation_mode="dict") as _:
            assert type(_.transformation_mode) is Enum__HTML__Transformation_Mode
            assert _.transformation_mode       == Enum__HTML__Transformation_Mode.DICT

    def test_to_json_payload(self):                                                 # Test JSON payload generation
        html_content = "<html><body>Test Content</body></html>"

        with Schema__HTML__Service__Request(html=html_content, transformation_mode="hashes") as _:
            payload = _.to_json_payload()

            assert type(payload) is dict
            assert payload == {"html": html_content}                                # Only html field in payload
            assert "transformation_mode" not in payload                             # Mode not in payload

    def test_to_json_payload__empty_html(self):                                     # Test payload with empty HTML
        with Schema__HTML__Service__Request() as _:
            payload = _.to_json_payload()

            assert payload == {"html": ""}

    def test_to_json_payload__large_html(self):                                     # Test payload with large HTML
        large_html = "<html><body>" + ("x" * 10000) + "</body></html>"

        with Schema__HTML__Service__Request(html=large_html) as _:
            payload = _.to_json_payload()

            assert payload["html"]  == large_html
            assert len(payload["html"]) > 10000

    def test__obj__comparison(self):                                                # Test .obj() method for comprehensive comparison
        html_content = "<html><body>Test</body></html>"

        with Schema__HTML__Service__Request(html=html_content, transformation_mode="xxx") as _:
            assert _.obj() == __(html                = html_content                    ,
                                 transformation_mode = Enum__HTML__Transformation_Mode.XXX)