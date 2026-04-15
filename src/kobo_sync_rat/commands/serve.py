from logging import DEBUG
from logging import basicConfig as basic_config
from logging import getLogger as get_logger

import uvicorn
from typer import Typer

from kobo_sync_rat.app import app as fastapi_app

app = Typer()

logger = get_logger(__name__)


@app.command()
def serve(
    host: str = "0.0.0.0",
    port: int = 8080,
):
    # Configure logging
    default_format = "%(asctime)s - %(levelname)8s - %(message)s"

    basic_config(level=DEBUG, format=default_format)

    uvicorn_log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": default_format,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": '%(asctime)s - %(levelname)8s - %(client_addr)s - "%(request_line)s" %(status_code)s',
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    logger.info("Serving kobo_sync at %d", port)

    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        access_log=False,
        use_colors=False,
        log_config=uvicorn_log_config,
    )


if __name__ == "__main__":
    app()
