import os


BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'mysql://root:zfds1245@127.0.0.1:3306/jump_to_flask'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev"
