from google import genai
from dotenv import load_dotenv
from database import save_message, get_history
from PIL import Image
import os

# -----------------------------
# Load .env
# -----------------------------
load_dotenv()

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
    import fitz


def ask_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    if len(text.strip()) == 0:
        return "❌ این فایل متنی ندارد."

    prompt = f"""
تو یک دستیار هوش مصنوعی هستی.

متن زیر از یک فایل PDF استخراج شده است.

لطفاً:

1. خلاصه کامل تهیه کن.
2. نکات مهم را استخراج کن.
3. اگر سؤال یا تمرینی وجود دارد، توضیح بده.

{text[:80000]}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text