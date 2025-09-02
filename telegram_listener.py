import requests
import os
import subprocess
import sys
from datetime import datetime


class TelegramListener:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

        # File to track last processed message
        self.last_update_file = "/tmp/last_update_id.txt"

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
        """Get new messages since last check"""
        try:
            last_update_id = self.get_last_update_id()

            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': last_update_id + 1,
                'limit': 5,
                'timeout': 10
            }

            response = requests.get(url, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()

                if data.get('ok') and data.get('result'):
                    messages = data['result']

                    # Update last processed ID
                    if messages:
                        latest_update_id = messages[-1]['update_id']
                        self.save_last_update_id(latest_update_id)

                    return messages

            return []

        except Exception as e:
            print(f"Error getting messages: {e}")
            return []

    def is_recent_message(self, message_timestamp, max_age_minutes=30):
        """Check if message is recent enough to process"""
        try:
            message_time = datetime.fromtimestamp(message_timestamp)
            current_time = datetime.now()
            age = current_time - message_time

            return age.total_seconds() <= (max_age_minutes * 60)
        except:
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
        """Check if message is a valid TOTO request (1, 2, 3, or 4)"""
        text = message_text.strip()
        return text in ['1', '2', '3', '4']

    def run_toto_generator(self, sets_count):
        """Run the toto-generator.py with the specified number of sets"""
        try:
            print(f"🎲 Running TOTO generator with {sets_count} sets...")

            result = subprocess.run(
                ['python', 'toto-generator.py', sets_count],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("✅ TOTO generator completed successfully")
                return True
            else:
                print(f"❌ TOTO generator failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ TOTO generator timed out")
            return False
        except Exception as e:
            print(f"❌ Error running TOTO generator: {e}")
            return False

    def process_telegram_messages(self):
        """Main function - check for messages and respond"""
        print("👂 Checking for Telegram messages...")

        new_messages = self.get_new_messages()

        if not new_messages:
            print("📭 No new messages found")
            return False

        processed_any = False

        for update in new_messages:
            if 'message' not in update:
                continue

            message = update['message']

            # Check if message is from the correct chat
            if str(message['chat']['id']) != str(self.chat_id):
                continue

            message_text = message.get('text', '').strip()
            message_id = message.get('message_id')
            message_date = message.get('date', 0)
            user = message.get('from', {})
            user_name = user.get('first_name', 'User')

            # Skip empty messages
            if not message_text:
                continue

            # Skip old messages (older than 30 minutes)
            if not self.is_recent_message(message_date, max_age_minutes=30):
                print(f"⏰ Skipping old message: '{message_text}'")
                continue

            print(f"📨 New message from {user_name}: '{message_text}'")

            # Check if it's a valid TOTO request
            if self.is_valid_toto_request(message_text):
                # Send acknowledgment
                self.send_response(
                    f"🎲 Got it! Generating {message_text} set{'s' if message_text != '1' else ''}...",
                    reply_to_message_id=message_id
                )

                # Run TOTO generator
                success = self.run_toto_generator(message_text)

                if success:
                    processed_any = True
                    print(f"✅ Successfully processed request for {message_text} sets")
                else:
                    # Send error message
                    self.send_response(
                        "⚠️ Sorry, there was an error generating your numbers. Please try again!",
                        reply_to_message_id=message_id
                    )
            else:
                # Send help message
                help_text = """🎲 *TOTO Generator Bot*

Send me a number. For example: 
• `1` → 1 set of numbers
• `2` → 2 sets of numbers  
• `3` → 3 sets of numbers
• `4` → 4 sets of numbers

That's it! 🍀"""

                self.send_response(help_text, reply_to_message_id=message_id)

        return processed_any


def main():
    """Main function"""
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ Missing Telegram credentials")
        print("Make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set")
        sys.exit(1)

    listener = TelegramListener()

    # Check for messages and process them
    had_messages = listener.process_telegram_messages()

    if not had_messages:
        print("📅 No TOTO requests found, running scheduled generation...")
        # Run default TOTO generator (1 set)
        listener.run_toto_generator('1')


if __name__ == "__main__":
    main()