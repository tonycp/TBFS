FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia el script de inicialización al contenedor
COPY init.sh ./init.sh
RUN chmod +x ./init.sh

# Copia el archivo de requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación
COPY . .

# Comando por defecto para iniciar una consola bash
CMD ["./init.sh"]