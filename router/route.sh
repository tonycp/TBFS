#!/bin/sh

# Generar el archivo .env a partir de docker-compose.yml
cat <<EOL > .env
# Variables de entorno para el router
ROUTER_CLIENT_IP=${ROUTER_CLIENT_IP}
ROUTER_SERVER_IP=${ROUTER_SERVER_IP}
PROXY_CLIENT_IP=${PROXY_CLIENT_IP}
PROXY_SERVER_IP=${PROXY_SERVER_IP}
EOL
echo ".env file created."

# Configuración de red
iptables -t nat -A POSTROUTING -s ${CLIENT_NETWORK} -o eth0 -j MASQUERADE
iptables -t nat -A POSTROUTING -s ${SERVER_NETWORK} -o eth0 -j MASQUERADE

sleep 5
ip route add 224.0.0.0/4 dev eth1
python multicast_proxy.py