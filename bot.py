from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import os

from ai import ask_ai, ask_image

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# -----------------------------
# /start
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🤖 چت با هوش مصنوعی"],
        ["🖼 تحلیل عکس"],
        ["🆔 آیدی من", "ℹ️ راهنما"],
    ]

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "سلام 🌸\n\n"
        "به ربات هوش مصنوعی خوش اومدی.\n"
        "هر سوالی داری بپرس 😊",
        reply_markup=markup
    )


# -----------------------------
# /myid
# -----------------------------
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🆔 آیدی شما:\n{update.effective_user.id}"
    )


# -----------------------------
# تحلیل عکس
# -----------------------------
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    telegram_file = await photo.get_file()

    image_path = "photo.jpg"

    await telegram_file.download_to_drive(image_path)

    wait = await update.message.reply_text(
        "🖼 در حال تحلیل عکس..."
    )

    try:

        answer = ask_image(
            image_path,
            "این تصویر را کامل و دقیق به زبان فارسی توضیح بده."
        )

        await wait.delete()

        await update.message.reply_text(answer)

    except Exception as e:

        print(e)

        await wait.edit_text(
            f"❌ خطا:\n{e}"
        )


# -----------------------------
# چت
# -----------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🆔 آیدی من":
        await update.message.reply_text(
            str(update.effective_user.id)
        )
        return

    if text == "ℹ️ راهنما":
        await update.message.reply_text(
            "هر سوالی داری از من بپرس 😊\n\n"
            "همچنین می‌توانی برای تحلیل، عکس ارسال کنی."
        )
        return

    if text == "🖼 تحلیل عکس":
        await update.message.reply_text(
            "📷 لطفاً عکس موردنظر را ارسال کن."
        )
        return

    if text == "🤖 چت با هوش مصنوعی":
        await update.message.reply_text(
            "سؤالت را بنویس 😊"
        )
        return

    wait = await update.message.reply_text(
        "🤔 در حال فکر کردن..."
    )

    try:

        answer = ask_ai(
            update.effective_user.id,
            text
        )

        await wait.delete()

        await update.message.reply_text(answer)

    except Exception as e:

        print(e)

        await wait.edit_text(
            f"❌ {e}"
        )


# -----------------------------
# Main
# -----------------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo,
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat,
    )
)

print("🤖 Bot is Running...")

app.run_polling()