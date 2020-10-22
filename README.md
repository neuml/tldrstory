# tldrstory: AI-powered understanding of headlines and story text

tldrstory is a framework for AI-powered understanding of headlines and text content related to stories. tldrstory applies zero-shot labeling over text, which allows dynamically categorizing content. This framework also builds a txtai index that enables text similarity search. A customizable Streamlit application and FastAPI backend service allows users to review and analyze the data processed.

## Examples

The following links are example applications built with tldrstory. These demos can also be found on https://tldrstory.com

- [Election 2020](https://tldrstory.com/election-2020) [(Configuration files)](https://github.com/neuml/tldrstory/tree/master/apps)

<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/tldrstory/master/apps/election/demo.gif"/>
</p>

- [Mobile Tech News](https://tldrstory.com/mobile-tech) [(Configuration files)](https://github.com/neuml/tldrstory/tree/master/apps)

<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/tldrstory/master/apps/devices/demo.gif"/>
</p>

- [Sports News](https://tldrstory.com/sports) [(Configuration files)](https://github.com/neuml/tldrstory/tree/master/apps)

<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/tldrstory/master/apps/sports/demo.gif"/>
</p>

## Installation
The easiest way to install is via pip and PyPI

    pip install tldrstory

You can also install tldrstory directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/tldrstory

Python 3.6+ is supported

Check out [troubleshooting link](https://github.com/neuml/txtai#troubleshooting) to help resolve environment-specific install issues.

## Configurating an application

Once installed, an application must be configured to run. A tldrstory application consists of three separate processes:

- Indexing
- API backend
- Streamlit application

This section will show how to start the "Sports News" application.

1. Download the folder https://github.com/neuml/tldrstory/tree/master/apps/sports locally to sports.

2. The default configuration uses a sentence-transformers model not currently on the Hugging Face model hub. For ease of install,
the setting embeddings.path can be changed to "sentence-transformers/bert-base-nli-mean-tokens" as shown below.

```yaml
# Embeddings index configuration
embeddings:
  method: transformers
  path: sentence-transformers/bert-base-nli-mean-tokens
```

3. Start the indexing process:

_Note_: The default configuration is on a schedule. The line in index.yml beginning with schedule can be removed to run immediately.

```bash
python -m tldrstory.index sports/index.yml
```

4. Start the API process:

```bash
INDEX_SETTINGS=sports/index.yml API_CLASS=tldrstory.api.API uvicorn "txtai.api:app"
```

5. Start Streamlit:

$SITE_PACKAGES refers to the actual install directory of tldrstory. For example, if you have a virtual env at /env/python, you need
to find the site-packages directory, /env/python/lib/python3.8/site-packages/ in this case.

```bash
streamlit run $SITE_PACKAGES/tldrstory/app.py sports/app.yml "Sports" "🏆"
```

6. Open a web browser and go to http://localhost:8501

## Parameter Reference
The following sections define configuration parameters for each process that is part of a tldrstory application.

## Indexing

Configures the indexing of content. Currently supports pulling data via the Reddit API, RSS and custom user-defined sources.

### name
```yaml
name: string
```

Application name

### schedule
```yaml
schedule: string
```

Cron-style string that enables scheduled running of the indexing job. See [this link](https://en.wikipedia.org/wiki/Cron) for more information on cron strings.

### sources

Data source configuration.

#### reddit
```yaml
reddit.subreddit: name of subreddit to pull from 
reddit.sort: sort type
reddit.time: time range
reddit.queries: list of text queries to run
```

Runs a series of Reddit API queries. A Reddit API key will need to be created and configured for this method to work. Authentication parameters can be set within the enviroment or in a praw.ini file. See [this link](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) for more information on setting up a Reddit API account, read-only access is all that is needed.

See [PRAW documentation](https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html) for more details on how to configure the query settings.

#### rss
```yaml
rss: list of RSS urls
```

Reads a series of RSS feeds and builds articles for each article link found.

#### source
```yaml
source: string
```

Configures a custom source. This parameter takes a full class path as a string, for example "tldrstory.source.rss.RSS"

Custom sources can be use any data that has a date, text string and reference url. See the documentation in [source.py](https://github.com/neuml/tldrstory/blob/master/src/python/tldrstory/source/source.py) for information on how to create a custom source. [rss.py](https://github.com/neuml/tldrstory/blob/master/src/python/tldrstory/source/rss.py) and [reddit.py](https://github.com/neuml/tldrstory/blob/master/src/python/tldrstory/source/reddit.py) are example implementations.

### ignore
```yaml
ignore: list of url patterns
```

List of url patterns to ignore. Supports strings and regular expressions.

### labels
```yaml
labels: dict
```

Label configuration for zero-shot classifier. This configuration sets a category along with a list of topic values.

Example:

```yaml
labels:
  topic:
    values: [Label 1, Label 2]
```

The example above configures the category "Topic" with two possible labels, "Label 1" and "Label 2". Any label can be set here and a large-scale
NLP model will be used to categorize input text into those labels.

### path
```yaml
path: string
```

Where to store model output, path will be created if it doesn't already exist. 

### embeddings
```yaml
embeddings: dict
```

Configures a txtai index used for searching topics. See [txtai configuration](https://github.com/neuml/txtai#configuration) for more details on this. 

## API

Configures a FastAPI backed interface for pulling indexed data.

### path
```yaml
path: string
```

Path to a model index.

## Application

The default application is powered by Streamlit and driven by a YAML configuration file. The configuration file sets the application name, API endpoint for pulling content, and component configuration. A custom Streamlit application or any other application can be used in place of this to pull content from the API endpoint directly.

### name
```yaml
name: string
```

Application name

### api
```yaml
api: url
```

API endpoint for pulling content. 

### layout
```yaml
description: string
```

Markdown string that is used to build a sidebar description.

#### queries
```yaml
queries.name: Queries drop down header
queries.values: List of values to use for queries drop down
```

Configures the query drop down box. This should be a list of pre-canned queries to use. If a value of "Latest" is present, it will query for the last N
articles. If a value of "--Search--" is present, it will present another text box to allow entering custom queries.

#### filters
```yaml
filters: list
```

List of slider filters. This should map to the zero-shot labels configured in the indexing section.

#### chart
```yaml
chart.name: Chart name
chart.x: Chart x-axis column
chart.y: Chart y-axis column
chart.scale: Color scale for list of colors
chart.colors: List of colors
```

Allows configuration of a scatter plot that graphs two label points. This chart can be used to plot and apply coloring to applied labels.

#### table
```yaml
"column name": dynamic range of coloring
```

Data table that shows result details. In addition to default columns, this section allows adding additional columns based on the zero-shot
labels applied. The default mode is to show the numeric value of the label but a range of text labels can also be applied.

For example:
  - [0, 5.0, Label 1, "color: #F00"]
  - [5.0, 10.0, Label 2, "color: #0F0"]

The above would output the text "Label 1" in red for values between 0 and 5. Values between 5 and 10 would output the text "Label 2" in green. 
