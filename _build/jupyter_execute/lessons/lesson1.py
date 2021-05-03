## Get the data  

To get started, we have to request the SQLite file.

import requests

url = "https://ndownloader.figshare.com/files/2292171"
r = requests.get(url)

with open('../data/portals_mammal.sqlite', 'wb') as f:
    f.write(r.content)

## Connecting to the database  

Now that we have the data, we can connect through SQLite.

import sqlite3
con= sqlite3.connect('../data/portals_mammal.sqlite')

type(con)

Here, we perform a basic SELECT operation, selecting:
* year, species_id, and plot_id from _surveys_.  
This selects those attributes from the surveys relation, and ignores all others.

cursor = con.cursor()
cursor.execute("select year, species_id, plot_id from surveys")

Print the first row from the selected attributes.

row1 = cursor.fetchone()
print(row1)

print(" The first value is", row1[0])

Here, we try the same select, but limit the number of rows to 10.

cursor.execute("select year, species_id, plot_id from surveys limit 10")
all_rows = cursor.fetchall()
for row in all_rows:
    print(row)

In this SQL operation, we are going to add both _conditionals_ and the _JOIN_ operator.  

The _JOIN_ operator combines rows from two or more tables, using the following syntax:  
> (SET 1) join (SET 2) on (set1.id = set2.id)  
 
We can also add additional conditions to the join by adding a _where_ operation:

> where (condition = "value")  

In the following example, we join the _surveys_ and _species_ relations, using species_id as the relationship key. We select only species matching the species name "flavus" surveyed past the year 2000.
Limit of 10 is added to reduce the table size.

sql = """
select surveys.year, surveys.month, surveys.day, species.genus, species.species
from surveys
join species
on surveys.species_id = species.species_id
where species.species = "flavus"
and surveys.year > 2000
limit 10
"""

cursor.execute(sql)
for row in cursor:
    print(row)

  
In this example, we perform the same select and join operations as the previous code block, but rather than select all surveys of "flavus" above year 2000, we select only surveys taken in 1996, 1997, or 1998.
Again, we limit 10 to reduce table size.

sql = """
select surveys.year, surveys.month, surveys.day, species.genus, species.species
from surveys
join species
on surveys.species_id = species.species_id
where species.species = "flavus"
and surveys.year in (1996, 1997, 1998)
limit 10
"""

cursor.execute(sql)
for row in cursor:
    print(row)

## SQL and Pandas

**Challenge: modify last query to find surveys that were conducted in July or December in the year 1996, 1997, or 1998**

import pandas as pd
import sqlite3

con = sqlite3.connect("../data/portals_mammal.sqlite")

sql = """
select surveys.year, surveys.month, surveys.day, species.genus, species.species
from surveys
join species
on surveys.species_id = species.species_id
where species.species = "flavus"
and surveys.year > 2000
"""

df = pd.read_sql_query(sql, con)
print(df.head())
con.close()


Answer:
> and surveys.year in (1996, 1997, 1998) and surveys.month = "December"


## Creating a SQL table with pandas

Pandas is a data analysis tool built on the Numpy package that makes it very easy to manipulate and format databases and tables into usable structures.  

First off, it is important to have both Pandas and SQLite3 installed and up-to-date. These rely on Python3, so you may need to update your PATH if you are still on Python 2.x.  

#### A quick explanation of Pandas

Pandas utilizes a key datastructure called the DataFrame. DataFrames allow you to store and manipulate tabular data in rows of obervations and columns of variables.  

There are many ways to create DataFrames from existing files (for example, one popular method is reading from CSV files). In this instance, we will be reading data from our SQLite file into a DataFrame using a custom SQL query, similar to the previous examples.

import pandas as pd
import sqlite3

con = sqlite3.connect("../data/portals_mammal.sqlite")
# load the data into a DataFrame
survey_df = pd.read_sql_query("select * from surveys", con)

# Select only data from 2002
surveys2002 = survey_df[survey_df.year == 2002]

# Write the new dataframe to a new sqlite 
surveys2002.to_sql("surveys2002", con, if_exists="replace")



We can use the DataFrames to create new SQL tables, as seen in the final line of the previous example. Now, we can perform additional SQL operations to manipulate our data further.

df = pd.read_sql_query("select * from surveys2002", con)
print(df.head())
con.close()