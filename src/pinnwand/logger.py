import logging

LoggerClass = logging.getLoggerClass()


def setup_logging():
    """Sets up basic log levels & formats."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )


def get_logger(name: str) -> LoggerClass:
    return logging.getLogger(name)
