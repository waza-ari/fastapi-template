from contextvars import ContextVar

from sqlalchemy.ext.asyncio import async_scoped_session, async_sessionmaker, create_async_engine

from app.core import settings

db_session_context: ContextVar[str | None] = ContextVar("db_session_context", default=None)


class DatabaseConnectionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, any] = None):
        self._host = host
        self._engine_kwargs = engine_kwargs or {}
        self.engine = None
        self.scoped_session = None

    async def connect(self) -> None:
        """
        Connect to the database
        """
        self.engine = create_async_engine(self._host, **self._engine_kwargs)

        # Magic happens here
        self.scoped_session = async_scoped_session(
            session_factory=async_sessionmaker(bind=self.engine, autoflush=False, autocommit=False),
            scopefunc=db_session_context.get,
        )

    async def disconnect(self) -> None:
        """
        Close the database connection
        """
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None


sessionmanager = DatabaseConnectionManager(settings.POSTGRES_URI)
