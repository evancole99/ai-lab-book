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

# Benchmarking

In this lesson, we are going to go over some simple forms of benchmarking databases. We will be focusing on three different libraries built for Python:
* Pandas
* SQLite3
* DuckDB

For information about how to use these libraries, visit lessons 1 and 2.

## Importing the libraries

First, we will begin by importing the necessary libraries.
You may need to download the prerequisite packages prior to running the code, particularly for Pandas. The necessary installation packages are contained in the _requirements.txt_ file. You may install it with pip by using the following command while in the correct working directory:
> pip install -r requirements.txt  
If this does not work, consult Pandas documentation.

```python
import pandas as pd
import duckdb
import csv, sqlite3
from datetime import datetime
```

The _datetime_ library is how we will measure the time it took to execute each part of the Python script that we wish to benchmark.

All we must do to time an operation is to subtract the starting _datetime.now()_ from the ending _datetime.now()_. 

## Get the dataset

For this example, we will be reading data from a COVID 19 case surveillance database provided by the CDC.
You can get the CSV file yourself from [the CDC's website](https://data.cdc.gov/Case-Surveillance/COVID-19-Case-Surveillance-Public-Use-Data/vbim-akqf).  

NOTE: The CSV file is over **20 million** rows, amounting to over **2 GB** large. This means it takes a relatively large amount of memory to process, and can easily corrupt/crash lower-end systems or Virtual Machines. Consider if your machine's specifications can handle the operations before trying to process the dataset.


## Benchmark Pandas

Let's begin by benchmarking the COVID dataset using Pandas.
First, we will test how long it takes to read the CSV file into a dataframe, and write the dataframe to a new SQL database.

```python
# -- BENCHMARK PANDAS --
start = datetime.now()

# Set datatypes before-hand, because it is very memory intensive for Pandas to guess
dtypes = {'cdc_case_earliest_dt ': 'str', 'cdc_report_dt': 'str', 'pos_spec_dt': 'str',
'onset_dt': 'str', 'current_status': 'str', 'sex': 'str', 'age_group': 'str',
'race_ethnicity_combined': 'str', 'hosp_yn': 'str', 'icu_yn': 'str', 'death_yn': 'str',
'medcond_yn': 'str'}
df = pd.read_csv('covid19.csv', dtype=dtypes)
```

In this case, it is important that we tell Pandas' read\_csv function which datatypes to expect and which column names they correspond to, since it is very memory intensive for Pandas to guess. In our circumstance, the COVID dataset is provided entirely as strings.  

The read\_csv function does just as it says: it reads a CSV file and writes it into a dataframe. For large files, this can take a while, particularly for machines with low processing power.  

Now that we have read the CSV file into a dataframe, we will use Pandas' to\_sql function to write the dataframe to an SQL database.

```python
# Connect to database
con1 = sqlite3.connect(":memory:")
# Write to SQL database
df.to_sql("t", con1, if_exists='replace')
con1.commit()
```

First, we connect to the SQLite3 database. Here, we are using an in-memory database, rather than saving it to a file or connecting to an online database. This means that when the Python process has terminated, all data written to memory will be wiped. This will allow us to save a lot of disk space that normally would have been consumed by writing the file.  

Next, we used the to\_sql function with the parameter if\_exists='replace'. This tells the process to overwrite the file if one of that name already exists.
In order for the database to be saved, we must **commit** the changes.  

Lastly, we can print the time it took to execute:

```python
# Print Pandas to_sql results
print("Pandas read/write:")
print(datetime.now() - start)
```  

My machine's results:  
**131.60 sec avg**  


## Benchmark SQLite3

Now we will repeat the process for SQLite3. Rather than using Pandas syntax, we will use SQL queries in addition to functions built-in to the SQLite3 library.  

As usual, we begin by setting the start time and connecting to the in-memory database.
```python
# -- BENCHMARK SQLITE3 --
start = datetime.now()

# Connect to database
con2 = sqlite3.connect(":memory:")
cur2 = con2.cursor()
```  

Next, we will create a table using SQL, and specify the correct column names.
Once the table has been created, we can use the CSV library's _DictReader_ module to iterate over file, but only on rows that match the field names.   
```python
# Create table with headers
cur2.execute("CREATE TABLE t (cdc_case_earliest_dt , cdc_report_dt, pos_spec_dt, onset_dt, current_status, sex, age_group, race_ethnicity_combined, hosp_yn, icu_yn, death_yn, medcond_yn);")
# Open the CSV and populate columns
with open ('covid19.csv', 'r') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['cdc_case_earliest_dt '], i['cdc_report_dt'], i['pos_spec_dt'], i['onset_dt'], i['current_status'], i['sex'], i['age_group'], i['race_ethnicity_combined'], i['hosp_yn'], i['icu_yn'], i['death_yn'], i['medcond_yn']) for i in dr]
```

We then iterate over each value read by the DictReader and store it in a variable, that we can now write directly to the database using the _INSERT_ SQL query.


```python
# Insert columns into table and commit
cur2.executemany("INSERT INTO t (cdc_case_earliest_dt , cdc_report_dt, pos_spec_dt, onset_dt, current_status, sex, age_group, race_ethnicity_combined, hosp_yn, icu_yn, death_yn, medcond_yn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con2.commit()
```  

Now that we have inserted our rows of data, and committed the changes, we can print our results.

```python
# Print SQLite results
print("SQLite read/write:")
print(datetime.now() - start)
start = datetime.now()
```

My machine's results:  
**153.80 sec avg**  


## Benchmark DuckDB  

Last but certainly not least, we will benchmark DuckDB. It functions exactly the same as SQLite3, but with a couple slight syntax differences.  

As always, we will begin the timer, and connect to the in-memory database.

```python 
# -- BENCHMARK DUCKDB --
start = datetime.now()

# Connect to database
con3 = duckdb.connect(database=':memory:', read_only=False)
cur3 = con3.cursor()
```

In order to read the data from the CSV file, we first have to create the table using SQL queries, exactly the same as in the SQLite3 section.  

However, when it comes to reading the data, DuckDB differs slightly from SQLite3. DuckDB has a built in CSV reader function compatible with SQL queries.  

This allows us to use an _INSERT_ operation in conjunction with a _SELECT_ operation directly from the read\_csv\_auto module.  

```python
# Create table with headers
cur3.execute("CREATE TABLE t (cdc_case_earliest_dt  VARCHAR, cdc_report_dt VARCHAR, pos_spec_dt VARCHAR, onset_dt VARCHAR, current_status VARCHAR, sex VARCHAR, age_group VARCHAR, race_ethnicity_combined VARCHAR, hosp_yn VARCHAR, icu_yn VARCHAR, death_yn VARCHAR, medcond_yn VARCHAR);")
# Insert values into table from CSV
cur3.execute("INSERT INTO t SELECT * FROM read_csv_auto('covid19.csv', HEADER=TRUE);")
con3.commit()
```

And that is it! Now that we have committed our changes, we can print our results.  
```python
# Print DuckDB results
print("DuckDB read/write:")
print(datetime.now() - start)
```  

My machine's results:  
**23.6 sec avg**  

After viewing the results, we can see that DuckDB is significantly faster than Pandas and SQLite3. However, the catch is that the database file it produces (in our example, we use in-memory, so the difference is not visible) is over 1 GB larger than its counterparts.  

## Benchmarking count functions  

We have tested the time it takes to read and write from a CSV file, but what about querying the database itself?  

Here, we will test each library with the same query:  
Get the count of each hospitalization status for the age group 0 - 9 years.  

NOTE: In this example, the queries were executed after the data had been written to the in-memory database. To query from a database file, simply replace _:memory:_ with the file location in the connect line.

### Pandas Query

For the Pandas query, we can use the built-in value\_counts() function. All we have to do is isolate the columns we wish to count.  

```python
start = datetime.now()
countdf = df[['hosp_yn', 'age_group']]
print(countdf.loc[countdf['age_group'] == '0 - 9 Years'].value_counts())
# Print Pandas count results
print("Pandas count:")
print(datetime.now() - start)
con1.close()
```

My machine's results:  
**1.67 sec avg**

### SQLite3  

To repeat the exact same query for SQLite3, we will use SQL's _COUNT_ operation in conjunction with a _SELECT_.  

```python
start = datetime.now()
cur2.execute("SELECT hosp_yn, COUNT(hosp_yn) FROM t WHERE age_group='0 - 9 Years' GROUP BY hosp_yn")
print(cur2.fetchall())
# Print count results
print("SQL count:")
print(datetime.now() - start)
con2.close()
```  

My machine's results:  
**3.23 sec avg**

### DuckDB  

In this case, DuckDB's query will be identical to SQLite3's.  

```python
start = datetime.now()
cur3.execute("SELECT hosp_yn, COUNT(hosp_yn) FROM t WHERE age_group='0 - 9 Years' GROUP BY hosp_yn")
print(cur3.fetchall())
# Print count results
print("DuckDB count:")
print(datetime.now() - start)
con3.close()
```  

My machine's results:  
**.096 sec avg**  

## Results  

Our results tell us a few interesting things. SQLite and Pandas are very nice solutions for working locally, and on smaller-scale datasets. DuckDB is surprisingly fast, at the expense of increased disk space. This is because DuckDB is a columnar-based data store, whereas SQLite and Pandas are row-based.  

This makes querying entire columns a lot more efficient, which is why the aggregating count query we tried was so much faster for DuckDB to process. As a result, DuckDB is a popular choice for machine learning implementations, as it can execute operations on columns several orders of magnitude faster than most counterparts.
