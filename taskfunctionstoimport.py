### Libraries & Setup

import requests
from bs4 import BeautifulSoup   

import pandas as pd
import numpy as np  
from datetime import datetime  
from collections import defaultdict   
import csv   
import re   
import matplotlib.pyplot as plt  
import os  

import warnings
warnings.filterwarnings('ignore')

#1.1

def collect_urls(filename):

    '''
    Retrieve all URLs of the "Most popular places" places listed in the first $400$ pages and store them in the filename.txt file
    '''

    with open(filename, 'w') as f:
        for i in range(400):
            url = "https://www.atlasobscura.com/places?page={}&sort=likes_count".format(i+1)
            list_page = requests.get(url)
            list_soup = BeautifulSoup(list_page.text, features="lxml")
            list_places = ["https://www.atlasobscura.com" + x.get("href") for x in list_soup.find_all("a", {"class": "content-card-place"})]
            for line in list_places:
                f.write(f"{line}\n")

#1.2

def collect_html_pages(url_pair):

    '''
    Retrieve HTML content from the input URL and store it into a .html file, saved in the proper folder
    (according to the page in which the URL was listed)
    INPUT: (URL, URL index)
    '''
    import requests
    from bs4 import BeautifulSoup
    import os

    url, index = url_pair
    result = requests.get(url)
    list_soup = BeautifulSoup(result.text, features="lxml")

    doc_id = index + 1
    page_id = index//18 + 1

    dirName = "HTML_Pages\Page{}".format(page_id)

    if not os.path.exists(dirName): os.makedirs(dirName)

    with open(dirName+"\Doc{}.html".format(doc_id), 'w', encoding='utf-8') as f:
        f.write(str(list_soup))

#1.3
def parse_page(index, urls_list):

    '''
    Extract desired information from the target HTML page and store them into a .tsv file
    '''

    with open("HTML_Pages\Page{}\Doc{}.html".format(index//18 + 1, index + 1), "r", encoding='utf-8') as f:

        text = f.read()
        soup = BeautifulSoup(text, features="lxml")

        placeName = soup.find_all("h1", {"class": "DDPage__header-title"})[0].contents[0].strip()

        placeTags = [x.contents[0].strip() for x in soup.find_all("a", {"class": "js-item-tags-link"})]

        numPeopleVisited = soup.find_all("div", {"class": "item-action-count"})[0].contents[0]

        numPeopleWant = soup.find_all("div", {"class": "item-action-count"})[1].contents[0]

        placeDesc = [" ".join(x.text.strip().replace("\xa0","").split()) for x in soup.find_all("div", {"id": "place-body"})].pop()

        placeShortDesc = " ".join(soup.find_all("h3", {"class": "DDPage__header-dek"})[0].contents[0].strip().replace("\xa0","").split())

        placeNearby = list(set([x.contents[0].strip() for x in soup.find_all("div", {"class": "DDPageSiderailRecirc__item-title"})]))

        placeAddress = " ".join(str(soup.find_all("address", {"class": "DDPageSiderail__address"})[0]).split("<div>")[1].strip().replace("<br/>"," - ").split())

        placeAlt = float(soup.find("div", {"class": "DDPageSiderail__coordinates"})["data-coordinates"].split(",")[0].strip())

        placeLong = float(soup.find("div", {"class": "DDPageSiderail__coordinates"})["data-coordinates"].split(",")[1].strip())

        try:
            placeEditors = list(set([soup.find("a", {"class": "DDPContributorsList__contributor"}).contents[0].strip()] + [x.contents[0].strip() for x in [x.find("span") for x in soup.find_all("a", {"class": "DDPContributorsList__contributor"}) if x.find("span") is not None]]))
        except:
            placeEditors = []

        try:
            placePubDate = datetime.strptime(str(soup.find_all("div", {"class": "DDPContributor__name"})[0].contents[0]), "%B %d, %Y")
        except:
            placePubDate = []

        try:
            placeRelatedLists = [x.contents[0].strip() for x in [x.find("span") for x in soup.find_all("a", {"class": "Card --content-card-v2 --content-card-item Card--list"}) if x.find("span") is not None]]
        except:
            placeRelatedLists = []

        try:
            placeRelatedPlaces = [x.contents[0].strip() for x in (x.find_all("span") for x in soup.find_all("div", {"class": "full-width-container CardRecircSection"}) if str(x.find("div", {"class": "CardRecircSection__title"}).contents[0])=="Related Places").__next__()]
        except:
            placeRelatedPlaces = []

        placeURL = urls_list[index]

        data = [placeName, placeTags, numPeopleVisited, numPeopleWant, placeDesc, placeShortDesc, placeNearby, placeAddress, placeAlt, placeLong, placeEditors, placePubDate, placeRelatedLists, placeRelatedPlaces, placeURL]

        for i in range(len(data)):
            if isinstance(data[i], list) and len(data[i])==0: data[i]=""

        with open("TSV_Files\place_{}.tsv".format(index+1), 'w', encoding='utf-8') as f:
            tsv_writer = csv.writer(f, delimiter="\t", quotechar=None)
            tsv_writer.writerow(data)

#2

def check_empty(a):
    if len(a) == 0:
        return False
    else:
        return True

def pre_process(path, stemmer):

    '''
    Document "placeDesc" field preprocessing
    '''

    Description = defaultdict(str)
    curr_path = os.getcwd()
    os.chdir(path)
    files = os.listdir()
    for file_name in files:
        f = open(file_name, 'r', encoding='utf-8')
        a = f.read()
        a = re.split(r'\t+', a)
        a_sub = a[4]
        a_sub = re.split('\?|\.|; |, |\*|\n|! |\t| |\(|\)|- ', a_sub)
        a_sub = list(filter(check_empty, a_sub))
        for i in range(len(a_sub)):
            a_sub[i] = stemmer.stem(a_sub[i]).lower()
        Description[file_name] = ' '.join(a_sub)
        f.close()

    os.chdir(curr_path)
    return Description

#2.1

def build_inv_idx(collection, vocabulary):

    '''
    Build inverted index
    '''

    inv_idx = defaultdict(set)

    for i in collection:
        descr_list = set(collection[i].split())
        for word in descr_list:
            term_i = vocabulary[word]
            inv_idx[term_i].add(i)

    return inv_idx


def searchText(path, query, inverted_index, vocabulary):

    '''
    Execute input query and output result
    '''

    curr_path = os.getcwd()
    os.chdir(path)
    docs = inverted_index[vocabulary[query[0]]]
    for word in query:
        docs = docs.intersection(inverted_index[vocabulary[word]])
    result = pd.DataFrame(columns = ['Title', 'Description', 'URL'])
    for i in docs:
        f = open(i , "r", encoding="utf8")
        a = f.read()
        a = re.split(r'\t', a)
        result = result.append({'Title': a[0].strip(),'Description': a[4].strip(), 'URL': a[14].strip() }, ignore_index=True)
        f.close()
    os.chdir(curr_path)
    return result, docs

def build_inv_idx2(important_words, vocabulary, inverted_index, files, result, names):

    '''
    Build inverted index with tfidf
    '''

    inverted_index2 = defaultdict(set)
    for i in important_words:
        term_id = vocabulary[i]
        score_list = [x[0] for x in np.array(result[:, names.index(i)])]
        for doc in inverted_index[term_id]:
            index = files.index(doc)
            score = score_list[index]
            inverted_index2[term_id].add((doc, score))

