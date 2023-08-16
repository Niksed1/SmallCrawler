# This is a sample Python script.
from crawl import Crawler
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def console_interface(index):
    inp = ''
    while True:
        inp = input("Enter the word to search for resources: (-1 to exit) ")
        if inp == '-1':
            break
        elif inp.lower() not in index.keys():
            print("Sorry! word does not exist!\n")
        else:
            for elem in index[inp.lower()]:
                print(elem)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    crawler = Crawler()
    inverted_index = crawler.read_page()
    console_interface(inverted_index)




# See PyCharm help at https://www.jetbrains.com/help/pycharm/