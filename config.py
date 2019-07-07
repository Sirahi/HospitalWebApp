class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital.db'
    SECRET_KEY = 'hospital'
    SQLALCHEMY_TRACK_MODIFICATIONS = False