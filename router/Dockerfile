FROM python:3.11-alpine

WORKDIR /root

RUN apk add iptables && echo "net.ipv4.ip_forward=1" | tee -a /etc/sysctl.conf

# run apk add procps iptables iproute2

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r ./requirements.txt

CMD /bin/shw

COPY route.sh ./route.sh

COPY multicast_proxy.py ./multicast_proxy.py

RUN chmod +x ./route.sh

ENTRYPOINT ./route.sh