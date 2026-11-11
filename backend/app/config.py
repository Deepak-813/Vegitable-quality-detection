import os
import re
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

_database_url = os.getenv('DATABASE_URL')
if _database_url is None:
    _database_path = os.path.join(BASE_DIR, 'vegetable_quality.db')
    DATABASE_URL = f"sqlite:///{os.path.abspath(_database_path).replace('\\', '/')}"
elif _database_url.startswith('sqlite:///'):
    sqlite_path = _database_url[len('sqlite:///'):]
    if not sqlite_path.startswith('/') and not re.match(r'^[A-Za-z]:/', sqlite_path):
        sqlite_path = os.path.join(BASE_DIR, sqlite_path)
    DATABASE_URL = f"sqlite:///{os.path.abspath(sqlite_path).replace('\\', '/')}"
else:
    DATABASE_URL = _database_url

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '60'))
UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
REPORT_DIR = os.getenv('REPORT_DIR', 'reports')
MODEL_PATH = os.getenv('MODEL_PATH', 'trained_model/vegetable_quality_model.keras')
