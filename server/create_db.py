# Configura la URL de conexión a tu base de datos
import os
from dotenv import load_dotenv
from data import Base
from sqlalchemy import create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "'postgresql://postgres:ranvedi@localhost/SDDB'")
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
print("Base de datos y tablas creadas exitosamente.")