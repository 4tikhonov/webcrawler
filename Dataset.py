#!/usr/bin/python

import re
import urllib2
import time
import string
import random
import openpyxl
import pandas as pd
import datetime
import config
from pymongo import MongoClient

def create_excel_dataset(fullpath, data):
    wb = openpyxl.Workbook(encoding='utf-8')
    ws = wb.get_active_sheet()
    ws.title = "Data"

    i = 0
    for item in result:
        j = 0
        for field in item:
            if field == 'title':
                print item[field].encode("utf-8")
            c = ws.cell(row=i, column=j)
            c.value = str(item[field]).encode("utf-8")
            j+=1
        i+=1
        
    wb.save(fullpath)
    return fullpath
    
client = MongoClient()
pricesdb = client.get_database('pricesmay')
db = pricesdb.data

def getmonth():
    now = datetime.datetime.now()
    monname = time.strftime("%B")
    year = now.year
    if int(now.month) < 10:
        month = "0%s" % now.month
    else:
        month = "%s" % now.month
    monthpat = "%s-%s" % (str(year), str(month))
    return (monthpat, monname, year)

(monthpat, monname, year) = getmonth()
regx = re.compile(monthpat, re.IGNORECASE)
result = db.find({"date": regx})
filename = "webcrawler_bigdata_%s%s" % (monname, year)
create_excel_dataset("%s/webcrawler/%s.xlsx" % (homepath, filename), result)

