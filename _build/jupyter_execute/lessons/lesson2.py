[![Lesson 2 Video](http://img.youtube.com/vi/bU2_C6YILmo/0.jpg)](http://www.youtube.com/watch?v=bU2_C6YILmo "Lesson 2")

## Get the data

import requests

url = "https://ndownloader.figshare.com/files/2292171"
r = requests.get(url)

with open('../data/portals_mammal.sqlite', 'wb') as f:
    f.write(r.content)

## Connecting to the database

import sqlite3
con= sqlite3.connect('../data/portals_mammal.sqlite')

Let's get some info about the database we connected to:

type(con)

Just like spreadsheets, SQLite databases can contain several different tables.  
In this example, we have three tables:  
* plots
* species
* surveys  
Each table has its own attributes. We can list a table's meta data, including its column headers (labels) using a _pragma statement_:

cursor = con.cursor()
cursor.execute("pragma table_info(surveys)")
print(cursor.fetchall())

From the output, we can see that the table _surveys_ has the following attributes:  
* record\_id
* month
* day
* year
* plot\_id
* species\_id
* sex
* hindfoot\_length
* weight

## Querying the database with SQL syntax

Now that we understand the underlying database structure, we can query the database using SQL commands, and display data contained in the tables.

cursor.execute("select year, species_id, plot_id from surveys")
row1 = cursor.fetchone()
print(row1)

print(" The first value is", row1[0])

## Querying the database with Pandas syntax

Pandas is a powerful data analysis and manipulation tool built on top of Python. Using Pandas, it is possible to perform the same operations as SQL using only Pandas syntax.  

Pandas operates using data structures called DataFrames. They are essentially tables of data operating by the normal row-column format. A variety of operations and commands are built in to Pandas, making it a very flexible data analysis tool.

import pandas as pd
import sqlite3

con = sqlite3.connect("../data/portals_mammal.sqlite")

# load data from sqlite file into DataFrame
surveys = pd.read_sql_query("select * from surveys", con)

surveys.head()

The _head()_ command lists the first 5 rows of a DataFrame.
We can see the entire shape of the table using  _shape_:

surveys.shape

We can see that the _surveys_ table has shape 9 columns x 35549 rows.

### SQL translation

The following SQL query returns the first 5 rows from _surveys_:
``` sql
SELECT *
FROM `surveys`
LIMIT 5
```
Pandas translates your Python code into SQL, submits it to the database, and translates the database's response into a DataFrame. This example is equivalent to Pandas' _head()_ command.

### Simple queries

Let's try some simple queries of the _surveys_ table using Pandas. First, we will try to request rows from _surveys_ where _weight_ is less than 5. We will only keep the species\_id, sex, and weight columns.

ltwt = surveys[surveys["weight"] < 5]
result = ltwt[["species_id", "sex", "weight"]]
result.head()

### Complex queries

We can perform more complicated queries across multiple tables.
Since we are operating on a relational database, each table may contain _primary key_ and _foreign key_ attributes.  

A primary key attribute is a unique identifier for an entry in the table. For example, survey\_id is the primary key attribute for the _surveys_ table.  
A foreign key attribute is a unique identifier for an entry in another table. For example, the plot\_id attribute of the _surveys_ table is a foreign key referencing the _plots_ table.  

We can use these primary and foreign keys to join multiple DataFrames with matching key values.  

Let's test this by extracting all surveys for the first plot, which has plot\_id of 1.

# first, let's define our plots and species dataframes
plots = pd.read_sql_query("select * from plots", con)
species = pd.read_sql_query("select * from species", con)

# In order to join by key values, we must set the index to the same key in both dataframes

both = surveys.join(plots.set_index('plot_id'), on='plot_id')
plot_1 = both[both.plot_id == 1]
plot_1.head()


Above, we have joined the _plots_ and _surveys_ tables using plot\_id as the key value. Then, we select only surveys matching plot\_id of 1.

#### Challenge:  

Write a Pandas query that returns the number of rodents observed in each plot in each year.  
Hint: Create a new DataFrame to join the species and survey tables together. Then exclude non-rodents. The query should return counts of rodents by year.  

``` sql
SELECT table.col, table.col
FROM table1 JOIN table2
ON table1.key = table2.key
JOIN table3 ON table2.key = table3.key
```

<details>
<summary>Answer:</summary>

spcs_survs = surveys.join(species.set_index('species_id'), on='species_id')
result = spcs_survs[spcs_survs.taxa != 'Rodent']
result['taxa'].groupby(result['year']).agg({'count'})

</details>

#### Challenge:

Write a Pandas query that returns the total number of rodents in each genus caught in the different plot types.  
Hint: Write a query that joins species, plot, and surveys tables together. Then group by plot type, and return counts of genus.  

<details>
<summary>Answer:</summary>

spcs_survs = surveys.join(species.set_index('species_id'), on='species_id')
all = spcs_survs.join(plots.set_index('plot_id'), on='plot_id')
result = all[all.taxa != 'Rodent']
result['genus'].groupby(result['plot_type']).agg({'count'})

</details>


### Creating a new SQLite database

Until now, we have used a previously prepared SQLite database. However, it is possible to use Pandas to create a new database. One way to do this is using existing _csv_ files. We are going to recreate the mammals database in Python using Pandas.

url = "https://ndownloader.figshare.com/files/3299483"
r = requests.get(url)

with open('../data/species.csv', 'wb') as f:
    f.write(r.content)

url = "https://ndownloader.figshare.com/files/10717177"
r = requests.get(url)

with open('../data/surveys.csv', 'wb') as f:
    f.write(r.content)

url = "https://ndownloader.figshare.com/files/3299474"
r = requests.get(url)

with open('../data/plots.csv', 'wb') as f:
    f.write(r.content)

# We can use pandas read_csv to easily create dataframes
surveys = pd.read_csv('../data/surveys.csv')
species = pd.read_csv('../data/species.csv')
plots = pd.read_csv('../data/plots.csv')


Now arises the problem of writing the DataFrames to an SQLite database. Thankfully, Pandas offers a very handy built in function. All we have to do is create the database and call to\_sql on the dataframe.

con = sqlite3.connect('../data/mammals.sqlite')
surveys.to_sql('surveys', con, if_exists='replace')
species.to_sql('species', con, if_exists='replace')
plots.to_sql('plots', con, if_exists='replace')

cursor = con.cursor()
cursor.execute('select * from surveys')
row1 = cursor.fetchone()
print (row1)

And that is it! Our SQLite database is built. From there, we can perform any SQL queries like usual, or continue to use Pandas to alter the data.