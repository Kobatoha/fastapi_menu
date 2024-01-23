from dotenv import load_dotenv
import os

load_dotenv()

user = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
port = os.getenv("DB_PORT")

DB_URL = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
