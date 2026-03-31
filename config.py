import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    MYSQL_HOST     = os.getenv('MYSQLHOST',     'ud6gv3.h.filess.io')
    MYSQL_PORT     = int(os.getenv('MYSQLPORT', 61002))
    MYSQL_USER     = os.getenv('MYSQLUSER',     'Brainboost_runeventto')
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD', 'e6d943bcd85339a3c0e49ba6bbbfa1ef9f881310')
    MYSQL_DATABASE = os.getenv('MYSQLDATABASE', 'Brainboost_runeventto')
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





