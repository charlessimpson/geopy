from geopy.exc import GeocoderQueryError
from geopy.geocoders import USCensus
from test.geocoders.util import GeocoderTestBase


class USCensusTestCase(GeocoderTestBase):

    @classmethod
    def setUpClass(cls):
        cls.geocoder = USCensus(timeout=10)

    def test_user_agent_custom(self):
        geocoder = USCensus(
            user_agent='my_user_agent/1.0'
        )
        self.assertEqual(geocoder.headers['User-Agent'], 'my_user_agent/1.0')

    def test_invalid_benchmark(self):
        self.geocoder = USCensus(
            benchmark='Invalid_benchmark'
        )
        with self.assertRaises(GeocoderQueryError):
            self.geocode_run(
                {'query': '175 5th Avenue NYC'},
                {},
                expect_failure=True
            )

    def test_empty_response(self):
        self.geocode_run(
            {'query': 'Invalid address with no expected results'},
            {},
            expect_failure=True
        )

    def test_geocode_with_address(self):
        location = self.geocode_run(
            {'query': '175 5th Avenue NYC'},
            {'latitude': 40.741043, 'longitude': -73.989944},
        )
        self.assertEqual('175 5TH AVE, NEW YORK, NY, 10010', location.address)

    def test_geocode_structured(self):
        query = {
            'street': '175 5th Ave',
            'city': 'New York',
            'state': 'NY',
            'zip': '10010',
        }
        location = self.geocode_run(
            {'query': query},
            {'latitude': 40.741043, 'longitude': -73.989944},
        )
        self.assertEqual('175 5TH AVE, NEW YORK, NY, 10010', location.address)

    def test_geocode_structured_partial_fields(self):
        # Matches the unstructured query above
        query = {
            'street': '175 5th Avenue',
            'city': 'NYC',
            'zip': '10010',
        }
        location = self.geocode_run(
            {'query': query},
            {'latitude': 40.741043, 'longitude': -73.989944},
        )
        self.assertEqual('175 5TH AVE, NEW YORK, NY, 10010', location.address)
