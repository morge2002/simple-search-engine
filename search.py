import os
import time

import requests
import tabulate
import typer
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
    """Wipe the index and crawl the website to rebuild the index."""
    indexer.wipe_index()
    global index_loaded
    index_loaded = False
    crawler.reset_crawler()
    print(
        "Building index. The number of pages to crawl will increase as more pages are found. This is shown in the "
        "progress bar."
    )
    crawler.crawl(website_url)
    indexer.save_index()


@app.command(name="load")
def load():
    """Load the index from the file."""
    indexer.load_index()
    global index_loaded
    index_loaded = True
    print("Index loaded.")


@app.command(name="print")
def print_index(search_word: str):
    """Print the index for a specific word."""
    search_word = indexer.parse_word(search_word)

    if search_word not in indexer.word_index:
        print(f"Word '{search_word}' not in index.")
        return
    index = {}
    for page_id, value in indexer.word_index[search_word].items():
        index[indexer.id_to_url[page_id]] = value

    output = {"Page": [], "Word Positions": []}
    for page_id, value in indexer.word_index[search_word].items():
        output["Page"].append(indexer.id_to_url[page_id])
        output["Word Positions"].append(value)

    print(f"Word '{search_word}' index:")
    print(tabulate.tabulate(output, headers="keys", showindex="always", tablefmt="simple_grid"))


@app.command(name="find")
def find(search_phrase: str):
    """Search the index for a specific phrase."""
    results = search_engine.search(search_phrase)

    output = {"Page": [], "Match Type (phrase, all_words, other)": [], "Score": [], "Matched Words": []}
    for i, page_id in enumerate(results):
        output["Page"].append(indexer.id_to_url[page_id])
        output["Match Type (phrase, all_words, other)"].append(results[page_id]["match_type"])
        # TODO: Remove the following line and the next line
        output["Score"].append(results[page_id]["score"])
        output["Matched Words"].append(len(results[page_id]["all_words"]))

    print(f"Top 10 results for '{search_phrase}':")
    print(tabulate.tabulate(output, headers="keys", showindex="always", tablefmt="simple_grid"))
    print("Search complete.")


def main():
    """Main function to run the CLI."""
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
            f"Index size: [underline]{len(indexer.id_to_url)}[/underline] pages)"
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
