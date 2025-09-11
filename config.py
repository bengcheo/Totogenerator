import os
from datetime import datetime
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
    CURRENT_DATE_TIME = datetime.now().strftime("%Y-%m-%d")

    # TOTO settings
    MIN_SETS = 1
    MAX_SETS = 10
    NUMBERS_PER_SET = 6
    NUMBER_RANGE = (1, 49)

    # Toto-scraping settings
    url = "https://en.lottolyzer.com/history/singapore/toto"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    FILENAME_URL = f"https://script.google.com/macros/s/AKfycbxTAFg7rJAIqq9r_kEYY8vMmJlVTpJVa6p2JnhxAidSyG2BlMWN4v45C1yMMWVOyTzTfw/exec"

    @classmethod
    def get_telegram_api_url(cls):
        """Get Telegram API URL"""
        return f"https://api.telegram.org/bot{cls.BOT_TOKEN}"

    @classmethod
    def validate_credentials(cls):
        """Check if required credentials are present"""
        return bool(cls.BOT_TOKEN and cls.CHAT_ID)