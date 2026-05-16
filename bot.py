import os
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
DATA_FILE = "users.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_phase(days):
    if days <= 5:
        return "🔴 أنتِ في أيام الدورة - خذي راحتك 💙"
    elif days <= 13:
        return "🌱 مرحلة التعافي - طاقتك ترجع شوي شوي"
    elif days <= 17:
        return "✨ مرحلة الإباضة - أعلى طاقة عندك!"
    elif days <= 28:
        return "🍂 مرحلة ما قبل الدورة - عادي تحسين بثقل"
    else:
        return "⏰ يبدو الدورة تأخرت - راقبي نفسك"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/سجلي_دورتي", "/وضعي_الحالي"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "أهلاً بك في Cycle Buddy 🤍\n\nأنا هنا أساعدك تتابعين دورتك بهدوء.\n\nاضغطي /سجلي_دورتي لتبدئي!",
        reply_markup=reply_markup
    )

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسلي لي تاريخ آخر دورة بهذا الشكل:\n\nمثال: 2024-12-01"
    )
    context.user_data["waiting_for_date"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_date"):
        try:
            date = datetime.strptime(update.message.text.strip(), "%Y-%m-%d")
            data = load_data()
            user_id = str(update.message.from_user.id)
            data[user_id] = {"last_period": update.message.text.strip()}
            save_data(data)
            context.user_data["waiting_for_date"] = False
            await update.message.reply_text("✅ تم الحفظ! أرسلي /وضعي_الحالي لتشوفي مرحلتك 🌸")
        except:
            await update.message.reply_text("❌ الصيغة غلط. أرسلي التاريخ هكذا: 2024-12-01")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    user_id = str(update.message.from_user.id)
    if user_id not in data:
        await update.message.reply_text("ما عندي تاريخ دورتك بعد.\nأرسلي /سجلي_دورتي أول 🌸")
        return
    last = datetime.strptime(data[user_id]["last_period"], "%Y-%m-%d")
    days = (datetime.now() - last).days
    phase = get_phase(days)
    await update.message.reply_text(f"اليوم {days} من دورتك 🗓\n\n{phase}")

def main():
    token = os.environ.get("BOT_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("سجلي_دورتي", register))
    app.add_handler(CommandHandler("وضعي_الحالي", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
