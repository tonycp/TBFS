# Configura la URL de conexión a tu base de datos
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData

import os

from data.const import *

load_dotenv()

# Leer la URL de la base de datos desde el archivo .env
base_url = os.getenv(DB_BASE_URL_ENV_KEY, DEFAULT_DB_BASE_URL)
db_name = os.getenv(DB_NAME_ENV_KEY, DEFAULT_DB_NAME)
DB_URL = base_url + db_name

# Crear el motor de la base de datos
engine = create_engine(DB_URL)

# Crear todas las tablas (asumiendo que ya tienes modelos definidos)
metadata = MetaData()
metadata.create_all(engine)
print("Base de datos y tablas creadas exitosamente.")
