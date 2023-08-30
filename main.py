# This is a sample Python script.
from crawl import Crawler
import json
import os
import MySQLdb # import the MySQLdb module
from dotenv import load_dotenv
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
def save_to_file(index):
    print("Started writing dictionary to a file")

    with open("C:/Users/image/Documents/index.txt", "w") as fp:
        json.dump(index, fp, indent=4)  # encode dict into JSON

    print("Done writing dict into index.txt file")

def store_in_database(index):
    load_dotenv()
    print(os.getenv("DB_HOST"))
    # Create the connection object
    connection = MySQLdb.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        passwd=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        ssl_mode="VERIFY_IDENTITY",
        ssl={
            'ca': os.getenv("SSL_CERT")
        }
    )
    insert_query = """INSERT INTO Links (keyword, link, occurrences) VALUES (%s, %s, %s) """
    # Create cursor and use it to execute SQL command
    cursor = connection.cursor()

    link_data = [] #needs to be a list of tuples (keyword, link, occurences)

    for keyword, values in index.items():
        for url, occurence in values:
            link_data.append((keyword, url, occurence))

    cursor.executemany(insert_query, link_data)
    #version = cursor.fetchone()
    #print(version)
    connection.commit()
    print("done")

    cursor.close()
    connection.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    crawler = Crawler()
    inverted_index = crawler.read_page()
    #console_interface(inverted_index)
    save_to_file(inverted_index)
    store_in_database(inverted_index)

