#!/usr/bin/env python
import re
import time
import linecache

f=open("/media/sf_virtual_share/ab.log","r")
first_time=re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',f.readline()).group(0)
ftime=time.mktime(time.strptime(first_time,'%Y-%m-%d %H:%M:%S'))
ftime+=10*60
x = time.localtime(ftime)
print time.strftime('%Y-%m-%d %H:%M:%S',x)
end=linecache.getline("/media/sf_virtual_share/ab.log",len(open("/media/sf_virtual_share/ab.log",'r').readlines()))
end_time=re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',end).group(0)
etime=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))

list=[]
for line in f:
    rtime=re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',line).group(0)
    ctime=ftime=time.mktime(time.strptime(rtime,'%Y-%m-%d %H:%M:%S'))
    if ctime <= ftime :
         command=re.search(r'\t([\d\w\W]*)\s\s',line).group(0)
         list.append(command)
    else:
         break;


print list





f.close()
