import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen
from collections import defaultdict

from nltk.corpus import stopwords
'''strategies to improve: lemmatization, assign weights to the text with more value (headers, bold etc),
recursion to crawl more pages and collect more information, store inverted index in a database '''

STOP_LIST = set(stopwords.words('english')) #common english stop words


class Crawler:

    def __init__(self):
        self._url_seeds = ["https://www.admissions.uci.edu/", "https://catalogue.uci.edu/undergraduatedegrees/", "https://www.ofas.uci.edu/", "https://housing.uci.edu/", "https://food.uci.edu/"]
        self._index = defaultdict(list) #inverted index of word -> url

    def read_page(self):
        '''requests an html, and uses Beautiful Soup to parse it
        and create a list of extracted texts from the pages.'''


        try:
            for url in self._url_seeds:
                text_list = []  # holds -> [url, soup]

                response = urlopen(url)  # response is the html of the page
                new_soup = BeautifulSoup(response, features="html.parser")
                # print(soup.get_text())
                text_list.append([url, new_soup])

                for elem in text_list:
                    token_list = self.tokenize(elem[1].get_text())
                    #print(len(token_list))
                    # print(token_list)

                    word_dict = self.computeWordFrequencies(token_list)
                    self.add_data(elem[0], word_dict)

        except Exception as e:
            print("EXCEPTION in read_page:\t", e)


        #print(self._index)
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

    def is_valid(self):
        '''function to determine if the url should be fetched.
        Avoiding calendars, links without information, and traps. For future development'''
        pass
