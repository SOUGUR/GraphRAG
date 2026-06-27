from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.retrieval.hybrid_retriever import hybrid_retrieve  
from app.llm.answer_generator import generate_answer

class QueryState(TypedDict):
    project_id: str
    query: str
    top_n: int
    retrieved_chunks: list[dict]
    answer: str

def retrieve_node(state: QueryState) -> dict:
    """Retrieve relevant code chunks directly using the hybrid retriever."""
    chunks = hybrid_retrieve(
        query=state["query"],
        project_id=state["project_id"],
        rerank_n=state["top_n"],
    )
    return {"retrieved_chunks": chunks}

def generate_node(state: QueryState) -> dict:
    """Generate answer from retrieved chunks."""
    answer = generate_answer(state["query"], state["retrieved_chunks"])
    return {"answer": answer}

def build_query_graph():
    """Build the LangGraph query workflow."""
    workflow = StateGraph(QueryState)
    
    # Add nodes
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)
    
    # Set entry point
    workflow.set_entry_point("retrieve")
    
    # Add edges
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    
    return workflow.compile()

# Singleton graph instance
query_graph = build_query_graph()