from bulkcopylib.url_cache import UrlCache

def make_gitlab_url_cache(cache_dir):
    return UrlCache(cache_dir)
