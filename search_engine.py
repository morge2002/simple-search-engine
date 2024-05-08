from indexer import Indexer


class SearchEngine:
    """
    A class to perform search queries on an inverted index stored and created by the Indexer object. Search queries
    are ranked by their each word's frequency in a page multiplied by the tf-idf score of the word in the query.
    """

    def __init__(self, indexer_object: Indexer):
        self.indexer = indexer_object

    def search(self, query: str):
        """
        Perform a search query on the index.
        :param query: Query string
        """
        query_words = query.split()
        ranks = {}
        # Go through each word, find the rank for each page and sum them
        for word in set(query_words):
            word = self.indexer.parse_word(word)

            if word not in self.indexer.word_index:
                continue
            # Calculate rank for each page for the word
            for page_id in self.indexer.word_index[word].keys():
                if page_id not in ranks:
                    ranks[page_id] = {"score": 0, "all_words": set(), "phrase_positions": []}

                ranks[page_id]["score"] += self.calculate_rank(page_id, word)
                ranks[page_id]["all_words"].add(word)

                if len(query_words) > 1:
                    ranks[page_id]["phrase_positions"].extend(self.indexer.word_index[word][page_id])

        if not ranks:
            print("No results found.")
            return ranks

        # Filter pages that contain all words
        all_words_pages = {
            page_id: {**rank, "match_type": "all_words"}
            for page_id, rank in ranks.items()
            if len(rank["all_words"]) == len(query_words)
        }
        other_pages = {
            page_id: {**rank, "match_type": "other"}
            for page_id, rank in ranks.items()
            if len(rank["all_words"]) < len(query_words)
        }

        # Sort pages by score
        all_words_pages: dict = dict(
            sorted(all_words_pages.items(), key=lambda rank_tuple: rank_tuple[1]["score"], reverse=True)
        )
        # Sort other pages by number of words and then by score
        other_pages = dict(
            sorted(
                other_pages.items(),
                key=lambda rank_tuple: (len(rank_tuple[1]["all_words"]), rank_tuple[1]["score"]),
                reverse=True,
            )
        )

        # Check if words appear next to each other
        phrase_pages = {}
        for page_id, rank in all_words_pages.copy().items():
            positions = rank["phrase_positions"]
            positions.sort()
            for i in range(len(positions) - len(query_words) + 1):
                if positions[i : i + len(query_words)] == list(range(positions[i], positions[i] + len(query_words))):
                    # rank['score'] *= 2  # Increase score if words appear next to each other
                    phrase_pages.update({page_id: {**all_words_pages.pop(page_id), "match_type": "phrase"}})
                    break
        # Sort phrase pages by score
        phrase_pages = dict(sorted(phrase_pages.items(), key=lambda rank_tuple: rank_tuple[1]["score"], reverse=True))
        results = dict(phrase_pages, **all_words_pages, **other_pages)
        return results

    def calculate_rank(self, page_id, word):
        """Rank is calculated by the frequency of the word in the page."""
        if page_id not in self.indexer.word_index[word]:
            return 0

        return len(self.indexer.word_index[word][page_id])


if __name__ == "__main__":
    # Crawling |################################| 214 / 214 , 0:22:52
    indexer = Indexer()
    indexer.load_index()
    engine = SearchEngine(indexer)
    print(engine.search("steve martin"))
    print(engine.search("albert einstein"))
    print(engine.search("i am looking for albert einstein"))
