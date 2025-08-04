from fastapi import FastAPI
from pydantic import BaseModel
from mcp_core import MCP
from agents import MonitoringAgent, LogAnalyzerAgent, IncidentResponderAgent
import uvicorn
import asyncio

app = FastAPI()
mcp = MCP()
monitor = MonitoringAgent()
log_analyzer = LogAnalyzerAgent()
responder = IncidentResponderAgent()

class AgentRequest(BaseModel):
    query: str
    agent: str = "auto"  # auto|monitor|log|responder

@app.post("/query")
async def handle_query(request: AgentRequest):
    try:
        # Ensure we're using thread-safe operations
        if request.agent == "auto":
            decision = mcp.make_decision(request.query)
            agent = decision.lower()
        else:
            agent = request.agent
            
        if agent == "monitor":
            response = monitor.get_metrics()
        elif agent == "log":
            response = log_analyzer.analyze()
        elif agent == "responder":
            response = responder.take_action(request.query)
        else:
            response = {"error": "Unknown agent"}
        
        mcp.store_interaction(agent, request.query, str(response))
        return {"agent": agent, "response": response}
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)