#!/usr/bin/ksh
mdate=`date "+%Y-%m-%d %H:%M:%S"`
ndate=`awk -F ';' '{print("mdate=",$18)}' lastline.dat`
echo ${ndate}
echo ${mdate}
echo $(`awk -F'  ' '{print $1}' A`)
