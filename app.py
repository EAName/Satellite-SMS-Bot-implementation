import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from datetime import datetime, date
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

def parse_and_validate_msg(message: str):
    """Parses and validates the incoming message format"""
    # Expected format: "location, country code, date (optional)"
    parts = [part.strip() for part in message.split(',')]
    
    if len(parts) < 2:
        raise ValueError('Please provide a location and country code in the format: "location, country code, date (optional)"')
    
    location = parts[0]
    country_code = parts[1].upper()
    
    # Validate country code format (2 letters)
    if not re.match(r'^[A-Z]{2}$', country_code):
        raise ValueError('Country code must be 2 letters (e.g., US, UK, FR)')
    
    # Parse date if provided, otherwise use today
    date = None
    if len(parts) > 2:
        try:
            date = datetime.strptime(parts[2].strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    return location, country_code, date

def geocode_location(location: str, country_code: str):
    """Geocodes a location into a latitude and longitude"""
    api_key = os.environ.get('HERE_API_KEY')
    # Convert 2-letter country code to 3-letter ISO code
    country_code_map = {
        'FR': 'FRA',
        'US': 'USA',
        'GB': 'GBR',
        'DE': 'DEU',
        'IT': 'ITA',
        'ES': 'ESP',
        'CA': 'CAN',
        'AU': 'AUS',
        'JP': 'JPN',
        'CN': 'CHN',
        # Add more mappings as needed
    }
    iso_country_code = country_code_map.get(country_code, country_code)
    response = requests.get('https://geocode.search.hereapi.com/v1/geocode', params={
        'q': location,
        'in': f'countryCode:{iso_country_code}',
        'apiKey': api_key
    })
    response.raise_for_status()

    json = response.json()

    if 'items' not in json or len(json['items']) < 1:
        raise ValueError('We could not geocode your location. Is it correct?')

    position = json['items'][0]['position']
    return position['lat'], position['lng']

def fetch_satellite_image_uri(lat, lng, date_str=None):
    """Fetches the URI of a satellite image of the given location for the given time"""
    api_key = os.environ.get('NASA_API_KEY')
    from datetime import date as dt_date
    response = requests.get('https://api.nasa.gov/planetary/earth/assets', params={
        'lat': lat,
        'lon': lng,
        'date': date_str or dt_date.today().strftime('%Y-%m-%d'),
        'dim': '0.15',
        'api_key': api_key
    })

    if response.status_code == 404:
        raise ValueError('No satellite image is available for the specified date and time.')

    response.raise_for_status()

    json = response.json()

    return json['url']

def respond(message, media_url=None):
    """Creates a TwiML response with optional media"""
    resp = MessagingResponse()
    if media_url:
        resp.message(message).media(media_url)
    else:
        resp.message(message)
    return str(resp)

@app.route('/sms', methods=['POST'])
def sms():
    print("Received SMS request")
    print("Request values:", request.values)
    message_text = request.values.get('Body', None)
    from_number = request.values.get('From', None)
    print(f"Message from: {from_number}")

    # Ensure there is a message
    if message_text is None:
        print("No message body found")
        return respond('The location was malformed. Please try again.')

    try:
        print(f"Processing message: {message_text}")
        # Pull the location, country, and date out of the string
        location, country_code, date = parse_and_validate_msg(message_text)
        print(f"Parsed values - Location: {location}, Country: {country_code}, Date: {date}")

        # Geocode the location into coordinates
        lat, lng = geocode_location(location, country_code)
        print(f"Geocoded coordinates - Lat: {lat}, Lng: {lng}")

        # Fetch the image uri
        uri = fetch_satellite_image_uri(lat, lng, date)
        print(f"Fetched image URI: {uri}")

        # Send the MMS response
        return respond('Your satellite image:', uri)
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return respond(str(e))
    except Exception as e:
        print(f"Error in /sms endpoint: {str(e)}")
        return respond('An error occurred')

if __name__ == '__main__':
    app.run(debug=True) 