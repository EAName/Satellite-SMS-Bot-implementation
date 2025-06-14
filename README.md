# NASA Satellite Imagery SMS Bot

A Flask application that allows users to request satellite imagery via SMS using Twilio, NASA's Earth API, and HERE Geocoding API.

## Features

- Receive SMS messages with location requests
- Geocode locations using HERE API
- Fetch satellite imagery using NASA's Earth API
- Send back satellite images via MMS

## Prerequisites

- Python 3.9+
- Twilio Account
- NASA API Key
- HERE API Key
- ngrok (for local development)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Satellite_SMS.git
cd Satellite_SMS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API credentials:
```
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
NASA_API_KEY=your_nasa_api_key_here
HERE_API_KEY=your_here_api_key_here
```

4. Start the Flask application:
```bash
python app.py
```

5. Start ngrok to expose your local server:
```bash
ngrok http 5000
```

6. Update your Twilio webhook URL to point to your ngrok URL + `/sms`

## Usage

Send an SMS to your Twilio number in the format:
```
location, country code, date (optional)
```

Example:
```
washington d.c., us, 2021-02-01
```

## API Keys

- [Twilio](https://www.twilio.com/try-twilio)
- [NASA API](https://api.nasa.gov/)
- [HERE API](https://developer.here.com/)

## License

MIT 