import zmq, json, os
from typing import Optional
from datetime import datetime, timezone


__all__ = ["FileClient"]

_commands = {
    # Create, Update, Delete, Get, GetAll
    "add": {
        "command_name": "Create",
        "function": "add",
        "dataset": ["file", "tag_list"],
    },
    "delete": {
        "command_name": "Delete",
        "function": "delete",
        "dataset": ["tag_query"],
    },
    "list": {
        "command_name": "GetAll",
        "function": "list",
        "dataset": ["tag_query"],
    },
    "add_tags": {
        "command_name": "Create",
        "function": "add_tags",
        "dataset": ["tag_query", "tag_list"],
    },
    "delete_tags": {
        "command_name": "Delete",
        "function": "delete_tags",
        "dataset": ["tag_query", "tag_list"],
    },
}


class FileClient:
    def __init__(self, server_url: str) -> None:
        self.server_url = server_url
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.server_url)

    def get_file_info(self, file_path: str, user_id: int = 1) -> dict:
        """Get file information."""
        if not os.path.isfile(file_path):
            raise ValueError(f"File not found: {file_path}")

        name = os.path.basename(file_path)
        creation_time = os.path.getctime(file_path)
        update_time = os.path.getmtime(file_path)

        file_info = {
            "name": os.path.splitext(name)[0],
            "file_type": os.path.splitext(name)[1][1:],
            "size": os.path.getsize(file_path),
            "user_id": user_id,
            "creation_date": datetime.fromtimestamp(
                creation_time, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "update_date": datetime.fromtimestamp(
                update_time, tz=timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "content": False,
        }

        return file_info

    def send_multipart_message(
        self, command: str, content, data: dict[str, Optional[str]]
    ) -> str:
        """Send a multipart message to the server."""
        message = json.dumps(data).encode("utf-8")

        if command not in _commands:
            raise ValueError(f"Unknown command: {command}")

        header = _commands[command]
        command_message = json.dumps(header).encode("utf-8")

        parts = [command_message, message]

        if content is not None:
            parts.append(content)

        self.socket.send_multipart(parts)
        response = self.socket.recv_multipart()
        return response[0].decode("utf-8")
