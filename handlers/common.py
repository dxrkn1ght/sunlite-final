from aiogram import Router
from aiogram.filters import Text
from keyboards import back_kb, main_keyboard
from utils import get_lang
import texts

router = Router()

@router.message(Text(['⬅️ Ortga', '⬅️ Назад']))
async def back_to_main(message):
    lang = await get_lang(message.chat.id)
    await message.answer(texts.TEXTS[lang]['offer_confirmed'], reply_markup=main_keyboard(lang))

@router.message(Text(['❓ Bot haqida','❓ О боте']))
async def about_info(message):
    lang = await get_lang(message.chat.id)
    await message.answer(texts.TEXTS[lang]['about'], reply_markup=main_keyboard(lang))
