#!/bin/sh

# Habilitar reenvío IP
echo 1 > /proc/sys/net/ipv4/ip_forward

# Permitir tráfico entre las dos redes
iptables -A FORWARD -i server_network -o client_network -j ACCEPT
iptables -A FORWARD -i client_network -o server_network -j ACCEPT

# Mantener el contenedor en ejecución
tail -f /dev/null