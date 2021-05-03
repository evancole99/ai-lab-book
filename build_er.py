import sqlite3
from eralchemy import render_er

## Draw from SQLalchemy base
#renderer(Base, 'erd_from_sqlalchemy.png')
render_er("sqlite:///data/mammals.sqlite", 'data/erd_from_sqlite.png')
