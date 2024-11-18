# Sistema de Ficheros Distribuido

## Descripción

El objetivo principal es implementar, utilizando Python y SQLAlchemy en una arquitectura por capas, un sistema de ficheros distribuido basado en etiquetas. El sistema almacenará ficheros que cuyos metadatos son el nombre y las etiquetas que posee. El sistema de ficheros estará constituido por nodos los cuales tendrán una responsabilidad específica (role), que puede ser almacenar datos, enrutar pedidos, consultar el sistema, etc. La existencia de un único role para cada nodo no impide que dos nodos no puedan estar en un mismo host. El sistema debe estar disponible siempre que halla algún nodo disponible por cada role (eso no implica que deba dar una respuesta rápida ante los pedidos). El sistema no puede perder datos en caso de que falle un nodo de almacenamiento. En caso de que el sistema sufra una partición (se divida en dos o más subsistemas producto de la pérdida de nodos o enlaces entre nodos), debe ser capaz de reconectarse y funcionar como un solo sistema cuando exista la posibilidad de comunicación entre los nodos de los subsistemas.

## Tecnologías Utilizadas

- **Python**: Lenguaje de programación.
- **SQLAlchemy**: ORM para interactuar con bases de datos.
- **PostgreSQL**: Sistema de gestión de bases de datos.
- **Click**: Biblioteca para crear interfaces de línea de comandos.
- **Sphinx**: Herramienta para generar documentación.
- **PyZMQ**: Biblioteca para comunicación entre procesos.

## Instalación

Para instalar el proyecto, sigue estos pasos:

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tonycp/TBFS.git
    cd TBFS
    ```

2. Crea un entorno virtual:

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Comandos

1. ***Agregar ficheros***: Copia uno o más ficheros hacia el sistema y estos son inscritos con las etiquetas contenidas en tag-list.

    ``` bash
    add file-list tag-list
    ```

2. ***Eliminar ficheros***: Elimina todos los ficheros que cumplan con la consulta tag-query.

    ``` bash
    delete tag-query
    ```

3. ***Listar ficheros y etiquetas***: Lista el nombre y las etiquetas de todos los ficheros que cumplan con la consulta tag-query.

    ``` bash
    list tag-query
    ```

4. ***Agregar etiquetas a ficheros***: Añade las etiquetas contenidas en tag-list a todos los ficheros que cumpan con la consulta tag-query.

    ``` bash
    add-tags tag-query tag-list
    ```

5. ***Eliminar etiquetas a ficheros***: Elimina las etiquetas contenidas en tag-list de todos los ficheros que cumpan con la consulta tag-query.

    ``` bash
    delete-tags tag-query tag-list
    ```

## Estructura

``` bash
TBFS/
│
├── app/                # Presentation layer
│   ├── __init__.py     # Indicates that this directory is a package
│   ├── main.py         # Main entry point of the application
│   └── ui_logic.py     # User interface logic and interactions
│
├── business_logic/     # Business logic layer
│   ├── __init__.py     # Indicates that this directory is a package
│   ├── core.py         # Implementation of the core business logic
│   └── services.py     # Additional services and utilities
│
├── data_access/        # Data access layer
│   ├── __init__.py     # Indicates that this directory is a package
│   ├── models.py       # SQLAlchemy model definitions
│   └── repository.py   # Data repository for database interactions
│
├── tests/              # Unit and integration tests
│   ├── __init__.py     # Indicates that this directory is a package
│   ├── test_app.py     # Tests for the presentation layer
│   ├── test_core.py    # Tests for the business logic layer
│   └── test_data.py    # Tests for the data access layer
│
├── docker-compose.yml  # File to define and run containers
├── Dockerfile          # File to define the Docker image
├── LICENSE             # File to define the MIT license
├── README.md           # Project documentation
└── requirements.txt    # Application dependencies
```
