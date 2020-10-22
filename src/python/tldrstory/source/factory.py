"""
Factory module
"""

from .reddit import Reddit
from .rss import RSS

class Factory(object):
    """
    Factory methods for creating sources.
    """

    @staticmethod
    def create(config):
        """
        Creates a new source instance.

        Args:
            config: index configuration

        Returns:
            source object
        """

        if "reddit" in config:
            # Reddit API
            return Reddit(config)
        elif "rss" in config:
            # List of RSS Feeds
            return RSS(config)
        elif "source" in config:
            # Dynamically create source from full object path
            return Factory.construct(config["source"], config)

        return None

    @staticmethod
    def construct(source, config):
        """
        Lookups a class name and constructs an instance of that class.

        Args:
            source: full source object name (for example tldrstory.source.rss.RSS)
            config: index configuration

        Returns:
            new instance of source
        """

        # Split into module and class
        parts = source.split('.')
        module = ".".join(parts[:-1])

        # Get class instance
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)

        # Create object instance
        return m(config)
