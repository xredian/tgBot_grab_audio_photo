import os
import traceback
import cv2 as cv
import subprocess
from collections import defaultdict
import numpy as np
from typing import cast
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          PicklePersistence)
from telegram.ext.callbackcontext import CallbackContext
from logger import log_msg
from db.db_handler import DataHandler


class AudioPhotoBot:

    def __init__(self, env, tg_bot):
        persistence = PicklePersistence('./pickle')
        self.updater = Updater(env.token, use_context=True,
                               persistence=persistence)
        self.dp = self.updater.dispatcher
        self.tg_bot = tg_bot
        self.data = DataHandler(env)
        self.env = env
        self.file_num = 0
        self.photo_num = 0
        self.cur_dir = os.getcwd()
        self.uid_mes = defaultdict(list)
        self.audio_msgs = defaultdict()
        self.photo_path = f'{self.cur_dir}/photo'
        self.audio_path = f'{self.cur_dir}/audio'
        self.dp.add_handler(CommandHandler('start', self.start, run_async=True))
        self.dp.add_handler(
            MessageHandler(Filters.voice, self.audio_messages, run_async=True))
        self.dp.add_handler(
            MessageHandler(Filters.photo, self.photo, run_async=True))
        self.dp.add_error_handler(self.error)

    def start_polling(self):
        """Start the bot"""
        self.updater.start_polling()
        self.updater.idle()

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            "Hi, I can collect audio messages and photos with faces from groups"
            " or chats, just add me to your group/chat")
        for path in [self.photo_path, self.audio_path]:
            try:
                os.mkdir(path)
            except FileExistsError:
                log_msg('info', 'Paths already exist')

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

    def audio_messages(self, update, context):
        """
        Download voice messages from dialogs where bot is added
        :param update: Updater
        :param context: CallbackContext
        :return: oga_to_wav() which convert .oga file to .wav file with a sampling rate of 16 kHz
        """
        msg = update.message.voice
        user_id = str(update.message.from_user.id)
        if user_id not in self.audio_msgs.keys():
            self.audio_msgs[user_id] = 0
            print('if', self.audio_msgs[user_id])
        else:
            self.audio_msgs[user_id] += 1
            print('else', self.audio_msgs[user_id])
        self.file_num = self.audio_msgs[user_id]
        new_dir = f'{self.audio_path}/{user_id}'
        try:
            os.mkdir(new_dir)
        except OSError:
            log_msg('info', f'Dir {new_dir} already exist')
        os.chdir(new_dir)

        self.tg_bot.get_file(msg.file_id).download(
            f'audio_message_{self.file_num}.oga')
        log_msg('success', f'Audio message {self.file_num} saved')
        return self.oga_to_wav(update)

    def oga_to_wav(self, update):
        """
        Convert .oga file to .wav file with a sampling rate of 16 kHz
        :return: db_rec() which make a record to DB
        """
        user_id = str(update.message.from_user.id)
        src_filename = f'audio_message_{self.file_num}.oga'
        dest_filename = f'audio_message_{self.file_num}.wav'
        self.uid_mes[user_id].append(dest_filename)

        process = subprocess.run(
            ['ffmpeg', '-i', src_filename, '-ar', '16000', dest_filename])
        if process.returncode != 0:
            raise Exception("Something went wrong")
        os.remove(src_filename)
        os.chdir(self.cur_dir)
        if user_id in self.uid_mes.keys():
            return self.data.update_data(user_id, self.uid_mes[user_id])
        else:
            return self.data.insert_data(user_id, self.uid_mes[user_id])

    def photo(self, update, context):
        face_cascade = os.path.join(cv.__path__[0],
                                    'data/haarcascade_frontalface_alt.xml')
        eye_cascade = os.path.join(cv.__path__[0], 'data/haarcascade_eye.xml')
        smile_cascade = os.path.join(cv.__path__[0],
                                     'data/haarcascade_smile.xml')
        assert os.path.exists(face_cascade)
        assert os.path.exists(eye_cascade)
        faceCascade = cv.CascadeClassifier(face_cascade)
        eyeCascade = cv.CascadeClassifier(eye_cascade)
        smileCascade = cv.CascadeClassifier(smile_cascade)
        user_id = str(update.message.from_user.id)
        try:
            os.mkdir(f'{self.photo_path}/{user_id}')
        except FileExistsError:
            log_msg('info', f'Dir /photo/{user_id} already exists')
        msg = update.message.photo[-1]
        self.tg_bot.get_file(msg.file_id).download(
            f'{self.photo_path}/{user_id}/photo_{self.photo_num}.jpeg')
        img = cv.imread(
            f'{self.photo_path}/{user_id}/photo_{self.photo_num}.jpeg')
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Detect faces
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3,
                                             minNeighbors=4, minSize=(30, 30))
        eyes = []
        smile = []
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            eyes = eyeCascade.detectMultiScale(roi_gray, scaleFactor=1.3,
                                               minNeighbors=4)
            smile = smileCascade.detectMultiScale(roi_gray, 1.3, 4)
        if np.array_equal(faces, ()) and np.array_equal(eyes,
                                                        ()) and np.array_equal(
                smile, ()):
            os.remove(
                f'{self.photo_path}/{user_id}/photo_{self.photo_num}.jpeg')
            log_msg('info', 'No faces on photo')
        else:
            log_msg('success', f'Photo photo_{self.photo_num} saved')
            self.photo_num += 1
