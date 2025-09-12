import logging
import sys


def setup_logger(
    name: str, level: int = logging.INFO, filename: str | None = None
) -> logging.Logger:
    """
    Sets up a logger that outputs to stdout or a file.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (e.g., logging.INFO, logging.DEBUG).
        filename (str, optional): The filename to log to. If None, logs to stdout.
    Returns:
        logging.Logger: The configured logger.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers (to avoid duplicate logs)
    if logger.hasHandlers():
        logger.handlers.clear()

    handler: logging.Handler
    if filename:
        # Create a file handler
        handler = logging.FileHandler(filename)
    else:
        # Create a handler that writes to stdout
        handler = logging.StreamHandler(sys.stdout)

    handler.setLevel(level)

    # Create a logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger


agent_logger = setup_logger("agent", level=logging.WARNING)
