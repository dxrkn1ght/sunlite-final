from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import config, texts
from utils import list_products, create_product, add_transaction, approve_transaction, reject_transaction, set_order_status
from db_async import AsyncSessionLocal
from models import Transaction, Order, User, Product
from sqlalchemy import select

router = Router()

@router.message(F.text == "/admin")
async def admin_menu(message: Message):
    if message.chat.id not in config.ADMIN_IDS:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Mahsulotlar", callback_data="admin_products")],
        [InlineKeyboardButton(text="📩 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton(text="💳 Tranzaksiyalar", callback_data="admin_transactions")]
    ])
    await message.answer("Admin panel", reply_markup=kb)

@router.callback_query(F.data == "admin_transactions")
async def transactions_cb(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Transaction).where(Transaction.status=='pending'))
        txs = res.scalars().all()
        if not txs:
            await callback.message.answer("Hozir hech qanday pending tranzaksiya yo'q.")
            return
        for t in txs:
            caption = f"ID: {t.id}\nUser_id: {t.user_id}\nAmount: {t.amount}\nFile: {t.file_id}"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_tr_{t.id}"),
                 InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_tr_{t.id}")]
            ])
            if t.file_id:
                try:
                    await callback.message.bot.send_photo(callback.from_user.id, t.file_id, caption=caption, reply_markup=kb)
                except:
                    await callback.message.answer(caption, reply_markup=kb)
            else:
                await callback.message.answer(caption, reply_markup=kb)

@router.callback_query(F.data.startswith("approve_tr_"))
async def approve_tr_cb(callback: CallbackQuery):
    tr_id = int(callback.data.split("_")[-1])
    tr, user = await approve_transaction(tr_id)
    if tr:
        await callback.message.answer(f"Tranzaksiya {tr_id} tasdiqlandi. Balans yangilandi.")
        if user:
            try:
                await callback.bot.send_message(user.chat_id, texts.TEXTS[user.lang]['topup_approved'].format(amount=tr.amount))
            except: pass

@router.callback_query(F.data.startswith("reject_tr_"))
async def reject_tr_cb(callback: CallbackQuery):
    tr_id = int(callback.data.split("_")[-1])
    tr = await reject_transaction(tr_id)
    if tr:
        await callback.message.answer(f"Tranzaksiya {tr_id} rad etildi.")
        # notify user
        async with AsyncSessionLocal() as session:
            user = await session.get(User, tr.user_id)
            if user:
                try:
                    await callback.bot.send_message(user.chat_id, texts.TEXTS[user.lang]['topup_rejected'])
                except: pass

# Orders admin view
@router.callback_query(F.data == "admin_orders")
async def orders_cb(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Order).where(Order.status=='pending'))
        ords = res.scalars().all()
        if not ords:
            await callback.message.answer("Hozir hech qanday pending buyurtma yo'q.")
            return
        for o in ords:
            text = f"Order #{o.id}\nUser: {o.user_id}\nNickname: {o.nickname}\nProduct: {o.product.name}\nPrice: {o.product.price} UZS"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton("✅ Yuborildi", callback_data=f"order_send_{o.id}"),
                 InlineKeyboardButton("❌ Bekor", callback_data=f"order_reject_{o.id}")]
            ])
            await callback.message.answer(text, reply_markup=kb)

@router.callback_query(F.data.startswith("order_send_"))
async def order_send_cb(callback: CallbackQuery):
    oid = int(callback.data.split("_")[-1])
    order = await set_order_status(oid, 'completed')
    if order:
        # notify user
        async with AsyncSessionLocal() as session:
            user = await session.get(User, order.user_id)
            if user:
                try:
                    await callback.bot.send_message(user.chat_id, texts.TEXTS[user.lang]['order_confirmed_user'])
                except: pass
        await callback.message.answer(f"Order {oid} belgilandi: completed")

@router.callback_query(F.data.startswith("order_reject_"))
async def order_reject_cb(callback: CallbackQuery):
    oid = int(callback.data.split("_")[-1])
    order = await set_order_status(oid, 'rejected')
    if order:
        async with AsyncSessionLocal() as session:
            user = await session.get(User, order.user_id)
            if user:
                try:
                    await callback.bot.send_message(user.chat_id, "Buyurtmangiz bekor qilindi. Iltimos admin bilan bog'laning.")
                except: pass
        await callback.message.answer(f"Order {oid} bekor qilindi.")
