import random
import json
import requests
import os
import sys
from datetime import datetime

import telegram_listener

class InteractiveTotoBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def generate_toto_numbers(self):
        """Generate 6 unique random numbers from 1-49 for Singapore Toto"""
        numbers = random.sample(range(1, 50), 6)
        numbers.sort()  # Sort for better readability
        return numbers

    def generate_multiple_sets(self, count=1):
        """Generate multiple sets of Toto numbers"""
        if count > 10:
            count = 10  # Limit to prevent excessive generation
        elif count < 1:
            count = 1

        sets = []
        for i in range(count):
            numbers = self.generate_toto_numbers()
            sets.append({
                "set": i + 1,
                "numbers": numbers,
                "formatted": " - ".join(map(str, numbers))
            })

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_sets": count,
            "sets": sets
        }

    def parse_user_command(self, text):
        """Parse user input to get number of sets"""
        if text.isdigit():
            num = int(text)
            if 1 <= num <= 10:
                return num
            else:
                return 1  # Default to 1 if invalid
        return 1  # Default to 1 if not a number

    def create_telegram_message(self, toto_data):
        """Create Telegram message content"""
        message = f"🎲 *Your TOTO Numbers*\n"
        message += f"📅 Date: {toto_data['date']}\n"
        message += f"🎯 Total Sets: {toto_data['total_sets']}\n\n"

        for set_data in toto_data['sets']:
            message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

        message += f"\n🍀 Good luck with all {toto_data['total_sets']} sets!"

        return message

    def send_telegram_message(self, toto_data):
        """Send Telegram message with TOTO numbers"""
        if not self.bot_token or not self.chat_id:
            print("⚠️  Telegram credentials not found!")
            return False

        try:
            # Create message
            message = self.create_telegram_message(toto_data)

            # Telegram API URL
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            # Prepare payload
            payload = {
                'chat_id': self.chat_id,
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

    def generate_numbers(self, count_input=None):
        """Main function - generate numbers and send via Telegram"""

        # Get count from parameter or default to 1
        if count_input is None:
            count = 1  # Default
        else:
            count = self.parse_user_command(str(count_input))

        print(f"🎲 Generating {count} sets of TOTO numbers...")

        # Generate the numbers
        result = self.generate_multiple_sets(count)

        # Output as JSON for debugging
        print("Generated data:")
        print(json.dumps(result, indent=2))

        # Send via Telegram
        print("\n📱 Sending to Telegram...")
        success = self.send_telegram_message(result)

        if success:
            print("✅ TOTO system completed successfully!")
        else:
            print("❌ Failed to send Telegram message")
            exit(1)


def main():
    """Main function"""
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ Missing Telegram credentials")
        print("Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set")
        sys.exit(1)

    listener = telegram_listener.TelegramListener()

    # Check for messages and process them
    had_messages = listener.process_telegram_messages()

    if not had_messages:
        print("📭 No new TOTO requests from Telegram. Doing nothing.")


if __name__ == "__main__":
    main()