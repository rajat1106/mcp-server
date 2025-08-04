import requests
import gradio as gr

def query_agent(query, agent_mode):
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json={"query": query, "agent": agent_mode},
            timeout=15
        )
        result = response.json()
        
        if "error" in result:
            return f"ERROR: {result['error']}"
        
        formatted_response = (
            f"AGENT: {result['agent'].upper()}\n\n"
            f"RESPONSE:\n{result['response']}"
        )
        return formatted_response
        
    except requests.exceptions.RequestException as e:
        return (
            "Connection failed. Please ensure:\n"
            "1. The backend is running (python app.py)\n"
            "2. You're using the correct port\n"
            f"Error details: {str(e)}"
        )

iface = gr.Interface(
    fn=query_agent,
    inputs=[
        gr.Textbox(label="Query", placeholder="Check CPU usage..."),
        gr.Radio(
            ["auto", "monitor", "log", "responder"],
            label="Agent Mode",
            value="auto"
        )
    ],
    outputs=gr.Textbox(label="Result", lines=10),
    title="Infrastructure Admin MCP",
    description="LLM-powered infrastructure management system"
)

if __name__ == "__main__":
    iface.launch()