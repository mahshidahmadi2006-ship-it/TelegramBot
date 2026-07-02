from database import save_message, get_history
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
print("API KEY:", os.getenv("GEMINI_API_KEY"))
print("BOT TOKEN:", os.getenv("BOT_TOKEN"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_ai(user_id, prompt):
    # ذخیره پیام کاربر در دیتابیس
    save_message(user_id, "user", prompt)

    # بازیابی کل تاریخچه از دیتابیس
    rows = get_history(user_id)

    history = ""
    for role, message in rows:
        history += f"{role}: {message}\n"

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
    )

    answer = response.text

    # ذخیره پاسخ مدل در دیتابیس
    save_message(user_id, "assistant", answer)

    return answer
