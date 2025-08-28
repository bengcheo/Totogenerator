import requests
import json
import os
from datetime import datetime


def load_toto_numbers():
    """Load generated TOTO numbers from file"""
    try:
        with open('toto_numbers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def create_telegram_message(toto_data):
    """Create Telegram message content"""
    if not toto_data:
        return "❌ No TOTO numbers were generated."

    message = f"🎲 *Your Daily TOTO Numbers*\n"
    message += f"📅 Generated: {toto_data['date']}\n\n"

    for set_data in toto_data['sets']:
        message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

    message += f"\n🍀 Good luck with your {toto_data['total_sets']} sets!"
    message += f"\n💡 Remember to play responsibly"

    return message


def send_telegram_message():
    """Send Telegram message with TOTO numbers"""

    # Get credentials from environment variables (GitHub secrets)
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not found!")
        print("Make sure to set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in GitHub secrets")
        return False

    # Load TOTO numbers
    toto_data = load_toto_numbers()

    try:
        # Create message
        message = create_telegram_message(toto_data)

        # Telegram API URL
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        # Prepare payload
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        # Send message
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("✅ Telegram message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send Telegram message: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False


if __name__ == "__main__":
    success = send_telegram_message()
    if not success:
        exit(1)