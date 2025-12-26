import logging
import sys


def setup_logging(level=logging.INFO) -> None:
    """
    Global logging configuration for the application.
    """

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 🔇 Silence noisy third-party libraries unless debugging
    logging.getLogger("httpx").setLevel(logging.WARNING)
