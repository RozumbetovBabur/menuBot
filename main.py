from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from user import get_user_language, get_user, save_user_info, save_user_phone
from Dictionaries import translations
from profile import get_user_profile

TOKEN = "TOKEN"


def start_handler(update, context):
    user_id = update.message.chat_id
    user = get_user(user_id)  # Foydalanuvchini tekshiramiz
    if user:  # Agar user mavjud bo‘lsa
        language = user[0]  # Tilini olish
        user_lang = translations[language]
        update.message.reply_text(user_lang["already_registered"])
    else:
        show_language_selection(update)

def show_language_selection(update):
    keyboard = [
        ["🇬🇦 Qaraqalpaq tili", "🇺🇿 O'zbek tili"],
        ["🇷🇺 Русский язык"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(translations["uz"]["choose_language"], reply_markup=reply_markup)

def language_selection(update, context):
    user_id = update.message.chat_id
    text = update.message.text

    languages = {
        "🇬🇦 Qaraqalpaq tili": "kk",
        "🇺🇿 O'zbek tili": "uz",
        "🇷🇺 Русский язык": "ru"
    }

    # ❌ Profile tugmasi bosilganda bu kod ishlamasligi kerak
    if text not in languages:
        return

    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    username = update.message.chat.username
    language = languages[text]

    # Ma'lumotni bazaga saqlaymiz
    save_user_info(user_id, first_name, last_name, username, language)

    user_lang = translations[language]
    contact_button = KeyboardButton(user_lang["send_phone"], request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True)
    update.message.reply_text(user_lang["ask_phone"], reply_markup=reply_markup)


def profile_handler(update, context):
    user_id = update.message.chat_id
    user_profile = get_user_profile(user_id)

    if user_profile:
        user_lang = translations[user_profile["language"]]

        profile_text = (
            f"{user_lang['profile_info']}\n"
            f"👤 {user_lang['name']}: {user_profile['first_name']} {user_profile['last_name']}\n"
            f"🔹 {user_lang['username']}: @{user_profile['username']}\n"
            f"📞 {user_lang['phone_number']}: {user_profile['phone_number']}\n"
            f"🌍 {user_lang['language']}: {user_profile['language'].upper()}"
        )
        update.message.reply_text(profile_text)
    else:
        update.message.reply_text(translations["uz"]["not_registered"])  # Default: Uzbek tili

# 🔹 Foydalanuvchining tiliga qarab "Profil" tugmasini tekshirish
def profile_button_handler(update, context):
    user_id = update.message.chat_id
    user_lang_code = get_user_language(user_id)  # Foydalanuvchining tilini olish
    user_lang = translations.get(user_lang_code, translations["uz"])  # Default: uzbek tili
    text = update.message.text

    if text == user_lang["profile"]:
        profile_handler(update, context)


def change_language_handler(update, context):
    user_id = update.message.chat_id
    show_language_selection(update)  # Tilni qaytadan tanlash

def save_contact(update, context):
    user_id = update.message.chat_id
    contact = update.message.contact
    language = get_user_language(user_id)  # Foydalanuvchining tilini olish

    if contact:
        save_user_phone(user_id, contact.phone_number)
        user_lang = translations[language]

        update.message.reply_text(user_lang["phone_saved"])

        # Asosiy menyu (Tilga qarab tugmalar)
        menu_keyboard = [
            [user_lang["profile"], user_lang["order"]],
            [user_lang["change_language"]]
        ]
        reply_markup = ReplyKeyboardMarkup(menu_keyboard, resize_keyboard=True)

        update.message.reply_text(user_lang["welcome"], reply_markup=reply_markup)
def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start_handler))
    # 🔹 **Profil tugmasini ajratib olish** (Regex orqali)
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(👤 Profil|👤 Профиль|👤 Profil)$'), profile_button_handler))
    # 🔹 **Tilni o'zgartirish tugmasi**
    dispatcher.add_handler(MessageHandler(Filters.regex(r'^(Tildi ózgertiw|Tilni o‘zgartirish|Изменить язык|change_language)$'), change_language_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, language_selection))
    dispatcher.add_handler(MessageHandler(Filters.contact, save_contact))


    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
