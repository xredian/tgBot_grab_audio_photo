import traceback
from typing import cast
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler)
from telegram.ext.callbackcontext import CallbackContext
from logger import log_msg
from db.db_handler import DataHandler


class AudioPhotoBot:

    def __init__(self, env, tg_bot):
        self.updater = Updater(env.token, use_context=True)
        self.dp = self.updater.dispatcher
        self.tg_bot = tg_bot
        self.data = DataHandler(env)
        self.env = env
        self.dp.add_handler(CommandHandler('start', self.start))
        self.dp.add_error_handler(self.error)

    def start_polling(self):
        """Start the bot"""
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hi, I can collect audio messages and photos with faces from groups"
            " or chats, just add me to your group/chat")

    @staticmethod
    def help(update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hey, you can add me to your group or chat to collect audio"
            " messages and photos with faces")

    @staticmethod
    def error(update: Update, context: CallbackContext):
        """Handling telegram errors"""
        tb_list = traceback.format_exception(
            None, context.error, cast(Exception, context.error).__traceback__
        )
        tb_string = "".join(tb_list)
        log_msg("warning", f"Update {update} caused error {context.error} with "
                           f"traceback {tb_string}")

