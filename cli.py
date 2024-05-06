import json
import os
import time
import requests

import typer
import progressbar
from rich import print

from crawler import Crawler
from indexer import Indexer
from search_engine import SearchEngine

app = typer.Typer()
session = requests.Session()

website_url = "https://quotes.toscrape.com/"
indexer = Indexer()
crawler = Crawler(website_url, indexer=indexer)
search_engine = SearchEngine(indexer)

index_loaded = False


@app.command(name="build")
def build():
    bar = progressbar.ProgressBar(maxval=progressbar.UnknownLength)
    indexer.wipe_index()
    crawler.reset_crawler()
    crawler.crawl(website_url)
    indexer.save_index()


@app.command(name="load")
def load():
    indexer.load_index()
    index_loaded = True
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


@app.command(name="find")
def find(search_phrase: str):
    print(f"Searching for {search_phrase}:")
    search_engine.search(search_phrase)
    print("Search complete.")


def main():
    commands = ", ".join([command.name for command in app.registered_commands])
    print("\n[bold underline green]Welcome to the search engine CLI![/bold underline green]")
    while True:
        time.sleep(0.1)
        print(f"\n[green]Enter a command ({commands}), or 'exit' to quit:[/green]")
        print(
            f"[blue]"
            f"INFO: "
            f"Index present: [underline]{os.path.exists(indexer.index_file_path)}[/underline], "
            f"Index loaded: [underline]{index_loaded}[/underline], "
            f"Website: {website_url}, "
            f"Index size: [underline]{len(indexer.page_index)}[/underline] pages)"
            f"[/blue]"
        )

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
