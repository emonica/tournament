#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from games;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("delete from players;")
    db.commit()
    db.close()


def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    c.execute("select count(*) from players;")
    result = c.fetchone()
    db.close()
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into players(name) values(%s);", (name,))
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins and
    ties. Uses the 'winner' field in the game database, that can be one of the
    following: 1 (player1 won), 2 (player2 won), 0 (tie)

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches, ties):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        ties: the number of player's matches that ended in tie
    """
    db = connect()
    c = db.cursor()
    c.execute("select players.id, name, \
        sum (case when (players.id = player1 and winner = 1) or \
                       (players.id = player2 and winner = 2) \
             then 1 else 0 end) as wins, \
        sum (case when players.id = player1 or players.id = player2 \
             then 1 else 0 end) as matches, \
        sum (case when (players.id = player1 or players.id = player2) and \
                       winner = 0 \
             then 1 else 0 end) as ties \
        from players left join games \
        on (players.id = player1 or players.id = player2) \
        group by players.id \
        order by wins desc, ties desc;")
    standings = c.fetchall()
    db.close()
    return standings


def reportMatch(player1, player2, winner):
    """Records the outcome of a single match between two players.

    Args:
      player1:  the id number of the first player
      player2:  the id number of the second player
      winner:   can be 1, 2 or 0:
                   1 if player1 won
                   2 if player2 won
                   0 for tie
    """
    db = connect()
    c = db.cursor()
    c.execute("insert into games(player1, player2, winner) values(%s,%s,%s);",
              (player1, player2, winner))
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairings = []
    for i in xrange(0, len(standings), 2):
        pairings.append((standings[i][0], standings[i][1],
                         standings[i+1][0], standings[i+1][1]))
    return pairings
