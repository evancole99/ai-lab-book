---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---


[![Lesson 4 Video](http://img.youtube.com/vi/lm7pT90TsxY/0.jpg)](http://www.youtube.com/watch?v=lm7pT90TsxY "Lesson 4")


## Using APIs

In this lesson, we will use Yahoo Finance's API to download stock data and insert it into our investment tracking database, upon which we can do additional calculations.

The only table in the database that we are concerned with for this lesson is the _stock_ table. However, there are many more tables to play around with, allowing for more complex programs and queries. For a more detailed overview of the database, watch the video embedded below.

### Stock table: Schema

Below is an overview of the schema of the stock table.
Note: The database is updated often, so it is possible this schema is out of date.  You can check the current schema by running the _.schema table_ command in sqlite3.  

Stock:
* **ticker** varchar(5)
    * The stock's ticker symbol, as listed on the stock exchange. Up to 5 characters.
* **mkt**\_**date** varchar(10)
    * Date in YYYY-MM-DD format.
* **open** float(16)
    * Price per share at market open.
* **high** float(16)
    * Highest price during trading hours.
* **low** float(16)
    * Lowest price during trading hours.
* **close** float(16)
    * Price per share at market close.
* **adj**\_**close** float(16)
    * The stock's adjusted closing price, factoring in other actions after close. Considered to be more accurate.
* **volume** int
    * Number of shares traded during trading hours.  

The primary key of this table is (mkt\_date, ticker).


### Importing libraries

First of all, we have to import all of the necessary libraries. We will be using pandas, pandas datareader, datetime, yfinance, and sqlite3.  

Then, as usual, we connect to the database using sqlite3.

```{code-cell} python3
from pandas_datareader import data as pdr
from datetime import datetime, date, timedelta
import yfinance as yf
yf.pdr_override() # overrides yfinance to expect pandas datareader
import pandas as pd
import sqlite3

con = sqlite3.connect("../data/invest_tracker.db")
cur = con.cursor()
```

### Calling the API  

Now, we will build a simple function to download today's stock market prices from the given ticker. Thankfully, YFinance does all of the hard work for us, so weonly need to make a single API call.  

The get\_data\_yahoo call on pandas datareader automatically queries the API, downloads data on the given ticker and date range, and writes it to a dataframe. Since we are only querying a single day, the returned dataframe will only contain a single row.

```{code-cell} python3 

today = date.today()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
def getData(ticker):
    print("Fetching ", ticker)
    data = pdr.get_data_yahoo(ticker, start=yesterday, end=tomorrow)
    return data
```

### Read and write data

All that is left to do now is pick a list of stock tickers, and use the function we just built to download the data. Once we have done that, we can prepare the data to be inserted into the database via SQL queries.  

Let's break down each line of the for loop below, to better understand exactly what is going on.  

For each ticker in the ticker list:
* Call the API to download data into dataframe
* Reset the index of the dataframe, so it is not indexed by the date
* Set the dataframe's column names and in the correct order
* Insert a column for the ticker at index 1
* Prepare SQL insertion command
* Get the single row of data
* Convert the date into proper format
* Execute the SQL command, making sure to give the proper datatype to each column  



```{code-cell} python3
ticker_list = ['AAPL', 'GOOGL', 'FB', 'MSFT']

for tik in ticker_list:
    tik_data = getData(tik)
    tik_data.reset_index(inplace=True)
    
    tik_data.columns = ['mkt_date', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    tik_data.insert(1, 'ticker', tik)
    tik_data.set_index('ticker')
    
    sql = "INSERT or IGNORE INTO stock (mkt_date, ticker, open, high, low, close, adj_close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
    row = tik_data.iloc[0]
    print(row)
    date_stripped = row.mkt_date.date()
    cur.execute(sql, (str(date_stripped), str(row.ticker), float(row.open), float(row.high), float(row.low), float(row.close), float(row.adj_close), int(row.volume)))

con.commit()
con.close()
```

And with those few lines of code, we now have up-to-date stock market data on any ticker we want in our database. We could expand upon this code to download as many days, weeks, or months of data as we wish, and could perform all sorts of different plots, graphs, or calculations.  

For a more comprehensive example on how this data can be used to track personal investments, see the advanced version of the stock API code found in the [extra content](https://github.com/uri-ai-lab/ai-lab-book) folder.

The YFinance module is also capable of a lot more. For full documentation on its uses, you can find the [code on GitHub](https://github.com/ranaroussi/yfinance).
