# Configura la URL de conexión a tu base de datos
import os
from dotenv import load_dotenv
from data import Base
from sqlalchemy import create_engine, MetaData

load_dotenv()

# Leer la URL de la base de datos desde el archivo .env
DB_URL = os.getenv("DB_URL", "sqlite:///mydatabase.db")

# Crear el motor de la base de datos
engine = create_engine(DB_URL)

# Crear todas las tablas (asumiendo que ya tienes modelos definidos)
metadata = MetaData()
metadata.create_all(engine)
print("Base de datos y tablas creadas exitosamente.")
