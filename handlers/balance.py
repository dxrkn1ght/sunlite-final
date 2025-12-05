from aiogram import Router, F
from aiogram.types import Message, ContentType, ReplyKeyboardMarkup, KeyboardButton
from keyboards.back_kb import back_kb
import texts, config, re
from utils import add_transaction, get_lang
router = Router()

# store pending topup amounts per chat (simple in-memory)
_pending_topup = {}

@router.message(F.text.in_(["💸 Hisobni to'ldirish","💸 Пополнить счёт"]))
async def topup_start(message: Message):
    lang = await get_lang(message.chat.id)
    await message.answer(texts.TEXTS[lang]['enter_topup_amount'].format(min=config.MIN_TOPUP, max=config.MAX_TOPUP), reply_markup=back_kb(lang))

@router.message()
async def capture_amount(message: Message):
    text = message.text or ""
    digits = re.sub(r'[^0-9]', '', text)
    if not digits:
        return
    amount = int(digits)
    lang = await get_lang(message.chat.id)
    if amount < config.MIN_TOPUP or amount > config.MAX_TOPUP:
        await message.answer(texts.TEXTS[lang]['invalid_amount'].format(min=config.MIN_TOPUP, max=config.MAX_TOPUP))
        return
    tr = await add_transaction(message.chat.id, amount, status='pending')
    # save pending transaction id, expect photo next
    _pending_topup[message.chat.id] = tr.id
    await message.answer(texts.TEXTS[lang]['send_screenshot'])

@router.message(content_types=[ContentType.PHOTO])
async def receive_screenshot(message: Message):
    if message.chat.id not in _pending_topup:
        return
    tr_id = _pending_topup.get(message.chat.id)
    # get biggest photo file_id
    file_id = message.photo[-1].file_id
    # update transaction with file_id
    from db_async import AsyncSessionLocal
    from models import Transaction
    async with AsyncSessionLocal() as session:
        tr = await session.get(Transaction, tr_id)
        if tr:
            tr.file_id = file_id
            await session.commit()
    # notify admins
    import config
    for aid in config.ADMIN_IDS:
        try:
            kb = None
            # send photo to admin with inline approve/reject buttons? simple message:
            await message.bot.send_photo(aid, file_id, caption=f"Yangi to'lov id={tr_id} user @{message.from_user.username or message.chat.id} summa: {tr.amount} UZS")
        except: pass
    lang = await get_lang(message.chat.id)
    await message.answer(texts.TEXTS[lang]['topup_sent_admin'])
    _pending_topup.pop(message.chat.id, None)
