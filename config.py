import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    MYSQL_HOST     = os.getenv('MYSQL_HOST',     'localhost')
    MYSQL_PORT     = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER     = os.getenv('MYSQL_USER',     'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'priya@2004')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'brainboost_v2')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{quote_plus(MYSQL_PASSWORD)}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY               = os.getenv('SECRET_KEY',     'abc123')
    JWT_SECRET_KEY           = os.getenv('JWT_SECRET_KEY', 'xyz456')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    UPLOAD_FOLDER       = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH  = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS  = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
