import click, logging
from typing import List
from .clients import FileClient

__all__ = ["add", "delete", "list", "add_tags", "delete_tags"]

_client = FileClient("tcp://localhost:5555")


def set_client(client: FileClient = FileClient("tcp://localhost:5555")) -> None:
    """Set the default client to send messages to."""
    global _client
    _client = client


def _send_data(command: str, **kwargs) -> None:
    """Send a message to the default client."""
    try:
        response = _client.send_multipart_message(command, kwargs)
        logging.info(response)
    except Exception as e:
        logging.error(e)


@click.group()
def cli() -> None:
    """Cliente para gestionar archivos y etiquetas en el sistema de ficheros distribuido."""
    pass


@cli.command()
@click.option(
    "--files",
    "-f",
    multiple=True,
    required=True,
    help="Lista de archivos a agregar.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Lista de etiquetas para los archivos.",
)
def add(files: List[str], tags: List[str]) -> None:
    """Copia uno o más ficheros hacia el sistema y los inscribe con las etiquetas contenidas en TAG_LIST."""
    _send_data("add", files=files, tag_list=tags)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Consulta de etiquetas para eliminar archivos.",
)
def delete(tag_query: str) -> None:
    """Elimina todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("delete", tag_query=tag_query)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=False,
    help="Consulta de etiquetas para listar archivos.",
)
def list(tag_query: str) -> None:
    """Lista el nombre y las etiquetas de todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("list", tag_query=tag_query)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Consulta de etiquetas para añadir nuevas.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Etiquetas a añadir a los archivos.",
)
def add_tags(tag_query: str, tags: List[str]) -> None:
    """Añade las etiquetas contenidas en TAG_LIST a todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("add_tags", tag_query=tag_query, tag_list=tags)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Consulta de etiquetas para eliminar.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Etiquetas a eliminar de los archivos.",
)
def delete_tags(tag_query: str, tags: List[str]) -> None:
    """Elimina las etiquetas contenidas en TAG_LIST de todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("delete_tags", tag_query=tag_query, tag_list=tags)
