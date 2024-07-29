from app.database.models import async_session
from app.database.models import User, Category, Item, Cart, Sale
from sqlalchemy import select, delete, update

async def set_user(tg_id,number):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        phone_number = await session.scalar(select(User).where(User.number == number))
        if not user or not phone_number:
            session.add(User(tg_id=tg_id,number=number))
            await session.commit()



async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))

async def get_sales():
    async with async_session() as session:
        return await session.scalars(select(Sale))
async def get_sale(sale_id):
    async with async_session() as session:
        return await session.scalar(select(Sale).where(Sale.id == sale_id))
async def rename_sale(sale_id,sale_name,price,description):
    async with async_session() as session:
        await session.execute(update(Sale).where(Sale.id == sale_id).values(sale_name=sale_name,price=price,description=description))
        await session.commit()

async def add_sale(name,price,description):
    async with async_session() as session:
        session.add(Sale(name=name,price=price,description=description))
        await session.commit()    

async def get_category_item(category_id):
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.category_id == category_id))

async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == item_id))

async def add_to_cart(user_id, item_id, quantity=1):
    async with async_session() as session:
        cart_item = await session.scalar(select(Cart).where(Cart.user_id == user_id, Cart.item_id == item_id))
        if cart_item:
            cart_item.quantity += quantity
        else:
            session.add(Cart(user_id=user_id, item_id=item_id, quantity=quantity))
        await session.commit()

async def get_cart(user_id):
    async with async_session() as session:
        cart_items = await session.scalars(select(Cart).where(Cart.user_id == user_id))
        result = []
        for cart_item in cart_items:
            item = await get_item(cart_item.item_id)
            result.append({
                'item': item,
                'quantity': cart_item.quantity
            })
        return result

async def get_image(img_id):
    async with async_session() as session:
        item = await session.scalar(select(Item).where(Item.img_id == img_id))
        return item.img_id if item else None


async def clear_cart(user_id):
    async with async_session() as session:
        await session.execute(delete(Cart).where(Cart.user_id == user_id))
        await session.commit()

async def add_category(name):
    async with async_session() as session:
        session.add(Category(name=name))
        await session.commit()

async def add_item(name, price, description, img_id, category_id):
    async with async_session() as session:
        file_id = img_id.file_id if hasattr(img_id, 'file_id') else img_id
        n_i = Item(category_id=category_id, price=price, name=name, description=description, img_id=file_id)
        session.add(n_i)
        await session.commit()


async def delete_sale(sale_id):
    async with async_session() as session:
        await session.execute(delete(Sale).where(Sale.id == sale_id))
        await session.commit()
async def delete_category(category_id):
    async with async_session() as session:
        await session.execute(delete(Category).where(Category.id == category_id))
        await session.commit()

async def rename_category(category_id, new_name):
    async with async_session() as session:
        await session.execute(update(Category).where(Category.id == category_id).values(name=new_name))
        await session.commit()

async def update_item(item_id, name, price, description):
    async with async_session() as session:  
        await session.execute(update(Item).where(Item.id == item_id).values(name=name, price=price, description=description))
        await session.commit()

async def delete_item(item_id):
    async with async_session() as session:
        await session.execute(delete(Item).where(Item.id == item_id))
        await session.commit()
