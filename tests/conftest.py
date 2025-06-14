import os
import pytest

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables before each test"""
    os.environ['TWILIO_ACCOUNT_SID'] = 'test_account_sid'
    os.environ['TWILIO_AUTH_TOKEN'] = 'test_auth_token'
    os.environ['HERE_API_KEY'] = 'test_here_api_key'
    os.environ['NASA_API_KEY'] = 'test_nasa_api_key'
    yield
    # Clean up after tests
    for key in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'HERE_API_KEY', 'NASA_API_KEY']:
        if key in os.environ:
            del os.environ[key] 