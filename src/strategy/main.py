import os
import sys
from backtesting import Backtest
from smacross import SmaCross
import pandas as pd


def list_files_in_directory(directory):
    return os.listdir(directory)


if __name__ == "__main__":
    ticker = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    filepath = f"/tmp/marketdata_{ticker}_{start_date}_{end_date}.csv"
    files = list_files_in_directory("/tmp")

    print(f"Files in directory {filepath}: {files}")

    data = pd.read_csv(filepath, index_col="Date", parse_dates=True)
    backtest = Backtest(data, SmaCross, cash=10_000, commission=.002)
    stats = backtest.run()
    stats.to_csv(f'/tmp/results_{ticker}_{start_date}_{end_date}.csv')
