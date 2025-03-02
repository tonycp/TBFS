#!/bin/bash

# Generar el archivo .env a partir de docker-compose.yml
cat <<EOL > .env
# Variables de entorno para el servidor
DATABASE_URL=sqlite:///./test.db
EOL

echo ".env file created."

# Ejecutar scripts de la aplicación
python create_db.py
python app.py

# Mantener el contenedor en ejecución
tail -f /dev/null
