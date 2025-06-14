import unittest
from unittest.mock import patch, MagicMock
from app import app, parse_and_validate_msg, geocode_location, fetch_satellite_image_uri

class TestSatelliteSMSBot(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_parse_and_validate_msg_valid(self):
        # Test valid message parsing
        location, country_code, date = parse_and_validate_msg('Paris, FR, 2021-01-01')
        self.assertEqual(location, 'Paris')
        self.assertEqual(country_code, 'FR')
        self.assertEqual(date, '2021-01-01')

    def test_parse_and_validate_msg_invalid_format(self):
        # Test invalid message format
        with self.assertRaises(ValueError):
            parse_and_validate_msg('Invalid Format')

    def test_parse_and_validate_msg_invalid_country_code(self):
        # Test invalid country code
        with self.assertRaises(ValueError):
            parse_and_validate_msg('Paris, FRA')

    def test_parse_and_validate_msg_invalid_date(self):
        # Test invalid date format
        with self.assertRaises(ValueError):
            parse_and_validate_msg('Paris, FR, 01-01-2021')

    @patch('requests.get')
    def test_geocode_location_success(self, mock_get):
        # Mock successful geocoding response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'items': [{'position': {'lat': 48.8566, 'lng': 2.3522}}]
        }
        mock_get.return_value = mock_response

        lat, lng = geocode_location('Paris', 'FR')
        self.assertEqual(lat, 48.8566)
        self.assertEqual(lng, 2.3522)

    @patch('requests.get')
    def test_geocode_location_no_results(self, mock_get):
        # Mock geocoding response with no results
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            geocode_location('NonexistentCity', 'FR')

    @patch('requests.get')
    def test_fetch_satellite_image_uri_success(self, mock_get):
        # Mock successful NASA API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'url': 'https://api.nasa.gov/planetary/earth/imagery/example.jpg'
        }
        mock_get.return_value = mock_response

        uri = fetch_satellite_image_uri(48.8566, 2.3522, date_str=None)
        self.assertEqual(uri, 'https://api.nasa.gov/planetary/earth/imagery/example.jpg')

    @patch('requests.get')
    def test_fetch_satellite_image_uri_no_image(self, mock_get):
        # Mock NASA API response with no image
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            fetch_satellite_image_uri(48.8566, 2.3522, date_str=None)

    @patch('app.geocode_location')
    @patch('app.fetch_satellite_image_uri')
    def test_sms_endpoint_valid_request(self, mock_fetch, mock_geocode):
        # Test valid SMS request
        mock_geocode.return_value = (48.8566, 2.3522)
        mock_fetch.return_value = 'https://api.nasa.gov/planetary/earth/imagery/example.jpg'

        response = self.app.post('/sms', data={'Body': 'Paris, FR, 2021-01-01'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Your satellite image:', response.data.decode())

    def test_sms_endpoint_invalid_request(self):
        # Test invalid SMS request
        response = self.app.post('/sms', data={'Body': 'Invalid Format'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please provide a location and country code', response.data.decode())

if __name__ == '__main__':
    unittest.main() 