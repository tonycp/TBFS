# Usa la imagen base de Alpine
FROM alpine

WORKDIR /app

# Instala iptables y otras utilidades necesarias
RUN apk add --no-cache iptables iproute2

# Copia el script de inicialización al contenedor
COPY init.sh ./init.sh
RUN chmod +x ./init.sh

# Comando por defecto para ejecutar el script de inicialización
CMD ["./init.sh"]