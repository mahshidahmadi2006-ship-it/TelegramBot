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
def ask_image(image_path, prompt):

    try:

        image = Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                image,
            ],
        )

        return response.text

    except Exception as e:

        return f"❌ {e}"