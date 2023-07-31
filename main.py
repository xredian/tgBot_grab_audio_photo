from telegram import Bot
from sys import exit as sys_exit
from bot import AudioPhotoBot
from env_handler import Env
from logger import init_logger


if __name__ == '__main__':
    env = Env()
    tg_bot = Bot(token=env.token)
    if not env.token:
        sys_exit("Error: no token provided")

    init_logger()
    bot = AudioPhotoBot(env, tg_bot)
    bot.start_polling()
