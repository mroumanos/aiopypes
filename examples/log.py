import logging


def get_logger(name: str,
               level: str = "INFO"):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logging.basicConfig(format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        return logger