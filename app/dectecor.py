from typing import Literal

from dotenv import load_dotenv
from fastapi import APIRouter
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

router = APIRouter(tags=["Code Review"])

# Initialize Mistral model
model = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0
)


# ===========================
# Request Model
# ===========================

class CodeRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze")


# ===========================
# Response Models
# ===========================

class Issue(BaseModel):
    summary: str = Field(description="Short summary of the issue")
    severity: Literal["low", "medium", "high"] = Field(
        description="Severity level"
    )
    suggestion: str = Field(description="Recommended fix")


class CodeReport(BaseModel):
    language: str = Field(description="Detected programming language")
    is_clean: bool = Field(description="Whether the code is clean")
    review: str = Field(description="Overall review")

    issues: list[Issue] = Field(
        default_factory=list,
        description="Issues found"
    )

    top_suggestions: list[str] = Field(
        default_factory=list,
        description="Top improvements"
    )


# Structured Output
structured_model = model.with_structured_output(CodeReport)


# ===========================
# API Endpoint
# ===========================

@router.post(
    "/analyze-code",
    response_model=CodeReport,
    summary="Analyze Source Code"
)
def analyze_code(request: CodeRequest):

    prompt = ChatPromptTemplate.from_template(
        """
        You are a Senior Software Engineer and Code Reviewer.
        
        Analyze the given source code.
        
        Return ONLY the structured response.
        
        Tasks:
        
        1. Detect the programming language.
        2. Review the overall code quality.
        3. Find bugs.
        4. Find performance issues.
        5. Find security issues.
        6. Find readability issues.
        7. Suggest improvements.
        
        If there are no issues:
        
        - is_clean = true
        - issues = []
        
        Otherwise:
        
        - is_clean = false
        
        Code:
        
        {code}
        """
    )

    messages = prompt.format_messages(code=request.code)

    report: CodeReport = structured_model.invoke(messages)

    return report

def run_code_analysis(code: str) -> CodeReport:
    prompt = ChatPromptTemplate.from_template(
        """
        You are a Senior Software Engineer and Code Reviewer.
        Analyze the given source code.
        Return ONLY the structured response.
        ...
        Code:
        {code}
        """
    )
    messages = prompt.format_messages(code=code)
    return structured_model.invoke(messages)


@router.post("/analyze-code", response_model=CodeReport, summary="Analyze Source Code")
def analyze_code(request: CodeRequest):
    return run_code_analysis(request.code)