"""Small, application-owned logging setup with no external handlers."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure concise local logging once at the application boundary."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

