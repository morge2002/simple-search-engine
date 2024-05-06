import math

import numpy as np

from indexer import Indexer


class SearchEngine:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer
        self.ranking_index = {}
        self.page_vector_length = len(self.indexer.word_index.keys())
        self.page_vector_word_order = list(self.indexer.word_index.keys()).sort()

    def search(self, query):
        query_words = query.split()
        search_results = []
        ranks = {}
        query_vector = self.build_query_vector(query_words)
        for page_id, page_vector in self.ranking_index.items():
            rank = self.calculate_similarity(page_vector, query_vector)
            if rank > 0:
                ranks[page_id] = rank

        ranks = sorted(ranks.items(), key=lambda rank_tuple: rank_tuple[1], reverse=True)
        if not ranks:
            print("No results found.")
            return ranks

        print("Ranked Pages:")
        for i, rank in enumerate(ranks):
            print(f"{i + 1} (Freq: {rank[1]}): {self.indexer.id_to_url[rank[0]]}")
        return ranks

    def calculate_rank(self, page_id, word):
        if word not in self.indexer.page_index[page_id]:
            return 0
        # tf = self.indexer.word_index[word][page_id] / sum(self.indexer.page_index[page_id].values())
        # idf = math.log(len(self.indexer.url_to_id.keys()) / len(self.indexer.word_index[word].keys()))
        # tf_idf = tf * idf
        # return tf_idf
        return self.indexer.word_index[word][page_id]

    @staticmethod
    def calculate_similarity(page_vector, query_vector):
        dot_product = np.dot(query_vector, page_vector)
        query_norm = np.linalg.norm(query_vector)
        page_norm = np.linalg.norm(page_vector)
        if query_norm == 0 or page_norm == 0:
            return 0  # Handle zero norm case to avoid division by zero
        return dot_product / (query_norm * page_norm)

    def build_ranking_index(self):
        page_vector_length = len(self.indexer.word_index.keys())
        self.page_vector_length = page_vector_length
        words = list(self.indexer.word_index.keys())
        words.sort()
        self.page_vector_word_order = words
        initial_page_vector = [0] * page_vector_length
        # Precompute idf
        idfs = []
        number_of_pages = len(self.indexer.url_to_id.keys())
        for word in words:
            idfs.append(math.log((number_of_pages + 1) / (len(self.indexer.word_index[word].keys()) + 1)))

        for page_id in self.indexer.page_index.keys():
            page_vector = initial_page_vector.copy()
            for word in self.indexer.page_index[page_id].keys():
                vector_index = words.index(word)
                tf = self.indexer.word_index[word][page_id] / sum(self.indexer.page_index[page_id].values())
                idf = idfs[vector_index]
                tf_idf = tf * idf
                page_vector[vector_index] = tf_idf

            self.ranking_index[page_id] = page_vector

    def build_query_vector(self, query_words):
        query_vector = [0] * self.page_vector_length

        for word in query_words:
            if word not in self.page_vector_word_order:
                continue
            tf = query_words.count(word) / len(query_words)
            idf = math.log(len(self.indexer.url_to_id.keys()) / len(self.indexer.word_index[word].keys()))
            tf_idf = tf * idf
            vector_index = self.page_vector_word_order.index(word)
            query_vector[vector_index] = tf_idf
        return query_vector


if __name__ == "__main__":
    # Crawling |################################| 214 / 214 , 0:22:52
    indexer = Indexer()
    indexer.load_index()
    engine = SearchEngine(indexer)
    engine.build_ranking_index()
    print(engine.search("steve martin"))
    print(engine.search("albert einstein"))
    print(engine.search("I am looking for a page that is about albert einstein"))
