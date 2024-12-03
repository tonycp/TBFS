# Usa la imagen base de Alpine
FROM alpine

# Instala iptables y otras utilidades necesarias
RUN apk add --no-cache iptables iproute2

# Habilita el reenvío IP
RUN echo "net.ipv4.ip_forward=1" | tee -a /etc/sysctl.conf

# Copia el script de inicialización al contenedor
COPY route.sh /root/route.sh
RUN chmod +x /root/route.sh

# Establece el punto de entradas
ENTRYPOINT /root/route.sh