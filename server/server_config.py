class Config(object):
    CSRF_ENABLED = True
    SECRET_KEY = "\xbf\xf0\xdf\x0c\xac0\xeb\xf1\x118q\xfcWcu\xc6\xa4-Ot=\xc9+\x1f"
    COMPRESS_MIMETYPES = [
        "application/json",
        "application/javascript",
        "text/json",
        "text/javascript",
        "text/css",
        "text/html",
        "text/plain",
        "text/xml"]

class ConfigProduction(Config):
    DEBUG = False
    COMPRESS_DEBUG = False

class ConfigDevelopment(Config):
    DEBUG = True
    COMPRESS_DEBUG = True

