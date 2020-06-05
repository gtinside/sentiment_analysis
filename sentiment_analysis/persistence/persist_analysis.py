from sentiment_analysis.common.logger.log_util import logging_config
import logging
from logging.config import dictConfig
dictConfig(logging_config)

logger = logging.getLogger(__name__)


class AnalysisPersistence:
    def __init__(self, redis_conn):
        self._r = redis_conn

    def increment_counter(self, category):
        """
        :param category: The category for which counter is being maintained and incremented
        :return: None
        """
        if self._r.get(category) is None:
            self._r.set(category, 0)
        self._r.incr(category)
        logging.info(self._r.get(category))

    def get_counter(self, category):
        """
        :param category: The category for which counter is being maintained and incremented
        :return: counter value
        """
        if self._r.get(category) is None:
            self._r.set(category, 0)
        return self._r.get(category)
