from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class DatabaseConnectionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, any] = None):
        self._host = host
        self._engine_kwargs = engine_kwargs
        self.engine = None
        self.sessionmaker = None

    async def connect(self) -> None:
        """
        Connect to the database
        """
        self.engine = create_async_engine(self._host, **self._engine_kwargs)
        self.sessionmaker = async_sessionmaker(autocommit=False, bind=self.engine)

    async def disconnect(self) -> None:
        """
        Close the database connection
        """
        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
            self.sessionmaker = None

    @asynccontextmanager
    async def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        async_session = self.sessionmaker()
        try:
            yield async_session
            await async_session.commit()
        except Exception:
            await async_session.rollback()
            raise
        finally:
            await async_session.close()
