# toto_generator.py
import random
import json
from datetime import datetime
from config import Config
import re


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
        
    def user_input_test(self):
        print("Testing user input.... Please enter user input: ")
        user_input = input()
        print("You entered:", user_input)
        return user_input

    def parse_user_input(self, text):
        """Parse user input to get number of sets (1-10)"""
        text = text.strip()
        
        if text.isdigit():
            num = int(text)
            if 1 <= num <= 10:
                return num 
            return 1
        
        match = re.fullmatch(r"(\d+)(?:\s+([A-Za-z]+))?", text)
        if match:
            number = int(match.group(1))
            #word = match.group(2)  # will be None if only "1"
            # print(number, word)
            if 1 <= number <= 10:
                return number
            return 1
        
        return 1

def main():
    print("Running tests for Toto generator")
    toto_generator = TotoGenerator()
    
    text = toto_generator.user_input_test()
    
    parsed_number = toto_generator.parse_user_input(text)
    print("Numbers parsed: ", parsed_number)
    
    single_set = toto_generator.generate_toto_numbers()
    #print("Single Set Generated:", single_set)
    
    multi_set = toto_generator.generate_multiple_sets()
    #print("Multiple Sets Generated:", multi_set)


if __name__ == "__main__":
    main()
