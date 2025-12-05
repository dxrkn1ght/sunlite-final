from aiogram import Router
from aiogram.types import Message
import texts
from utils import get_lang
from db_async import AsyncSessionLocal
from models import User, Transaction, Order
from sqlalchemy import select
from keyboards.main_kb import main_keyboard

router = Router()

@router.message()
async def show_history(message: Message):
    # Triggered by 📜 Tarix button (registered in main keyboard)
    if message.text not in ['📜 Tarix','📜 История']:
        return
    lang = await get_lang(message.chat.id)
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(User).where(User.chat_id==message.chat.id))
        user = res.scalars().first()
        if not user:
            await message.answer(texts.TEXTS[lang]['no_history'], reply_markup=main_keyboard(lang))
            return
        txs = (await session.execute(select(Transaction).where(Transaction.user_id==user.id))).scalars().all()
        ords = (await session.execute(select(Order).where(Order.user_id==user.id))).scalars().all()
        text = f"💰 Balans: {user.balance} UZS\n\n"
        if not txs and not ords:
            text += texts.TEXTS[lang]['no_history']
        else:
            if txs:
                text += '\n🧾 To‘lovlar:\n' + '\n'.join([f"#{t.id}: {t.amount} UZS - {t.status}" for t in txs])
            if ords:
                text += '\n📦 Buyurtmalar:\n' + '\n'.join([f"#{o.id}: {o.nickname} - {o.status}" for o in ords])
        await message.answer(text, reply_markup=main_keyboard(lang))
