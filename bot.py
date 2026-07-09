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

from ai import (
    ask_ai,
    ask_image,
    ask_pdf,
    add_pdf,
    list_pdfs,
)
# -----------------------------
# Load ENV
# -----------------------------
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")



# -----------------------------
# Start
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
        "به ربات هوش مصنوعی خوش اومدی.",
        reply_markup=markup
    )


# -----------------------------
# My ID
# -----------------------------
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"🆔 آیدی شما:\n{update.effective_user.id}"
    )


# -----------------------------
# Photo
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
            f"❌ {e}"
        )


# -----------------------------
# PDF
# -----------------------------
async def pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):

    document = update.message.document

    telegram_file = await document.get_file()

    os.makedirs("pdfs", exist_ok=True)

    pdf_path = f"pdfs/{update.effective_user.id}_{document.file_name}"

    await telegram_file.download_to_drive(pdf_path)

    wait = await update.message.reply_text(
        "📄 در حال خواندن فایل..."
    )

    try:

        pages = ask_pdf(pdf_path)

        add_pdf(
            update.effective_user.id,
            document.file_name,
            pages
        )

        await wait.delete()

        await update.message.reply_text(
            f"✅ {document.file_name} اضافه شد.\n\n"
            f"{list_pdfs(update.effective_user.id)}\n\n"
            "حالا هر سوالی درباره فایل‌ها داری بپرس."
        )

    except Exception:
        import traceback

        traceback.print_exc()

        await wait.edit_text(
            "❌ خطا رخ داد. جزئیات در CMD چاپ شد."
        )


# -----------------------------
# Chat
# -----------------------------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if text == "🆔 آیدی من":
        await myid(update, context)
        return

    if text == "ℹ️ راهنما":
        await update.message.reply_text(
            "✅ متن بفرست\n"
            "✅ عکس بفرست\n"
            "✅ فایل PDF بفرست"
        )
        return

    if text == "🖼 تحلیل عکس":
        await update.message.reply_text(
            "📷 عکس را ارسال کن."
        )
        return

    if text == "🤖 چت با هوش مصنوعی":
        await update.message.reply_text(
            "سوالت را بنویس 😊"
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
# App
# -----------------------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("myid", myid))

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        photo
    )
)

app.add_handler(
    MessageHandler(
        filters.Document.PDF,
        pdf
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        chat
    )
)

print("🤖 Bot is Running...")

app.run_polling()