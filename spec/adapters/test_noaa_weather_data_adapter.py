from spec.datagen import adapter_config
import unittest
import time

from src.adapters.noaa_weather_data_adapter import NOAAWeatherDataAdapter
from src.shared.db_client import DBClient
from src.shared.throttled_http_client import ThrottledHttpClient

class TestNOAAWeatherDataAdapter(unittest.TestCase):

    def test_create_job_data(self):
        adapter = self._inialize_adapter()
        self.assertEqual(True, True)

    def _inialize_adapter(self, overrides=None):
        return NOAAWeatherDataAdapter(DBClient({}), ThrottledHttpClient({}, 1), adapter_config(overrides))


if __name__ == '__main__':
    unittest.main()

