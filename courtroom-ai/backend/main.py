import os
import json
import time
import queue
import asyncio
import threading
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.graph.graph import build_graph
from backend.graph.state import CourtState

app = FastAPI(title="Courtroom AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

court_graph = build_graph()

class SimulateRequest(BaseModel):
    complaint: str

@app.get("/health")
def health_check():
    return {"ok": True, "message": "Backend is running"}

@app.post("/simulate/full")
async def simulate_full(request: SimulateRequest):
    initial_state: CourtState = {
        "complaint": request.complaint,
        "is_running": True,
        "execution_times": {}
    }
    
    def run_graph():
        return court_graph.invoke(initial_state)
    
    final_state = await asyncio.to_thread(run_graph)
    return final_state

@app.post("/simulate")
async def simulate_stream(request: SimulateRequest):
    initial_state: CourtState = {
        "complaint": request.complaint,
        "is_running": True,
        "execution_times": {}
    }
    
    async def event_generator() -> AsyncGenerator[str, None]:
        q = queue.Queue()
        start_time = time.time()
        
        def run_graph_in_thread():
            try:
                for node_output in court_graph.stream(initial_state):
                    elapsed = time.time() - start_time
                    for node_name in node_output:
                        node_output[node_name]["_elapsed"] = elapsed
                    q.put(("agent", node_output))
                q.put(("done", {}))
            except Exception as e:
                q.put(("error", {"error": str(e)}))
        
        thread = threading.Thread(target=run_graph_in_thread, daemon=True)
        thread.start()
        
        while True:
            try:
                event_type, data = await asyncio.to_thread(q.get, timeout=300)
                
                if event_type == "done":
                    yield f"event: done\\ndata: {json.dumps({'status': 'complete'})}\\n\\n"
                    break
                elif event_type == "error":
                    yield f"event: error\\ndata: {json.dumps(data)}\\n\\n"
                    break
                elif event_type == "agent":
                    yield f"event: agent\\ndata: {json.dumps(data)}\\n\\n"
                    
            except queue.Empty:
                yield f"event: error\\ndata: {json.dumps({'error': 'Timeout'})}\\n\\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
