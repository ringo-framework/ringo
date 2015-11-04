import os
import md5
from dogpile.cache.region import make_region

# Cache initialisation
########################

# dogpile cache regions.
regions = {}


def init_cache(cachedir, regions):

    if regions is None:
        regions = []

    if not os.path.exists(cachedir):
        #raw_input("Will create datafiles in %r.\n"
        #            "To reset the cache + database, delete this
        #            directory.\n" "Press enter to continue.\n" % root)
        os.makedirs(cachedir)

    for region in regions:
        name = region[0]
        time = int(region[1])
        create_region(cachedir, name, time)

    # optional; call invalidate() on the region
    # once created so that all data is fresh when
    # the app is restarted.  Good for development,
    # on a production system needs to be used carefully
    invalidate_cache()


def md5_key_mangler(key):
    """Receive cache keys as long concatenated strings;
    distill them into an md5 hash.

    """
    return md5.md5(key).hexdigest()


def create_region(cachedir, name, time):
    regions[name] = make_region(
                # the "dbm" backend needs
                # string-encoded keys
                key_mangler=md5_key_mangler
            ).configure(
            # using type 'file' to illustrate
            # serialized persistence.  Normally
            # memcached or similar is a better choice
            # for caching.
            'dogpile.cache.dbm',
            expiration_time=time,
            arguments={
                "filename": os.path.join(cachedir, "cache.dbm")
            }
        )


def invalidate_cache(cache_regions=[]):
    for key in regions.keys():
        if len(cache_regions) == 0 or key in cache_regions:
            regions[key].invalidate()


