from telegram import Update
from telegram.ext import CallbackContext
from user import get_user_language
from Dictionaries import translations

def order_handler(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_language = get_user_language(user_id)

    if not user_language:
        update.message.reply_text("Iltimos, avval tilni tanlang: /start")
        return

    user_lang = translations[user_language]
    update.message.reply_text(f"{user_lang['order']} berish jarayoni boshlanadi...")
