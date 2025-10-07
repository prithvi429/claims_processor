"""Entry point for the claims_processor skeleton."""
import logging
from .utils.logging import setup_logging
from .config import load_config

logger = logging.getLogger(__name__)


def main():
    setup_logging()
    cfg = load_config()
    logger.info('claims_processor skeleton started')
    logger.debug('Loaded config: %s', cfg)


if __name__ == '__main__':
    main()
