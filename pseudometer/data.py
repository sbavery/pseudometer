# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_data.ipynb.

# %% auto 0
__all__ = ['Webpage', 'get_page_all', 'get_all_links']

# %% ../nbs/01_data.ipynb 4
import warnings
warnings.filterwarnings('ignore')
import requests
from bs4 import BeautifulSoup
import enchant
import re
import random
from collections import Counter
from fastai.text.all import *
import hashlib
import pickle

# %% ../nbs/01_data.ipynb 8
class Webpage:
    def __init__(self, url):
        self.url = url
        self.hash = self.get_hash_str()
        self.requested = False
        self.page_text = ""
        self.html = ""
        self.links = []
        self.text = []
        self.cleaned_text = []
        self.most_common_words = []
    
    def get_page(self, headers, min_size, max_size):
        r = requests.get(self.url, stream=True, headers=headers)
        content_length = int(r.headers.get('Content-Length', 0))
        data = []
        length = 0

        if content_length > max_size:
            return None

        for chunk in r.iter_content(1024):
            data.append(chunk)
            length += len(chunk)
            if length > max_size:
                return None
        r._content = b''.join(data)
        if len(r.text) < min_size: return None
        return r.text

    def get_page_html(self, min_size=1000, max_size=2000000):
        user_agents = [ 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
            'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
            'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
        ] 
        user_agent = random.choice(user_agents) 
        headers = {'User-Agent': user_agent} 
        self.page_text = self.get_page(headers, min_size, max_size)
        self.html = BeautifulSoup(self.page_text, "html.parser")
        self.requested = True

    def get_hash_str(self, inp=""):
        return hashlib.sha3_256((self.url+inp).encode()).hexdigest()

    def get_html_anchors(self, keyword="http"):
        for anchor in self.html.findAll('a'):
            link = anchor.get('href')
            if link == None or link == "":
                continue
            if keyword in link:
                self.links.append(link)
                
    def get_html_text(self, tags=["p"]):
        for tag in tags:
            for p in self.html.findAll(tag):
                p_text = p.getText().strip()
                if p_text == None or p_text == '':
                    continue
                self.text.append(p_text)

    def clean_html_text(self, max_words, enchant_dict="en_US", ignore=[], rx="[^a-zA-Z ]+", min_word_len=2):
        all_text = ' '.join(self.text).lower()
        regex_text = re.sub(rx,'',all_text).strip()
        split = regex_text.split()
        split = [word for word in split if word not in ignore]
        if enchant_dict != "": d = enchant.Dict(enchant_dict)
        for word in split:
            if len(self.cleaned_text) >= max_words: break
            if len(word) >= min_word_len:
                if enchant_dict == "":
                    self.cleaned_text.append(word)
                elif d.check(word): 
                    self.cleaned_text.append(word)

    def k_common_words(self, k=10, ignore=[]):
        if self.cleaned_text == "":
            text = self.text
        else:
            text = self.cleaned_text
        all_text = ' '.join(text).lower()
        split = all_text.split()
        split_ignore = [word for word in split if word not in ignore]
        counts = Counter(split_ignore)
        k_most_common = counts.most_common(k)
        self.most_common_words = k_most_common

    def save_text(self, path, fname):
        file = open(path+fname, 'wb')
        pickle.dump(self.text, file)
        file.close()

    def load_text(self, path, fname):
        file = open(path+fname, 'rb')
        self.text = pickle.load(file)
        file.close()

    def save_links(self, path, fname):
        file = open(path+fname, 'wb')
        pickle.dump(self.links, file)
        file.close()

    def load_links(self, path, fname):
        file = open(path+fname, 'rb')
        self.links = pickle.load(file)
        file.close()

# %% ../nbs/01_data.ipynb 14
def get_page_all(url, k, max_words, ignore_text, ignore_common, path = None):
    page = Webpage(url)
    fname_text = page.hash+'.text'
    fname_links = page.hash+'.links'
    if path == None:
        page.get_page_html()
        page.get_html_text(tags=["p","h1","h2","h3","span"])
        page.get_html_anchors()
    else:
        if os.path.isfile(path+fname_text): 
            page.load_text(path, fname_text)
        else:
            page.get_page_html()
            page.get_html_text(tags=["p","h1","h2","h3","span"])
            page.save_text(path, fname_text)

        if os.path.isfile(path+fname_links): 
            page.load_links(path, fname_links)
        else:
            if page.html == "": page.get_page_html()
            page.get_html_anchors()
            page.save_links(path, fname_links)

    if page.text is not None:
        page.clean_html_text(max_words, ignore=ignore_text, rx="[^a-zA-Z ]+")
        page.k_common_words(k=k, ignore=ignore_common)
    return page

def get_all_links(url, dict, k, min_words=20, max_words=500, ignore_text=[], ignore_common=[], ignore_filenames=[".mp3",".jpg",".png"], max_links="", path=None):
    primary_page = get_page_all(url, k, max_words, ignore_text, ignore_common, path)
    if primary_page.cleaned_text is not []:
        dict[url] = [primary_page.cleaned_text, primary_page.most_common_words]
        if max_links == "" or max_links > len(primary_page.links): max_links=len(primary_page.links)
        
        for count, link in enumerate(primary_page.links[:max_links]):
            if all(x not in link for x in ignore_filenames):
                try:
                    page = get_page_all(link, k, max_words, ignore_text, ignore_common, path)
                    if page.cleaned_text is not []:
                        if len(page.cleaned_text) < min_words: continue
                        if [page.cleaned_text, page.most_common_words] in dict.values(): continue
                        dict[link] = [page.cleaned_text, page.most_common_words]
                except:
                    pass
            if link in dict:
                res = str(len(dict[link][0]))+" words | "+str(dict[link][1][:3])
            else:
                res = "Rejected"
            progress_message = "%s link %4d/%4d | %s = %s %s" % (url, count, len(primary_page.links), link, res, 200*' ')
            sys.stdout.write("\r" + progress_message)
            sys.stdout.flush()
    else:
        print(url,"returned None, Skipping...")
