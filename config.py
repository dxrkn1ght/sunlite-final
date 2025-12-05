import os
from dotenv import load_dotenv

# .env faylini o‘qish
load_dotenv()

# Telegram token
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError('Please set TOKEN in .env')

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./sunlite.db')

# Admin va owner
ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS','').split(',') if x.strip()]
OWNER_CHAT = int(os.getenv('OWNER_CHAT') or (ADMIN_IDS[0] if ADMIN_IDS else 0))

# Top-up limits
MIN_TOPUP = int(os.getenv('MIN_TOPUP') or 10000)
MAX_TOPUP = int(os.getenv('MAX_TOPUP') or 1000000)
