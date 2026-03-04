import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-eecs3311-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///booking_platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False