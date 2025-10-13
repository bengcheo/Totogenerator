from datetime import datetime
from config import Config
import os
import csv

def save_generated_numbers(numbers_set, user_id="Unknown", message_id=None):
    """Save generated numbers to CSV file with user ID and message ID"""

    file_exists = os.path.exists(Config.FILENAME_URL)

    with open(Config.FILENAME_URL, 'a', newline='') as csvfile:
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


def save_to_google_sheets(formatted_sets, user_id, message_id):
    """Save formatted number sets to Google Sheets"""
    webhook_url = Config.FILENAME_URL

    for formatted_numbers in formatted_sets:  # Changed variable name for clarity
        data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id,
            'message_id': message_id,
            'numbers': formatted_numbers  # Use the formatted string directly
        }

        try:
            print(f"Sending data to Google Sheets: {data}")
            response = requests.post(webhook_url, json=data)
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")