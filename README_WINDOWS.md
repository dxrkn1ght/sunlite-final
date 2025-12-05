SunLite - Windows setup & run guide (local / dev)

1. Install Python 3.10+ from https://www.python.org/downloads/
2. Download and extract the ZIP to a folder, e.g. C:\projects\SunLite
3. Open Command Prompt and change dir:
   cd C:\projects\SunLite
4. Create virtualenv and activate:
   python -m venv venv
   venv\Scripts\activate
5. Install dependencies:
   pip install -r requirements.txt
6. Copy .env.example to .env and edit values (TOKEN is required):
   copy .env.example .env
   (then open .env and put your BOT token)
7. Initialize database (creates SQLite DB or connect to Postgres if set):
   python -m sunlite_utils.init_db
8. Run bot:
   python main.py
9. Logs output will appear in console.

Notes:
- For production use PostgreSQL (set DATABASE_URL to postgresql+asyncpg://...)
- For Fly.io deploy use Dockerfile and fly.toml (provided).
