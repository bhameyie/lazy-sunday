import os

MONGO_URI = 'mongodb://localhost'
HLS_DIR = os.path.join(os.getcwd(), 'hls_stash')
TOOLS_DIR = os.path.join(os.getcwd(), 'tools')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'mp4_stash')
SECRET_KEY = 'dev'
MONGO_DB = 'flixdb'
DEBUG = True

IN_PROD = os.environ.get("MOVIEFRIDAY_INPROD", default=False)

if IN_PROD:
    MONGO_DB = os.environ.get("MOVIEFRIDAY_MONGO_DB", default=None)
    if not MONGO_DB:
        raise ValueError("No secret key set for Flask application")

    MONGO_URI = os.environ.get("MOVIEFRIDAY_MONGO_URI", default=None)
    if not MONGO_URI:
        raise ValueError("No secret key set for Flask application")

    SECRET_KEY = os.environ.get("MOVIEFRIDAY_SECRET_KEY", default=None)
    if not SECRET_KEY:
        raise ValueError("No secret key set for Flask application")
