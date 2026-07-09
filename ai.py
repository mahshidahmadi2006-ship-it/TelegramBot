from google import genai
from dotenv import load_dotenv
from database import save_message, get_history
from PIL import Image
import fitz
import os

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()
# -----------------------------
# PDF Memory
# -----------------------------
pdf_memory = {}

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# Chat
# -----------------------------
def ask_ai(user_id, prompt):

    save_message(user_id, "user", prompt)

    history = get_history(user_id)

    conversation = ""

    for role, message in history:
        if role == "user":
            conversation += f"User: {message}\n"
        else:
            conversation += f"Assistant: {message}\n"

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=conversation,
        )

        answer = response.text

        save_message(user_id, "assistant", answer)

        return answer

    except Exception as e:

        return f"❌ {e}"


# -----------------------------
# Image Analysis
# -----------------------------
def ask_image(image_path, prompt=""):

    image = Image.open(image_path)

    final_prompt = """
تو یک دستیار هوش مصنوعی هستی.

اگر تصویر شامل متن بود:
- متن را بخوان.
- خلاصه کن.
- اگر سؤالی داخل تصویر بود، جوابش را بده.

اگر تصویر معمولی بود:
- دقیق توضیح بده داخل تصویر چه چیزهایی دیده می‌شود.
- اشیا، افراد، رنگ‌ها و محیط را توصیف کن.

همیشه پاسخ را به زبان فارسی بده.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[final_prompt, image]
    )

    return response.text
    

def ask_pdf(pdf_path):

    print(">>> ask_pdf started")
    print("fitz =", fitz)

    doc = fitz.open(pdf_path)

    pages = []

    for i, page in enumerate(doc):

        text = page.get_text().strip()

        if text:

            pages.append({
                "page": i + 1,
                "text": text
            })

    return pages

# -----------------------------
# PDF Manager
# -----------------------------

def add_pdf(user_id, file_name, pages):
    if user_id not in pdf_memory:
        pdf_memory[user_id] = []

    pdf_memory[user_id].append({
        "name": file_name,
        "pages": pages
    })


def get_pdfs(user_id):
    return pdf_memory.get(user_id, [])


def clear_pdfs(user_id):
    if user_id in pdf_memory:
        del pdf_memory[user_id]


def list_pdfs(user_id):
    pdfs = get_pdfs(user_id)

    if not pdfs:
        return "📂 هیچ فایل فعالی وجود ندارد."

    text = "📚 فایل‌های فعال:\n\n"

    for i, pdf in enumerate(pdfs, start=1):
        text += f"{i}. {pdf['name']}\n"

    return text


def search_pdf(user_id, question):

    pdfs = get_pdfs(user_id)

    if not pdfs:
        return None

    all_text = ""

    for pdf in pdfs:

        all_text += f"\n\n===== {pdf['name']} =====\n"

        for page in pdf["pages"]:

            all_text += (
                f"\nصفحه {page['page']}\n"
                f"{page['text']}\n"
            )

    prompt = f"""
تو فقط اجازه داری بر اساس PDFهای زیر پاسخ بدهی.

اگر جواب سؤال داخل فایل‌ها نبود فقط بنویس:

NOT_FOUND

------------------------

سؤال:

{question}

------------------------

{all_text[:180000]}
"""
print("===== PDF SENT TO GEMINI =====")
print(question)
print(all_text[:1000])
print("==============================")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    answer = response.text.strip()
     print("Gemini جواب داد:", answer)

    if answer == "NOT_FOUND":
        return None

    return answer


    
