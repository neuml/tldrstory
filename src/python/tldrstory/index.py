"""
Indexing module
"""

import logging
import re
import sys
import time

from datetime import datetime

import yaml

from croniter import croniter
from txtai.embeddings import Embeddings
from txtai.pipeline import Labels

from .source.factory import Factory
from .sqlite import SQLite

class Index(object):
    """
    Methods to build a new embeddings index.
    """

    @staticmethod
    def baseurl(url):
        """
        Extracts a base unique url for the input url. Used to help with url duplicate detection.

        Args:
            url: input url

        Returns:
            base url
        """

        # Remove parameters
        url = url.split("?", 1)[0]

        # Remove leading http(s?)://www
        url = re.sub(r"^http(s)?:\/\/(www.)?", "", url)

        # Remove trailing index.html
        url = re.sub(r"(index.htm(l)?)$", "", url)

        # Remove trailing slashes
        url = re.sub(r"\/?$", "", url)

        return url

    @staticmethod
    def accept(database, article, ignore):
        """
        Filters an article based on a series of rules.

        Args:
            database: database connection
            article: article object
            ignore: list of domains to ignore

        Returns:
            True if accepted, False otherwise
        """

        # Get base url
        baseurl = Index.baseurl(article.url)

        # Check that article doesn't already exist
        database.cur.execute("SELECT 1 FROM articles WHERE Id=? OR Reference LIKE ?", [article.uid, "%" + baseurl + "%"])

        # Accept submission if:
        #  - Submission id or url doesn't already exist
        #  - Submission link isn't an ignored pattern
        return not database.cur.fetchone() and article.url.startswith("http") and \
               all([not re.search(pattern, article.url) for pattern in ignore])

    @staticmethod
    def labels(name, config, result):
        """
        Transforms a result into a set of labels. This method will create an aggregate field
        and normalize the range if set. Otherwise, the raw result is returned.

        Args:
            name: label name
            config: label configuration
            result: classifier results

        Returns:
            transformed labels and scores
        """

        # Build aggregate value for a list of fields
        if "aggregate" in config:
            score = sum([score for label, score in result if label in config["aggregate"]])

            # Normalize range
            if "normalize" in config:
                minscore, maxscore = config["normalize"]
                score = min(max(0.0, (score - minscore) / (maxscore - minscore)), 1.0)

            return [(name, score)]

        # Return results
        return result

    @staticmethod
    def embeddings(index, database):
        """
        Builds an embeddings index.

        Args:
            index: index configuration
            database: database handle with content to index
        """

        # Create embeddings model, backed by sentence-transformers & transformers
        embeddings = Embeddings(index["embeddings"])

        database.execute("SELECT Id, Title FROM articles")

        # Create an index for the list of articles
        articles = [(uid, text, None) for uid, text in database.cur.fetchall()]
        embeddings.index(articles)

        logging.info("Built embedding index over %d stored articles", len(articles))

        # Save index
        embeddings.save(index["path"])

    @staticmethod
    def execute(index):
        """
        Executes an index run.

        Args:
            index: index configuration
        """

        logging.info("Refreshing index: %s", index["name"])

        # Text classifier
        classifier = Labels()

        # Data source
        source = Factory.create(index)

        # Output database
        database = SQLite(index["path"])

        # Process each result
        for article in source.run():
            # Only process recent external link posts
            if Index.accept(database, article, index["ignore"]):
                # Build list of classification labels for text
                labels = []
                for name, config in index["labels"].items():
                    # Run classifier
                    result = classifier(article.title, config["values"])

                    # Transform into labels
                    result = Index.labels(name, config, [(config["values"][x], score) for x, score in result])

                    # Build list of labels for text
                    labels.extend([(None, article.uid, name) + x for x in result])

                # Save article
                database.save((article, labels))

        # Complete processing
        database.complete()

        # Build embeddings index
        Index.embeddings(index, database)

        # Close database
        database.close()

        logging.info("Indexing complete")

    @staticmethod
    def schedule(index):
        """
        Schedules index runs through a job scheduler.

        Args:
            index: index configuration
        """

        logging.info("Indexing scheduler enabled for %s using schedule %s", index["name"], index["schedule"])

        while True:
            # Schedule using localtime
            schedule = croniter(index["schedule"], datetime.now().astimezone()).get_next(datetime)
            logging.info("Next run scheduled for %s", schedule.isoformat())
            time.sleep(schedule.timestamp() - time.time())

            Index.execute(index)

    @staticmethod
    def run(index):
        """
        Runs an indexing process.

        Args:
            index: path to index configuration
        """

        # Initialize logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(module)-10s: %(message)s")

        # Load pipeline YAML file
        with open(index, "r") as f:
            # Read configuration
            index = yaml.safe_load(f)

        if "name" not in index:
            logging.error("Name is required")
            return

        # Check if indexing should be scheduled or run a single time
        if "schedule" in index:
            # Job scheduler
            Index.schedule(index)
        else:
            # Single run
            Index.execute(index)

if __name__ == "__main__":
    Index.run(sys.argv[1])
