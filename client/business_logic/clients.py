import zmq, json
from typing import Optional

__all__ = ["FileClient"]

_commands = {
    # Create, Update, Delete, Get, GetAll
    "add": {"command_name": "Create"},
    "delete": {"command_name": "Delete"},
    "list": {"command_name": "GetAll"},
    "add_tags": {"command_name": "Create"},
    "delete_tags": {"command_name": "Delete"},
}


class FileClient:
    def __init__(self, server_url: str) -> None:
        self.server_url = server_url
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.server_url)

    def send_multipart_message(
        self, command: str, data: dict[str, Optional[str]]
    ) -> str:
        """Send a multipart message to the server."""
        message = json.dumps(data).encode("utf-8")

        if command not in _commands:
            raise ValueError(f"Unknown command: {command}")

        command_message = json.dumps(_commands[command]).encode("utf-8")

        self.socket.send_multipart([command_message, message])
        response = self.socket.recv_multipart()
        return response[1].decode("utf-8")
