import io
import logging
import sys


def setup_collector_logger(namespace):
    """
    Configures a specific logger for your application that captures logs only in memory.

    Args:
        namespace (str): Logger namespace, used to differentiate from other modules.

    Returns:
        tuple: (logger, memory_stream) where memory_stream contains the logs in memory.
    """
    logger = logging.getLogger(namespace)
    logger.setLevel(logging.INFO)

    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    memory_stream = io.StringIO()
    memory_handler = logging.StreamHandler(memory_stream)
    memory_handler.setFormatter(log_format)
    logger.addHandler(memory_handler)

    logger.propagate = True

    return logger, memory_stream
