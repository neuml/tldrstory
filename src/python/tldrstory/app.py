"""
Streamlit application
"""

import logging
import sys

import altair as alt
import pandas as pd
import requests
import streamlit as st
import yaml

class Components(object):
    """
    Streamlit application components.
    """

    @staticmethod
    def css():
        """
        Sets application wide css
        """

        style = """
            <style>
                a {
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        """

        # Apply style
        st.markdown(style, unsafe_allow_html=True)

    @staticmethod
    def header(name):
        """
        Renders a header.

        Args:
            name: name to show in header
        """

        # Set title on page body
        st.title(name)

    @staticmethod
    def description(layout):
        """
        Renders markdown in sidebar which describes the application.

        Args:
            layout: layout configuration
        """

        if "description" in layout:
            st.sidebar.markdown(layout["description"])

    @staticmethod
    def query(layout):
        """
        Renders a query box.

        Args:
            layout: layout configuration

        Returns:
            query text, topic flag
        """

        query, topic = None, 1
        if "queries" in layout:
            query = st.selectbox(layout["queries"]["name"], layout["queries"]["values"])
            if query == "--Search--":
                query, topic = st.text_input("Search"), None

        return query, topic

    @staticmethod
    def filters(layout):
        """
        Renders a list of slider components.

        Args:
            layout: layout configuration

        Returns:
            list of slider values
        """

        filters = []
        if "filters" in layout:
            for name in layout["filters"]:
                filters.append((name, [x / 10 for x in st.slider(name, 0, 10, (0, 10), 1)]))

        return filters

    @staticmethod
    def chart(df, layout):
        """
        Renders a summary chart.

        Args:
            df: dataframe
            layout: layout configuration
        """

        if "chart" in layout:
            config = layout["chart"]

            # Conditional colors
            scale = alt.Scale(domain=config["scale"], range=config["colors"])

            st.header(config["name"])
            st.altair_chart(
                alt.Chart(df).mark_circle(size=90)
                             .encode(x=alt.X(config["x"], scale=alt.Scale(domain=[0, 10]), axis=alt.Axis(labels=False, ticks=False)),
                                     y=alt.Y(config["y"], scale=alt.Scale(domain=[0, 10])),
                                     color=alt.Color(config["x"], scale=scale, legend=None))
                             .configure_axis(grid=False).configure_view(strokeOpacity=0), use_container_width=True
            )

    @staticmethod
    def summary(df, layout):
        """
        Renders a summary block.

        Args:
            df: dataframe
            layout: layout configuration
        """

        summary = []

        for column, config in layout["table"].items():
            mean = df[column].mean()
            if config:
                # Apply style to summary section
                summary.append("%s: %s" % (column, Components.style(config, mean)))

                # Apply style to column
                df[column] = df.apply(lambda x: Components.style(config, x[column]), axis=1)
            else:
                summary.append("%s: ```%.1f```" % (column, mean))

        summary.append("Articles: " + "```%d```" % len(df))

        # Summary
        st.markdown(" ".join(summary), unsafe_allow_html=True)

    @staticmethod
    def table(df):
        """
        Renders query results.

        Args:
            df: dataframe
        """

        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    @staticmethod
    def link(url, name):
        """
        Renders a hyperlink.

        Args:
            url: url
            name: text to show

        Returns:
            hyperlink text
        """

        return '<a href="{}" rel="noopener noreferrer" target="_blank">{}</a>'.format(url, name)

    @staticmethod
    def style(config, value):
        """
        Renders a style span.

        Args:
            config: style configuration
            value: input value

        Returns:
            styled result
        """

        for low, high, name, style in config:
            if low <= value <= high:
                return '<span style="{}">{}</span>'.format(style, name)

        return None

class App(object):
    """
    Streamlit application
    """

    def __init__(self, index):
        """
        Creates a new application.

        Args:
            index: index configuration
        """

        # Initialize logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(module)-10s: %(message)s")

        # Load YAML settings
        with open(index, "r") as f:
            # Read configuration
            self.index = yaml.safe_load(f)

    def query(self, query, topic, filters):
        """
        Runs an API query.

        Args:
            query: query to run
            topic: flag that signals query is a pre-defined topic (1) or ad hoc query (0 or None)
            filters: additional filters to apply

        Returns:
            query results
        """

        params = {"query": query, "limit": 100, "topic": topic, "filters": ":".join([name.lower() for name, _ in filters])}

        # Encode each filter value as additional parameters
        for name, value in filters:
            params[name.lower()] = ":".join([str(x) for x in value])

        return requests.get(self.index["api"] + "/search", params=params).json()

    def search(self, query, topic, filters):
        """
        Executes a search.

        Args:
            query: query to run
            topic: flag that signals query is a pre-defined topic (1) or ad hoc query (0 or None)
            filters: additional filters to apply

        Returns:
            query results
        """

        # Run query against API
        results = self.query(query, topic, filters)

        # Dataframe columns
        columns = ["Date", "Title", "Reference"] + [name for name, _ in filters]

        # Format common fields
        df = pd.DataFrame(results, columns=columns)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        df["Title"] = df.apply(lambda x: Components.link(x["Reference"], x["Title"]), axis=1)

        return df.drop(columns=["Reference"])

    def render(self):
        """
        Renders application.
        """

        # Streamlit layout configuration
        layout = self.index["layout"]

        # Apply global css rules
        Components.css()

        # Application title
        Components.header(self.index["name"])

        # Application description
        Components.description(layout)

        # Query filters
        query, topic = Components.query(layout)

        # Slider filters
        filters = Components.filters(layout)

        # Execute query and build dataframe
        df = self.search(query, topic, filters)

        # Normalize slider ranges
        for name, _ in filters:
            df[name] = df.apply(lambda x: x[name] * 10, axis=1).round(1)

        # Build summary chart
        Components.chart(df, layout)

        # Build summary details
        Components.summary(df, layout)

        # Table
        Components.table(df)

@st.cache
def create(index):
    """
    Creates and caches an application instance.

    Args:
        index: configuration file path

    Returns:
        Application
    """

    return App(index)

# Set page title and icon
if len(sys.argv) > 3:
    st.beta_set_page_config(sys.argv[2], sys.argv[3], "centered", initial_sidebar_state="expanded")

# Create the application
app = create(sys.argv[1])

# Render the application
app.render()
