#!/bin/bash
#desc: pxe install centos5.4 config script
#date: 2016-03-23

IP_DHCP=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'|cut -d. -f1-3`
IP_ADDR=${IP_DHCP}.0
IP_MASK="255.255.255.0"
IP_LOCAL=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'`

yum install -y xinetd dhcp tftp-server system-config-kickstart

if [ -e /etc/xinetd.d/tftp ]; then
 /bin/sed -i '14 s/yes/no/' /etc/xinetd.d/tftp
else
 echo "tftp-server no install "
 exit 0
fi

#dhcp config file
cat > /etc/dhcpd.conf <<end..
ddns-update-style interim; 
ignore client-updates; 
authoritative;
allow booting; 
allow bootp; 
subnet $IP_ADDR netmask $IP_MASK {
    range ${IP_DHCP}.1 ${IP_DHCP}.255; 
    option routers ${IP_DHCP}.1; 
    option subnet-mask 255.255.255.0;  
    option domain-name-servers 203.103.24.68;
    default-lease-time 21600;
    max-lease-time 43200; 
    next-server $IP_LOCAL;
    filename "/pxelinux.0"; 
} 
end..

#config pxe boot file
#mount /media/CentOS_6.4_Final /var/www/html/centos/6/x84_64
mkdir -p /tftpboot 
cp /usr/share/syslinux/pxelinux.0 /tftpboot
cp /media/CentOS_6.4_Final/images/pxeboot/initrd.img  /tftpboot
cp /media/CentOS_6.4_Final/images/pxeboot/vmlinuz  /tftpboot
cp /media/CentOS_6.4_Final/isolinux/*.msg  /tftpboot

mkdir -p /tftpboot/pxelinux.cfg 

#pxe boot file
cat > /tftpboot/pxelinux.cfg/default <<end..
default linux       /*自动进入linux选项进行安装*/
prompt 1
timeout 30
display boot.msg
F1 boot.msg
F2 options.msg
F3 general.msg
F4 param.msg
F5 rescue.msg
F7 snake.msg
label local
localboot 0
label linux
kernel vmlinuz
append ks=http://${IP_LOCAL}/ks.cfg initrd=initrd.img devfs=nomount ramdisk_size=9216
label text
kernel vmlinuz
append initrd=initrd.img text devfs=nomount ramdisk_size=9216
label expert
kernel vmlinuz
append expert initrd=initrd.img devfs=nomount ramdisk_size=9216
label ks
kernel vmlinuz
append ks initrd=initrd.img devfs=nomount ramdisk_size=9216
label nofb
kernel vmlinuz
append initrd=initrd.img devfs=nomount nofb ramdisk_size=9216
label lowres
kernel vmlinuz
append initrd=initrd.img lowres devfs=nomount ramdisk_size=9216
kernel vmlinuz

end..

service httpd restart
service xinetd restart
service dhcpd restart

system-config-kickstart &
