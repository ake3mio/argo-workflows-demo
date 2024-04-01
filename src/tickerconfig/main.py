import json
import sys


# This could be something that reads from a database, s3 etc.
def load_ticker_config(start_date, end_date):
    return [
        {
            "ticker": "MSFT",
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "ticker": "AAPL",
            "start_date": start_date,
            "end_date": end_date,
        },
        {
            "ticker": "TSLA",
            "start_date": start_date,
            "end_date": end_date,
        },
    ]


if __name__ == "__main__":
    # The last line from a argo task can be used as in put into another task
    # You can also write things to files which can be passed as artifacts to other task
    # obviously you can write things to a database/etc. also.
    json.dump(load_ticker_config(sys.argv[1], sys.argv[2]), sys.stdout)
