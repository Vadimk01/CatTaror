import os
import random
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TOKEN")
BASE_IMG_PATH = os.path.join(os.path.dirname(__file__), "TarotBot_img")

sent_messages = {}

# === АВТОГЕНЕРАЦИЯ КАРТ ===
card_images = {}

# Старшие арканы
major_arcana = {
    "Шут": "RWS_Tarot_00_Fool.jpg",
    "Маг": "RWS_Tarot_01_Magician.jpg",
    "Верховная Жрица": "RWS_Tarot_02_High_Priestess.jpg",
    "Императрица": "RWS_Tarot_03_Empress.jpg",
    "Император": "RWS_Tarot_04_Emperor.jpg",
    "Иерофант": "RWS_Tarot_05_Hierophant.jpg",
    "Влюблённые": "RWS_Tarot_06_Lovers.jpg",
    "Колесница": "RWS_Tarot_07_Chariot.jpg",
    "Сила": "RWS_Tarot_08_Strength.jpg",
    "Отшельник": "RWS_Tarot_09_Hermit.jpg",
    "Колесо Фортуны": "RWS_Tarot_10_WheelOf_Fortune.jpg",
    "Справедливость": "RWS_Tarot_11_Justice.jpg",
    "Повешенный": "RWS_Tarot_12_Hanged_Man.jpg",
    "Смерть": "RWS_Tarot_13_Death.jpg",
    "Умеренность": "RWS_Tarot_14_Temperance.jpg",
    "Дьявол": "RWS_Tarot_15_Devil.jpg",
    "Башня": "RWS_Tarot_16_Tower.jpg",
    "Звезда": "RWS_Tarot_17_Star.jpg",
    "Луна": "RWS_Tarot_18_Moon.jpg",
    "Солнце": "RWS_Tarot_19_Sun.jpg",
    "Страшный суд": "RWS_Tarot_20_Judgement.jpg",
    "Мир": "RWS_Tarot_21_World.jpg"
}
for name, filename in major_arcana.items():
    card_images[name] = os.path.join(BASE_IMG_PATH, filename)

# Младшие арканы
suits = {
    "кубков": "Cups",
    "мечей": "Swords",
    "пентаклей": "Pents",
    "жезлов": "Wands"
}
names = {
    1: "Туз",
    2: "Двойка",
    3: "Тройка",
    4: "Четвёрка",
    5: "Пятёрка",
    6: "Шестёрка",
    7: "Семёрка",
    8: "Восьмёрка",
    9: "Девятка",
    10: "Десятка",
    11: "Паж",
    12: "Рыцарь",
    13: "Королева",
    14: "Король"
}
for suit_ru, suit_en in suits.items():
    for num in range(1, 15):
        card_name = f"{names[num]} {suit_ru}"
        filename = f"{suit_en}{num:02}.jpg"
        card_images[card_name] = os.path.join(BASE_IMG_PATH, filename)

# === КНОПКИ ===
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔮 Вытянуть карту", callback_data="draw_card")],
        [InlineKeyboardButton("🧹 Очистить чат", callback_data="clear_chat")]
    ])

# === СЛУЧАЙНАЯ КАРТА ===
def get_random_card():
    seed = int(time.time() * 1000)
    random.seed(seed)
    card = random.choice(list(card_images.keys()))
    #position = random.choice(["прямое", "перевёрнутое"])
    return card #, position

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text(
        "Привет! Нажми кнопку, чтобы вытянуть карту Таро 🔮", reply_markup=get_keyboard())
    sent_messages.setdefault(update.effective_chat.id, []).append(message.message_id)

# === ОБРАБОТКА КНОПОК ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat.id
    await query.answer()

    if query.data == "draw_card":
        card """, position""" = get_random_card()
        caption = f"🃏 Твоя карта: {card} "
        image_path = card_images.get(card)

        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as img:
                msg = await query.message.reply_photo(photo=img, caption=caption, reply_markup=get_keyboard())
        else:
            msg = await query.message.reply_text(caption + "\n(Изображение не найдено)", reply_markup=get_keyboard())

        sent_messages.setdefault(chat_id, []).append(msg.message_id)

    elif query.data == "clear_chat":
        for msg_id in sent_messages.get(chat_id, []):
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except:
                pass
        sent_messages[chat_id] = []
        msg = await query.message.reply_text("🧹 Очищено!", reply_markup=get_keyboard())
        sent_messages[chat_id].append(msg.message_id)

# === ЗАПУСК ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
