import time
import pyupbit
import datetime
import numpy as np

access = "BxJcocqRrInQl05jBwFMzRURfVLnWx5Ckq28oxmx"
secret = "tEhVaGCbkZ96G4BngCv3Eau5NKOxJqrRbkKGg79I"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]
    
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

get_bestks()
tickers = pyupbit.get_tickers(fiat="KRW")


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=600):
            for i in tickers:
                target_price = get_target_price(i, bestks[i])
                current_price = get_current_price(i)
                if target_price < current_price:
                    krw = get_balance("KRW")
                    if krw * 0.5 > 5000:
                        upbit.buy_market_order(i, krw * 0.5)
        else:
            for i in tickers:
                balance = get_balance(i)
                current_price = get_current_price(i)
                if balance > 5000 / current_price:
                    upbit.sell_market_order(i, balance*0.9995)
            get_bestks()
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
