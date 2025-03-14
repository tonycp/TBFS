import debugpy, socket, logging, logging.handlers as handlers

from data.const import HOST_KEY
from logic.configurable import Configurable
from dist import ChordLeader, set_chord_server

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
    debugpy.listen(("0.0.0.0", 5678))
    logging.info("listening for debugger in port: 5678...")

    ip = str(socket.gethostbyname(socket.gethostname()))
    config = Configurable({HOST_KEY: ip})
    server = ChordLeader(config)
    set_chord_server(server)
    try:
        logging.info(f"Starting the server in {ip}...")
        server.run()
    except KeyboardInterrupt as e:
        logging.warning("Stopping the server...")
    except Exception as e:
        logging.error(f"Error starting the server: {e}")
    logging.info("Server stopped.")
