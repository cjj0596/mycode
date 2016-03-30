#!/bin/bash
#desc: pxe install centos6.4 or centos7.0 config script
#date: 2016-03-29

IP_DHCP=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'|cut -d. -f1-3`
IP_ADDR=${IP_DHCP}.0
IP_MASK=`ifconfig|grep Mask|grep -v 127.0.0.1|cut -d: -f4`
IP_LOCAL=`ifconfig|grep "inet addr:"|grep -v "127.0.0.1"|cut -d: -f2|awk '{print $1}'`
#ISO_PATH
CentOS6=`cat ISO_DIR.conf|grep 6.4|cut -d= -f2`
CentOS7=`cat ISO_DIR.conf|grep 7.0|cut -d= -f2`

#install packages
yum install -y dhcp tftp tftp-server syslinux system-config-kickstart httpd >/dev/null 2>&1

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

#Config tftp file
cat > /etc/xinetd.d/tftp <<end..
# default: off
# description: The tftp server serves files using the trivial file transfer \
#       protocol.  The tftp protocol is often used to boot diskless \
#       workstations, download configuration files to network-aware printers, \
#       and to start the installation process for some operating systems.
service tftp
{
        socket_type             = dgram
        protocol                = udp
        wait                    = yes
        user                    = root
        server                  = /usr/sbin/in.tftpd
        server_args             = -s /tftpboot
        disable                 = no
        per_source              = 11
        cps                     = 100 2
        flags                   = IPv4
}
end..

#config pxe boot file
mkdir -p /tftpboot
cp /usr/share/syslinux/pxelinux.0 /tftpboot

#ISO_PATH
CentOS6=`cat ISO_DIR|grep 6.4|cut -d= -f2`
CentOS7=`cat ISO_DIR|grep 7.0|cut -d= -f2`

#config centos6.4 boot file
mkdir -p /tftpboot/CentOS6.4
status6=0
if [ ! -z ${CentOS6} ]
then
    cp ${CentOS6}/images/pxeboot/initrd.img  /tftpboot/CentOS6.4/ >/dev/null 2>&1
    if [ $? -eq 0 ]
    then
        cp ${CentOS6}/images/pxeboot/vmlinuz  /tftpboot/CentOS6.4/ >/dev/null 2>&1
        echo "CentOS6 boot file copy done."
        status6=1
    else
        echo "Can't find CentOS6 boot file in the path."
    fi
else
    echo "CentOS6's path is empty."
fi

#config centos7 boot file
mkdir -p /tftpboot/CentOS7.0
status7=0
if [ ! -z ${CentOS7} ]
then
    cp ${CentOS7}/images/pxeboot/initrd.img  /tftpboot/CentOS7.0/ >/dev/null 2>&1
    if [ $? -eq 0 ]
    then
        cp ${CentOS7}/images/pxeboot/vmlinuz  /tftpboot/CentOS7.0/ >/dev/null 2>&1
        echo "CentOS7 boot file copy done."
        status7=1
    else
        echo "Can't find CentOS7 boot file in the path."
    fi
else
    echo "CentOS7's path is empty."
fi


#pxe boot file
mkdir -p /tftpboot/pxelinux.cfg
cp /usr/share/syslinux/vesamenu.c32 /tftpboot/
cat > /tftpboot/pxelinux.cfg/default <<end..
default vesamenu.c32
prompt 0
timeout 300
ONTIMEOUT 3
menu title                     PXE Boot Menu
label 1
menu label ^1) Install CentOS 7 x64 
kernel CentOS7.0/vmlinuz
append ks=http://${IP_LOCAL}/centos/7/ks.cfg initrd=CentOS7.0/initrd.img
label 2
menu label ^2) Install CentOS 6.4 x64 
kernel CentOS6.4/vmlinuz
append ks=http://${IP_LOCAL}/centos/6/ks.cfg initrd=CentOS6.4/initrd.img
label 3
menu label ^3) Boot from local drive
localboot 1

end..

#mount iso in httpd
mount|grep "/var/www/html/centos/6/x86_64" >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "CentOS 6.4 is ready."
else
    if [ ${status6} ]
    then
        mkdir -p /var/www/html/centos/6/x86_64/
        mount --bind ${CentOS6} /var/www/html/centos/6/x86_64/
    else
        echo "CentOS 6.4 NOT FOUND."
    fi
fi

mount|grep "/var/www/html/centos/7/x86_64" >/dev/null 2>&1
if [ $? -eq 0 ]
then
    echo "CentOS 7.0 is ready."
else
    if [ ${status7} ]
    then
        mkdir -p /var/www/html/centos/7/x86_64/
        mount --bind ${CentOS7} /var/www/html/centos/7/x86_64/
    else
        echo "CentOS 7.0 NOT FOUND."
    fi
fi

setenforce 0
service iptables stop
service httpd restart
service xinetd restart
service dhcpd restart
