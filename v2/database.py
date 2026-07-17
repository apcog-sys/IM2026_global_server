import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import declarative_base
from common.dbutil import init_db, make_session_factory, SessionProxy
from common import settings

DB_NAME = settings.get("GLOBAL_DB_NAME", "global_server", "db_name", "global_registry_db")
Base = declarative_base()
engine = None
SessionLocal = SessionProxy()


def init():
    global engine
    import global_server.models  # noqa: F401
    engine = init_db(DB_NAME, Base)
    SessionLocal.configure(make_session_factory(engine))
