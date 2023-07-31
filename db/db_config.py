from logger import log_msg
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column
from sqlalchemy.dialects.postgresql import VARCHAR


def setup_db(env):
    """
    Setting up DB

    :return: database, questions, additional_questions, users
    """
    base_url = env.db_engine
    metadata = MetaData()

    audio_messages = Table(
        'audio_messages',
        metadata,
        Column('uid', VARCHAR(255), primary_key=True),
        Column('audio_message', VARCHAR(255)),
    )

    engine = create_engine(base_url)
    metadata.create_all(engine)
    log_msg('success', 'Tables created in DB')
    return engine, audio_messages
