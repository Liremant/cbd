from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.database.models import Item, CartItem

async def get_products(db: Session):
    result = await db.execute(select(Item))
    return result.scalars().all()

async def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int):
    cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item

async def get_cart_items(db: Session, user_id: int):
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id))
    return result.scalars().all()

async def remove_from_cart(db: Session, user_id: int, product_id: int):
    result = await db.execute(select(CartItem).where(CartItem.user_id == user_id, CartItem.product_id == product_id))
    item = result.scalar_one_or_none()
    if item:
        await db.delete(item)
        await db.commit()
