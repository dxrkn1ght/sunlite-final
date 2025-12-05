from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Text
import texts
from utils import get_lang, list_products, create_order
router = Router()

@router.message(Text(in_=["⭐ Rank sotib olish", "⭐ Купить Rank"]))
async def rank_menu(message: Message):
    lang = await get_lang(message.chat.id)
    prods = await list_products(kind='rank')
    if not prods:
        await message.answer("Hozir hech qanday mahsulot yo'q", reply_markup=None)
        return
    kb_rows = []
    for p in prods:
        kb_rows.append([KeyboardButton(f"{p.id} - {p.name} - {p.price}")])
    kb_rows.append([KeyboardButton('⬅️ Ortga' if lang=='uz' else '⬅️ Назад')])
    kb = ReplyKeyboardMarkup(keyboard=kb_rows, resize_keyboard=True)
    await message.answer('Mahsulotlar:', reply_markup=kb)

@router.message(Text(in_=["🌕 Coin sotib olish","🌕 Купить Coin"]))
async def coin_menu(message: Message):
    lang = await get_lang(message.chat.id)
    prods = await list_products(kind='coin')
    if not prods:
        await message.answer("Hozir hech qanday mahsulot yo'q", reply_markup=None)
        return
    kb_rows = []
    for p in prods:
        kb_rows.append([KeyboardButton(f"{p.id} - {p.name} - {p.price}")])
    kb_rows.append([KeyboardButton('⬅️ Ortga' if lang=='uz' else '⬅️ Назад')])
    kb = ReplyKeyboardMarkup(keyboard=kb_rows, resize_keyboard=True)
    await message.answer('Mahsulotlar:', reply_markup=kb)

# Simple stateful flow using bot data dict (per-process). For production replace with FSM or DB temp store.
_pending_buy = {}

@router.message()
async def parse_selection(message: Message):
    text = (message.text or "").strip()
    if not text:
        return
    if text.startswith('⬅️') or text.lower().startswith('back'):
        # ignore / go back
        lang = await get_lang(message.chat.id)
        await message.answer("Bekor qilindi.", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text='🏠 Меню' if lang!='uz' else '🏠 Menyu')]],
            resize_keyboard=True
        ))
        return
    parts = text.split()
    try:
        pid = int(parts[0])
    except:
        return
    # ask nickname
    await message.answer(texts.TEXTS[await get_lang(message.chat.id)]['ask_nickname'])
    _pending_buy[message.chat.id] = pid

@router.message()
async def buy_nick(message: Message):
    if message.chat.id not in _pending_buy:
        return
    pid = _pending_buy.get(message.chat.id)
    nick = (message.text or "").strip()
    order, err = await create_order(message.chat.id, pid, nick)
    lang = await get_lang(message.chat.id)
    if err == 'insufficient_balance':
        await message.answer(texts.TEXTS[lang]['insufficient_balance'], reply_markup=None)
        _pending_buy.pop(message.chat.id, None)
        return
    # notify admins
    import config
    for aid in config.ADMIN_IDS:
        try:
            await message.bot.send_message(aid, f"🛒 Yangi buyurtma!\n👤 @{message.from_user.username or message.chat.id}\n🆔 Order ID: {order.id}\nNomi: {order.product.name}\nNarxi: {order.product.price} UZS")
        except: pass
    await message.answer(texts.TEXTS[lang]['order_sent_admin'])
    _pending_buy.pop(message.chat.id, None)
