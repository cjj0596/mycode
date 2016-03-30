#!/usr/bin/python
#--coding:utf-8--
#mongo -port 20000    db:testdb   collection:pay 
import time
import re
import pymongo

f=open("日志.txt",'r')
r1 = re.compile(r'(\d){4}-(\d){2}-(\d){2}')
r2 = re.compile(r'("orderid":")((.){24})')
#date1 = r1.search(f.read()).group()
dateC = time.mktime(time.strptime(r1.search(f.read()).group(),'%Y-%m-%d'))
f.close()
f=open("日志.txt",'r')
conn = pymongo.MongoClient('localhost',20000)
db = conn.testdb
i=1
found=0
not_found=0
for line in f:
    order_date = r1.search(line)
    if (order_date != None):
        order_dateC = time.mktime(time.strptime(order_date.group(),'%Y-%m-%d'))
        if (dateC == order_dateC):
            if (i):
                print order_date.group()
                i=0
        else:
            print "总数："+str(found+not_found),"\t成功入库数："+str(found),"\t失败入库数："+str(not_found)
            print "\n"+order_date.group()
            found=0
            not_found=0
    dateC = order_dateC 
    order_id = r2.search(line)
    if (order_id != None):
       if (db.pay.find_one({"data.orderid" : order_id.group(2)}) == None):
           print "orderid: "+order_id.group(2),"\t入库失败"
           not_found += 1
       else:
          # print order_id.group(2),"\t成功入库"
           found += 1
print "总数："+str(found+not_found),"\t成功入库数："+str(found),"\t失败入库数："+str(not_found)+"\n"
f.close()
