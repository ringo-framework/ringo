"""Caching of items."""
import logging
import datetime
from pyramid.events import NewRequest

log = logging.getLogger(__name__)


class Cache(object):

    """Cache container to store elements"""

    def __init__(self, validity_period=0):
        """Intitialises a new Cache container. You can set the the
        validity_period in seconds. This parameter will ensure that the
        cache will stay available at least the amount of seconds defined
        in validity_period even if the clear method of the cache has
        been called earlier. If the no validity_period is provided. The
        cache will be cleared on every call of the clear method.

        :validity_period: Number of seconds the cache will be available,
        before it can be cleared.

        """
        self._created = datetime.datetime.now()
        self._validity_period = validity_period
        self._data = {}
        log.debug("New cache created")

    def clear(self, force=False):
        """Will clear cache if it is older then the the validity_period
        of the cache. If force is true the cache will be cleared even if
        the validity_period has not been exeeded.

        :force: Force clearing the cache. Defaults to False
        :returns: None

        """
        td = (datetime.datetime.now() - self._created)
        if force or td.seconds > self._validity_period:
            self._data = {}

    def set(self, key, value):
        """Will set a new value for the given key in the cache. If there
        is already a value stored then the value will be overwritten.

        :key: String idenditifier for the cached value
        :value: The value to cache
        :returns: None

        """
        self._data[key] = value

    def get(self, key):
        """Will return the cached value for the key. If there is no
        value stored for the given key None will be returned.

        :key: String idenditifier for the cached value
        :returns: The cached value

        """
        return self._data.get(key)


def setup_cache(config):
    config.add_subscriber(init_cache, NewRequest)


def init_cache(event):
    request = event.request

    if hasattr(request, "cache_item_list"):
        request.cache_item_list.clear()
    else:
        request.cache_item_list = Cache()

    if hasattr(request, "cache_item_modul"):
        request.cache_item_modul.clear()
    else:
        request.cache_item_modul = Cache()
    CACHE_TABLE_CONFIG.clear()
    CACHE_FORM_CONFIG.clear()
    CACHE_MODULES.clear()

CACHE_MODULES = Cache()
# GLOBAL CACHE INSTANCES
CACHE_TABLE_CONFIG = Cache()
CACHE_FORM_CONFIG = Cache()
CACHE_MISC = Cache()
