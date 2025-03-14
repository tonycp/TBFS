import debugpy, logging, logging.handlers as handlers
from logic.commands import check_client, cli, check_default, set_config

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

    config = check_default()
    set_config(config)
    check_client()
    try:
        cli()
    except KeyboardInterrupt as e:
        logging.info("KeyboardInterrupt")
    except Exception as e:
        logging.error(e)
