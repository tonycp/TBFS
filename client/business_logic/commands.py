import click, logging, os
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
from .clients import FileClient

__all__ = [
    "add",
    "delete",
    "list",
    "add_tags",
    "delete_tags",
    "set_config",
    "check_default",
]

_socket_config: Dict[str, Optional[Union[str, int]]] = {}


def check_default(
    config: Dict[str, Optional[Union[str, int]]] = {}
) -> Dict[str, Optional[Union[str, int]]]:
    """Check and set default values for the configuration."""
    load_dotenv()
    default_config: Dict[str, Optional[Union[str, int]]] = {
        "protocol": os.getenv("PROTOCOL", "tcp"),
        "host": os.getenv("HOST", "localhost"),
        "port": int(os.getenv("PORT", 5555)),
    }

    for key, value in default_config.items():
        config.setdefault(key, value)
    return config


def set_config(config: Dict[str, Optional[Any]]) -> None:
    """Set the configuration for the server."""
    global _socket_config
    _socket_config.update(config)


_client: FileClient = None


def check_client() -> None:
    global _client
    if _client is not None:
        return
    _client = FileClient(
        f"{_socket_config['protocol']}://{_socket_config['host']}:{_socket_config['port']}"
    )


def _send_data(command: str, **kwargs) -> None:
    """Send a message to the default client."""
    try:
        logging.info("Executing command: %s", command)
        response = _client.send_message(command, kwargs)
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
@click.argument("tags", nargs=-1, type=str)
def add(files: List[str], tags: List[str]) -> None:
    """Copy one or more files to the system and register them with the tags contained in TAG_LIST."""
    for file in files:
        try:
            file_data = _client.get_file_info(file)
            _send_data("add", file=file_data, tags=tags)
        except Exception as e:
            logging.error(f"Error processing file {file}: {e}")


@cli.command()
@click.argument("tag_query", nargs=-1, type=str)
def delete(tag_query: List[str]) -> None:
    """Delete all files that match the TAG_QUERY."""
    _send_data("delete", tag_query=tag_query)


@cli.command()
@click.argument("tag_query", nargs=-1, type=str)
def list(tag_query: List[str]) -> None:
    """List the name and tags of all files that match the TAG_QUERY."""
    _send_data("list", tag_query=tag_query)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    multiple=True,
    required=True,
    help="Tag query to add new tags.",
)
@click.argument("tags", nargs=-1, type=str)
def add_tags(tag_query: str, tags: List[str]) -> None:
    """Add the tags contained in TAG_LIST to all files that match the TAG_QUERY."""
    _send_data("add_tags", tag_query=tag_query, tags=tags)


@cli.command()
@click.option(
    "--tag-query",
    "-q",
    type=str,
    multiple=True,
    required=True,
    help="Tag query to delete.",
)
@click.argument("tags", nargs=-1, type=str)
def delete_tags(tag_query: str, tags: List[str]) -> None:
    """Delete the tags contained in TAG_LIST from all files that match the TAG_QUERY."""
    _send_data("delete_tags", tag_query=tag_query, tags=tags)
