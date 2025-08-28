import random
import json
import requests
import os
from datetime import datetime


def generate_toto_numbers():
    """Generate 6 unique random numbers from 1-49 for Singapore Toto"""
    numbers = random.sample(range(1, 50), 6)
    numbers.sort()  # Sort for better readability
    return numbers


def generate_multiple_sets(count=1):
    """Generate multiple sets of Toto numbers"""
    if count > 10:
        count = 10  # Limit to prevent excessive generation

    sets = []
    for i in range(count):
        numbers = generate_toto_numbers()
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


def create_telegram_message(toto_data):
    """Create Telegram message content"""
    message = f"🎲 *Your Daily TOTO Numbers*\n"
    message += f"📅 Date: {toto_data['date']}\n"
    message += f"🎯 Total Sets: {toto_data['total_sets']}\n\n"

    for set_data in toto_data['sets']:
        message += f"*Set {set_data['set']}:* `{set_data['formatted']}`\n"

    message += f"\n🍀 Good luck with all {toto_data['total_sets']} sets!"

    return message


def send_telegram_message(toto_data):
    """Send Telegram message with TOTO numbers"""

    # Get credentials from environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("⚠️  Telegram credentials not found!")
        return False

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


def main():
    """Main function - generate numbers and send via Telegram"""
    print("🎲 Generating TOTO numbers...")

    # Generate the numbers
    result = generate_multiple_sets()

    # Output as JSON for debugging
    print("Generated data:")
    print(json.dumps(result, indent=2))

    # Send via Telegram
    print("\n📱 Sending to Telegram...")
    success = send_telegram_message(result)

    if success:
        print("✅ TOTO system completed successfully!")
    else:
        print("❌ Failed to send Telegram message")
        exit(1)


if __name__ == "__main__":
    main()