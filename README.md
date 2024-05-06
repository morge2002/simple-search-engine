# Web Crawler and Search Engine

This project is a simple web crawler and search engine built in Python. It uses the BeautifulSoup library to parse HTML
and extract text content from web pages, and the requests library to fetch web pages. The crawler follows links on each
page to discover new pages, and it observes a politeness window to avoid overwhelming the website with requests.

The text content of each page is indexed by the Indexer class, which stores a dictionary of word frequencies to pages.
Each page has an ID used to reference the page in the index. The index is saved to a file and can be loaded from a file.

The SearchEngine class performs search queries on the index. Search queries are ranked by their each word's frequency in
a page multiplied by the tf-idf score of the word in the query.

## Files

- `crawler.py`: Contains the Crawler class which is responsible for crawling a website and indexing its content.
- `indexer.py`: Contains the Indexer class which is responsible for indexing the text content of web pages.
- `search_engine.py`: Contains the SearchEngine class which performs search queries on the index.
- `search.py`: Contains the command line interface for the project.

## Usage

To use this project, you must the command line interface.

```bash
python3 search.py
```

First, build the index by running the `build` command. This will crawl the website and index its content. The index is
saved to a file.

```bash
> build
```

Next, load the index by running the `load` command. This will load the index from the file.

```bash
> load
```

You can print the index of a word by running the `print` command followed by the word.

```bash
> print <word>
```

Finally, you can perform a search query by running the `find` command followed by the search phrase.

```bash
> find <search phrase>
```

## Requirements

- Python 3.8+
- BeautifulSoup
- requests
- typer
- rich
- progress

## Installation

1. Clone the repository
2. Install the requirements

```bash
pip install -r requirements.txt
```

3. Run the CLI

```bash
python3 search.py
```

## Note

This project is for educational purposes only. Please respect the terms of service of any website you crawl.