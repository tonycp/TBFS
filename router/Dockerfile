# Usa la imagen base de Alpine
FROM alpine

# Instala iptables y otras utilidades necesarias
RUN apk add --no-cache iptables iproute2

# Habilita el reenvío de IP
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

# Aplica la configuración de sysctl
RUN sysctl -p /etc/sysctl.conf || true

# Comando por defecto para mantener el contenedor en ejecución
CMD ["sh", "-c", "sysctl -p && tail -f /dev/null"]