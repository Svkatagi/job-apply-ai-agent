# config/settings.py

# Import necessary libraries
from dotenv import load_dotenv  # For loading environment variables from .env file # type: ignore
import os  # For accessing environment variables

# Load all variables defined inside the .env file
load_dotenv()

# Email and password used for login or account creation on job portals
EMAIL_FOR_LOGIN = os.getenv("EMAIL_FOR_LOGIN")
PASSWORD_FOR_LOGIN = os.getenv("PASSWORD_FOR_LOGIN")

# API key for accessing Google's Gemini AI models
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
