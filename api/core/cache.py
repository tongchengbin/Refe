import pickle

import redis
from flask import current_app, g


class LocalRedis(redis.StrictRedis):

    def set(self, name, value,
            ex=None, px=None, nx=False, xx=False, keepttl=False, pick=False):
        if pick:
            value = pickle.dumps(value)
        return super(LocalRedis, self).set(name, value, ex, px, nx, xx, keepttl=keepttl)

    def get(self, name, pick=False):
        """
        Return the value at key ``name``, or None if the key doesn't exist
        """
        if pick:
            return pickle.loads(self.execute_command('GET', name))
        return self.execute_command('GET', name)


def get_cache():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "cache" not in g:
        g.cache = LocalRedis(**current_app.config["CACHE_CONFIG"])
    return g.cache
