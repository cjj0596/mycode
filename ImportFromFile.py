#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Martin Wu <martin.wu2dream@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""
import os
import pymongo
import json
import datetime
import time
import re
import linecache
from pymongo.errors import (OperationFailure,
                            NetworkTimeout)

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
        try:
            field[a] = re.search(REGEX_STR,fp).group(a+1)
        except:
            return fp
    return field

def checkerror(file_import):
    end=linecache.getline(file_import,len(open(file_import,'r').readlines()))
    result = re.search(r'Error_output|Output:row (\d*)',end)
    if (result == None ):
        return 0
    else:
        print "Countine from row "+str(int(result.group(1))+1)
        return (result.group(1))

def error_import(doc,show,reason):
    f=open("error_log.txt",'a+')
    f.write(doc)
    f.write("Error_output:row "+str(show)+"\n")
    f.close()
    print "data error in "+str(show+1)+reason

def transform_data(IMPORT_IN,URI_OUT):
    conn_out = pymongo.MongoClient(URI_OUT)
    count = 0
    error_count = 0
    package = []
    if os.path.exists("error_log.txt"):
        show = int(checkerror("error_log.txt"))
    else:
        show = 0
    try:
        for i in linecache.getlines(IMPORT_IN)[show:]:
            data = readfiles(i)
            if isinstance(data,str):
                error_count += 1
                error_import(i,show,"   Readfiles error.")
            else:
                if count < 100:
                    try:
                        package.append(translate_data(data))
                    except:
                        error_count += 1
                        error_import(i,show,"   Translate error.")
                    count += 1
                else:
                    conn_out["log"]["q2"].insert_many(package)
                    time.sleep(1)
                    count = 0
                    package = []
                    package.append(translate_data(data))
                    count += 1
            show += 1
            if show % 2000 == 0:
                print show
        conn_out["log"]["q2"].insert_many(package)
        #print show
    except (KeyboardInterrupt,OperationFailure,NetworkTimeout,ValueError):
        f=open("error_log.txt",'a+')
        f.write("Error_output:row "+str(show)+"\n")
        f.close()
        print "\nError Stop.Inserted to row "+str(show-error_count)+".\nNext time will start from row "+str(show+1-error_count)+"."
    conn_out.close()
    print "Finished! Total:"+str(show)+"  Import Successed :"+str(show-error_count)+"  Import Failed :"+str(error_count)
    f=open("error_log.txt",'a+')
    f.write("Output:row "+str(show)+"\n")
    f.close()

def translate_data(doc):
    time = datetime.datetime(int(doc[0]),int(doc[1]),int(doc[2]),int(doc[3]),int(doc[4]),int(doc[5]),tzinfo=TransTZ(8))
    level = str(doc[6])
    type1 = str(doc[7])
    data = json.loads(doc[8])
    document = {"level":level,"type":type1,"data":data,"time":time}
    return document

if __name__ == "__main__":
    IMPORT_IN = "log2.txt"
    URI_OUT = "127.0.0.1:20000"
    transform_data(IMPORT_IN, URI_OUT)

