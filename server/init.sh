#!/bin/bash

# Generar el archivo .env a partir de docker-compose.yml

cat <<EOL > .env
# Variables de entorno para el servidor
PROTOCOL=${PROTOCOL}
HOST=${HOST}
PORT=${PORT}
DATABASE_URL=${DATABASE_URL}
EOL

echo ".env file created."

# Mantener el contenedor en ejecución
python create_db.py
python app.py
