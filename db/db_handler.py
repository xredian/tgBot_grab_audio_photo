from sqlalchemy import update
from logger import log_msg
from db.db_config import setup_db


class DataHandler:
    """
    Handler for PostgreSQL and Redis DB
    """

    def __init__(self, env):
        self.engine, self.audio_messages = setup_db(env)
        log_msg('success', 'PSQL: Connected to PostgreSQL')

    def insert_data(self, uid: int, audio_message: str):
        """
        Create new user in PostgreSQL

        :param uid: telegram user id
        :param audio_message: audiomessage string
        :return: None
        """
        query = self.audio_messages.insert()
        values = {"uid": uid, "audio_message": audio_message}
        self.engine.execute(query, values)
        log_msg('info', f'{uid}: Table audio_messages updated with new values '
                        f'in PostgreSQl')

    def update_data(self, uid: int, audio_message: str):
        """
        Update user info in PostgreSQL

        :param uid: telegram user id
        :param audio_message: audiomessage string
        :return: None
        """
        query = update(self.audio_messages)\
            .where(self.audio_messages.c.uid == uid)\
            .values(audio_message=audio_message)
        self.engine.execute(query)
        log_msg('info', f'{uid}: User`s messages updated in PostgreSQL')
