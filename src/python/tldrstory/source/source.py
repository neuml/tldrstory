"""
Source module
"""

from collections import namedtuple
from datetime import datetime

class Source(object):
    """
    Base class for all sources. A source maps input data into articles for further processing.
    """

    def __init__(self, config):
        """
        Create a new source

        Args:
            config: index configuration
        """

        # Source configuration
        self.config = config

        # Article schema definition
        self.article = namedtuple("Article", ["uid", "source", "date", "title", "url", "entry"])

    def run(self):
        """
        Maps a source into a list of articles.

        Articles have the following schema:
            uid - unique id
            source - source name
            date - article date
            title - article title
            url - reference url for data
            entry - entry date

        Sources must implement this method, returning a list of articles. Articles can be created via the call:
            self.article()

        The above method must be called with each article field defined. self.article is a namedtuple, fields can
        be added in the same order as the schema defined above or as named parameters.

        Returns:
            list of articles
        """

        return []

    def now(self):
        """
        Builds a timestamp for the current time.

        Returns:
            YYYY-MM-DD HH:MI:SS timestamp
        """

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
