from os import environ
from pathlib import Path

from dotenv import load_dotenv


dotenv_file = Path(__file__).parent.parent.joinpath('.env')
load_dotenv(dotenv_file)

DISCORD_BOT_TOKEN = environ.get("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = environ.get("OPENAPI_API_KEY")