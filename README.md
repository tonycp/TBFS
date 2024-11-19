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
├── app/                            # Presentation layer
│   ├── __init__.py                 # Indicates that this directory is a Python package
│   ├── main.py                     # Main entry point of the application; starts execution
│   └── ui_logic.py                 # User interface logic and handling interactions
│
├── business_logic/                 # Business logic layer
│   ├── dtos/                       # Data Transfer Objects (DTOs) to structure data between layers
│   │   ├─ __init__.py              # Indicates that this directory is a Python package
│   │   ├─ FileInputDto.py          # Definition of the DTO for file input
│   │   ├─ FileSourceInputDto.py    # Definition of the DTO for file source input
│   │   ├─ TagInputDto.py           # Definition of the DTO for tag input
│   │   └─ UserInputDto.py          # Definition of the DTO for user input
│   │
│   ├── services/                   # Services that encapsulate business logic
│   │   ├─ __init__.py              # Indicates that this directory is a Python package
│   │   ├─ FileService.py           # Service to handle operations related to files
│   │   ├─ FileSourceService.py     # Service to handle operations related to file sources
│   │   ├─ TagService.py            # Service to handle operations related to tags
│   │   └─ UserService.py           # Service to handle operations related to users
│   │
│   ├── __init__.py                 # Indicates that this directory is a Python package
│   ├── business_data.py            # Implementation of core business logic, such as rules and processes
│   ├── controllers.py              # Controllers that manage interactions between UI and business logic
│   ├── core.py                     # Implementation of the core business logic
│   ├── handlers.py                 # Handlers to process events and specific actions within the business logic
│   └── services.py                 # Additional services and utilities that can be used across the business layer
│
├── data_access/                    # Data access layer
│   ├── __init__.py                 # Indicates that this directory is a Python package
│   ├── models.py                   # SQLAlchemy model definitions representing database tables
│   └── repository.py               # Repository that handles interactions with the database
│
├── tests/                          # Unit and integration tests for the system
│   ├── __init__.py                 # Indicates that this directory is a Python package
│   ├── test_app.py                 # Tests for the presentation layer; ensures UI functions correctly
│   ├── test_core.py                # Tests for the business logic; verifies rules and processes execute as expected 
│   └── test_data.py                # Tests for the data access layer; ensures database interactions are correct 
│
├── docker-compose.yml              # File to define and run Docker containers; simplifies deployment of the environment 
├── Dockerfile                      # File to define how to build the Docker image for the project 
├── LICENSE                         # File that defines the MIT license under which the project is distributed 
├── README.md                       # Project documentation; includes information on installation, usage, and contributions 
└── requirements.txt                # Dependencies needed to run the project; specifies required packages 
```
