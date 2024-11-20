import logging, os
from dotenv import load_dotenv
from ..business_logic import start_listening, set_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)


def main():
    load_dotenv()
    set_config(
        config={
            "protocol": os.getenv("PROTOCOL", "tcp"),
            "host": os.getenv("HOST", "localhost"),
            "port": int(os.getenv("PORT", 5555)),
        }
    )

    try:
        logging.info("Starting the server...")
        start_listening()
    except KeyboardInterrupt as e:
        logging.warning("Stopping the server...")
    except Exception as e:
        logging.error(f"Error starting the server: {e}")
    logging.info("Server stopped.")
