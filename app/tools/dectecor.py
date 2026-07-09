# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Literal
from rich import print

load_dotenv()

model = ChatMistralAI(model="mistral-large-latest")


# ---- Schema ----

class Issue(BaseModel):
    summary: str = Field(description="Short summary of the issue")
    severity: Literal["low", "medium", "high"] = Field(description="Severity of the issue")
    suggestion: str = Field(description="Suggested fix for this specific issue")


class CodeReport(BaseModel):
    language: str = Field(description="Detected programming language of the code")
    is_clean: bool = Field(description="True if no issues were found at all")
    review: str = Field(description="A concise overall review/summary of the code quality")
    issues: list[Issue] = Field(default_factory=list, description="List of issues found, empty if clean")
    top_suggestions: list[str] = Field(
        default_factory=list,
        description="Top 3 actionable suggestions to improve the code, regardless of severity"
    )


structured_model = model.with_structured_output(CodeReport)


# ---- Tool ----

@tool
def analyze_code(code: str) -> str:
    """Analyze a code snippet: detect language, review quality, find issues, and give suggestions."""
    prompt = ChatPromptTemplate.from_template(
        "You are a senior code reviewer. Analyze the following code snippet.\n"
        "1. Detect the programming language.\n"
        "2. Give a concise overall review of the code quality.\n"
        "3. List any issues (bugs, performance, readability, best practices) with severity and a fix.\n"
        "4. Give the top 3 most actionable suggestions overall.\n"
        "If the code has no issues, set is_clean to true and leave issues empty.\n\n"
        "Code:\n{code}"
    )
    formatted = prompt.format_messages(code=code)
    report: CodeReport = structured_model.invoke(formatted)

    out = [
        f"Language: {report.language}",
        f"Review: {report.review}",
        "",
    ]

    if report.is_clean:
        out.append("No issues found. Code looks good.")
    else:
        out.append("Issues:")
        for issue in report.issues:
            out.append(f"  [{issue.severity.upper()}] {issue.summary}")
            out.append(f"    → {issue.suggestion}")

    if report.top_suggestions:
        out.append("")
        out.append("Top Suggestions:")
        for i, s in enumerate(report.top_suggestions, 1):
            out.append(f"  {i}. {s}")

    return "\n".join(out)



print(analyze_code.invoke({"code": "select * from users"}))