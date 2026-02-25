import os
from dotenv import load_dotenv

load_dotenv()

class SuperAdminCreds:

    USERNAME: str = os.getenv("SUPER_ADMIN_USERNAME")
    PASSWORD: str = os.getenv("SUPER_ADMIN_PASSWORD")