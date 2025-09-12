import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config import Config
import pytz

url = Config.url
headers = Config.headers
response = requests.get(url, headers=headers)
sg_tz = pytz.timezone('Asia/Singapore')
current_sg_date = datetime.now(sg_tz).strftime("%Y-%m-%d")

class ResultBot:
    def __init__(self):
        self.bot_token = Config.BOT_TOKEN
        self.chat_id = Config.CHAT_ID
        self.api_url = Config.get_telegram_api_url()

    def send_telegram_message(self, message):
        """Send message to Telegram"""
        payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'  # Allows HTML formatting
        }

        try:
            response = requests.post(f"{self.api_url}/sendMessage", json=payload)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error sending message to Telegram: {e}")
            return False

    def format_results_message(self, date, winning_numbers, additional_number):
        """Format the lottery results into a nice Telegram message"""
        message = f"""🎰 <b>Singapore TOTO Results</b> 🎰

    📅 <b>Date:</b> {date.strftime("%Y-%m-%d")}
    🎲 <b>Winning Numbers:</b> {winning_numbers}
    ⭐ <b>Additional Number:</b> {additional_number}

    Good luck! 🍀"""
        return message

    def web_scraper_tool(self):
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all rows in the tbody
        rows = soup.find('tbody').find_all('tr')

        latest_date = None
        latest_winning_numbers = None
        latest_additional_number = None

        for row in rows:
            # Get all sum-p1 cells in this row
            sum_p1_cells = row.find_all('td', class_='sum-p1')

            if len(sum_p1_cells) >= 3:  # Ensure we have date, winning numbers, and additional number
                date_str = sum_p1_cells[0].get_text(strip=True)
                winning_numbers = sum_p1_cells[1].get_text(strip=True)
                additional_number = sum_p1_cells[2].get_text(strip=True)

                # Parse the date
                current_date = datetime.strptime(date_str, '%Y-%m-%d')

                # Check if this is the latest date
                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
                    latest_winning_numbers = winning_numbers
                    latest_additional_number = additional_number

        # Output result
        if latest_winning_numbers:
        #if latest_winning_numbers  and current_sg_date == latest_date:
            latest_winning_numbers = latest_winning_numbers.replace(",", ", ")
            print(f"Latest date: {latest_date.strftime('%Y-%m-%d')}")
            print(f"Winning numbers: {latest_winning_numbers}")
            print(f"Additional number: {latest_additional_number}")

            message = self.format_results_message(
                latest_date,
                latest_winning_numbers,
                latest_additional_number
            )

            self.send_telegram_message(message)

            # Convert winning numbers to a list of integers
            winning_numbers_list = [int(num.strip()) for num in latest_winning_numbers.split(',')]
            additional_number_int = int(latest_additional_number)

            print(f"Winning numbers as list: {winning_numbers_list}")
            print(f"Additional number as integer: {additional_number_int}")

        else:
            print("No data found")

    def run(self):
        """Main method to run the bot"""
        print("🤖 Starting TOTO Results Bot...")
        self.web_scraper_tool()

# Usage
if __name__ == "__main__":
    bot = ResultBot()
    bot.run()