#!/bin/bash

DIR=`pwd`
for i in `ls|grep '.txt'`
do
  awk 'FNR==NR{a[$0];b[++t]=$0;next}{for(i in a) {if(match($0,"^"i,c)) d[i]=$0}}END{for(i=1;i<=t;i++)if(d[b[i]]!="") print d[b[i]]}' c3.txt $i > $i_done.txt
done
