import zmq, json, os
from typing import Optional
from datetime import datetime, timezone


__all__ = ["FileClient"]

_commands = {
    # Create, Update, Delete, Get, GetAll
    "add": {
        "command_name": "Create",
        "function": "add",
        "dataset": ["file", "tags"],
    },
    "delete": {
        "command_name": "Delete",
        "function": "delete",
        "dataset": ["tag_query"],
    },
    "list": {
        "command_name": "GetAll",
        "function": "list_files",
        "dataset": ["tag_query"],
    },
    "add_tags": {
        "command_name": "Create",
        "function": "add_tags",
        "dataset": ["tag_query", "tags"],
    },
    "delete_tags": {
        "command_name": "Delete",
        "function": "delete_tags",
        "dataset": ["tag_query", "tags"],
    },
    "get_user_id": {
        "command_name": "Get",
        "function": "get_user_id",
        "dataset": ["user_name"],
    },
}


class FileClient:
    def __init__(self, server_url: str) -> None:
        self.server_url = server_url
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.server_url)
        self.user_id = self.get_user_id()

    def get_user_id(self) -> int:
        return int(self.send_multipart_message("get_user_id", {}))

    def get_file_info(self, file_path: str) -> dict:
        """Get file information."""
        absolute_path = os.path.abspath(file_path)

        if not os.path.exists(absolute_path):
            raise ValueError(f"File not found: {absolute_path}")

        name = os.path.basename(absolute_path)
        creation_time = os.path.getctime(absolute_path)
        update_time = os.path.getmtime(absolute_path)
        content = open(absolute_path, "rb").read()

        file_info = {
            "name": os.path.splitext(name)[0],
            "file_type": os.path.splitext(name)[1][1:],
            "size": os.path.getsize(absolute_path),
            "user_id": self.user_id,
            "creation_date": datetime.fromtimestamp(
                creation_time, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "update_date": datetime.fromtimestamp(
                update_time, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "content": content.decode("utf-8"),
        }

        return file_info

    def send_multipart_message(
        self, command: str, data: dict[str, Optional[str]]
    ) -> str:
        """Send a multipart message to the server."""
        message = json.dumps(data).encode("utf-8")

        if command not in _commands:
            raise ValueError(f"Unknown command: {command}")

        header = _commands[command]
        command_message = json.dumps(header).encode("utf-8")

        parts = [command_message, message]

        self.socket.send_multipart(parts)
        response = self.socket.recv_multipart()
        return response[0].decode("utf-8")
