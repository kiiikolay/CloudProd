import os
from dotenv import load_dotenv, dotenv_values, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

API = os.getenv("API_KEY")
DIR_PATH = os.getenv("DIR_PATH")
DISK_PATH = os.getenv("DISK_PATH")
URL = os.getenv("URL")
LOG_FILE = os.getenv("LOG_FILE")
