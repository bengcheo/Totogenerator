import requests
import os
import subprocess
import sys
import csv
import json
from datetime import datetime, timezone
from config import Config

class TelegramListener:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.chat_id = Config.CHAT_ID
        self.api_url = Config.get_telegram_api_url()
        self.last_update_file = Config.LAST_UPDATE_FILE

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

    def save_generated_numbers(self, numbers_set, user_id="Unknown", message_id=None):
        """Save generated numbers to CSV file with user ID and message ID"""

        file_exists = os.path.exists(Config.FILENAME)

        with open(Config.FILENAME, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)

            if not file_exists:
                writer.writerow([
                    'date', 'user_id', 'message_id', 'generated_numbers'
                ])

            for numbers in numbers_set:
                numbers_str = ','.join(map(str, numbers))
                writer.writerow([
                    Config.CURRENT_DATE_TIME,
                    user_id,
                    message_id,
                    numbers_str
                ])

    def save_to_google_sheets(self, numbers_sets, user_id, message_id):
        """Commit the CSV file back to the repository"""
        webhook_url = Config.FILENAME_URL

        for numbers in numbers_sets:
            data = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': user_id,
                'message_id': message_id,
                'numbers': ','.join(map(str, numbers))
            }

            try:
                print(f"Sending data to Google Sheets: {data}")
                response = requests.post(webhook_url, json=data)
                print(f"Response status: {response.status_code}")
                print(f"Response text: {response.text}")
            except Exception as e:
                print(f"Error saving to Google Sheets: {e}")

    def parse_generated_output(self, output):
        """Parse the JSON output from toto-generator.py to extract formatted strings"""
        try:
            print(f"DEBUG: Parsing output: {output}")

            # Parse the JSON output
            data = json.loads(output)

            formatted_sets = []

            # Extract the formatted strings from the JSON
            if 'sets' in data:
                for set_data in data['sets']:
                    if 'formatted' in set_data:
                        formatted_sets.append(set_data['formatted'])

            print(f"DEBUG: Extracted formatted sets: {formatted_sets}")
            return formatted_sets

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON output: {e}")
            print(f"Raw output was: {output}")
            return []
        except Exception as e:
            print(f"Error parsing generator output: {e}")
            return []

    def run_toto_generator(self, sets_count, user_id = None, message_id = None):
        """Run the toto-generator.py with the specified number of sets"""
        try:
            print(f"Running TOTO generator with {sets_count} sets...")

            result = subprocess.run(
                ['python', 'toto-generator.py', sets_count],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("TOTO generator completed successfully")
                # If we have user info, also save to our tracking CSV
                if user_id and message_id:
                    # Parse the output from toto-generator.py to extract numbers
                    generated_sets = self.parse_generated_output(result.stdout)
                    print("The generated sets are: ", generated_sets)
                    if generated_sets:
                        # Save to local CSV (optional backup)
                        self.save_generated_numbers(generated_sets, user_id, message_id)

                        # Save to Google Sheets
                        self.save_to_google_sheets(generated_sets, user_id, message_id)
                return True
            else:
                print(f"TOTO generator failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("TOTO generator timed out")
            return False
        except Exception as e:
            print(f"Error running TOTO generator: {e}")
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
            user_id = str(user.get('id', 'Unknown'))  # Get user ID instead of name
            user_name = user.get('first_name', 'User')  # Keep for display purposes

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
• 1 → 1 set of numbers
• 2 → 2 sets of numbers  
• 3 → 3 sets of numbers
• 4 → 4 sets of numbers
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
        # NO fallback generation here


if __name__ == "__main__":
    main()
