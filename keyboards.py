from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_keyboard(lang='uz'):
    if lang == 'ru':
        labels = [
            ['⭐ Rank купить', '🌕 Купить Coin'],
            ['💰 Мой баланс', "💸 Пополнить баланс"],
            ['❓ О боте', '📜 История']
        ]
    else:
        labels = [
            ['⭐ Rank sotib olish', '🌕 Coin sotib olish'],
            ['💰 Hisobim', "💸 Hisobni to'ldirish"],
            ['❓ Bot haqida', '📜 Tarix']
        ]
    keyboard = [[KeyboardButton(text=text) for text in row] for row in labels]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def offer_kb(lang='uz'):
    if lang == 'ru':
        buttons = ["Подтверждаю ✅"]
    else:
        buttons = ["Tasdiqlayman ✅"]
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=b)] for b in buttons], resize_keyboard=True, one_time_keyboard=True)

def back_kb(lang='uz'):
    text = "⬅️ Ortga" if lang == "uz" else "⬅️ Назад"
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=text)]], resize_keyboard=True, one_time_keyboard=True)

def admin_inline_for_transaction(tr_id, kind='topup'):
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve:{kind}:{tr_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject:{kind}:{tr_id}")
    ]])
    return kb
