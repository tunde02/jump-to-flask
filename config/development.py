from config.default import *


SQLALCHEMY_DATABASE_URI = 'mysql://root:PASSWORD@127.0.0.1:3306/DATABASE_NAME'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = 'GOOGLE_ID@gmail.com'
MAIL_PASSWORD = 'GOOGLE_PASSWORD'
MAIL_DEFAULT_SENDER = 'GOOGLE_ID@gmail.com'
MAIL_USE_TLS = False
MAIL_USE_SSL = True

SHOULD_CHANGED_PASSWORD = '5e77859f'

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
UPLOAD_FOLDER = './app/static/images'