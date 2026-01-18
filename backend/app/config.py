import os
from dotenv import load_dotenv  
load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

SMTP_SERVER =""
# os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = ""
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
