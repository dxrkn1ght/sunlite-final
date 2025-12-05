from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.command import CommandStart
import texts
from utils import ensure_user, set_lang, get_lang
from keyboards.main_kb import main_keyboard

router = Router()

@router.message(CommandStart())
async def bot_start(message: Message):
    # ensure user
    user = await ensure_user(message.chat.id, username=message.from_user.username or '', lang='uz')
    # bilingual greeting (both languages shown)
    greet = f"{texts.TEXTS['ru']['welcome']}\n\n{texts.TEXTS['uz']['welcome']}\n\n{texts.TEXTS['uz']['choose_lang']}"
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🇺🇿 O'zbеkcha"), KeyboardButton(text="🇷🇺 Русский")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(greet, reply_markup=kb)

@router.message()
async def catch_lang_and_offer(message: Message):
    # choose language
    if message.text == "🇺🇿 O'zbеkcha":
        await set_lang(message.chat.id, 'uz')
        await message.answer(texts.TEXTS['uz']['offer'], reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Tasdiqlayman ✅")]],
            resize_keyboard=True,
            one_time_keyboard=True
        ))
        return
    if message.text == "🇷🇺 Русский":
        await set_lang(message.chat.id, 'ru')
        await message.answer(texts.TEXTS['ru']['offer'], reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Подтверждаю ✅")]],
            resize_keyboard=True,
            one_time_keyboard=True
        ))
        return
    # Confirm offer
    if message.text in ["Tasdiqlayman ✅", "Подтверждаю ✅"]:
        lang = await get_lang(message.chat.id)
        await message.answer(texts.TEXTS[lang]['offer_confirmed'], reply_markup=main_keyboard(lang))
        return
