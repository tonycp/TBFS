import zmq, json, os, logging, socket, time
from typing import Any, Dict, Optional
from datetime import datetime, timezone


__all__ = ["FileClient"]

# Environment variable keys
HOST_ENV_KEY = "HOST"
PORT_ENV_KEY = "PORT"
MCAST_ADDR_ENV_KEY = "MCAST_ADDR"
DEFAULT_BROADCAST_PORT = 10002
WAIT_CHECK = 5

# Default values
PON_CALL = 5

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
    PON_CALL: {
        "command_name": "Chord",
        "function": "pon_call",
        "dataset": ["message"],
    },
}


class FileClient:
    def __init__(self, port) -> None:
        """Initialize the FileClient with the server's host and port."""
        self.port = port
        self.user_id = None
        self.server_ip = self._get_server_ip()

    def get_user_id(self) -> int:
        logging.info("Getting user id...")
        response = int(self._send_multipart_message("get_user_id", {}))
        logging.info("User id: %s", response)
        return response

    def get_file_info(self, file_path: str) -> dict:
        """Get file information."""
        absolute_path = os.path.abspath(file_path)
        logging.info("Getting file info: %s...", absolute_path)

        if not os.path.exists(absolute_path):
            raise ValueError(f"File not found: {absolute_path}")

        if self.user_id is None:
            self.user_id = self.get_user_id()
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

        logging.info("File info: %s", json.dumps(file_info))
        return file_info

    def send_message(self, command: str, data: Dict[str, Optional[str]]):
        if self.user_id is None:
            self.user_id = self.get_user_id()
        header = _commands[command]
        return self._socket_call(header, data)

    def _socket_call(
        self, server_ip, header: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        message = json.dumps({"header": header, "data": data})
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(WAIT_CHECK)
        port = self.port

        logging.info(f"Sending message to {server_ip}:{port} from chord reference")
        try:
            sock.connect((server_ip, port))
            sock.sendall(message.encode("utf-8"))
            response = sock.recv(1024)
            logging.info(f"Received response from {server_ip}:{port}: {response}")
            return json.loads(response.decode("utf-8"))
        except ConnectionRefusedError:
            logging.error(f"Connection refused by {server_ip}:{port}")
            return {"error": "Connection refused"}
        except socket.timeout:
            logging.error(
                f"Timeout occurred while communicating with {server_ip}:{port}"
            )
            return {"error": "Timeout"}
        except Exception as e:
            logging.error(
                f"An error occurred while communicating with {server_ip}:{port}: {e}"
            )
            return {"error": str(e)}
        finally:
            sock.close()

    def _get_server_ip(self) -> str:
        """Get the server IP either from the environment or via multicast."""
        server_ip = os.getenv(HOST_ENV_KEY, None)
        if not server_ip or not self._is_server_alive(server_ip):
            server_ip = self._send_multicast_request()
            os.environ[HOST_ENV_KEY] = server_ip
        return server_ip

    def _is_server_alive(self, server_ip: str) -> bool:
        """Check if the server is alive by sending a request to the ChordReference."""
        return self._ping_pong(server_ip)

    def _send_multicast_request(self) -> str:
        """Send a multicast request to discover the server IP."""
        multicast_ip = os.getenv(MCAST_ADDR_ENV_KEY, "224.0.0.1")
        port = DEFAULT_BROADCAST_PORT
        message = json.dumps({"request": "server_ip"}).encode("utf-8")

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
            sock.sendto(message, (multicast_ip, port))
            sock.settimeout(WAIT_CHECK)

            try:
                response, addr = sock.recvfrom(1024)
                logging.info(f"Received multicast response from {addr}: {response}")
                server_ip = json.loads(response.decode("utf-8")).get("server_ip")
                logging.info(f"Discovered server IP: {server_ip}")
                return server_ip
            except socket.timeout:
                raise RuntimeError("Failed to discover server IP via multicast")

    def _send_chord_message(
        self, server_ip, chord_data: int, data: str
    ) -> Dict[str, Any]:
        logging.info(f"Sending chord message with data: {data}")
        header = header_data(**_commands[chord_data])
        response = self._socket_call(server_ip, header, data)
        logging.info(f"Chord message sent with response: {response}")
        return response

    def _ping_pong(self, server_ip) -> bool:
        logging.info("Sending ping message")
        data = {"message": "Ping"}
        response = self._send_chord_message(server_ip, PON_CALL, data)
        logging.info("Ping message sent with response: Pong")
        return response.get("message") == "Pong"


def header_data(command_name: str, function: str, dataset: Dict[str, Any]) -> str:
    """Create a header string from the command name, function name, and dataset."""
    return {
        "command_name": command_name,
        "function": function,
        "dataset": dataset,
    }
