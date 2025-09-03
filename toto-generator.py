import random
import json
from sys import setswitchinterval

import requests
import os
import sys
from datetime import datetime


class TotoGenerator:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def generate_toto_numbers(self):
        """Generate 6 unique random numbers from 1-49 for Singapore Toto"""
        numbers = random.sample(range(1, 50), 6)
        numbers.sort()
        return numbers

    def generate_multiple_sets(self, count=1):
        """Generate multiple sets of Toto numbers"""
        if count > 10:
            count = 10
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

    def parse_user_input(self, text):
        """Parse user input to get number of sets (1-10)"""
        if text.isdigit():
            num = int(text)
            if 1 <= num <= 10:
                return num
        return 1

    def create_telegram_message(self, toto_data):
        """Create Telegram message content"""
        message = f"🎲 *Your TOTO Numbers*\n"
        message += f"📅 Date: {toto_data['date']}\n"
        message += f"🎯 Total Sets: {toto_data['total_sets']}\n\n"

        for set_data in toto_data['sets']:
            message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

        output_txt = ''
        if toto_data['sets'] > 1:
            output_txt = 'sets'
        else:
            output_txt = 'set'

        message += f"\n🍀 Good luck with all {toto_data['total_sets']} {output_txt}!"
        return message

    def send_to_telegram(self, toto_data):
        """Send TOTO numbers to Telegram"""
        if not self.bot_token or not self.chat_id:
            print("Missing Telegram credentials")
            return False

        try:
            message = self.create_telegram_message(toto_data)
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                print("Telegram message sent successfully")
                return True
            else:
                print(f"Failed to send Telegram message: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False

    def run(self, count_input=None):
        """Generate and send TOTO numbers"""
        count = self.parse_user_input(str(count_input)) if count_input else 1

        print(f"Generating {count} sets of TOTO numbers...")

        result = self.generate_multiple_sets(count)

        print("Generated data:")
        print(json.dumps(result, indent=2))

        success = self.send_to_telegram(result)

        if success:
            print("TOTO system completed successfully")
        else:
            print("Failed to send Telegram message")
            return False

        return True


def main():
    """Main function - handles command line arguments"""
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("Missing Telegram credentials")
        sys.exit(1)

    generator = TotoGenerator()

    if len(sys.argv) > 1:
        # Called with argument (from telegram_listener)
        count_input = sys.argv[1]
        print(f"Command line input: {count_input}")
        generator.run(count_input)
    else:
        # Called without arguments (scheduled run)
        print("Scheduled run - generating 1 set")
        generator.run(1)


if __name__ == "__main__":
    main()