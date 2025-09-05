import os
try:
    # Load environment variables from .env file (for local development)
    from dotenv import load_dotenv
    load_dotenv()  #
except ImportError:
    # dotenv not available (like on GitHub), skip loading .env
    pass

class Config:
    """Configuration constants for TOTO system"""

    # Telegram settings
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

    # File paths
    LAST_UPDATE_FILE = "/tmp/last_update_id.txt"

    # API settings
    TELEGRAM_TIMEOUT = 10
    MESSAGE_MAX_AGE_MINUTES = 30
    MESSAGE_LIMIT = 5

    # TOTO settings
    MIN_SETS = 1
    MAX_SETS = 10
    NUMBERS_PER_SET = 6
    NUMBER_RANGE = (1, 49)

    @classmethod
    def get_telegram_api_url(cls):
        """Get Telegram API URL"""
        return f"https://api.telegram.org/bot{cls.BOT_TOKEN}"

    @classmethod
    def validate_credentials(cls):
        """Check if required credentials are present"""
        return bool(cls.BOT_TOKEN and cls.CHAT_ID)