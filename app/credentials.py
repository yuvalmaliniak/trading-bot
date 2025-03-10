# credentials.py

# Global dictionary to store user credentials
USER_CREDENTIALS = {}

def store_credentials(email, api_key, api_secret):
    """Stores API credentials for a specific user."""
    USER_CREDENTIALS[email] = {
        "api_key": api_key,
        "api_secret": api_secret
    }

def get_credentials(email):
    """Retrieves API credentials for a specific user."""
    return USER_CREDENTIALS.get(email, None)
