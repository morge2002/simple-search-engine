import json
import os
import string


class Indexer:
    def __init__(self, index_file_path='index.json'):
        # Index of word frequencies to URLs
        self.word_index = {}
        self.page_index = {}
        self.url_to_id = {}
        self.id_to_url = {}
        self.translation_table = str.maketrans('', '', string.punctuation + '“”')
        self.index_file_path = index_file_path
        self.current_page_id = 0

    def index_page(self, url, text):
        if url in self.url_to_id:
            page_id = self.url_to_id[url]
        else:
            page_id = self.get_new_page_id()
            self.url_to_id[url] = page_id
            self.id_to_url[page_id] = url
        # Define a translation table to remove punctuation
        # Index the text content of a page
        words = text.split()
        for word in words:
            word = self.parse_word(word)
            self.add_word(word, page_id)
        # self.save_index()

    def parse_word(self, word):
        return word.translate(self.translation_table).lower()

    def add_word(self, word, page_id):
        if page_id not in self.page_index:
            self.page_index[page_id] = {}
        if word not in self.word_index:
            self.word_index[word] = {}

        if word not in self.page_index[page_id]:
            self.page_index[page_id][word] = 0
        if page_id not in self.word_index[word]:
            self.word_index[word][page_id] = 0

        self.page_index[page_id][word] += 1
        self.word_index[word][page_id] += 1

    def get_new_page_id(self):
        page_id = self.current_page_id
        self.current_page_id += 1
        return page_id

    def load_index(self):
        # Load the index from a file if it exists
        if not os.path.exists(self.index_file_path):
            print("No index file found")
            return

        with open(self.index_file_path, 'r') as f:
            index = json.load(f)
            try:
                self.word_index = index['word_index']
                self.page_index = index['page_index']
                self.url_to_id = index['url_to_id']
                self.id_to_url = index['id_to_url']
            except KeyError:
                print("Couldn't load index file correctly: Index reset.")
                self.word_index = {}
                self.page_index = {}
                self.url_to_id = {}
                self.id_to_url = {}

    def save_index(self):
        with open(self.index_file_path, 'w') as f:
            index = {
                'word_index': self.word_index,
                'page_index': self.page_index,
                'url_to_id': self.url_to_id,
                'id_to_url': self.id_to_url
            }
            json.dump(index, f)

    def wipe_index(self):
        self.word_index = {}
        self.page_index = {}
        self.url_to_id = {}
        self.id_to_url = {}
        self.current_page_id = 0
        if not os.path.exists(self.index_file_path):
            print("Index file does not exist")
            return

        os.remove(self.index_file_path)
