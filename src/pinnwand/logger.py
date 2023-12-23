import logging

LoggerClass = logging.getLoggerClass()


def get_logger(name: str) -> LoggerClass:
    logger = logging.getLogger(name)

    for handler in logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)

    return logger
