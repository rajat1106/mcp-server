import sqlite3
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import threading

class MCP:
    def __init__(self, db_path="mcp_context.db"):
        # Initialize thread-local storage
        self.local = threading.local()
        
        # Initialize database connection for this thread
        self.db_path = db_path
        self._init_db()
        
        # Setup semantic search
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.IndexFlatL2(384)
        
        # Setup LLM
        self.llm_model = "microsoft/phi-2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_model, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.llm_model,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        self.lock = threading.Lock()  # For thread-safe operations

    def _get_db(self):
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.local.conn.execute('''
            CREATE TABLE IF NOT EXISTS context (
                id INTEGER PRIMARY KEY,
                agent TEXT,
                query TEXT,
                response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        return self.local.conn

    def _init_db(self):
        conn = self._get_db()
        conn.commit()

    def store_interaction(self, agent, query, response):
        with self.lock:
            conn = self._get_db()
            conn.execute(
                "INSERT INTO context (agent, query, response) VALUES (?, ?, ?)",
                (agent, query, response)
            )
            conn.commit()
            
            embedding = self.embedder.encode(f"{agent}: {query} - {response}")
            self.index.add(np.array([embedding]))

    def retrieve_context(self, query, k=3):
        with self.lock:
            conn = self._get_db()
            query_embed = self.embedder.encode(query)
            distances, indices = self.index.search(np.array([query_embed]), k)
            
            context = []
            for idx in indices[0]:
                res = conn.execute(
                    "SELECT agent, query, response FROM context WHERE id = ?",
                    (int(idx)+1,)
                ).fetchone()
                if res:
                    context.append(f"{res[0]}: {res[1]}\n{res[2]}")
            return "\n\n".join(context)

    def make_decision(self, query):
        prompt = f"""Determine which agent should handle this query.
        Options: [MONITOR, LOG, RESPONDER]
        Context:
        {self.retrieve_context(query)}
        
        Query: {query}
        Decision:"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to("mps")
        outputs = self.model.generate(**inputs, max_new_tokens=20)
        decision = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "MONITOR" in decision.upper(): return "monitor"
        if "LOG" in decision.upper(): return "log"
        if "RESPONDER" in decision.upper(): return "responder"
        return "monitor"