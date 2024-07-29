from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass 

class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True,  autoincrement=True)
    tg_id = mapped_column(BigInteger)
    points = mapped_column(BigInteger,default=500)
    buy_count : Mapped[int] = mapped_column(BigInteger,default=0)
    number : Mapped[str] = mapped_column(String(11),default=0)
class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))

class Sale(Base):
    __tablename__ = 'sales'
    id: Mapped[int] = mapped_column(primary_key=True,  autoincrement=True)
    name : Mapped[str] = mapped_column(String(50))
    price : Mapped[int] = mapped_column(BigInteger, default=0)
    description: Mapped[str] = mapped_column(String(120))

class Item(Base):
    __tablename__ = 'items'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    img_id: Mapped[str] = mapped_column(String(255))  # Сохраняем file_id как строку


class Cart(Base):
    __tablename__ = 'cart'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    quantity: Mapped[int] = mapped_column(default=0)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создать все таблицы заново
