ADMIN_ID = 123456789
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
import os
from ai import ask_ai

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    await update.message.reply_text("🤔 در حال فکر کردن...")

    answer = ask_ai(
        update.effective_user.id,
        user_message
    )

    await update.message.reply_text(answer)


async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Your ID: {update.effective_user.id}"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات روشنه ✅")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

print("AI Bot is Running...")

app.run_polling()
