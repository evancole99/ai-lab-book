from pandas_datareader import data as pdr
from datetime import datetime, date, timedelta
import yfinance as yf
yf.pdr_override() # overrides yfinance to expect pandas datareader
import pandas as pd
import sqlite3

con = sqlite3.connect("../data/invest_tracker.db")
cur = con.cursor()

ticker_list = ['APHA', 'MAXR', 'ICLN', 'NIO', 'QS', 'SPCE', 'SUBZ', 'NCLH', 'SATS', 'OZON', 'GMBL', 'XPEV', 'DIS', 'TSLA', 'RIOT']

today = date.today()
yesterday = today - timedelta(days=1)
def getData(ticker):
    print("Fetching ", ticker)
    data = pdr.get_data_yahoo(ticker, start=yesterday, end=today)
    return data

for tik in ticker_list:
    tik_data = getData(tik)
    tik_data.reset_index(inplace=True)
    
    tik_data.columns = ['mkt_date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    tik_data.insert(1, 'ticker', tik)
    tik_data.set_index('ticker')
    
    sql = "INSERT INTO stock (mkt_date, ticker, open, high, low, close, adj_close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    row = tik_data.iloc[0]
    date_stripped = row.mkt_date.date()
    cur.execute(sql, (str(date_stripped), str(row.ticker), float(row.open), float(row.high), float(row.low), float(row.close), float(row.adj_close), int(row.volume)))

con.commit()
con.close()

