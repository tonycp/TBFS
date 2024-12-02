import logging, logging.handlers as handlers
from business_logic import start_listening

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
    try:
        logging.info("Starting the server...")
        start_listening()
    except KeyboardInterrupt as e:
        logging.warning("Stopping the server...")
    except Exception as e:
        logging.error(f"Error starting the server: {e}")
    logging.info("Server stopped.")
