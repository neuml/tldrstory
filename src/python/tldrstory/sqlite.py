"""
SQLite module
"""

import os
import logging
import sqlite3

from .database import Database

class SQLite(Database):
    """
    Defines data structures and methods to store article content in SQLite.
    """

    # Articles schema
    ARTICLES = {
        "Id": "TEXT PRIMARY KEY",
        "Source": "TEXT",
        "Date": "DATETIME",
        "Title": "TEXT",
        "Reference": "TEXT",
        "Entry": "DATETIME"
    }

    # Labels schema
    LABELS = {
        "Id": "INTEGER PRIMARY KEY",
        "Article": "TEXT",
        "Category": "TEXT",
        "Name": "TEXT",
        "Value": "REAL"
    }

    # SQL statements
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {table} ({fields})"
    INSERT_ROW = "INSERT INTO {table} ({columns}) VALUES ({values})"
    CREATE_INDEX = "CREATE INDEX IF NOT EXISTS labels_article ON labels(article)"

    def __init__(self, outdir):
        """
        Creates and initializes a new output SQLite database.

        Args:
            outdir: output directory
        """

        # Create if output path doesn't exist
        os.makedirs(outdir, exist_ok=True)

        # Output database file
        dbfile = os.path.join(outdir, "articles.db")

        # Index fields
        self.aindex = 0

        # Create output database
        self.db = sqlite3.connect(dbfile)

        # Create database cursor
        self.cur = self.db.cursor()

        # Create articles table
        self.create(SQLite.ARTICLES, "articles")

        # Create labels table
        self.create(SQLite.LABELS, "labels")

        # Start transaction
        self.cur.execute("BEGIN")

    def save(self, article):
        # Unpack data
        article, labels = article

        # Article
        self.insert(SQLite.ARTICLES, "articles", article)

        # Labels
        for label in labels:
            self.insert(SQLite.LABELS, "labels", label)

        # Increment number of articles processed
        self.aindex += 1
        if self.aindex % 1000 == 0:
            logging.info("Inserted %d articles", self.aindex)

            # Commit current transaction and start a new one
            self.transaction()

    def complete(self):
        logging.info("Total articles inserted: %d", self.aindex)

        # Create articles index for sections table
        self.execute(SQLite.CREATE_INDEX)

    def close(self):
        self.db.commit()
        self.db.close()

    def transaction(self):
        """
        Commits current transaction and creates a new one.
        """

        self.db.commit()
        self.cur.execute("BEGIN")

    def create(self, table, name):
        """
        Creates a SQLite table.

        Args:
            table: table schema
            name: table name
        """

        columns = ["{0} {1}".format(name, ctype) for name, ctype in table.items()]
        create = SQLite.CREATE_TABLE.format(table=name, fields=", ".join(columns))

        # pylint: disable=W0703
        try:
            self.cur.execute(create)
        except Exception as e:
            logging.error(create)
            logging.error(e)

    def execute(self, sql):
        """
        Executes SQL statement against open cursor.

        Args:
            sql: SQL statement
        """

        self.cur.execute(sql)

    def insert(self, table, name, row):
        """
        Builds and inserts a row.

        Args:
            table: table object
            name: table name
            row: row to insert
        """

        # Build insert prepared statement
        columns = [name for name, _ in table.items()]
        insert = SQLite.INSERT_ROW.format(table=name,
                                          columns=", ".join(columns),
                                          values=("?, " * len(columns))[:-2])

        try:
            # Execute insert statement
            self.cur.execute(insert, self.values(table, row, columns))
        # pylint: disable=W0703
        except Exception as ex:
            logging.error("Error inserting row: %s", row)
            logging.error(ex)

    def values(self, table, row, columns):
        """
        Formats and converts row into database types based on table schema.

        Args:
            table: table schema
            row: row tuple
            columns: column names

        Returns:
            Database schema formatted row tuple
        """

        values = []
        for x, column in enumerate(columns):
            # Get value
            value = row[x]

            if table[column].startswith("TEXT"):
                # Clean empty text and replace with None
                values.append(value if value and len(value.strip()) > 0 else None)
            else:
                values.append(value)

        return values
