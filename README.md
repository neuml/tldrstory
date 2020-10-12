# tldrstory: AI-powered understanding of headlines and story text

tldrstory is a framework for AI-powered understanding of headlines and text content related to stories. tldrstory applies zero-shot labeling over text, which allows dynamically categorizing content. This framework also builds a txtai index that enables text similarity search. A customizable Streamlit application and FastAPI backend service allows users to review and analyze the data processed.

## Examples

The following links are example applications built with tldrstory.

- [Election 2020](https://tldrstory.com/election-2020) [(Configuration files)](https://github.com/neuml/tldrstory/tree/master/apps)

<p align="center">
    <img src="https://raw.githubusercontent.com/neuml/tldrstory/master/demo.gif"/>
</p>

## Installation
The easiest way to install is via pip and PyPI

    pip install tldrstory

You can also install tldrstory directly from GitHub. Using a Python Virtual Environment is recommended.

    pip install git+https://github.com/neuml/tldrstory

Python 3.6+ is supported

Check out [troubleshooting link](https://github.com/neuml/txtai#troubleshooting) to help resolve environment-specific install issues.

## Indexing

Configures indexing of content. Currently supports pulling data via the Reddit API. See [this link](https://praw.readthedocs.io/en/latest/getting_started/quick_start.html) for more information on setting up a Reddit API account, read-only access is all that is needed. 

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

### path
```yaml
path: string
```

Where to store model output, path will be created if it doesn't already exist. 

### api
```yaml
api.subreddit: name of subreddit to pull from 
api.sort: sort type
api.time: time range
api.queries: list of text queries to run
api.ignore: list of url patterns to ignore
```

Runs a series of Reddit API queries. See [PRAW documentation](https://praw.readthedocs.io/en/latest/code_overview/models/subreddit.html) for more details on this.

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
