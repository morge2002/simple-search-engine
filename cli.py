import json
import time
import requests

import typer
import progressbar

from crawler import Crawler
from indexer import Indexer
from search_engine import SearchEngine

app = typer.Typer()
session = requests.Session()

website_url = "https://quotes.toscrape.com/"
indexer = Indexer()
crawler = Crawler(website_url, indexer=indexer)
search_engine = SearchEngine(indexer)


@app.command()
def build():
    bar = progressbar.ProgressBar(maxval=progressbar.UnknownLength)
    indexer.wipe_index()
    crawler.reset_crawler()
    crawler.crawl(website_url)
    indexer.save_index()


@app.command()
def load():
    indexer.load_index()
    print("Index loaded.")


@app.command(name="print")
def print_index(search_word: str):
    search_word = indexer.parse_word(search_word)

    if search_word not in indexer.word_index:
        print(f"Word '{search_word}' not in index.")
        return
    index = {}
    for page_id, value in indexer.word_index[search_word].items():
        index[indexer.id_to_url[page_id]] = value

    print(f"Word '{search_word}' index:")
    print(json.dumps(index, indent=2))


@app.command()
def find(search_phrase: str):
    print(search_phrase)
    search_engine.search(search_phrase)
    print("Search complete.\n")


def main():
    while True:
        typer.echo("Enter a command (build, load, print, find), or 'exit' to quit:")
        time.sleep(0.5)
        command = input("> ").strip()

        if command == "exit":
            session.close()
            break

        try:
            # Split the command into a list if it contains spaces to pass to the Typer app
            command_list = [command]
            if " " in command:
                command_list = command.split(" ")
                # Join the words after the words after the main command so a single string is passed
                command_list = [command_list[0], " ".join(command_list[1:])]
            app(command_list)
        except SystemExit:
            continue


if __name__ == "__main__":
    main()
