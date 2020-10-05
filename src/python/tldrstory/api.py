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

        # Execute search and order by date desc
        results = super().search(query, request)
        ids = ",".join(["'" + uid + "'" for uid, _ in results])
        ids = "(" + ids + ")"

        cur.execute("SELECT id, date FROM articles WHERE id in %s" % ids)
        lookup = {uid:date for uid, date in cur.fetchall()}

        return sorted(results, key=lambda x: lookup[x[0]], reverse=True)

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

        database = sqlite3.connect(os.path.join(self.index["path"], "articles.db"))
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
                    # Lookup label select
                    values = self.index["labels"][name]["select"]

                    fields = " OR ".join(["Name = ?"] * len(values))
                    sql += ", (SELECT SUM(value) FROM labels WHERE Article=? AND (%s)) AS %s" % (fields, name)
                    params.append(uid)
                    params.extend(values)

                sql += " FROM articles WHERE Id = ?"
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
