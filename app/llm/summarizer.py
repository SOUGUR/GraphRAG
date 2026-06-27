from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config.settings import GOOGLE_API_KEY, LLM_MODEL

SUMMARIZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a code summarizer. Provide a brief, technical summary."),
    ("human", "Summarize this code in 2-3 sentences:\n\n{code}"),
])

def summarize_code(code: str) -> str:
    """Generate a brief summary of code."""
    if not code or len(code) < 50:
        return code
    
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
        max_tokens=200,
    )
    
    chain = SUMMARIZE_PROMPT | llm | StrOutputParser()
    return chain.invoke({"code": code[:1500]})