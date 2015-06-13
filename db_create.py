#!/usr/bin/python

# Create database script for the polarbear/automator
# Because the first database schema I make will probably
# suck and I'd just like to write down what I did in case
# of FUBAR

import sqlite3 as sq

conn = sq.connect('polarbear.db')
c = conn.cursor()

c.execute('PRAGMA foreign_keys = ON;')

c.execute('DROP TABLE IF EXISTS run_ident;')
c.execute('''CREATE TABLE run_ident 
          (id INTEGER PRIMARY KEY, 
          date TEXT, 
          sample_name TEXT, 
          measurement_type INTEGER, 
          temperature REAL,
          port INTEGER);''')

c.execute('DROP TABLE IF EXISTS run_data;')
c.execute('''CREATE TABLE run_data
          (id INTEGER REFERENCES run_ident(id) ON UPDATE CASCADE, 
          bias REAL, 
          sensitivity REAL, 
          reading REAL);''')

conn.commit()
conn.close()

