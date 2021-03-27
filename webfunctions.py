import os
import random

from bs4 import BeautifulSoup
import urllib.request
import re

#Get all the links from a page that contain a specific substring.
def getLinks(url, searchString):
    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page, 'html.parser')
    #print (soup.prettify())

    links = []
    for link in soup.findAll('a',  href=re.compile(searchString, re.IGNORECASE)):
        links.append(link.get('href'))

    return links