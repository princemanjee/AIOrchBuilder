import os
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import io
import zipfile
from supabase import create_client, Client
from dotenv import load_dotenv
from llm_router import llm_router
from providers.factory import provider_factory

load_dotenv()

app = FastAPI(title="AIOrch Orcherstrator")

class ClientRegistry:
    def __init__(self):
        self.hub: Optional[Client] = None
        self.satellites: Dict[str, Client] = {}
        self._initialize_hub()

    def _initialize_hub(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            self.hub = create_client(url, key)
            print("🚀 Hub Instance connected")
            self._restore_satellites()

    def _restore_satellites(self):
        """Fetches existing satellite configs from the Hub database."""
        if not self.hub: return
        try:
            response = self.hub.table("projects").select("id, satellite_url, satellite_key").execute()
            for project in response.data:
                if project["satellite_url"] and project["satellite_key"]:
                    self.satellites[str(project["id"])] = create_client(project["satellite_url"], project["satellite_key"])
                    print(f"📡 Restored Satellite: {project['id']}")
        except Exception as e:
            print(f"⚠️ Failed to restore satellites: {e}")

    def get_satellite(self, project_id: str, url: str = None, key: str = None) -> Client:
        if project_id in self.satellites:
            return self.satellites[project_id]
        
        if url and key:
            client = create_client(url, key)
            self.satellites[project_id] = client
            return client
        
        raise HTTPException(status_code=400, detail="Satellite credentials required for new project")

registry = ClientRegistry()

class SatelliteConfig(BaseModel):
    project_id: str
    url: str
    key: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TaskUpdate(BaseModel):
    status: str

@app.get("/")
async def root():
    return {"status": "AIOrch Orchestrator Online", "mode": "Satellite Scaling Active"}

@app.post("/connect-satellite")
async def connect_satellite(config: SatelliteConfig):
    registry.get_satellite(config.project_id, config.url, config.key)
    return {"status": "connected", "project_id": config.project_id}

@app.get("/projects")
async def get_projects(project_id: Optional[str] = None):
    # If no project_id, fetch from Hub (Registry)
    client = registry.hub if not project_id else registry.satellites.get(project_id)
    if not client: raise HTTPException(status_code=404, detail="Client not found")
    
    response = client.table("projects").select("*").execute()
    return response.data

@app.get("/tasks/{project_id}")
async def get_tasks(project_id: str):
    client = registry.get_satellite(project_id)
    response = client.table("tasks").select("*").eq("project_id", project_id).execute()
    return response.data

@app.post("/audit-log")
async def log_audit(task_id: str, agent: str, message: str, project_id: str):
    # Audit logs always go to the Hub for global telemetry
    if not registry.hub: raise HTTPException(status_code=500, detail="Hub not connected")
    
    response = registry.hub.table("agent_audit_logs").insert({
        "task_id": task_id,
        "agent_name": agent,
        "message": message,
        "metadata": {"project_id": project_id}
    }).execute()
    return response.data

from logic_engine import agent_logic
from orchestrator import task_orchestrator
from models import RequirementRequest, ArchitectureBlueprint, AgentTask, TaskList, ApprovalRequest

# Temporary in-memory store for pending approvals
pending_approvals: Dict[str, ApprovalRequest] = {}
# Project history: Map project_name -> List of task lists (limited to REVISION_LIMIT)
project_history: Dict[str, List[List[AgentTask]]] = {}

# Admin configuration
DEFAULT_CONFIG = {
    "revision_limit": 3,
    "agent_speed": "M",  # S, M, L
    "token_limit": 50000,
    "unlimited_admin_tokens": True,
    "active_llm_engine": "Ollama (Local/Remote)",
    "active_model": "llama3",
    "ollama_url": "http://localhost:11434",
    "lmstudio_url": "http://localhost:1234",
    "gpt4all_url": "http://localhost:4891",
    "vllm_url": "http://localhost:8000",
    "perplexity_api_key": "",
    "multi_llm_orchestration": True,
    "webhook_url": "",
    "agent_mappings": {
        "AGENT_DATA": "Dynamic",
        "AGENT_API": "Dynamic",
        "AGENT_UI": "Dynamic",
        "AGENT_LOGIC": "Dynamic",
        "AGENT_AUTH": "Dynamic",
        "AGENT_TEST": "Dynamic"
    },
    "llm_engines": [
        {"name": "Ollama (Local/Remote)", "models": ["llama3", "mistral", "codellama", "phi3"]},
        {"name": "Perplexity", "models": ["llama-3-sonar-large-32k-online", "llama-3-sonar-small-32k-chat"]},
        {"name": "LMStudio", "models": ["local-model"]},
        {"name": "GPT-For-All", "models": ["gpt4all-l13b-snoozy"]},
        {"name": "vLLM", "models": ["custom-vllm-model"]},
        {"name": "Anthropic (Coming Soon)", "models": ["claude-3-5-sonnet-latest"]},
        {"name": "OpenAI (Coming Soon)", "models": ["gpt-4o", "gpt-4o-mini"]},
        {"name": "Google (Coming Soon)", "models": ["gemini-1.5-pro"]}
    ],
    "mcp_tools": [
        {"name": "Docker Context", "status": "Active"},
        {"name": "Notion Sync", "status": "Active"},
        {"name": "GitHub CLI", "status": "Active"}
    ]
}

system_config = DEFAULT_CONFIG.copy()

class AdminConfigRequest(BaseModel):
    revision_limit: Optional[int] = None
    agent_speed: Optional[str] = None
    token_limit: Optional[int] = None
    unlimited_admin_tokens: Optional[bool] = None
    active_llm_engine: Optional[str] = None
    active_model: Optional[str] = None
    ollama_url: Optional[str] = None
    lmstudio_url: Optional[str] = None
    gpt4all_url: Optional[str] = None
    vllm_url: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    multi_llm_orchestration: Optional[bool] = None
    webhook_url: Optional[str] = None
    agent_mappings: Optional[Dict[str, str]] = None

@app.post("/admin/config")
async def update_config(config: AdminConfigRequest, x_role: str = Header(None)):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    # Update only provided fields
    update_data = config.dict(exclude_unset=True)
    system_config.update(update_data)
    
    # Audit logging for config change
    if registry.hub:
        registry.hub.table("agent_audit_logs").insert({
            "agent_name": "SYSTEM_ADMIN",
            "message": f"Governance update: {list(update_data.keys())}",
            "metadata": {"config_delta": update_data}
        }).execute()
        
    return {"status": "Configuration updated", "config": system_config}

@app.get("/admin/config")
async def get_config():
    return system_config

@app.get("/admin/test-connectivity/{engine}")
async def test_connectivity(engine: str):
    try:
        provider = provider_factory.get_provider(engine, system_config)
        # Fast test: ask for a single word
        response = await provider.generate(
            prompt="Respond with only one word: 'OK'",
            model=system_config.get("active_model", "default")
        )
        return {"status": "connected", "engine": engine, "response": response}
    except Exception as e:
        return {"status": "error", "engine": engine, "detail": str(e)}

@app.post("/admin/reset")
async def reset_config(x_role: str = Header(None)):
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    global system_config
    system_config = DEFAULT_CONFIG.copy()
    return {"status": "System restored to factory defaults", "config": system_config}

@app.post("/logic/parse-requirements", response_model=ArchitectureBlueprint)
async def parse_requirements(request: RequirementRequest):
    try:
        blueprint = await agent_logic.parse(request, system_config)
        return blueprint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logic/decompose", response_model=TaskList)
async def decompose_blueprint(blueprint: ArchitectureBlueprint):
    try:
        tasks = task_orchestrator.decompose(blueprint)
        # Store for approval
        approval_id = "current_session" # Simple for POC
        pending_approvals[approval_id] = ApprovalRequest(blueprint=blueprint, tasks=tasks)
        return TaskList(tasks=tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logic/approve-build")
async def approve_build(approval: ApprovalRequest):
    # Retrieve the active tasks for this session
    approval_id = "current_session"
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="No pending build found")
    
    current_approval = pending_approvals[approval_id]
    
    # --- History Persistence Logic ---
    # In a real app, 'persist_history' would come from the request body/approval object
    persist_history = True # For POC demonstration
    
    if persist_history:
        project_name = current_approval.blueprint.project_name
        if project_name not in project_history:
            project_history[project_name] = []
        
        # Keep only the last N versions based on config
        limit = system_config["revision_limit"]
        project_history[project_name].insert(0, current_approval.tasks)
        project_history[project_name] = project_history[project_name][:limit]
        print(f"📊 History updated for {project_name}. Versions stored: {len(project_history[project_name])} (Limit: {limit})")

    # Define a callback for status updates
    async def status_callback(task: AgentTask):
        # 1. Log to the Hub's audit logs (Real-time feed on dashboard)
        if registry.hub:
            registry.hub.table("agent_audit_logs").insert({
                "agent_name": task.agent_name,
                "message": f"Task Status Update: {task.status}",
                "metadata": {"task_id": task.id, "status": task.status}
            }).execute()
        print(f"📡 [REALTIME] Task {task.id} ({task.agent_name}) -> {task.status}")

    # For POC, we run this in the background
    # In production, this would be a separate worker/queue
    import asyncio
    asyncio.create_task(task_orchestrator.run_simulation(current_approval.tasks, system_config, status_callback))
    
    return {"status": "Build approved and started"}

import httpx
import random

async def health_check_loop():
    """Background task to monitor LLM providers and ping webhooks."""
    while True:
        if system_config.get("webhook_url"):
            # Simple simulation: 1% chance a provider "goes down" for POC
            if random.random() < 0.01:
                engine = system_config["active_llm_engine"]
                print(f"⚠️ Provider {engine} health check failed! Pinging webhook...")
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(system_config["webhook_url"], json={
                            "event": "PROVIDER_DOWN",
                            "engine": engine,
                            "severity": "CRITICAL",
                            "message": f"Cloud provider {engine} is currently unresponsive."
                        })
                except Exception as e:
                    print(f"❌ Failed to ping webhook: {e}")
        
        await asyncio.sleep(60) # Check every minute

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(health_check_loop())

@app.get("/logic/download-bundle")
async def download_bundle():
    """Generates a ZIP of all artifacts from the latest build."""
    approval_id = "current_session"
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="No active build found")
    
    tasks = pending_approvals[approval_id].tasks
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for task in tasks:
            # Note: tasks are updated in-memory via the simulation background task
            if task.artifacts:
                for path, content in task.artifacts.items():
                    zip_file.writestr(path, content)
            elif task.output_artifact:
                # Fallback for single file tasks
                zip_file.writestr(f"{task.agent_name}/output.txt", task.output_artifact)
                
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": "attachment; filename=project_swarm_bundle.zip"
        }
    )
