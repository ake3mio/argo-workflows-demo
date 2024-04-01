import sys

from datetime import datetime

from yahoo import save_downloaded_historical_market_data


def string_to_timestamp(value):
    args = value.split("-")
    return int(datetime(int(args[0]), int(args[1]), int(args[2])).timestamp())


if __name__ == "__main__":
    ticker = sys.argv[1]
    start_date = string_to_timestamp(sys.argv[2])
    end_date = string_to_timestamp(sys.argv[3])

    # the data from this task will be saved to a file that will be passed as an artifact to another task
    filepath = f"/tmp/marketdata_{ticker}_{sys.argv[2]}_{sys.argv[3]}.csv"
    save_downloaded_historical_market_data(ticker, start_date, end_date, filepath)
