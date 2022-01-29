import pyupbit
import numpy as np

def get_ror(ticker, k = 0.5):
    df = pyupbit.get_ohlcv(ticker, count = 30)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0.00005
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def get_bestk(ticker):
  ror = []
  for k in np.arange(0.1, 1.0, 0.1):
    ror.append(get_ror(ticker, k))
  bestk = (ror.index(max(ror)) * 0.1) + 0.1
  return bestk

def get_bestks():
    tickers = pyupbit.get_tickers(fiat="KRW")
    bestks = {}
  for i in tickers:
    bestks[i] = get_bestk(i)
