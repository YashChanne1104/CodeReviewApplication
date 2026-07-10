# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv

load_dotenv()

def get_model():
    return ChatMistralAI(model="mistral-large-latest")
