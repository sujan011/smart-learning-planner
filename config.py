import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-jwt-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    uri = os.environ.get('DATABASE_URL', 'sqlite:///planner.db')
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = uri