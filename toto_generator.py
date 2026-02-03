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
        """Generate unique random numbers from 1-49 for Singapore Toto"""
        min_num, max_num = Config.NUMBER_RANGE
        numbers = random.sample(range(min_num, max_num + 1), numbers_per_set)
        numbers.sort()
        return numbers

    def generate_multiple_sets(self, count=1, numbers_per_set=Config.NUMBERS_PER_SET):
        """Generate multiple sets of Toto numbers"""
        if count > 10:
            count = 10
        elif count < 1:
            count = 1

        # Validate numbers_per_set (6 or 7 for TOTO)
        if numbers_per_set not in [6, 7]:
            numbers_per_set = Config.NUMBERS_PER_SET

        sets = []
        for i in range(count):
            numbers = self.generate_toto_numbers(numbers_per_set)
            sets.append({
                "set": i + 1,
                "numbers": numbers,
                "formatted": " - ".join(map(str, numbers))
            })

        return {
            "total_sets": count,
            "numbers_per_set": numbers_per_set,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sets": sets
        }
        
    def user_input_test(self):
        print("Testing user input.... Please enter user input: ")
        user_input = input()
        print("You entered:", user_input)
        return user_input

    def parse_user_input(self, text):
        """Parse user input to get number of sets (1-10) and numbers per set (6 or 7).
        Format: '<sets>' or '<sets> <6|7>'
        Examples: '5' -> 5 sets of 6, '3 7' -> 3 sets of 7 numbers
        Returns: dict with 'sets' and 'numbers_per_set' or None if invalid"""
        text = text.strip()
        
        # Single number: just sets, default to 6 numbers per set
        if text.isdigit():
            num = int(text)
            if 1 <= num <= 10:
                return {'sets': num, 'numbers_per_set': Config.NUMBERS_PER_SET}
            return None
        
        # Two numbers: sets and numbers_per_set
        parts = text.split()
        if len(parts) == 2:
            try:
                sets = int(parts[0])
                numbers_per_set = int(parts[1])
                if 1 <= sets <= 10 and numbers_per_set in [6,7,8]:
                    return {'sets': sets, 'numbers_per_set': numbers_per_set}
            except ValueError:
                pass
        
        return None

def main():
    print("Running tests for Toto generator")
    toto_generator = TotoGenerator()
    
    text = toto_generator.user_input_test()
    
    parsed_numbers = toto_generator.parse_user_input(text)
    number_of_sets = list(parsed_numbers.values())[0]
    numbers_per_set = list(parsed_numbers.values())[1]
    
    print("Numbers parsed: ", number_of_sets)
    print("Numbers per set parsed: ", numbers_per_set)
        
    multi_set = toto_generator.generate_multiple_sets(number_of_sets, numbers_per_set)
    print(multi_set)


if __name__ == "__main__":
    main()
