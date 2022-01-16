from os import environ
from dotenv import load_dotenv

load_dotenv()
DB_NAME = "API.db"
SQLALCHEMY_DATABASE_URI = f'sqlite:///'+DB_NAME
SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQL_TRACK')
SECRET_KEY = environ.get('SECRET_KEY')
S3_SECRET_KEY = environ.get('S3_SECRET_KEY')
S3_ACCESS_KEY = environ.get('S3_ACCESS_KEY')
S3_REGION = environ.get('S3_REGION')
S3_BUCKET = environ.get('S3_BUCKET')
S3_BUCKET_URL = 'https://{}.s3.amazonaws.com/'.format(S3_BUCKET)
ADMIN_EMAIL = environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD')
