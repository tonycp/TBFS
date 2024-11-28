import logging, logging.handlers as handlers
from dotenv import load_dotenv
from business_logic.commands import cli

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


def main():
    load_dotenv()

    logging.info("Starting the client...")

    try:
        cli()
    except KeyboardInterrupt as e:
        logging.info("KeyboardInterrupt")
    except Exception as e:
        logging.error(e)

    logging.info("Closing the client...")
