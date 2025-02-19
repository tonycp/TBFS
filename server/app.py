import logging, logging.handlers as handlers
import socket

from data.const import HOST_KEY
from logic.configurable import Configurable
from servers import ChordServer
from dist.chord_controlers import set_chord_node

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        handlers.TimedRotatingFileHandler(
            filename="logs\\app.log", when="M", interval=10
        ),
    ],
)


if __name__ == "__main__":
    ip = str(socket.gethostbyname(socket.gethostname()))
    config = Configurable({HOST_KEY: ip})
    server = ChordServer(config)
    set_chord_node(server)
    try:
        logging.info(f"Starting the server in {ip}...")
        server.run()
    except KeyboardInterrupt as e:
        logging.warning("Stopping the server...")
    except Exception as e:
        logging.error(f"Error starting the server: {e}")
    logging.info("Server stopped.")
