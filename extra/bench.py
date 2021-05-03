import pandas as pd
import duckdb
import csv, sqlite3
from datetime import datetime

# -- BENCHMARK PANDAS --
start = datetime.now()

# Set datatypes before-hand, because it is very memory intensive for Pandas to guess
dtypes = {'cdc_case_earliest_dt ': 'str', 'cdc_report_dt': 'str', 'pos_spec_dt': 'str',
'onset_dt': 'str', 'current_status': 'str', 'sex': 'str', 'age_group': 'str',
'race_ethnicity_combined': 'str', 'hosp_yn': 'str', 'icu_yn': 'str', 'death_yn': 'str',
'medcond_yn': 'str'}
df = pd.read_csv('covid19.csv', dtype=dtypes)

# Print Pandas read_csv results
# print("Pandas read_csv:")
# print(datetime.now() - start)
# start = datetime.now()

# Connect to database
con1 = sqlite3.connect(":memory:")
# Write to SQL database
df.to_sql("t", con1, if_exists='replace')
con1.commit()
# Print Pandas to_sql results
print("Pandas read/write:")
print(datetime.now() - start)

start = datetime.now()
countdf = df[['hosp_yn', 'age_group']]
print(countdf.loc[countdf['age_group'] == '0 - 9 Years'].value_counts())
# Print Pandas count results
print("Pandas count:")
print(datetime.now() - start)
print('\n')
con1.close()



# -- BENCHMARK SQLITE3 --
start = datetime.now()

# Connect to database
con2 = sqlite3.connect(":memory:")
cur2 = con2.cursor()
# Create table with headers
cur2.execute("CREATE TABLE t (cdc_case_earliest_dt , cdc_report_dt, pos_spec_dt, onset_dt, current_status, sex, age_group, race_ethnicity_combined, hosp_yn, icu_yn, death_yn, medcond_yn);")
# Open the CSV and populate columns
with open ('covid19.csv', 'r') as fin:
    dr = csv.DictReader(fin)
    to_db = [(i['cdc_case_earliest_dt '], i['cdc_report_dt'], i['pos_spec_dt'], i['onset_dt'], i['current_status'], i['sex'], i['age_group'], i['race_ethnicity_combined'], i['hosp_yn'], i['icu_yn'], i['death_yn'], i['medcond_yn']) for i in dr]

# Insert columns into table and commit
cur2.executemany("INSERT INTO t (cdc_case_earliest_dt , cdc_report_dt, pos_spec_dt, onset_dt, current_status, sex, age_group, race_ethnicity_combined, hosp_yn, icu_yn, death_yn, medcond_yn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con2.commit()

# Print SQLite results
print("SQLite read/write:")
print(datetime.now() - start)
start = datetime.now()

cur2.execute("SELECT hosp_yn, COUNT(hosp_yn) FROM t WHERE age_group='0 - 9 Years' GROUP BY hosp_yn")
print(cur2.fetchall())

# Print count results
print("SQL count:")
print(datetime.now() - start)
print('\n')
con2.close()

# -- BENCHMARK DUCKDB --
start = datetime.now()

# Connect to database
con3 = duckdb.connect(database=':memory:', read_only=False)
cur3 = con3.cursor()
# Create table with headers
cur3.execute("CREATE TABLE t (cdc_case_earliest_dt  VARCHAR, cdc_report_dt VARCHAR, pos_spec_dt VARCHAR, onset_dt VARCHAR, current_status VARCHAR, sex VARCHAR, age_group VARCHAR, race_ethnicity_combined VARCHAR, hosp_yn VARCHAR, icu_yn VARCHAR, death_yn VARCHAR, medcond_yn VARCHAR);")
# Insert values into table from CSV
cur3.execute("INSERT INTO t SELECT * FROM read_csv_auto('covid19.csv', HEADER=TRUE);")
con3.commit()

# Print DuckDB results
print("DuckDB read/write:")
print(datetime.now() - start)

start = datetime.now()
cur3.execute("SELECT hosp_yn, COUNT(hosp_yn) FROM t WHERE age_group='0 - 9 Years' GROUP BY hosp_yn")
print(cur3.fetchall())

# Print count results
print("DuckDB count:")
print(datetime.now() - start)
con3.close()

