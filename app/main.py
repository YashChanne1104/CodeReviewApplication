from fastapi import FastAPI
from llm.factory import get_model
from tools.dectecor import detect_language

app = FastAPI(title="AI Code Reviewer")

model = get_model()


@app.get("/get_first_review")
def get_first_review():
    response = model.invoke("Hello, how are you?")
    return {"message": response.content}



@app.post("/review")
def review_code(code: str):
    """Review the given code snippet."""
    return {"review": detect_language(code)}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)