from unittest                                            import TestCase
from tests.unit.Mitmproxy_Service__Fast_API__Test_Objs   import setup__service_fast_api_test_objs, TEST_API_KEY__NAME, TEST_API_KEY__VALUE


class test_Routes__Info__client(TestCase):
    @classmethod
    def setUpClass(cls):
        with setup__service_fast_api_test_objs() as _:
            cls.client = _.fast_api__client
            cls.client.headers[TEST_API_KEY__NAME] = TEST_API_KEY__VALUE

    def test__info_version(self):
        response = self.client.get('/info/versions')
        assert response.status_code == 200

    def test__info_status(self):
        response = self.client.get('/info/status')
        result = response.json()
        assert response.status_code == 200
        assert result['name'  ]     == 'osbot_fast_api_serverless'
        assert result['status']     == 'operational'