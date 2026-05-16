# File: backend/logic_engine.py
import json
from typing import Dict, Any, Optional
from models import ArchitectureBlueprint, RequirementRequest
from llm_router import llm_router, ModelType
from providers.factory import provider_factory

class RequirementParser:
    """
    Core engine for AGENT_LOGIC. 
    Transforms free-form text into a structured ARCHITECTURE_BLUEPRINT.
    """
    
    def __init__(self):
        self.phase = "01_ANALYSIS"

    async def parse(self, request: RequirementRequest, config: Optional[Dict[str, Any]] = None) -> ArchitectureBlueprint:
        if not config:
            from main import system_config as config
            
        model_type = llm_router.get_model_type_for_phase(self.phase)
        engine = config.get("active_llm_engine", "Ollama (Local/Remote)")
        model = config.get("active_model", "llama3")
        
        # Resolve specialized model if it's a dynamic routing scenario
        if config.get("multi_llm_orchestration"):
            model = llm_router.resolve_actual_model(model_type, engine)
        
        provider = provider_factory.get_provider(engine, config)
        
        print(f"🧠 Routing to {engine} ({model}) for requirement parsing...")
        
        system_prompt = """
        You are the AGENT_LOGIC orchestrator for AIOrchBuilder. 
        Your task is to transform a user's app idea into a technical ARCHITECTURE_BLUEPRINT.
        
        Requirements:
        1. project_name: A slug-style name (e.g. 'task_manager').
        2. description: A clear 1-2 sentence overview.
        3. data_layer: Define tables (columns, types) and basic RLS policies.
        4. api_layer: Define REST endpoints (method, path) and needed middleware.
        5. ui_layer: Define primary pages, key components, and a style_guide (hex colors).
        6. reasoning: Explain why you chose this architecture.

        IMPORTANT: ALWAYS return ONLY valid JSON matching the requested schema. No conversational filler.
        """
        
        prompt = f"User Request: {request.prompt}\n\nReturn the ArchitectureBlueprint JSON:"
        
        try:
            response_text = await provider.generate(
                prompt=prompt, 
                system_prompt=system_prompt,
                model=model
            )
            
            # Clean response text in case LLM adds markdown blocks
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = response_text.strip()
                
            blueprint_data = json.loads(json_str)
            return ArchitectureBlueprint(**blueprint_data)
            
        except Exception as e:
            print(f"❌ LLM Parsing Error: {e}")
            # Fallback to mock for robustness during testing if needed, or raise
            raise e

    def generate_frontend_logic(self, table_name: str) -> str:
        """Generates a React Hook for state management."""
        name = table_name.capitalize().rstrip('s')
        return f"""// File: hooks/use{name}.js
import { 'useState', 'useEffect' } from 'react';
import { 'supabase' } from '../lib/supabase';

export const use{name} = () => {{
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {{
        const fetch{name} = async () => {{
            const {{ data, error }} = await supabase.from('{table_name}').select('*');
            if (!error) setData(data);
            setLoading(false);
        }};
        fetch{name}();
    }}, []);

    return {{ data, loading }};
}};
"""

    def generate_backend_logic(self, table_name: str) -> str:
        """Generates a Service Layer for business logic."""
        name = table_name.capitalize().rstrip('s')
        return f"""# File: services/{table_name}_service.py
from typing import List
from models import {name}

class {name}Service:
    @staticmethod
    async def process_business_rules(data: {name}):
        # Custom business logic implementation
        print(f"Processing rules for {name}")
        return data

    @staticmethod
    async def validate_integrity(items: List[{name}]):
        return True
"""

agent_logic = RequirementParser()
