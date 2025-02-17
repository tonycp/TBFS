FROM python:3.11-alpine

# Establece el directorio de trabajo
WORKDIR /app

RUN pip install -U pip

# Instala iptables, PostgreSQL y otras utilidades necesarias
RUN apk add --no-cache iptables iproute2 postgresql postgresql-contrib

# Copia el script de inicialización al contenedor
COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

# Copia el archivo de requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . /app

# Comando por defecto para iniciar una consola bash
CMD ["sh", "/app/init.sh"]