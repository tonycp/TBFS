FROM python:3.11-alpine

RUN apk add iptables && echo "net.ipv4.ip_forward=1" | tee -a /etc/sysctl.conf

# run apk add procps iptables iproute2

CMD /bin/shw

COPY route.sh /root/route.sh

COPY multicast_proxy.py /root/multicast_proxy.py

RUN chmod +x /root/route.sh

ENTRYPOINT /root/route.sh