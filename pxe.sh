#!/bin/bash
#desc: pxe install centos6.4 or centos7.0 config script
#date: 2016-03-23
IP_DHCP=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'|cut -d. -f1-3`
IP_ADDR=${IP_DHCP}.0
IP_MASK=`ifconfig|grep Mask|grep -v 127.0.0.1|cut -d: -f4`
IP_LOCAL=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'`

#check dhcp
rpm -qa|grep dhcp >/dev/null 2>&1
if [ $? -eq 0 ]
then 
    echo "dhcp already exist."
else
    yum install -y dhcp
fi

#dhcp config file
cat > /etc/dhcp/dhcpd.conf <<end..
ddns-update-style interim; 
ignore client-updates; 
authoritative;
allow booting; 
allow bootp; 
subnet ${IP_ADDR} netmask ${IP_MASK} {
    range ${IP_DHCP}.1 ${IP_DHCP}.255; 
    option routers ${IP_DHCP}.1; 
    option subnet-mask ${IP_MASK};  
    default-lease-time 21600;
    max-lease-time 43200; 
    next-server ${IP_LOCAL};
    filename "/pxelinux.0"; 
} 
end..

#check tftp
rpm -qa|grep tftp >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "tftp already exist."
else 
    yum install -y tftp tftp-server
fi

#check system-config-kickstart
rpm -qa|grep tftp >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "kickstart already exist."
else 
    yum install -y system-config-kickstart
fi

#check httpd 
rpm -qa|grep httpd >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "httpd already exist."
else
    yum install -y httpd
fi

#config pxe boot file
mkdir -p /tftpboot
cp /usr/share/syslinux/pxelinux.0 /tftpboot
#config centos6.4 boot file
cp /media/CentOS_6.4_Final/images/pxeboot/initrd.img  /tftpboot/initrd6.4.img
cp /media/CentOS_6.4_Final/images/pxeboot/vmlinuz  /tftpboot/vmlinuz6.4
cp /media/CentOS_6.4_Final/isolinux/*.msg  /tftpboot

#config centos7 boot file
cp /media/CentOS\ 7\ x86_64/images/pxeboot/initrd.img  /tftpboot/initrd7.0.img
cp /media/CentOS\ 7\ x86_64/images/pxeboot/vmlinuz  /tftpboot/vmlinuz7.0

#modify boot.msg
sed -i 's/^.*Press.*$/ -  To install CentOS-6.4 , please input centos6.4 then press ^O01<ENTER>^O07 to begin the installation process.\n\n\n -  To install CentOS-7.0 , please input centos7.0 then press ^O01<ENTER>^O07 to begin the installation process./g' /tftpboot/boot.msg

#pxe boot file
mkdir -p /tftpboot/pxelinux.cfg
cat > /tftpboot/pxelinux.cfg/default <<end..
default centos6.4   /*自动进入centos6.4选项进行安装*/
prompt 1
timeout 300
display boot.msg
F1 boot.msg
label centos6.4
  kernel vmlinuz6.4
  append ks=http://${IP_LOCAL}/ks6.4.cfg initrd=initrd6.4.img
label centos7.0
  kernel vmlinuz7.0
  append ks=http://${IP_LOCAL}/ks7.0.cfg initrd=initrd7.0.img
end..

#mount iso in httpd
mount|grep "/var/www/html/centos/6/x86_64"
if [ $? -eq 0 ]
then
    echo "CentOS 6.4 is ready."
else
    mkdir -p /var/www/html/centos/6/x86_64/
    mount --bind /media/CentOS_6.4_Final /var/www/html/centos/6/x86_64/
fi

mount|grep "/var/www/html/centos/7/x86_64"
if [ $? -eq 0 ]
then
    echo "CentOS 7.0 is ready."
else
    mkdir -p /var/www/html/centos/7/x86_64/
    mount --bind /media/CentOS\ 7\ x86_64 /var/www/html/centos/7/x86_64/
fi

setenforce 0
service iptables stop
service httpd restart
service xinetd restart
service dhcpd restart
