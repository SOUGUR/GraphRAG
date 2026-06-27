# 🚀 CodeGraphAI (GraphRAG)

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-45818e.svg)](https://neo4j.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GraphRAG](https://img.shields.io/badge/RAG-GraphRAG-ff69b4.svg)](#-what-is-graphrag)

**CodeGraphAI** is an advanced AI-powered system designed to help developers and architects understand complex Python codebases instantly. By combining **Python AST analysis**, **Neo4j Knowledge Graphs**, and **Semantic Vector Search**, it enables high-precision "GraphRAG" (Graph Retrieval-Augmented Generation) for deep repository exploration.

> "Stop reading hundreds of files. Start asking your codebase questions."

---

## 📖 Table of Contents
- [✨ Features](#-features)
- [🤔 What is GraphRAG?](#-what-is-graphrag)
- [🛠️ How it Works (Pipeline)](#️-how-it-works-pipeline)
- [🏗️ Architecture](#️-architecture)
- [🚀 Getting Started](#-getting-started)
- [💻 Usage Guide](#-usage-guide)
- [📊 Knowledge Graph Schema](#-knowledge-graph-schema)
- [🗺️ Roadmap](#️-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| **📦 ZIP Ingestion** | Upload entire Python projects as ZIP folders for automated processing. |
| **🔍 AST Parsing** | Deep static analysis using Python's Abstract Syntax Tree to extract classes, functions, and imports. |
| **🕸️ Knowledge Graph** | Builds a rich relationship map in **Neo4j** showing how code components interact. |
| **🧠 Semantic Search** | Generates code embeddings using **Cohere** and stores them in **ChromaDB** for vector retrieval. |
| **⚖️ Hybrid Retrieval** | Combines graph traversal with vector search to provide context-aware answers. |
| **🤖 LLM Integration** | Powered by **Groq (Llama 3)** and **Google Gemini** for lightning-fast reasoning. |
| **🔌 Modular Design** | Extensible architecture allowing for easy addition of new parsers or LLM providers. |

---

## 🤔 What is GraphRAG?

Traditional RAG (Retrieval-Augmented Generation) treats code as plain text chunks. This often loses the **structural context**—for example, which class a method belongs to or which functions call it.

**GraphRAG** solves this by:
1. **Mapping Relationships**: Understanding that `Function A` *calls* `Function B` and `Class X` *inherits* from `Class Y`.
2. **Contextual Retrieval**: When you ask about a specific function, GraphRAG retrieves not just the code snippet, but its neighbors in the graph (its callers, dependencies, and parent class).
3. **Improved Reasoning**: By providing the LLM with the "structural map" of the code, it can answer complex architectural questions that vector-only search would miss.

---

## 🛠️ How it Works (Pipeline)

```text
User Uploads ZIP
      ↓
[ Extract Project ] → Scans all .py files
      ↓
[ AST Parsing ] → Extracts Classes, Functions, Imports, Variables
      ↓
[ IR Generation ] → Creates an Intermediate Representation
      ↓
[ Knowledge Graph Construction ] → Populates Neo4j with Nodes & Edges
      ↓
[ Code Embeddings ] → Chunks code & stores in ChromaDB
      ↓
[ Hybrid Retrieval ] ← User Query
      ↓
[ LangGraph Workflow ] → Combines Graph + Vector context
      ↓
[ LLM (Groq/Gemini) ] → Generates Answer
```

---

## 🏗️ Architecture

The project is organized into modular services:

*   `app/api`: FastAPI endpoints for uploads, health checks, and querying.
*   `app/parser`: The "brain" that reads Python code using AST to understand structure.
*   `app/graph`: Manages Neo4j connections and builds the knowledge graph.
*   `app/embeddings`: Handles text chunking and vector database (ChromaDB) operations.
*   `app/llm`: Prompt management and LLM provider integrations (Groq, Gemini).
*   `app/services`: Orchestration layer connecting the parser, graph, and embeddings.
*   `app/models/ir`: Data models for the Intermediate Representation of code.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Neo4j Database (Local or AuraDB)
*   API Keys: Groq, Cohere, or Google Gemini

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/SOUGUR/GraphRAG.git
    cd GraphRAG
    ```

2.  **Set Up Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_key
    COHERE_API_KEY=your_cohere_key
    GOOGLE_API_KEY=your_gemini_key
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=password
    ```

4.  **Run the Application**
    ```bash
    uvicorn app.main:app --reload
    ```
    Access the interactive API docs at: `http://localhost:8000/docs`

---

## 💻 Usage Guide

### 1. Upload & Analyze
Upload your Python project (ZIP) to the `/api/v1/upload` endpoint. This triggers the AST parser.

### 2. Build the Graph
Call the `/api/v1/graph/build` endpoint to transform the parsed data into a Neo4j Knowledge Graph.

### 3. Generate Embeddings
Call `/api/v1/embed/generate` to chunk the code and store it in ChromaDB for semantic search.

### 4. Query Your Code
Use the `/api/v1/query` endpoint to ask questions like:
*   *"Explain the authentication flow in this project."*
*   *"Which functions are affected if I change the User model?"*
*   *"Show me the inheritance hierarchy of the BaseService class."*

---

## 📊 Knowledge Graph Schema

Our graph represents code as a network of interconnected entities:

*   **Nodes**: `Project`, `Package`, `File`, `Class`, `Function`, `Variable`, `Parameter`.
*   **Edges**: 
    *   `CONTAINS`: (Package → File)
    *   `DEFINES`: (File → Class/Function)
    *   `CALLS`: (Function → Function)
    *   `INHERITS`: (Class → Class)
    *   `DEPENDS_ON`: (File → Import)

---

## 🗺️ Roadmap

- [ ] **Multi-language Support**: Adding parsers for TypeScript, Java, and C++.
- [ ] **Web UI**: A built-in dashboard for graph visualization and chat.
- [ ] **Git Integration**: Directly analyze GitHub repositories via URL.
- [ ] **IDE Plugins**: VS Code extension for "Chat with your Repo" functionality.
- [ ] **Change Impact Analysis**: Predict which parts of the code will break after a change.

---

## 🤝 Contributing

Contributions are welcome! Whether it's fixing bugs, improving documentation, or adding new features:

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with ❤️ for the Open Source Community.**
