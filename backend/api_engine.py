# File: backend/api_engine.py
from typing import List, Dict, Any, Optional
from models import ArchitectureBlueprint, APILayerSpec

class APIEngine:
    """
    AGENT_API core logic.
    Generates modular FastAPI code based on the data layer and architectural bluepint.
    """
    
    def generate_models(self, tables: List[Dict[str, Any]]) -> str:
        """Generates Pydantic models for the API."""
        code = "from pydantic import BaseModel\nfrom typing import Optional, List\nfrom datetime import datetime\nfrom uuid import UUID\n\n"
        
        for table in tables:
            name = table["name"].capitalize().rstrip('s')
            code += f"class {name}Base(BaseModel):\n"
            for col in table.get("columns", []):
                col_name = col.split(' ')[0]
                # Defaulting to Optional[str] for simplicity in POC
                code += f"    {col_name}: Optional[str] = None\n"
            code += "    created_at: Optional[datetime] = None\n\n"
            
            code += f"class {name}Create({name}Base):\n    pass\n\n"
            code += f"class {name}({name}Base):\n    id: UUID\n\n    class Config:\n        from_attributes = True\n\n"
            
        return code

    def generate_router(self, project_name: str, tables: List[Dict[str, Any]]) -> str:
        """Generates a modular FastAPI router for a specific resource."""
        # For simplicity in this POC, we generate one router that includes endpoints for all tables
        # Following best practices for Modular approach
        code = f"from fastapi import APIRouter, HTTPException, Depends\nfrom typing import List\nfrom models import *\n\nrouter = APIRouter(prefix='/{project_name.lower()}', tags=['{project_name}'])\n\n"
        
        for table in tables:
            resource = table["name"]
            model_name = resource.capitalize().rstrip('s')
            
            # GET List
            code += f"@router.get('/{resource}', response_model=List[{model_name}])\n"
            code += f"async def list_{resource}():\n    # Logic to fetch from satellite instance\n    return []\n\n"
            
            # POST Create
            code += f"@router.post('/{resource}', response_model={model_name})\n"
            code += f"async def create_{resource}(item: {model_name}Create):\n    # Logic to insert into satellite instance\n    return item\n\n"
            
            # GET Item
            code += f"@router.get('/{resource}/{{id}}', response_model={model_name})\n"
            code += f"async def get_{resource}(id: str):\n    # Logic to fetch single record\n    return {{}}\n\n"
            
        return code

    def generate_main(self, project_name: str) -> str:
        """Generates the main entry point for the satellite backend."""
        code = f"from fastapi import FastAPI\nfrom routers.main import router\n\napp = FastAPI(title='{project_name} API')\n\napp.include_router(router)\n\n@app.get('/')\nasync def root():\n    return {{'message': 'Welcome to {project_name} API'}}\n"
        return code

    def generate_requirements(self) -> str:
        return """fastapi==0.104.1
uvicorn==0.24.0.post1
pydantic==2.5.2
pydantic-settings==2.1.0
supabase==2.3.0
python-dotenv==1.0.0
"""

    def generate_dockerfile(self) -> str:
        return """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

    async def generate_router_llm(self, api_layer, data_layer, project_name: str, provider, models) -> str:
        """LLM-driven FastAPI router generation with real Supabase CRUD. Falls back
        to the deterministic generate_router at the call site on failure."""
        from agent_specs import get_spec
        from llm_client import agent_generate

        spec = get_spec("AGENT_API")
        context = {
            "project_name": project_name,
            "api_layer": api_layer.dict() if hasattr(api_layer, "dict") else api_layer,
            "data_layer": data_layer.dict() if hasattr(data_layer, "dict") else data_layer,
        }
        instruction = (
            "Generate a FastAPI APIRouter module implementing every endpoint above "
            "with REAL Supabase CRUD against the given schema. Honor the HARD RULES "
            "in your system prompt (auth dependency on every endpoint, Pydantic "
            "validation, no stub returns)."
        )
        return await agent_generate(
            provider,
            models=models,
            system_prompt=spec["system_prompt"],
            context=context,
            instruction=instruction,
        )

agent_api = APIEngine()
