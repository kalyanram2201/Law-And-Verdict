Rajasthan High Court Judgment Scraper

This Python script automates the scraping of judgments from the Rajasthan High Court website. It allows users to download recent judgments in PDF format and saves the details in a CSV file.

Features

Fetches judgments from the last n days (configurable).

Filters for Reportable judgments.

Downloads PDFs of the judgments automatically.

Saves judgment details (case details, judge, order date, PDF file name) into a CSV file.

Supports manual captcha input for accessing the search results.

Prerequisites

Make sure you have the following installed:

Python 3.8+

Google Chrome Browser

ChromeDriver (automatically handled by webdriver_manager)

Python packages:

pip install selenium pandas requests webdriver-manager

Usage

Clone or download this repository.

Run the script:

python scrape_rajasthan_hc.py


The script will open a Chrome browser window and navigate to the Rajasthan High Court judgments page.

Enter the captcha manually when prompted.

The script will download the judgment PDFs to a downloads/ folder and save the details in judgments_master.csv.

Configuration

last_n_days (default 10): Number of past days to scrape judgments from.

reportable (default "YES"): Filter judgments that are reportable ("YES" or "NO").

Example:

scrape_rajasthan_hc(last_n_days=5, reportable="NO")

Folder Structure
├── scrape_rajasthan_hc.py      # Main script
├── judgments_master.csv        # Output CSV file
├── downloads/                  # Folder containing downloaded PDFs
└── state/                      # Folder containing captcha image

Notes

The script uses manual captcha input, so user interaction is required.

Ensure a stable internet connection for downloading PDFs.

The script handles file names automatically by replacing spaces with underscores and adding the order date.

License

This project is open for personal and educational use.
