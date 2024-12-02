import logging, logging.handlers as handlers
import os
from dotenv import load_dotenv
from business_logic.commands import cli, set_client
from client.business_logic.clients import FileClient

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
    load_dotenv()
    set_client(
        FileClient(f"{os.getenv("PROTOCOL", "tcp")}://{os.getenv("HOST", "localhost")}:{int(os.getenv("PORT", 5555))}")
    )
    try:
        cli()
    except KeyboardInterrupt as e:
        logging.info("KeyboardInterrupt")
    except Exception as e:
        logging.error(e)
