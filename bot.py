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
from ai import ask_ai

# -------------------------
# Load Environment Variables
# -------------------------
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# -------------------------
# Start Command
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🤖 چت با هوش مصنوعی"],
        ["🆔 آیدی من", "ℹ️ راهنما"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "سلام 🌸\n\n"
        "به ربات هوش مصنوعی خوش اومدی.\n"
        "هر سوالی داری از من بپرس 😊",
        reply_markup=reply_markup
    )


# -------------------------
# My ID Command
# -------------------------
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🆔 آیدی شما:\n{update.effective_user.id}"
    )


# -------------------------
# Chat Handler
# -------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_message = update.message.text

    # دکمه آیدی
    if user_message == "🆔 آیدی من":
        await update.message.reply_text(
            f"🆔 آیدی شما:\n{update.effective_user.id}"
        )
        return

    # دکمه راهنما
    if user_message == "ℹ️ راهنما":
        await update.message.reply_text(
            "💡 فقط سوالت رو برام بنویس تا با هوش مصنوعی جواب بدم."
        )
        return

    # دکمه چت
    if user_message == "🤖 چت با هوش مصنوعی":
        await update.message.reply_text(
            "هر سوالی داری بپرس 😊"
        )
        return

    # پیام در حال فکر کردن
    wait = await update.message.reply_text(
        "🤔 در حال فکر کردن..."
    )

    try:

        answer = ask_ai(
            update.effective_user.id,
            user_message
        )

        await wait.delete()

        await update.message.reply_text(answer)

    except Exception as e:

        print(e)

        await wait.edit_text(
            "❌ متأسفانه خطایی رخ داد."
        )


# -------------------------
# Main
# -------------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat,
    )
)

print("🤖 AI Bot is Running...")

app.run_polling()