#!/bin/bash

# Generar el archivo .env a partir de docker-compose.yml
cat <<EOL > .env
# Variables de entorno para el cliente
EOL

echo ".env file created."

# Establecer la ruta predeterminada
ip route del default
ip route add default via ${ROUTER_IP}

# Mantener el contenedor en ejecución
tail -f /dev/null
