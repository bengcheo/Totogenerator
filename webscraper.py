import subprocess
import json
import os

class SGLotteryWrapper:
    def __init__(self, project_path):  # Fixed: __init__ not **init**
        """
        Initialize wrapper for existing sg-lottery-scraper
        project_path: path to the cloned sg-lottery-scraper directory
        """
        self.project_path = project_path

    def run_toto_scraper(self):
        """
        Run the existing Node.js scraper and return TOTO results
        """
        original_dir = os.getcwd()
        os.chdir(self.project_path)

        # Use shell=True for Windows
        result = subprocess.run(
            'npm run dev:scrape',
            capture_output=True,
            text=True,
            shell=True,
            timeout=60
        )

        print("Exit code:", result.returncode)
        print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        os.chdir(original_dir)
        return result.stdout

    def find_toto(self):
        toto_directory_path = 'data/singapore/singaporePools/toto'
        toto_directory = os.path.join(self.project_path, toto_directory_path)
        latest_version = -1
        latest_file = None

        # Walk through the directory
        for subdir, dirs, files in os.walk(toto_directory):
            for file in files:
                if file.endswith(".json"):
                    # Get just the filename without extension
                    filename_without_ext = os.path.splitext(file)[0]

                    # Try to extract draw number (assuming filename is just a number)
                    if filename_without_ext.isdigit():
                        toto_draw_number = int(filename_without_ext)

                        if toto_draw_number > latest_version:
                            latest_version = toto_draw_number
                            latest_file = os.path.join(subdir, file)

        return latest_file

    def read_latest_toto(self):
        """
        Find and read the latest TOTO file
        """
        latest_file_path = self.find_toto()
        print(f"Reading latest TOTO file: {latest_file_path}")

        with open(latest_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data


project_path = "D:/Users/sebas/PycharmProjects/Totogenerator/sg-lottery-scraper"

lottery = SGLotteryWrapper(project_path)

# Test the simple version
simple_result = lottery.read_latest_toto()
print(f"Simple version result: {simple_result}")