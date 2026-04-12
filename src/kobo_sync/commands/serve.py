from logging import DEBUG
from logging import basicConfig as basic_config
from logging import getLogger as get_logger

import uvicorn
from typer import Typer

from kobo_sync.app import app as fastapi_app

app = Typer()

logger = get_logger(__name__)


@app.command()
def serve():
    # Configure logging
    basic_config(level=DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    host = "0.0.0.0"
    port = 6060

    logger.info("Serving kobo_sync at %d", port)

    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
    )


if __name__ == "__main__":
    app()
