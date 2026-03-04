from functools import wraps

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.common.config import common_settings


def connection(method):
    @wraps(method)
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                if "db_session" in kwargs:
                    return await method(*args, **kwargs)
                else:
                    has_session = False
                    for arg in args:
                        if isinstance(arg, AsyncSession):
                            has_session = True
                            break

                    if not has_session:
                        kwargs['db_session'] = session

                    return await method(*args, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper


DATABASE_URL = common_settings.get_db_url()

engine = create_async_engine(url=DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)