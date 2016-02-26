#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Martin Wu <martin.wu2dream@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""

import pymongo
import datetime
import time
import re

class TransTZ(datetime.tzinfo):
    def __init__(self, offset=0):
        self._offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(hours=self._offset)

    def tzname(self, dt):
        return "UTC +%s" % self._offset

    def dst(self, dt):
        return datetime.timedelta(hours=self._offset)

def readfiles(fp):
    REGEX_STR = '\[(\d*)-(\d*)-(\d*)\s(\d*).(\d*).(\d*)\]\[(.*)\]\[(.*)\](\{.*\})'
    field = ["year","month","day","hour","min","sec","level","type","data"]
    for a in range(0, len(field)):
        field[a] = re.search(REGEX_STR,fp).group(a+1).decode("GBK")
    return field

def transform_data(IMPORT_IN,URI_OUT):
    f = open(IMPORT_IN,"r") 
    conn_out = pymongo.MongoClient(URI_OUT)
    count = 0
    package = []
    show = 0
    for i in f :
        show += 1
        data = readfiles(i)
        if count <= 100:
            package.append(translate_data(data))
            count += 1
        else:
            conn_out["log"]["q2"].insert_many(package)
            time.sleep(1)
            count = 0
            package = []
            package.append(translate_data(data))
            count += 1
        if show % 2000 == 0:
            print show
    conn_out["log"]["q2"].insert_many(package)
    print show
    conn_out.close()
    f.close()

def translate_data(doc):
    try:
       time = datetime.datetime(int(doc[0]),int(doc[1]),int(doc[2]),int(doc[3]),int(doc[4]),int(doc[5]),tzinfo=TransTZ(8))
       level = str(doc[6])
       type1 = str(doc[7])
       data = eval(doc[8])
       document = {"level":level,"type":type1,"data":data,"time":time}
    except KeyError:
        doc = None
        print "KeyError"
    return document

if __name__ == "__main__":
    IMPORT_IN = "log.txt"
    URI_OUT = "127.0.0.1:20000"
    transform_data(IMPORT_IN, URI_OUT)
