"""
Reddit module
"""

import logging

from datetime import datetime

import praw

from .source import Source

class Reddit(Source):
    """
    Builds articles from a series of Reddit API queries.
    """

    def run(self):
        # List of articles created
        articles = []

        # Reddit API connection
        connection = praw.Reddit()

        # Reddit API configuration
        api = self.config["reddit"]

        # Execute each query
        for query in api["queries"]:
            # Filter for safe links
            query += " self:0 nsfw:0"

            logging.info("Running query: %s", query)

            for submission in connection.subreddit(api["subreddit"]).search(query, sort=api["sort"], time_filter=api["time"], limit=None):
                # Parse create date
                date = datetime.fromtimestamp(submission.created_utc)

                # Only consider link posts
                if not submission.is_self:
                    # Build article object
                    article = self.article(submission.id, submission.subreddit.display_name.lower(), date, submission.title,
                                           submission.url, self.now())

                    # Append to articles list
                    articles.append(article)

        return articles
