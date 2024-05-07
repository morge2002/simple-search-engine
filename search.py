import json
import os
import time

import requests
import typer
from rich import print
import tabulate

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
    indexer.wipe_index()
    crawler.reset_crawler()
    crawler.crawl(website_url)
    indexer.save_index()


@app.command(name="load")
def load():
    indexer.load_index()
    global index_loaded
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

    output = {"Page": [], "Word Frequency": []}
    for page_id, value in indexer.word_index[search_word].items():
        output["Page"].append(indexer.id_to_url[page_id])
        output["Word Frequency"].append(value)

    print(f"Word '{search_word}' index:")
    print(tabulate.tabulate(output, headers="keys", showindex="always", tablefmt="simple_grid"))


@app.command(name="find")
def find(search_phrase: str):
    results = search_engine.search(search_phrase)

    output = {"Page": [], "Rank": []}
    for i, rank in enumerate(results):
        if i >= 10:
            break
        output["Page"].append(indexer.id_to_url[rank[0]])
        output["Rank"].append(rank[1])
    print(f"Top 10 results for '{search_phrase}':")
    print(tabulate.tabulate(output, headers="keys", showindex="always", tablefmt="simple_grid"))
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
