Core Concept

The system uses an LLM as a "dispatcher" to automatically route user queries to specialized agents that handle different infrastructure tasks (monitoring, logs, incident response). It maintains context across conversations using semantic search.

graph TD
    A[User Query] --> B{Gradio UI}
    B --> C[FastAPI Server]
    C --> D{MCP Router}
    D -->|LLM Decision| E[Monitoring Agent]
    D -->|LLM Decision| F[Log Analyzer]
    D -->|LLM Decision| G[Incident Responder]
    D --> H[(Context DB)]

Key Components Explained

1. MCP (Model Context Protocol)

The "brain" of the system that:

Uses Phi-2 LLM (2.7B parameter model) for decision making
Maintains conversation history in SQLite database
Implements semantic search (FAISS + SentenceTransformers) to find relevant context
Thread-safe design with connection pooling


2. Agents

Agent	Function	Tools Used
Monitoring	Checks CPU/Memory/Disk	psutil
Log Analyzer	Reads system logs	File I/O
Incident Responder	Restarts services	subprocess


3. LLM Integration Flow

User asks "Why is the system slow?"
LLM analyzes query + context
Routes to Monitoring Agent
Returns CPU/memory metrics
Stores interaction in context DB
