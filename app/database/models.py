from sqlalchemy import BigInteger , String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column , relationship 
from sqlalchemy.ext.asyncio import AsyncAttrs , async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')



async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass 


class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))

class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    category: Mapped[int] = mapped_column(ForeignKey('categories.id'))

class CartItem(Base):
    __tablename__ = 'cart_items'

    id : Mapped[int]= mapped_column(primary_key=True, index=True)
    product_id : Mapped[int] = mapped_column(ForeignKey('items.id'))
    user_id : Mapped[int] = mapped_column(index=True)
    quantity : Mapped[int] = mapped_column()

    product: Mapped[Item] = relationship("Item")




async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

