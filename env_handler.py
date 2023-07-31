from dotenv import load_dotenv
from os import getenv, getcwd


class Env:
    def __init__(self, env_path: str = f".env") -> None:
        a = load_dotenv(env_path)
        if not a:
            raise FileExistsError("there is no .env file")

        self.token = getenv("TOKEN")

        self.db_host = getenv("DB_HOST")
        self.db_user = getenv("DB_USER")
        self.db_pass = getenv("DB_PASS")
        self.db_name = getenv("DB_NAME")
        self.db_engine = getenv("DB_ENGINE")
