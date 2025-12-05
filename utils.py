from sqlalchemy import select
from db_async import AsyncSessionLocal
from models import User, Product, Transaction, Order

# User helpers
async def ensure_user(chat_id, username=None, lang='uz'):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.chat_id==chat_id))
        user = res.scalars().first()
        if not user:
            user = User(chat_id=chat_id, username=username or '', lang=lang, balance=0)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user

async def set_lang(chat_id, lang):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.chat_id==chat_id))
        user = res.scalars().first()
        if user:
            user.lang = lang
            await session.commit()

async def get_lang(chat_id):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.chat_id==chat_id))
        user = res.scalars().first()
        return user.lang if user else 'uz'

# Products
async def create_product(kind, name, price, description=''):
    async with AsyncSessionLocal() as session:
        p = Product(kind=kind, name=name, price=price, description=description)
        session.add(p)
        await session.commit()
        await session.refresh(p)
        return p

async def list_products(kind=None):
    async with AsyncSessionLocal() as session:
        q = select(Product)
        if kind:
            q = q.where(Product.kind==kind)
        res = await session.execute(q)
        return res.scalars().all()

# Transactions
async def add_transaction(chat_id, amount, status='pending', file_id=None):
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.chat_id==chat_id))).scalars().first()
        uid = user.id if user else None
        tr = Transaction(user_id=uid, amount=amount, status=status, file_id=file_id)
        session.add(tr)
        await session.commit()
        await session.refresh(tr)
        return tr

async def approve_transaction(tr_id):
    async with AsyncSessionLocal() as session:
        tr = await session.get(Transaction, tr_id)
        if not tr: return None
        tr.status = 'approved'
        user = await session.get(User, tr.user_id)
        if user:
            user.balance += tr.amount
        await session.commit()
        return tr, user

async def reject_transaction(tr_id):
    async with AsyncSessionLocal() as session:
        tr = await session.get(Transaction, tr_id)
        if not tr: return None
        tr.status = 'rejected'
        await session.commit()
        return tr

# Orders
async def create_order(chat_id, product_id, nickname):
    async with AsyncSessionLocal() as session:
        user = (await session.execute(select(User).where(User.chat_id==chat_id))).scalars().first()
        product = await session.get(Product, product_id)
        if not user: return None, 'user_not_found'
        if not product: return None, 'product_not_found'
        if user.balance < product.price: return None, 'insufficient_balance'
        order = Order(user_id=user.id, product_id=product.id, nickname=nickname, status='pending')
        user.balance -= product.price
        session.add(order)
        await session.commit()
        await session.refresh(order)
        return order, None

async def set_order_status(order_id, status):
    async with AsyncSessionLocal() as session:
        order = await session.get(Order, order_id)
        if not order: return None
        order.status = status
        await session.commit()
        return order
