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
    search_pdf,
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

        user_prompt = context.user_data.get("image_prompt", "")

        answer = ask_image(
            image_path,
            user_prompt
        )

        await wait.delete()

        await update.message.reply_text(answer)

        context.user_data.pop("image_prompt", None)

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

    image_commands = [
        "متن این عکس را استخراج کن",
        "متن عکس را استخراج کن",
        "ترجمه کن",
        "خلاصه کن",
        "جواب سوال‌های عکس را بده",
        "جواب سوال های عکس را بده",
        "عکس را تحلیل کن"
    ]

    if text in image_commands:

        context.user_data["image_prompt"] = text

        await update.message.reply_text(
            "📷 حالا عکس را ارسال کن."
        )

        return

    wait = await update.message.reply_text(
        "🤔 در حال فکر کردن..."
    )

    try:

        user_id = update.effective_user.id

        answer = search_pdf(user_id, text)

        if answer is None:
            answer = ask_ai(user_id, text)

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