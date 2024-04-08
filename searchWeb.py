import os
import ssl
import pickle

CACHE_FILE = "cache.pkl"

def readCache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def writeCache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)
