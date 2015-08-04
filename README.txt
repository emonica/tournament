Archive contents
================

* tournament.sql
   the two tables creation

* tournament.py
   the file containing the application logic

* tournament_test.py
   supplied file with test functions, with a couple of changes in order 
   to accomodate the possibility of tie games

* README.txt



Usage
=====

create database tournament
psql -f tournament.sql
python tournament_test.py
