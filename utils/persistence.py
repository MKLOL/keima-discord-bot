import __main__
import sqlite3
from pathlib import Path

DATA_DIR = Path(__main__.__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def get_guild_ids():
    db_path = DATA_DIR / "db.db"

    connection = sqlite3.connect(db_path)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS guild (
            guild_id INTEGER PRIMARY KEY
        )
    """)

    res = connection.execute("SELECT * FROM guild").fetchall()
    connection.close()

    return [row[0] for row in res]

def add_guild_id(guild_id):
    db_path = DATA_DIR / "db.db"

    connection = sqlite3.connect(db_path)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS guild (
            guild_id INTEGER PRIMARY KEY
        )
    """)

    connection.execute("INSERT INTO guild VALUES (?)", (guild_id, ))
    connection.commit()
    connection.close()

from utils.interfaces import IActivity, IActivityMemberRel, IFutureSession, IPastSession

class Activity(IActivity):
    def __init__(self, row : tuple[str, str, str]):
        self.activity_name, self.description, _archived_flag = row
        self.archived_flag = (_archived_flag == '1')

class ActivityMemberRel(IActivityMemberRel):
    def __init__(self, row : tuple[str, int, str]):
        self.activity_name, self.member_id, _core_flag = row
        self.core_flag = (_core_flag == '1')

class FutureSession(IFutureSession):
    def __init__(self, row : tuple[str, str, int, int]):
        self.activity_name, self.start_time, self.message_id, self.channel_id = row

class PastSession(IPastSession):
    def __init__(self, row : tuple[str, str, str]):
        self.activity_name, self.start_time, _confirmed_flag = row
        self.confirmed_flag = (_confirmed_flag == '1')

def create_tables_if_not_exist(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS activity (
            activity_name TEXT PRIMARY KEY,
            description TEXT,
            archived_flag TEXT
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS activity_member_rel (
            activity_name TEXT,
            member_id INTEGER,
            core_flag TEXT,
            UNIQUE ( activity_name, member_id )
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS future_session (
            activity_name TEXT PRIMARY KEY,
            start_time TEXT,
            message_id INTEGER,
            channel_id INTEGER
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS past_session (
            activity_name TEXT,
            start_time TEXT,
            confirmed_flag TEXT
        )
    """)

def get_connection(guild_id):
    db_path = DATA_DIR / f"guild_{guild_id}.db"
    connection = sqlite3.connect(db_path)

    create_tables_if_not_exist(connection)

    return connection

def get_activities(guild_id):
    connection = get_connection(guild_id)
    res : list[tuple[str, str, str]] = connection.execute("SELECT * FROM activity").fetchall()
    connection.close()
    return [Activity(row) for row in res]

def get_activity_member_rels(guild_id):
    connection = get_connection(guild_id)
    res : list[tuple[str, int, str]] = connection.execute("SELECT * FROM activity_member_rel").fetchall()
    connection.close()
    return [ActivityMemberRel(row) for row in res]

def get_future_sessions(guild_id):
    connection = get_connection(guild_id)
    res : list[tuple[str, str, int, int]] = connection.execute("SELECT * FROM future_session").fetchall()
    connection.close()
    return [FutureSession(row) for row in res]

def get_past_sessions(guild_id):
    connection = get_connection(guild_id)
    res : list[tuple[str, str, str]]  = connection.execute("SELECT * FROM past_session").fetchall()
    connection.close()
    return [PastSession(row) for row in res]

def add_activity_member_rel(guild_id, activity_name, member_id, core_flag='0'):
    connection = get_connection(guild_id)
    connection.execute("INSERT INTO activity_member_rel VALUES (?, ?, ?)", (activity_name, member_id, core_flag, ))
    connection.commit()
    connection.close()

def remove_activity_member_rel(guild_id, activity_name, member_id):
    connection = get_connection(guild_id)
    deleted_count = connection.execute("DELETE FROM activity_member_rel WHERE activity_name=? AND member_id=?", (activity_name, member_id, )).rowcount
    connection.commit()
    connection.close()
    return deleted_count

def remove_future_session(guild_id, activity_name):
    connection = get_connection(guild_id)
    deleted_count = connection.execute("DELETE FROM future_session WHERE activity_name=?", (activity_name, )).rowcount
    connection.commit()
    connection.close()
    return deleted_count