from contextlib import asynccontextmanager
from enum import Enum, auto

from api import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


class EngineType(Enum):
    PLAYERDATA = auto()
    DISCORD = auto()


class Engine:
    def __init__(self, engine_type: EngineType = EngineType.PLAYERDATA):
        self.type: EngineType = engine_type
        self.connection_string = self.__get_connection_string(engine_type)
        self.engine = self.__get_engine(self.connection_string)
        self.session = self.__get_session_factory(self.engine)

    def __get_connection_string(self, type: EngineType) -> str:
        """
        set class connection string
        """
        if type == EngineType.PLAYERDATA:
            connection_string = Config.sql_uri
        elif type == EngineType.DISCORD:
            connection_string = Config.discord_sql_uri
        else:
            raise ValueError(f"Engine type {type} not valid.")
        return connection_string

    def __get_engine(self, connection_string) -> AsyncEngine:
        engine = create_async_engine(
            connection_string,
            poolclass=QueuePool,
            pool_pre_ping=True,
            pool_size=100,
            max_overflow=5000,
            pool_recycle=3600,
        )
        return engine

    def __get_session_factory(self, engine) -> sessionmaker:
        # self.engine.echo = True
        session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        return session

    @asynccontextmanager
    async def get_session(self):
        yield self.session()


"""Our Database Engines"""
PLAYERDATA_ENGINE = Engine(EngineType.PLAYERDATA)
DISCORD_ENGINE = Engine(EngineType.DISCORD)
