#!/usr/bin/python
# coding: utf-8
import re
import urllib2
import urllib
import string
import random
import openpyxl
import pandas as pd
import datetime
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup
from selenium import webdriver
import HTMLParser
import config

def read_remote_page(url):
    #driver = webdriver.PhantomJS()
    driver = webdriver.Firefox()
   # driver.set_window_size(1024, 768)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return str(html)

xls_file = pd.ExcelFile(linksfile)

client = MongoClient()
db = client.get_database(origindb)
pricesdb = client.get_database('pricesmay')
collection = db.data
pricelist = pricesdb.data

def read_remote_page_ol_old(url):
    response = urllib2.urlopen(url)

    html = response.read()
    return html

def getuid(url):
    uid = ''
    g = re.match(r'bbn\=(\d+)', url)
    if g:
        uid = group(1)
    else:
        g = re.match(r'n\:\!(\d+)', url)
        if g:
            print g.group(0)
    return uid

def get_prices(url, html):
    parsed_html = BeautifulSoup(html)
    items = parsed_html.findAll('div', attrs={'class':'s-item-container'})
    result = []
    page = {}
    
    for item in items:
        #title = item.find('h2', attrs={'class':'a-size-base a-color-null s-inline s-access-title a-text-normal'})
  	title = item.find('a', attrs={'class':'a-link-normal s-access-detail-page  a-text-normal'})
        price = item.find('span', attrs={'class': 'a-size-base a-color-price s-price a-text-bold'})
	try:
            asin = item.find('input', {'name': 'asin'}).get('value')
	except:
	    asin = 'none'
    
	try:
	    if price:
		print "%s %s" % (price.text, title.text)
                page = {}
                line = "%s\t%s\t%s\t%s\t%s\t%s\n" % (country, seller, asin, title.text, price.text, currency)
                page['country'] = country
                page['seller'] = seller
                page['asin'] = asin
                page['title'] = title.text
                page['price'] = price.text
                page['currency'] = currency
                page['date'] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
                page['url'] = url
                result.append(page)
	except:
	    print "No price!"
        
    return result
    
def get_all_pages(url, html):
    query= ''
    pages = []

    pattern = re.compile(r'<span\s+class\=\"pagnDisabled\">(\d+)<\/span>', re.IGNORECASE)
    matchlast = pattern.findall(html)
    if matchlast:
        for page in range(2,int(matchlast[0])):
            thisurl = url + "&page=" + str(page)
            pages.append(thisurl)

    return pages 

def get_pages(root, html):
    query= ''
    pages = []
    pattern = re.compile(r'<span\s+class\=\"pagnLink\"><a\s+href\=\"(.+?)\"\s*>', re.IGNORECASE)
    match = pattern.findall(html)
    h = HTMLParser.HTMLParser()
    for q in match:
        thisurl = root + q
	normalurl = h.unescape(urllib2.unquote(thisurl.encode("utf8")))
	print normalurl
        pages.append(normalurl)
    return pages

df = xls_file.parse(0)
links = df['link']
df


# In[2]:
url = root + "/s/ref=sr_nr_p_n_feature_four_bro_0/477-8516616-3437758?fst=as:off&rh=n:2127215051,n:!2127216051,n:2134670051,n:2134671051,p_n_feature_four_browse-bin:2140438051&bbn=2134671051&ie=UTF8&qid=1453902974&rnid=2140437051"
print url
html = read_remote_page(url)
p = get_prices(url, html)
for item in p:
    result = pricelist.insert_one(item)
pages = get_all_pages(url, html)
# In[3]:

active = 1
import time
visited = {}
newpages = []
for url in links:        
    try:
        print 'URL: ' + str(url)
        html = read_remote_page(url)
        pages = get_all_pages(url, html)
	if not pages:
	    pages = get_pages(root, html)
	print str(pages)
        data = {}
        data['url'] = url
        data['root'] = ''
        data['html'] = html
        data['date'] = datetime.datetime.utcnow()
        result = collection.insert_one(data)                
        
        for urlpage in pages:
            if not visited.get(urlpage):                
		print urlpage
                html = read_remote_page(urlpage)
                data = {}
                data['url'] = urlpage
                data['root'] = url
                data['html'] = html
                data['date'] = datetime.datetime.utcnow()
                visited[urlpage] = data['date']
                result = collection.insert_one(data)
                p = get_prices(urlpage, html)
                
                for item in p:
                    result = pricelist.insert_one(item)
                time.sleep(10)
    except:
        print "Skip " + url
        visited[url] = 'skip'
    time.sleep(20)
        
#print len(html)
#pages


# In[ ]:



