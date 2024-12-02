import click
import logging
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
    """Client for managing files and tags in the distributed file system."""
    pass


@cli.command()
@click.option(
    "--files",
    "-f",
    multiple=True,
    required=True,
    help="List of files to add.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="List of tags for the files.",
)
def add(files: List[str], tags: List[str]) -> None:
    """Copy one or more files to the system and register them with the tags contained in TAG_LIST."""
    for file in files:
        try:
            logging.info(f"Processing file {file}")
            with open(file, "rb") as f:
                file_data = f.read()
                _send_data("add", files=[file_data], tags=tags)
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Tag query to delete files.",
)
def delete(tag_query: str) -> None:
    """Delete all files that match the TAG_QUERY."""
    _send_data("delete", tag_query=tag_query)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=False,
    help="Tag query to list files.",
)
def list(tag_query: str) -> None:
    """List the name and tags of all files that match the TAG_QUERY."""
    _send_data("list", tag_query=tag_query)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Tag query to add new tags.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Tags to add to the files.",
)
def add_tags(tag_query: str, tags: List[str]) -> None:
    """Add the tags contained in TAG_LIST to all files that match the TAG_QUERY."""
    _send_data("add_tags", tag_query=tag_query, tags=tags)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    required=True,
    help="Tag query to delete.",
)
@click.option(
    "--tags",
    "-t",
    multiple=True,
    required=True,
    help="Tags to remove from the files.",
)
def delete_tags(tag_query: str, tags: List[str]) -> None:
    """Delete the tags contained in TAG_LIST from all files that match the TAG_QUERY."""
    _send_data("delete_tags", tag_query=tag_query, tags=tags)
