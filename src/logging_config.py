import logging


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging() -> None:
    project_logger = logging.getLogger("src")
    project_logger.setLevel(logging.INFO)

    if project_logger.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    project_logger.addHandler(handler)
    project_logger.propagate = False
