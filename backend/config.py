import os
from dotenv import load_dotenv

load_dotenv()

FOOTBALL_API_KEY = os.getenv('FOOTBALL_API_KEY', '')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
PORT = int(os.getenv('PORT', 5000))