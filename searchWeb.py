import os
import ssl
import pickle
import sys
import socket
import json
from urllib.parse import urlparse, quote

CACHE_FILE = "cache.pkl"

def readCache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)
    return {}

def writeCache(cache):
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(cache, f)

def makeHttpRequest(host, path, redirectCount=0, maxRedirects=5):
    try:
        context = ssl.create_default_context()
        with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host) as s:
            s.connect((host, 443))
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            s.sendall(request.encode())
            response = b''
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data
        responseStr = response.decode("utf-8", errors="ignore")
        responseLines = responseStr.split("\r\n")
        headers = responseLines[:responseLines.index('')]
        body = '\r\n'.join(responseLines[responseLines.index('')+1:])

        if responseLines[0].startswith("HTTP/1.1 3"):
            for line in headers:
                if line.startswith("Location:"):
                    newLocation = line.split(": ", 1)[1]
                    newLocation = newLocation.strip()
                    newHost = urlparse(newLocation).netloc
                    newPath = urlparse(newLocation).path
                    return makeHttpRequest(newHost, newPath, redirectCount + 1, maxRedirects)

        for line in headers:
            if line.lower().startswith("content-type:") and "application/json" in line.lower():
                json_data = json.loads(body)
                return json_data

        return body
    except Exception as e:
        return f"Error: {str(e)}"
