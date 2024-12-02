import logging, logging.handlers as handlers
import os
from dotenv import load_dotenv
from business_logic.commands import cli, set_client
from business_logic.clients import FileClient

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
    
    config={
            "protocol": os.getenv("PROTOCOL", "tcp"),
            "host": os.getenv("HOST", "localhost"),
            "port": int(os.getenv("PORT", 5555)),
        }
    
    set_client(
        FileClient(f"{config['protocol']}://{config['host']}:{config['port']}")
    )
    try:
        cli()
    except KeyboardInterrupt as e:
        logging.info("KeyboardInterrupt")
    except Exception as e:
        logging.error(e)
