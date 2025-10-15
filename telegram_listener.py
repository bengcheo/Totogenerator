import requests
import os
import subprocess
import sys
import json
from datetime import datetime, timezone
from config import Config
from save_file import save_to_google_sheets
from toto_generator import TotoGenerator

class TelegramListener:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.chat_id = Config.CHAT_ID
        self.api_url = Config.get_telegram_api_url()
        self.last_update_file = Config.LAST_UPDATE_FILE
        self.generator = TotoGenerator()

    def get_last_update_id(self):
        """Get the last processed update ID"""
        try:
            if os.path.exists(self.last_update_file):
                with open(self.last_update_file, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return 0

    def save_last_update_id(self, update_id):
        """Save the last processed update ID"""
        try:
            with open(self.last_update_file, 'w') as f:
                f.write(str(update_id))
        except Exception as e:
            print(f"Warning: Could not save update ID: {e}")

    def get_new_messages(self):
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'limit': 100,  # Increase to see more messages
                'timeout': 10
            }

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('ok') and data.get('result'):
                    messages = data['result']
                    print(f"DEBUG: Found {len(messages)} total messages")
                    for i, msg in enumerate(messages):
                        if 'message' in msg:
                            text = msg['message'].get('text', '')
                            update_id = msg.get('update_id')
                            date = msg['message'].get('date', 0)
                            print(f"Message {i}: update_id={update_id}, text='{text}', timestamp={date}")
                    return messages
            return []
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

    def is_recent_message(self, message_timestamp, max_age_minutes=30):
        try:
            # Ensure both times are in UTC, check for latest messages
            message_time = datetime.fromtimestamp(message_timestamp, tz=timezone.utc)
            current_time = datetime.now(timezone.utc)
            age = current_time - message_time

            age_minutes = age.total_seconds() / 60
            print(f"Message time (UTC): {message_time}")
            print(f"Current time (UTC): {current_time}")
            print(f"Age: {age_minutes:.1f} minutes (limit: {max_age_minutes})")

            return age.total_seconds() <= (max_age_minutes * 60)
        except Exception as e:
            print(f"Error checking message age: {e}")
            return True

    def send_response(self, text, reply_to_message_id=None):
        """Send response message"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'Markdown'
            }

            if reply_to_message_id:
                payload['reply_to_message_id'] = reply_to_message_id

            url = f"{self.api_url}/sendMessage"
            response = requests.post(url, json=payload, timeout=10)

            return response.status_code == 200
        except Exception as e:
            print(f"Error sending response: {e}")
            return False

    def is_valid_toto_request(self, message_text):
        """Check if message is a valid TOTO request (1-10)"""
        text = message_text.strip()
        if text.isdigit():
            num = int(text)
            return 1 <= num <= 10
        return False

    def format_telegram_message(self, toto_data):
        """Format TOTO data as Telegram message"""
        message = f"🎲 *Your TOTO Numbers*\n"
        message += f"📅 Date: {toto_data['date']}\n"
        message += f"🎯 Total Sets: {toto_data['total_sets']}\n\n"

        for set_data in toto_data['sets']:
            message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

        output_txt = 'sets' if toto_data['total_sets'] > 1 else 'set'
        message += f"\n🍀 Good luck with all {toto_data['total_sets']} {output_txt}!"
        return message

    def run_toto_generator(self, sets_count, user_id=None, message_id=None):
        """Generate TOTO numbers and handle results"""
        try:
            print(f"Generating {sets_count} sets of TOTO numbers...")

            # Generate numbers directly (no subprocess!)
            result = self.generator.generate_multiple_sets(int(sets_count))

            # Format and send to Telegram
            message = self.format_telegram_message(result)
            self.send_response(message, reply_to_message_id=message_id)

            # Save to Google Sheets if we have user info
            if user_id and message_id:
                formatted_sets = [set_data['formatted'] for set_data in result['sets']]
                save_to_google_sheets(formatted_sets, user_id, message_id)
                #print("saved to Google Sheet!")

            print("TOTO generation completed successfully")
            return True

        except Exception as e:
            print(f"Error generating TOTO numbers: {e}")
            return False

    def process_telegram_messages(self):
        """Main function - check for messages and respond"""
        print("Checking for Telegram messages...")

        new_messages = self.get_new_messages()

        if not new_messages:
            print("No new messages found")
            return False

        processed_any = False

        for update in new_messages:
            if 'message' not in update:
                continue

            message = update['message']

            if str(message['chat']['id']) != str(self.chat_id):
                continue

            message_text = message.get('text', '').strip()
            message_id = message.get('message_id')
            message_date = message.get('date', 0)
            user = message.get('from', {})
            user_id = str(user.get('id', 'Unknown'))
            user_name = user.get('first_name', 'User')

            if not message_text:
                continue

            if not self.is_recent_message(message_date):
                print(f"Skipping old message: '{message_text}'")
                continue

            print(f"New message from {user_name}: '{message_text}'")

            if self.is_valid_toto_request(message_text):
                self.send_response(
                    f"Got it! Generating {message_text} set{'s' if message_text != '1' else ''}...",
                    reply_to_message_id=message_id
                )

                success = self.run_toto_generator(message_text, user_id, message_id)

                if success:
                    processed_any = True
                    print(f"Successfully processed request for {message_text} sets")
                else:
                    self.send_response(
                        "Sorry, there was an error generating your numbers. Please try again!",
                        reply_to_message_id=message_id
                    )
            else:
                help_text = """TOTO Generator Bot

Send me a number from 1 to 10:
- 1 → 1 set of numbers
- 2 → 2 sets of numbers  
- 3 → 3 sets of numbers
- 4 → 4 sets of numbers
...and so on up to 10"""

                self.send_response(help_text, reply_to_message_id=message_id)

        return processed_any


def main():
    """Main function - CHECK ONLY, NO FALLBACK GENERATION"""
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("Missing Telegram credentials")
        sys.exit(1)

    listener = TelegramListener()
    had_messages = listener.process_telegram_messages()

    if not had_messages:
        print("No TOTO requests found - doing nothing (check only mode)")


if __name__ == "__main__":
    main()
