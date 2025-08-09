import asyncio
from database.base import engine, Base
# Импортируйте здесь все модели, чтобы они были зарегистрированы в metadata

async def init_models():
    """
    Создает все таблицы, описанные в Base.metadata
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
    print("✅ DB created!")