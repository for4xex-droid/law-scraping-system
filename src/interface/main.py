import os
import sys

# Ensure root path is in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from src.core.logging import get_logger, setup_logging
from src.core.logic import BusinessLogic
from src.core.result import Err, Ok


def main() -> None:
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Starting Application...")
    result = BusinessLogic.process("Hello AI")

    match result:
        case Ok(data):
            logger.info(f"Success: {data.message}")
        case Err(e):
            logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
