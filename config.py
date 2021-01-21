import os
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
# Database URI parameters
DATABASE_MANAGEMENT_SYSTEM = 'postgres'
USER_NAME = 'ahmed'
IP_ADDRESS = 'localhost'
PORT_NUMBER = '5432'
DATABASE_NAME = 'fyyur'

class Config():
    DEBUG = False
    SECRET_KEY = os.urandom(32)
    # TODO IMPLEMENT DATABASE URL
    # [DONE]
    SQLALCHEMY_DATABASE_URI = f'{DATABASE_MANAGEMENT_SYSTEM}://{USER_NAME}@{IP_ADDRESS}:{PORT_NUMBER}/{DATABASE_NAME}'
class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
class ProductionConfig(Config):
    DevelopmentConfig = False





