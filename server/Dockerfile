FROM python:3.11-alpine

# Establece el directorio de trabajo
WORKDIR /app

RUN pip install -U pip

# Instala iptables, PostgreSQL y otras utilidades necesarias
RUN apk add --no-cache iptables iproute2 postgresql postgresql-contrib

# Inicializa la base de datos de PostgreSQL
RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql

# Copia el script de inicialización al contenedor
COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# Copia el archivo de requisitos
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . /app

# Exponer el puerto de PostgreSQL
EXPOSE 5432

# Comando por defecto para iniciar PostgreSQL y luego la aplicación
CMD ["sh", "/app/init.sh"]