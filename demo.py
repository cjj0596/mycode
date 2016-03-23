#!/usr/bin/python
#--coding:utf-8--
import ConfigParser
import time
import datetime
import re
import pymongo
import sys

start = time.time()
cf = ConfigParser.ConfigParser()
cf.read("demo.conf")

#mongodb配置信息
db_host = cf.get("db", "db_host")
db_port = cf.getint("db", "db_port")
#db_user = cf.get("db", "db_user")
#db_pass = cf.get("db", "db_pass")
db_name = cf.get("db", "db_name")
db_collection = cf.get("db", "db_collection")

#查询配置信息
log_name = cf.get("info","log_name")
period = cf.getint("info","period")

f=open(log_name,'r')
r1 = re.compile(r'(\d){4}-(\d){2}-(\d){2}') #匹配日志数据时间（年月日）
r2 = re.compile(r'((\d){2}).((\d){2}).((\d){2})')  #匹配日志数据时间（时分秒）
r3 = re.compile(r'\{(.*)\}')  #匹配"data"文档信息

dateC1 = time.mktime(time.strptime(r1.search(f.read()).group(),'%Y-%m-%d'))
dateC2 = dateC1 + (period-1)*24*60*60
f.close()

f = open(log_name,'r')
conn = pymongo.MongoClient(db_host,db_port)
#coon = MongoClient('mongodb://'+db_user+':' + db_pass + '@127.0.0.1')
db = conn[db_name]
col = db[db_collection]
log_all=len(open(log_name,'r').readlines()) #读取日志文件总行数
db_all=col.find().count()  #获取数据库总行数
status = "" #是否通过

if ((log_all/2) == db_all): #判断总数是否一致
    print "总数匹配。   总数为："+str(db_all)
    end = time.time()
    print "耗时: %fs" % (end - start)
    sys.exit(0)
else:
    count=0
    for line in f:
        order_date = r1.search(line)
        if (order_date != None):
            dateC3 = time.mktime(time.strptime(order_date.group(),'%Y-%m-%d'))
            if (dateC3 >= dateC1 and dateC3 <= dateC2):
		        count += 1
            else: #分别获取年月日int类型，后面pymongo的find和remove和insert会用到
                date1_Y = int(time.strftime('%Y',time.localtime(dateC1)))
                date1_m = int(time.strftime('%m',time.localtime(dateC1)))
                date1_d = int(time.strftime('%d',time.localtime(dateC1)))
                date2_Y = int(time.strftime('%Y',time.localtime(dateC2)))
                date2_m = int(time.strftime('%m',time.localtime(dateC2)))
                date2_d = int(time.strftime('%d',time.localtime(dateC2)))
                db_count = col.find({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}}).count()
				
                if (count == db_count): #判断日志和数据库的数量是否一致
                    status = "PASS"
                else:
                    status = "MISSED"
                    col.remove({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}})  #删除该时间段的数据	
                    #从日志中抽取该时间段的插入到数据库
                    fs = open(log_name,'r')
                    for a in fs:
                        cmp_date = r1.search(a)
                        if (cmp_date != None):
                            cmp_date1 = cmp_date.group()
                            cmp_dateC = time.mktime(time.strptime(cmp_date1,'%Y-%m-%d'))
                        else:
                            data_time = cmp_date1+r2.search(a).group()
                            data = r3.search(a).group().decode('GBK')
                            if (cmp_dateC >= dateC1 and cmp_dateC <=dateC2):
                                data = eval(data.encode('utf-8'))
                                col.insert(
                                    {
                                        "level" : "info",
                                        "type" : "pay",
                                        "data" : {
                                            "uid" : data.get('uid'),
                                            "ip" : data.get('ip'),
                                            "currency" : data.get('currency'),
                                            "money" : data.get('money'),
                                            "m_uid" : data.get('m_uid'),
                                            "product_id" : data.get('product_id'),
                                            "user_name" : data.get('user_name'),
                                            "yb" : data.get('yb'),
                                            "plat" : data.get('plat'),
                                            "user_lv" : data.get('user_lv'),
                                            "pay_time" : data.get('pay_time'),
                                            "channel_orderid" : data.get('channel_orderid'),
                                            "channel" : data.get('channel'),
                                            "udid" : data.get('udid'),
                                            "pay_channel" : data.get('pay_channel'),
                                            "user_game_time" : data.get('user_game_time'),
                                            "amount" : data.get('amount'),
                                            "orderid" : data.get('orderid')
                                        },
                                        "time" : datetime.datetime.strptime(data_time,"%Y-%m-%d%H:%M:%S"),
                                    }
                                )
                    fs.close()
                    #插入完毕
                if (status == "MISSED"):
                    print time.strftime('%Y-%m-%d',time.localtime(dateC1)),time.strftime('%Y-%m-%d',time.localtime(dateC2)),"  日志数："+str(count),"  数据库数："+str(db_count)+status+"  UPDATED ==>","  数据库数："+str(col.find({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}}).count())
                else:
                    print time.strftime('%Y-%m-%d',time.localtime(dateC1)),time.strftime('%Y-%m-%d',time.localtime(dateC2)),"  日志数："+str(count),"  数据库数："+str(db_count)+status
                count = 1
                dateC1 = dateC3
                dateC2 = dateC3 + (period-1)*24*60*60
				
#分别获取年月日int类型，后面pymongo的find和remove和insert会用到
date1_Y = int(time.strftime('%Y',time.localtime(dateC1)))
date1_m = int(time.strftime('%m',time.localtime(dateC1)))
date1_d = int(time.strftime('%d',time.localtime(dateC1)))
date2_Y = int(time.strftime('%Y',time.localtime(dateC2)))
date2_m = int(time.strftime('%m',time.localtime(dateC2)))
date2_d = int(time.strftime('%d',time.localtime(dateC2)))
db_count = col.find({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}}).count()

if (count == db_count):  #判断日志和数据库的数量是否一致
    status = "PASS"
else:
    status = "MISSED"
    col.remove({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}})   #删除该时间段的数据
    #从日志中抽取该时间段的插入到数据库
    fs = open(log_name,'r')
    for a in fs:
        cmp_date = r1.search(a)
        if (cmp_date != None):
            cmp_date1 = cmp_date.group()
            cmp_dateC = time.mktime(time.strptime(cmp_date1,'%Y-%m-%d'))
        else:
            data_time = cmp_date1+r2.search(a).group()
            data = r3.search(a).group().decode('GBK')
            if (cmp_dateC >= dateC1 and cmp_dateC <=dateC2):
                data = eval(data.encode('utf-8'))
                col.insert(
                    {
                        "level" : "info",
                        "type" : "pay",
                        "data" : {
                                "uid" : data.get('uid'),
                                "ip" : data.get('ip'),
                                "currency" : data.get('currency'),
                                "money" : data.get('money'),
                                "m_uid" : data.get('m_uid'),
                                "product_id" : data.get('product_id'),
                                "user_name" : data.get('user_name'),
                                "yb" : data.get('yb'),
                                "plat" : data.get('plat'),
                                "user_lv" : data.get('user_lv'),
                                "pay_time" : data.get('pay_time'),
                                "channel_orderid" : data.get('channel_orderid'),
                                "channel" : data.get('channel'),
                                "udid" : data.get('udid'),
                                "pay_channel" : data.get('pay_channel'),
                                "user_game_time" : data.get('user_game_time'),
                                "amount" : data.get('amount'),
                                "orderid" : data.get('orderid')
                            },
                        "time" : datetime.datetime.strptime(data_time,"%Y-%m-%d%H:%M:%S"),
                    }
                )
    fs.close()
    #插入完毕
if (status == "MISSED"):
    print time.strftime('%Y-%m-%d',time.localtime(dateC1)),time.strftime('%Y-%m-%d',time.localtime(dateC2)),"  日志数："+str(count),"  数据库数："+str(db_count)+status+"  UPDATED ==>","  数据库数："+str(col.find({"time":{"$gte":datetime.datetime(date1_Y,date1_m,date1_d),"$lte":datetime.datetime(date2_Y,date2_m,(date2_d+1))}}).count())
else:
    print time.strftime('%Y-%m-%d',time.localtime(dateC1)),time.strftime('%Y-%m-%d',time.localtime(dateC2)),"  日志数："+str(count),"  数据库数："+str(db_count)+status
f.close()
end = time.time()
print "更新后总数为："+str(col.find().count())
print "耗时: %fs" % (end - start)
