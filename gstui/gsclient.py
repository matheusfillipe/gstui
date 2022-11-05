import os
from pathlib import Path
from threading import Thread
from typing import List

from diskcache import Cache
from google.cloud import storage
from tqdm.std import tqdm

GsClient = storage.Client


def get_cache_path() -> str:
    """Get cache path in different OS's"""
    if os.name == "nt":
        path = Path(os.getenv("LOCALAPPDATA")) / "gstui" / "cache"
    path = Path.home() / ".cache" / "gstui"
    return str(path)


class ThreadedCachedClient:
    """
    Cached client. Spawns a thread with the google client.
    In case something is not cached, it will join the thread and block.
    """

    init_thread: Thread
    cache_path = get_cache_path()

    def spawn(self, cls, *args, **kwargs):
        # spawn init in thread
        self.init_thread = Thread(
            target=cls.__init__,
            args=(self, *args),
            kwargs=kwargs)
        self.init_thread.start()

    @classmethod
    def diskcache(cls, func):
        """Decorator to cache function results to disk"""

        def wrapper(self, *args, **kwargs):
            if not isinstance(self, ThreadedCachedClient):
                raise TypeError(
                    "Decorator only works with ThreadedCachedClient")
            cache = Cache(cls.cache_path)
            key = func.__name__ + ":" + str(args) + str(kwargs)
            result = cache.get(key)
            if result is None:
                # Ensure init thread is finished otherwise join it
                if self.init_thread.is_alive():
                    self.init_thread.join()
                result = func(self, *args, **kwargs)
                cache.set(key, result)
            else:
                # Warm up cache in thread
                Thread(target=func, args=(self, *args), kwargs=kwargs).start()
            return result

        return wrapper


class CachedClient(GsClient, ThreadedCachedClient):
    """Google cloud storage ThreadedCachedClient"""

    def __init__(self, *args, **kwargs):
        self.spawn(GsClient, *args, **kwargs)

    @ThreadedCachedClient.diskcache
    def list_buckets(self, *args, **kwargs) -> List[str]:
        return [bucket.name for bucket in super().list_buckets(*args, **kwargs)]

    @ThreadedCachedClient.diskcache
    def list_blobs(self, *args, **kwargs) -> List[str]:
        return [blob.name for blob in super().list_blobs(*args, **kwargs)]

    # TODO this should be responsability of the UI instead
    def download(self, blob, blob_name):
        destination_file_name = Path(blob_name).name
        if blob.size is not None:
            print(f"Downloading {blob.size/1024/1024:.2f} MB")
        with open(destination_file_name, "wb") as f:
            with tqdm.wrapattr(f, "write", total=blob.size) as file_obj:
                self.download_blob_to_file(blob, file_obj)
        print(f"Downloaded {blob_name}")