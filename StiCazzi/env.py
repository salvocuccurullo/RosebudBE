import os

MONGO_API_URL = os.environ.get('MONGO_API_URL', '')
MONGO_API_USER = os.environ.get('COVER_API_USER', '')
MONGO_API_PWD = os.environ.get('COVER_API_PW', '')
MONGO_SERVER_CERTIFICATE = os.environ.get('MONGO_SERVER_CERTIFICATE')
MAX_FILE_SIZE = os.environ.get('UPLOAD_MAX_SIZE', 512000)

