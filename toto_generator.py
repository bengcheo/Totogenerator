# toto_generator.py
import random
import json
from datetime import datetime
from config import Config


class TotoGenerator:
    def __init__(self):
        pass  # No longer needs Telegram credentials here

    def generate_toto_numbers(self, numbers_per_set=Config.NUMBERS_PER_SET):
        """Generate 6 unique random numbers from 1-49 for Singapore Toto"""
        min_num, max_num = Config.NUMBER_RANGE
        numbers = random.sample(range(min_num, max_num + 1), numbers_per_set)
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
            "date": datetime.now().strftime('%Y-%m-%d'),
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


# Keep standalone functionality for command line use
def main():
    """Main function for standalone command line use"""
    import sys
    import os
    import requests
    from save_file import save_to_google_sheets  # Import Google Sheets save function

    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("Missing Telegram credentials")
        sys.exit(1)

    bot_token = Config.BOT_TOKEN
    chat_id = Config.CHAT_ID

    generator = TotoGenerator()

    if len(sys.argv) > 1:
        count_input = sys.argv[1]
        print(f"Command line input: {count_input}")
        count = generator.parse_user_input(count_input)
    else:
        print("Scheduled run - generating 1 set")
        count = 1

    print(f"Generating {count} sets of TOTO numbers...")
    result = generator.generate_multiple_sets(count)

    print("Generated data:")
    print(json.dumps(result, indent=2))

    # Save to Google Sheets for scheduled runs
    formatted_sets = [set_data['formatted'] for set_data in result['sets']]
    try:
        save_to_google_sheets(formatted_sets, user_id="scheduled_run", message_id=None)
        print("Saved to Google Sheets successfully")
    except Exception as e:
        print(f"Warning: Could not save to Google Sheets: {e}")

    # Send to Telegram
    message = f"🎲 *Your TOTO Numbers*\n"
    message += f"📅 Date: {result['date']}\n"
    message += f"🎯 Total Sets: {result['total_sets']}\n\n"

    for set_data in result['sets']:
        message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

    output_txt = 'sets' if result['total_sets'] > 1 else 'set'
    message += f"\n🍀 Good luck with all {result['total_sets']} {output_txt}!"

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        response = requests.post(url, json=payload, timeout=10)

        if response.status_code == 200:
            print("Telegram message sent successfully")
            print("TOTO system completed successfully")
        else:
            print(f"Failed to send Telegram message: {response.status_code}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


if __name__ == "__main__":
    main()