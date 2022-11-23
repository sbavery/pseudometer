# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_data.ipynb.

# %% auto 0
__all__ = ['Webpage']

# %% ../nbs/01_data.ipynb 2
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter

# %% ../nbs/01_data.ipynb 4
class Webpage:
    def __init__(self, url):
        self.url = url
        self.html = ""
        self.links = []
        self.text = []

    def get_html(self):
        page = requests.get(self.url)
        self.html = BeautifulSoup(page.content, "html.parser")

    def get_html_anchors(self, keyword="http"):
        for anchor in self.html.findAll('a'):
            link = anchor.get('href')
            if link == None or link == "":
                continue
            if keyword in link:
                self.links.append(link)
                
    def get_html_text(self, tag="p"):
        rx = "[^a-zA-Z0-9 ]+"
        for p in self.html.findAll(tag):
            p_text = p.getText().strip()
            p_text = re.sub(rx,'',p_text).strip()
            if p_text == None or p_text == '':
                continue
            self.text.append(p_text)

    def most_common_words(self, k=10, ignore=["the","to","of","and","a","in","on","is","for","by"]):
        all_text = ' '.join(self.text).lower()
        split = all_text.split()
        split_ignore = [word for word in split if word not in ignore]
        counts = Counter(split_ignore)
        k_most_common = counts.most_common(k)
        return k_most_common


