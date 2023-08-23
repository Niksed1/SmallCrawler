import re
import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from collections import defaultdict

from nltk.corpus import stopwords
'''strategies to improve: lemmatization, assign weights to the text with more value (headers, bold etc),
recursion to crawl more pages and collect more information, store inverted index in a database '''

#depth-limited search
STOP_LIST = set(stopwords.words('english')) #common english stop words


class Crawler:

    def __init__(self):
        self._url_seeds = ["https://www.admissions.uci.edu/", "https://catalogue.uci.edu/undergraduatedegrees/", "https://www.ofas.uci.edu/", "https://housing.uci.edu/", "https://food.uci.edu/"]
        self._index = defaultdict(list) #inverted index of word -> url
        self._links_queue = []

    def depth_limited_crawl(self, base, soup, depth):
        '''crawling webpages up to the depth of 3
        Absolute links - links to a page on a separate website (starts with http(s))
        Relative links - links to a section under the domain name, represented as partial urls (starts with /)
        Inline links - links that lead to a section within the same page (starts with #)
        only crawling relative links '''


        if depth == 0:
            return
        else:
            #links = soup.find_all('a')
            #absolute links -> links = [item['href'] for item in soup.select('[href^=http]')]
            links = soup.find_all('a', href=lambda href: href and not href.startswith(('http', 'https', '#')) and '/' in href)
            #print(links)
            for link in links:
                try:
                    text_list = [] # holds -> [url, soup]
                    url = urljoin(base, link['href'])

                    if not self.is_valid_url(url): #checks url validity
                        break

                    self._links_queue.append(url)
                    print(f' FETCHED {url} QUEUE SIZE {len(self._links_queue)}')
                    response = urlopen(url)
                    new_soup = BeautifulSoup(response, features="lxml")
                    text_list.append([url, new_soup])

                    for elem in text_list:
                        soup = elem[1]
                        token_list = self.tokenize(soup.get_text())
                        word_dict = self.computeWordFrequencies(token_list)
                        self.add_data(elem[0], word_dict)

                    self.depth_limited_crawl(base, new_soup, depth-1)
                except:
                    print('wrong url format')

    def is_valid_url(self, url):
        """
                Returns True or False based on whether the url has to be fetched or not. This is a great place to
                filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
                in this method
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            return not len(str(url)) > 150 \
                and not parsed.fragment \
                and not re.match(".*(share|date|month|year|xml|=).*$", parsed.query.lower()) \
                and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|svg|png|tiff?|mid|mp2|mp3|mp4"
                                 + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                                 + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                                 + "|thmx|mso|arff|rtf|jar|csv"
                                 + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower()) \
                and not re.match("^.*\/.?[0-9].*\/$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False

    def read_page(self):
        '''requests an html, and uses Beautiful Soup to parse it
        and create a list of extracted texts from the pages.'''

        try:
            for url in self._url_seeds:
                response = urlopen(url)  # response is the html of the page
                new_soup = BeautifulSoup(response, features="lxml")
                #print(new_soup.get_text())
                self.depth_limited_crawl(url, new_soup, 1)

        except Exception as e:
            print("EXCEPTION in read_page:\t", e)


        print(self._links_queue)
        return self._index


    def add_data(self, url, data):
        '''function to add data to the inverted index
        values are sorted by the frequency they appeared on a page'''
        for key, val in data.items():
            if not self._index[key]:
                self._index[key].append((url, val))
            else:
                i = 0
                for elem in self._index[key]:
                    if i == len(self._index[key]):
                        self._index[key].append((url, val))
                    if val > elem[1]:
                        self._index[key].insert(i, (url, val))
                        break
                    else:
                        i+=1




    def tokenize(self, text):
        '''tokenizes the extracted text into the list of unique tokens
        returns a list of tokens'''

        token_list = []
        current_string = ""
        # with open(text, 'r') as file:
        # for line in file:
        for char in text.rstrip("\n"):
            if ord(char) <= 122 and ord(char) >= 65:
                current_string += char.lower()
            else:
                if (current_string != "" and
                        len(current_string) > 1 and
                        current_string not in STOP_LIST):
                    token_list.append(current_string)
                current_string = ""

        return token_list

    def computeWordFrequencies(self, tokenList):
        '''computing word frequences to determine the most number of words used on a certain website'''
        words_dict = defaultdict(int)
        for word in tokenList:
            words_dict[word] += 1
        return words_dict
