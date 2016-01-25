#!/bin/bash

atime=$(date +%s -d "`head -1 /media/sf_virtual_share/test_log.log|cut -f1`")
ltime=$(date +%s -d "`tail -1 /media/sf_virtual_share/test_log.log|cut -f1`")
ctime=$((${atime}+10*60))

while(( ${ctime} <= ${ltime} ))
do
    btime=`date -d "1970-01-01 UTC ${atime} seconds" "+%F %T"`
    etime=`date -d "1970-01-01 UTC ${ctime} seconds" "+%F %T"`
    echo -e "--------------------------------------------------------"
    echo "data from ${btime} to ${etime}"
   # sed -n '/'"${btime}"'/,/'"${etime}"'/p' /media/sf_virtual_share/test_log.log|awk '{a[$3]++}END{for(i in a){if(i!="")print i,a[i]}}'|column -t
    awk '/'"${btime}"'/,/'"${etime}"'/{a[$3]++}END{for(i in a){print i,a[i] | "sort -k 1"}}' /media/sf_virtual_share/test_log.log|column -t
    atime=${ctime}
    ctime=$(($ctime+10*60))
done

    echo -e "--------------------------------------------------------"
ftime=`date -d "1970-01-01 UTC ${ltime} seconds" "+%F %T"`
ztime=`date -d "1970-01-01 UTC ${atime} seconds" "+%F %T"`
echo "data from ${ztime} to ${ftime}"
   # sed -n '/'"${ztime}"'/,/'"${ftime}"'/p' /media/sf_virtual_share/test_log.log|awk '{a[$3]++}END{for(i in a){if(i!="")print i,a[i]}}'|column -t
    awk '/'"${ztime}"'/,/'"${ftime}"'/{a[$3]++}END{for(i in a){print i,a[i] | "sort -k 1"}}' /media/sf_virtual_share/test_log.log|column -t 
    echo -e "--------------------------------------------------------\n"
echo "Done!"

<<<<<<< HEAD

=======
>>>>>>> code_test
