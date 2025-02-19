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

# Inicializa la base de datos de PostgreSQL
su postgres -c "initdb -D /var/lib/postgresql/data"
su postgres -c "pg_ctl -D /var/lib/postgresql/data -l logfile start"

# Establecer la ruta predeterminada
ip route del default
ip route add default via ${ROUTER_IP}

# Ejecutar scripts de la aplicación
python create_db.py
python app.py

# Mantener el contenedor en ejecución
tail -f /dev/null
