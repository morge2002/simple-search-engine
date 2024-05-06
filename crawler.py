import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar

from indexer import Indexer


class Crawler:
    webpages = set()
    requested_urls = []

    def __init__(self, website_url, politeness_window=6, indexer=None):
        if indexer is None:
            indexer = Indexer()
        self.website_url = website_url
        self.politeness_window = politeness_window
        self.indexer = indexer
        self.last_request_time = 0
        self.max_pages = float('inf')
        # self.max_pages = 4
        self.fetched_pages = 0

    def fetch_page_content(self, url) -> bytes | None:
        # Ensure politeness window is observed
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.politeness_window:
            time.sleep(self.politeness_window - time_since_last_request)
        if not url.startswith("http"):
            url = urljoin(self.website_url, url)
        response = requests.get(url)
        self.requested_urls.append(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            return
        self.fetched_pages += 1
        self.last_request_time = time.time()
        # Add the url to the set of webpages
        self.webpages.add(url)
        return response.content

    def __crawl(self, url, bar):
        bar.update()
        if self.fetched_pages >= self.max_pages:
            print(f"Reached maximum number of pages: {self.max_pages}")
            bar.update()
            return
        # print(f"{url}: Crawling...")
        page_content = self.fetch_page_content(url)
        if not page_content:
            #             print(f"{url}: No content found or skipped")
            bar.update()
            return
        # Crawl the web page
        soup = BeautifulSoup(page_content, 'html.parser')
        # Extract text content from HTML
        text = self.extract_texts(soup)
        if not text:
            #             print(f"{url}: No text content found or skipped")
            bar.update()
            return
        # Index the text content
        self.indexer.index_page(url, text)
        # print(f"{url}: Indexed")
        # Extract links from HTML
        links: list = self.get_page_links(soup)
        links: list = self.filter_and_format_links(links)

        self.webpages.update(links)
        # print(f"{url}: Found {len(links)} unseen links")
        if len(links):
            #             print(f"{url}: Crawling {len(links)} links...")
            bar.max = len(self.webpages)

        bar.next()

        # Crawl each link
        for link in links:
            bar.update()
            self.__crawl(link, bar)

    #         print(f"{url}: Finished crawling.")

    def crawl(self, website_url=None):
        if website_url is None:
            website_url = self.website_url
        with Bar('Crawling', suffix='%(index)d / %(max)d , %(elapsed_td)s', max=10) as bar:
            crawler.__crawl(website_url, bar)

    @staticmethod
    def get_page_links(soup) -> list:
        # Extract links from HTML
        links = [link.get('href') for link in soup.find_all('a')]
        return links

    def filter_and_format_links(self, links) -> list:
        filtered_links = []
        links = set(links)
        for link in links:
            # Skip links that are not from the same website
            if link.startswith("http") and not link.startswith(self.website_url):
                continue
            # Add the website URL to relative links
            if link.startswith("/"):
                link = urljoin(self.website_url, link)
            # Skip links that have already been crawled or are going to be crawled
            if link in self.webpages:
                continue
            filtered_links.append(link)
        return filtered_links

    @staticmethod
    def extract_texts(soup):
        # Extract text content from HTML
        text = soup.get_text()
        return text

    def reset_crawler(self):
        self.webpages = set()
        self.requested_urls = []
        self.fetched_pages = 0
        self.last_request_time = 0


if __name__ == "__main__":
    crawler = Crawler("https://quotes.toscrape.com/")
    crawler.crawl("https://quotes.toscrape.com/")
    crawler.indexer.save_index()
    # bar.finish()
    print(crawler.webpages)
    print(crawler.requested_urls)
    print(crawler.indexer.word_index)
