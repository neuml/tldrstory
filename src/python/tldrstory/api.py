"""
Backend model API
"""

import os
import sqlite3

import txtai.api

class API(txtai.api.API):
    """
    Extended API on top of txtai to return enriched query results.
    """

    def find(self, cur, query, request):
        """
        Executes query against embeddings index and/or SQLite, depending on the query.

        Args:
            cur: open database cursor
            query: query text
            request: FastAPI request

        Returns:
            query results
        """

        if not query:
            return cur.execute("SELECT id, 1.0 as score FROM articles ORDER BY date DESC LIMIT 100").fetchall()

        elif query.startswith("url:"):
            query = query.replace("url:", "")
            query = "%" + query + "%"

            return cur.execute("SELECT id, 1.0 as score FROM articles WHERE reference like ? ORDER BY date DESC LIMIT 100", [query]).fetchall()

        elif "topic" in request.query_params and request.query_params["topic"] == "1":
            return cur.execute("SELECT id, 1.0 as score FROM articles a WHERE " +
                               "(SELECT value FROM labels WHERE article=a.id AND category = 'topic' AND name=?) >= 0.5 " +
                               "ORDER BY date DESC LIMIT 100", [query]).fetchall()

        return [(row["id"], row["score"]) for row in super().search(query, request)]

    def search(self, query, request):
        """
        Extends txtai API to enrich results with content.

        Args:
            query: query text
            request: FastAPI request

        Returns:
            query results
        """

        results, filters = [], []

        # Unpack filters
        if "filters" in request.query_params:
            filters = request.query_params["filters"].split(":")

        database = sqlite3.connect(os.path.join(self.config["path"], "articles.db"))
        cur = database.cursor()

        # Pull results
        for uid, score in self.find(cur, query if query != "Latest" else None, request):
            if score >= 0.3:
                # Statement parameters
                params = []

                # Build sql statement
                sql = "SELECT date, title, reference"

                # Build slider select sql
                for name in filters:
                    sql += ", (SELECT value FROM labels WHERE article=? AND category=? AND name=?) AS %s" % name
                    params.extend([uid, name, name])

                sql += " FROM articles WHERE id = ?"
                params.append(uid)

                # Add slider range filters
                for name in filters:
                    # Get current range from request
                    current = [float(x) for x in request.query_params[name].split(":")]

                    sql += " AND %s >= ? AND %s <= ?" % (name, name)
                    params.extend(current)

                # Run statement
                cur.execute(sql, params)

                result = cur.fetchone()
                if result:
                    results.append(result)

        return results
