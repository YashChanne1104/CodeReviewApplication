# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI


def get_model():
    return ChatMistralAI(model="mistral-large-latest")
