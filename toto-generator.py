import random
import json
from datetime import datetime

def generate_toto_numbers():
    """Generate 6 unique random numbers from 1-49 for Singapore Toto"""
    numbers = random.sample(range(1, 50), 6)
    numbers.sort()  # Sort for better readability
    return numbers

def format_toto_output(numbers):
    """Format Toto numbers for display"""
    today = datetime.now().strftime("%Y-%m-%d")
    formatted_numbers = " - ".join(map(str, numbers))

    message = f"🎲 Today's Toto Numbers ({today})\n\n"
    message += f"Numbers: {formatted_numbers}\n\n"
    message += "Good luck! 🍀"

    return {
        "date": today,
        "timestamp": datetime.now().isoformat(),
        "numbers": numbers,
        "formatted": formatted_numbers,
        "message": message
    }


def generate_multiple_sets(count=6):
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


def main():
    """Main function - can be called with different modes"""

    result = generate_multiple_sets()

    # Output as JSON for easy parsing
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()