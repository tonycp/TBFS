#!/bin/bash

# Generar el archivo .env a partir de docker-compose.yml
cat <<EOL > .env
# Variables de entorno para el servidor
PROTOCOL=${PROTOCOL}
HOST=${HOST}
PORT=${PORT}
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/${POSTGRES_DB}
EOL

echo ".env file created."

# Configurar PostgreSQL
pg_ctl initdb -D /var/lib/postgresql/data
pg_ctl start -D /var/lib/postgresql/data -l logfile
psql --username=${POSTGRES_USER} --command="CREATE DATABASE ${POSTGRES_DB};"

# Establecer la ruta predeterminada
ip route del default
ip route add default via ${ROUTER_IP}

# Mantener el contenedor en ejecución
python create_db.py
python app.py
