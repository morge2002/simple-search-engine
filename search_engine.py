import math

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
        for word in query_words:
            word = self.indexer.parse_word(word)

            if word not in self.indexer.word_index:
                continue
            # Calculate rank for each page for the word
            for page_id in self.indexer.word_index[word].keys():
                if page_id not in ranks:
                    ranks[page_id] = 0

                ranks[page_id] += self.calculate_rank(page_id, word, query_words)

        if not ranks:
            print("No results found.")
            return ranks

        ranks = sorted(ranks.items(), key=lambda rank_tuple: rank_tuple[1], reverse=True)
        return ranks

    def calculate_rank(self, page_id, word, query_words):
        """Rank is calculated by the frequency of the word in the page by its tf-idf."""
        if word not in self.indexer.page_index[page_id]:
            return 0

        tf_idf = self.query_word_tf_idf(word, query_words)
        return self.indexer.word_index[word][page_id] * tf_idf

    def query_word_tf_idf(self, word, query_words):
        """Calculate the tf-idf score of a word in a query."""
        tf = query_words.count(word) / len(query_words)
        idf = math.log(len(self.indexer.url_to_id.keys()) / len(self.indexer.word_index[word].keys()))
        return tf * idf


if __name__ == "__main__":
    # Crawling |################################| 214 / 214 , 0:22:52
    indexer = Indexer()
    indexer.load_index()
    engine = SearchEngine(indexer)
    print(engine.search("steve martin"))
    print(engine.search("albert einstein"))
    print(engine.search("i am looking for albert einstein"))
