import os
from urllib.parse import quote_plus

class Config:
    # URL encode the password
    encoded_password = quote_plus(os.getenv('DB_PASSWORD'))
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DB_USER')}:{encoded_password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('JWT_SECRET')
    API_KEY = os.getenv('API_KEY')
