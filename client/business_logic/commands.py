import click, logging
from typing import List, Optional
from .clients import FileClient

__all__ = ["add", "delete", "list", "add_tags", "delete_tags"]

_client = FileClient('tcp://localhost:5555')


def set_client(client: FileClient = FileClient('tcp://localhost:5555')) -> None:
    """Set the default client to send messages to."""
    global _client
    _client = client


def _send_data(command: str, **kwargs: Optional[str]) -> None:
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
@click.argument("files", nargs=-1, type=str)
@click.argument("tag_list", type=str)
def add(files: List[str], tag_list: str) -> None:
    """Copia uno o más ficheros hacia el sistema y los inscribe con las etiquetas contenidas en TAG_LIST."""
    _send_data("add", files=files, tag_list=tag_list)


@cli.command()
@click.argument("tag_query", type=str)
def delete(tag_query: str) -> None:
    """Elimina todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("delete", tag_query=tag_query)


@cli.command()
@click.argument("tag_query", type=str)
def list(tag_query: str) -> None:
    """Lista el nombre y las etiquetas de todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("list", tag_query=tag_query)


@cli.command()
@click.argument("tag_query", type=str)
@click.argument("tag_list", type=str)
def add_tags(tag_query: str, tag_list: str) -> None:
    """Añade las etiquetas contenidas en TAG_LIST a todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("add_tags", tag_query=tag_query, tag_list=tag_list)


@cli.command()
@click.argument("tag_query", type=str)
@click.argument("tag_list", type=str)
def delete_tags(tag_query: str, tag_list: str) -> None:
    """Elimina las etiquetas contenidas en TAG_LIST de todos los ficheros que cumplan con la consulta TAG_QUERY."""
    _send_data("delete_tags", tag_query=tag_query, tag_list=tag_list)
