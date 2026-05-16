# File: backend/models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DataLayerSpec(BaseModel):
    tables: List[Dict[str, Any]] = Field(description="SQL Table definitions including columns and types")
    rls_policies: List[str] = Field(description="Row Level Security policy descriptions")

class APILayerSpec(BaseModel):
    endpoints: List[Dict[str, Any]] = Field(description="REST API endpoint definitions (method, path, params)")
    middleware: List[str] = Field(description="Security, Logging, or Auth middleware requirements")

class UILayerSpec(BaseModel):
    pages: List[str] = Field(description="List of primary pages/routes to generate")
    components: List[str] = Field(description="Key reusable UI components needed")
    style_guide: Dict[str, str] = Field(description="Core color palette and typography tokens")

class ArchitectureBlueprint(BaseModel):
    project_name: str
    description: str
    target_platform: str = "web"
    data_layer: DataLayerSpec
    api_layer: APILayerSpec
    ui_layer: UILayerSpec
    reasoning: str = Field(description="The orchestrator's logic for these architectural choices")

class RequirementRequest(BaseModel):
    prompt: str
    context: Optional[Dict[str, Any]] = None

class AgentTask(BaseModel):
    id: str
    agent_name: str
    task_description: str
    dependencies: List[str] = []
    status: str = "pending" # pending, in_progress, complete, failed
    output_artifact: Optional[str] = None # Legacy/Single file
    artifacts: Dict[str, str] = {} # Path -> Content mapping for multiple files

class TaskList(BaseModel):
    tasks: List[AgentTask]

class ApprovalRequest(BaseModel):
    blueprint: ArchitectureBlueprint
    tasks: List[AgentTask]
    approved: bool = False
    comments: Optional[str] = None
