"""
database.py
------------
The main.py and services.py  just ask this file for
data, and this file goes and gets it from makerspace.db. If we ever
wanted to swap SQLite for another database, this is the only file we'd
have to change.


"""

import sqlite3


class Database:
    """Wraps a SQLite connection and creates and holds our three tables."""

    def __init__(self, db_name="makerspace.db"):
        
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row

        # Lets SQLite enforce that a loan's member_id/equipment_id must
        # point to a real row in members/equipment.
        self.connection.execute("PRAGMA foreign_keys = ON")

        self.create_tables()

    def create_tables(self):
        """Create the three tables if they don't already exist.

        """
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT NOT NULL,
                email      TEXT NOT NULL UNIQUE,
                phone      TEXT,
                join_date  TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                name     TEXT NOT NULL,
                category TEXT NOT NULL,
                status   TEXT NOT NULL DEFAULT 'available'
            )
        """)

        # status is either 'active' or 'returned'.
        # return_date is empty (NULL) until the item comes back.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id      INTEGER NOT NULL,
                equipment_id   INTEGER NOT NULL,
                checkout_date  TEXT NOT NULL,
                due_date       TEXT NOT NULL,
                return_date    TEXT,
                status         TEXT NOT NULL DEFAULT 'active',
                FOREIGN KEY (member_id) REFERENCES members (id),
                FOREIGN KEY (equipment_id) REFERENCES equipment (id)
            )
        """)

        self.connection.commit()

    
    
    # Everything above sets the tables up once. Everything below is
    # what the rest of the app actually calls, over and over, while
    # it's running.

    def execute(self, query, params=()):
        """Run an INSERT / UPDATE / DELETE statement and save the change.

        Returns the cursor so the caller can read cursor.lastrowid
        (the id SQLite just gave a new row) if they need it.
        """
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, query, params=()):
        """Run a SELECT and return a single row (or None if no match)."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetch_all(self, query, params=()):
        """Run a SELECT and return every matching row as a list."""
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def close(self):
        self.connection.close()
