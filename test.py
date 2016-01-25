#!/usr/bin/env python
import re
import time
import linecache
from collections import Counter

f=open("/media/sf_virtual_share/test_log.log",'r')
#print f.readline()
first_time=re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',f.readline()).group(0)
ftime=time.mktime(time.strptime(first_time,'%Y-%m-%d %H:%M:%S'))

end=linecache.getline("/media/sf_virtual_share/test_log.log",len(open("/media/sf_virtual_share/test_log.log",'r').readlines()))
end_time=re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',end).group(0)
etime=time.mktime(time.strptime(end_time,'%Y-%m-%d %H:%M:%S'))

#print end,end_time,etime
ctime=ftime+10*60
#print ctime
f.close()

f=open("/media/sf_virtual_share/test_log.log","r")
i = 0
list1=[]
print "------------------------------------------------"
for line in f:
    try:
       atime=re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',line).group(0)
       atime2=time.mktime(time.strptime(atime,'%Y-%m-%d %H:%M:%S'))
       if (atime2 <= ctime):
	   if (i == 0):
	       print "data from " + atime + " to " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ctime))
           i += 1
           command=re.search(r'\t([\d\w\W]*)\.[\w\s]',line).group(0)
           if (command != ''):
              #print command
	      list1.append(command)
       elif (atime2 > ctime and (ctime+10*60) <= etime):
	   result=dict(Counter(list1))
	  # print result
	   for k in result:
               print result[k],k
           print "------------------------------------------------"
           i=0
	   list1=[]
	   result={}
           if (atime2 > (ctime+10*60)):
               ctime+=10*60*2
           else:
               ctime+=10*60
           i += 1
          # print i,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(atime2)),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ctime))
           print "data from " + atime + " to " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ctime))
	   command=re.search(r'\t([\d\w\W]*)\.[\w\s]',line).group(0)
           if (command != ''):
	      list1.append(command)
       else:
	   result=dict(Counter(list1))
           for k in result:
	       print result[k],k
           print "------------------------------------------------"     
           i=0
           list1=[]
	   result={}
           i +=1
           ctime=etime
          # print i,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(atime2)),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ctime))
	   print "data from " + atime + " to " + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ctime))
           command=re.search(r'\t([\d\w\W]*)\.[\w\s]',line).group(0)
           if (command != ''):
	      list1.append(command)
    except AttributeError:
           continue
result=dict(Counter(list1))
for k in result:
    print result[k],k
print "------------------------------------------------"           
print "Done!"

f.close()
