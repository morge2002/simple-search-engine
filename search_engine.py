import math

from indexer import Indexer


class SearchEngine:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def search(self, query):
        query_words = query.split()
        search_results = []
        ranks = {}
        for word in query_words:
            word = self.indexer.parse_word(word)
            if word in self.indexer.word_index:
                for page_id in self.indexer.word_index[word].keys():
                    if page_id not in ranks:
                        ranks[page_id] = 0
                    ranks[page_id] += self.calculate_rank(page_id, word)
        # Rank search results based on relevance
        # ranks = {}
        # for page_id in search_results:
        #     rank = 0
        #     for word in query_words:
        #         word = self.indexer.parse_word(word)
        #         rank += self.calculate_tf_idf(page_id, word)
        #     ranks[page_id] = rank
        ranks = sorted(ranks.items(), key=lambda rank_tuple: rank_tuple[1], reverse=True)
        if not ranks:
            print("No results found.")
            return ranks

        print("Ranked Pages:")
        for i, rank in enumerate(ranks):
            print(f"{i+1} (Freq: {rank[1]}): {self.indexer.id_to_url[rank[0]]}")
        return ranks

    def calculate_rank(self, page_id, word):
        if word not in self.indexer.page_index[page_id]:
            return 0
        # tf = self.indexer.word_index[word][page_id] / sum(self.indexer.page_index[page_id].values())
        # idf = math.log(len(self.indexer.url_to_id.keys()) / len(self.indexer.word_index[word].keys()))
        # tf_idf = tf * idf
        # return tf_idf
        return self.indexer.word_index[word][page_id]


if __name__ == "__main__":
    # Crawling |################################| 214 / 214 , 0:22:52
    engine = SearchEngine(Indexer())
    print(engine.search("steve martin"))
