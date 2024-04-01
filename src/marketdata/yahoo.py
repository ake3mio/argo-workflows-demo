import csv

import requests


def get_request_headers():
    user_agent_values = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "AppleWebKit/537.36 (KHTML, like Gecko)",
        "Chrome/122.0.0.0 Safari/537.36"
    ]

    return {
        "user-agent": " ".join(user_agent_values)
    }


def download_historical_market_data(ticker, start_date, end_date):
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start_date}&period2={end_date}&interval=1d&events=history"

    try:
        response = requests.get(url, headers=get_request_headers())
        response.raise_for_status()  # Raise an exception for any HTTP errors

        return response.text.strip().split('\n')
    except requests.exceptions.RequestException as e:
        print("Error occurred:", str(e))


def save_downloaded_historical_market_data(ticker, start_date, end_date, filepath):
    market_data = download_historical_market_data(ticker, start_date, end_date)

    try:
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in market_data:
                writer.writerow(line.split(','))

        print("Data downloaded successfully and saved to:", filepath)
    except requests.exceptions.RequestException as e:
        print("Error occurred:", str(e))
