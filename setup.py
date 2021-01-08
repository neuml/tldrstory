# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r") as f:
    DESCRIPTION = f.read()

setup(name="tldrstory",
      version="1.3.0",
      author="NeuML",
      description="AI-powered understanding of headlines and story text",
      long_description=DESCRIPTION,
      long_description_content_type="text/markdown",
      url="https://github.com/neuml/tldrstory",
      project_urls={
          "Documentation": "https://github.com/neuml/tldrstory",
          "Issue Tracker": "https://github.com/neuml/tldrstory/issues",
          "Source Code": "https://github.com/neuml/tldrstory",
      },
      license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
      packages=find_packages(where="src/python"),
      package_dir={"": "src/python"},
      keywords="search embedding machine-learning nlp",
      python_requires=">=3.6",
      install_requires=[
          "croniter>=0.3.34",
          "feedparser>=6.0.1",
          "praw>=7.1.0",
          "requests>=2.24.0",
          "streamlit>=0.68.0",
          "txtai>=2.0.0"
      ],
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Scientific/Engineering :: Artificial Intelligence",
          "Topic :: Software Development",
          "Topic :: Text Processing :: Indexing",
          "Topic :: Utilities"
      ])
