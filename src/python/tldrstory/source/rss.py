"""
RSS module
"""

import hashlib
import logging

from datetime import datetime
from time import mktime

import feedparser

from .source import Source

class RSS(Source):
    """
    Builds articles from a series of RSS feeds.
    """

    def run(self):
        # List of articles created
        articles = []

        # Get list of RSS feeds
        feeds = self.config["rss"]

        # Parse each feed
        for url in feeds:
            logging.info("Reading feed: %s", url)

            # Parse RSS feed
            data = feedparser.parse(url)

            # Process each entry
            for entry in data.entries:
                # Generate uid as MD5 of title
                uid = hashlib.md5(entry.title.encode()).hexdigest()

                # Published date
                date = datetime.fromtimestamp(mktime(entry.published_parsed))

                # Build article object
                article = self.article(uid, data.feed.title, date, entry.title, entry.link, self.now())

                # Append to articles list
                articles.append(article)

        return articles
