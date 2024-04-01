from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd


def sma(values, n):
    return pd.Series(values).rolling(n).mean()


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        self.sma1 = self.I(sma, self.data.Close, self.n1)
        self.sma2 = self.I(sma, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()
