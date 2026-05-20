from typing import List, Dict, Any, Optional
from models import ArchitectureBlueprint, AgentTask, TaskList
from data_engine import agent_data
from api_engine import agent_api
from ui_engine import agent_ui
from logic_engine import agent_logic
from doc_engine import doc_engine
from providers.factory import provider_factory
from llm_router import llm_router, ModelType
from llm_client import agent_generate  # noqa: F401  (used by engines)
from auth_engine import agent_auth
from test_engine import agent_test
import uuid
import asyncio

class TaskOrchestrator:
    """
    Decomposes an ArchitectureBlueprint into discrete tasks for specialized agents.
    """
    
    def __init__(self):
        self.current_blueprint: Optional[ArchitectureBlueprint] = None

    def decompose(self, blueprint: ArchitectureBlueprint) -> List[AgentTask]:
        self.current_blueprint = blueprint
        tasks = []
        
        # 1. DATA LAYER TASKS
        data_task_id = f"task_data_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=data_task_id,
            agent_name="AGENT_DATA",
            task_description=f"Generate SQL schema and RLS policies for: {', '.join([t['name'] for t in blueprint.data_layer.tables])}.",
            dependencies=[]
        ))
        
        # 2. API LAYER TASKS
        api_task_id = f"task_api_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=api_task_id,
            agent_name="AGENT_API",
            task_description=f"Construct FastAPI endpoints for: {', '.join([e['path'] for e in blueprint.api_layer.endpoints])}. Ensure Auth middleware is integrated.",
            dependencies=[data_task_id]
        ))
        
        # 3. UI LAYER TASKS
        ui_task_id = f"task_ui_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=ui_task_id,
            agent_name="AGENT_UI",
            task_description=f"Build React pages ({', '.join(blueprint.ui_layer.pages)}) and components ({', '.join(blueprint.ui_layer.components)}) using the style guide: {blueprint.ui_layer.style_guide}.",
            dependencies=[api_task_id]
        ))
        
        # 4. Auth/Logic Deployment
        auth_task_id = f"task_auth_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=auth_task_id,
            agent_name="AGENT_AUTH",
            task_description="Implement Supabase Auth, RBAC, and Login UI",
            dependencies=[data_task_id, api_task_id, ui_task_id]
        ))

        # 5. Testing Phase
        test_task_id = f"task_test_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=test_task_id,
            agent_name="AGENT_TEST",
            task_description="Execute Unit Tests and E2E Browser Tests",
            dependencies=[auth_task_id]
        ))

        # 6. LOGIC LAYER TASKS (Integration)
        logic_task_id = f"task_logic_{uuid.uuid4().hex[:8]}"
        tasks.append(AgentTask(
            id=logic_task_id,
            agent_name="AGENT_LOGIC",
            task_description="Assemble business logic and integration functions",
            dependencies=[ui_task_id, api_task_id, auth_task_id, test_task_id]
        ))
        
        return tasks

    async def run_simulation(self, tasks: List[AgentTask], config: Dict[str, Any], callback):
        """
        Simulates the swarm working on tasks.
        Respects agent-to-provider mappings and handles dynamic selection.
        """
        active_engine = config.get("active_llm_engine", "Ollama (Local/Remote)")
        
        for task in tasks:
            # Determine Mapping
            mapping = config.get("agent_mappings", {}).get(task.agent_name, "Dynamic")
            engine = mapping if mapping != "Dynamic" else active_engine
            
            # Use Router to determine model type and resolve actual model
            # For build phase, we use ModelType.CODE or ModelType.BALANCED
            phase_name = "04_BUILD" # Default build phase for tasks
            if task.agent_name == "AGENT_TEST": phase_name = "05_VALIDATION"
            
            model_type = llm_router.get_model_type_for_phase(phase_name)
            model = llm_router.resolve_actual_model(model_type, engine)
            
            # Get the actual provider instance (Verify connectivity)
            provider = provider_factory.get_provider(engine, config)
            print(f"🤖 Agent {task.agent_name} executing on {engine} ({model})...")
            
            task.status = "in_progress"
            await callback(task)
            
            # --- REAL ARTIFACT GENERATION ---
            if task.agent_name == "AGENT_DATA" and self.current_blueprint:
                models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", config)
                try:
                    sql = await agent_data.generate_schema_llm(
                        self.current_blueprint.data_layer,
                        self.current_blueprint.project_name,
                        provider,
                        models,
                    )
                    print(f"📁 LLM-generated SQL for {task.agent_name}")
                except Exception as e:
                    print(f"⚠️ LLM schema generation failed ({e}); using deterministic fallback.")
                    sql = agent_data.generate_schema(self.current_blueprint.data_layer)
                task.artifacts = {
                    "supabase/migrations/01_init.sql": sql,
                    "supabase/seed.sql": agent_data.generate_seed_data(self.current_blueprint.data_layer),
                }
                task.output_artifact = sql
            
            if task.agent_name == "AGENT_API" and self.current_blueprint:
                models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_API", config)
                try:
                    router_code = await agent_api.generate_router_llm(
                        self.current_blueprint.api_layer,
                        self.current_blueprint.data_layer,
                        self.current_blueprint.project_name,
                        provider,
                        models,
                    )
                    print(f"📁 LLM-generated API router for {task.agent_name}")
                except Exception as e:
                    print(f"⚠️ LLM API generation failed ({e}); using deterministic fallback.")
                    router_code = agent_api.generate_router(
                        self.current_blueprint.project_name, self.current_blueprint.data_layer.tables
                    )
                task.artifacts = {
                    "backend/requirements.txt": agent_api.generate_requirements(),
                    "backend/Dockerfile": agent_api.generate_dockerfile(),
                    "backend/models.py": agent_api.generate_models(self.current_blueprint.data_layer.tables),
                    "backend/routers/main.py": router_code,
                    "backend/main.py": agent_api.generate_main(self.current_blueprint.project_name),
                }
                task.output_artifact = task.artifacts["backend/main.py"]

            if task.agent_name == "AGENT_UI" and self.current_blueprint:
                ui_artifacts = {
                    "frontend/package.json": agent_ui.generate_package_json(self.current_blueprint.project_name),
                    "frontend/Dockerfile": agent_ui.generate_dockerfile(),
                    "frontend/next.config.js": agent_ui.generate_next_config(),
                    "frontend/src/app/layout.jsx": agent_ui.generate_layout(self.current_blueprint.ui_layer.style_guide, self.current_blueprint.ui_layer.pages)
                }
                # Generate Components
                for comp in self.current_blueprint.ui_layer.components:
                    ui_artifacts[f"frontend/src/components/{comp}.jsx"] = agent_ui.generate_component(comp, self.current_blueprint.ui_layer.style_guide)
                # Generate Pages
                for page in self.current_blueprint.ui_layer.pages:
                    ui_artifacts[f"frontend/src/app/{page.lower()}/page.jsx"] = agent_ui.generate_page(page, self.current_blueprint.ui_layer.components, self.current_blueprint.ui_layer.style_guide)
                
                task.artifacts = ui_artifacts
                task.output_artifact = list(ui_artifacts.values())[0] if ui_artifacts else ""
                print(f"📁 Generated UI code for {task.agent_name}")

            if task.agent_name == "AGENT_LOGIC" and self.current_blueprint:
                logic_artifacts = {}
                for table in self.current_blueprint.data_layer.tables:
                    name = table["name"]
                    # Generate BOTH strategies as requested
                    logic_artifacts[f"frontend/src/hooks/use{name.capitalize().rstrip('s')}.js"] = agent_logic.generate_frontend_logic(name)
                    logic_artifacts[f"backend/services/{name}_service.py"] = agent_logic.backend_logic_simulation(name) if hasattr(agent_logic, 'backend_logic_simulation') else agent_logic.generate_backend_logic(name)
                
                # Add Success Artifacts (for the final logic phase/integration)
                logic_artifacts["README.md"] = doc_engine.generate_readme(self.current_blueprint.project_name, self.current_blueprint.description)
                logic_artifacts["DEPLOY.md"] = doc_engine.generate_deploy_guide()
                logic_artifacts["docker-compose.yml"] = doc_engine.generate_docker_compose(self.current_blueprint.project_name)
                logic_artifacts["install.sh"] = doc_engine.generate_install_script()
                
                task.artifacts = logic_artifacts
                task.output_artifact = logic_artifacts["README.md"]
                print(f"📁 Generated Logic & Success Artifacts for {task.agent_name}")

            if task.agent_name == "AGENT_AUTH" and self.current_blueprint:
                auth_artifacts = {
                    "backend/middleware/auth.py": agent_auth.generate_auth_middleware(),
                    "frontend/src/components/Login.jsx": agent_auth.generate_login_ui(self.current_blueprint.ui_layer.style_guide.get("primary", "#00f3ff"))
                }
                # Create policies for all tables
                for table in self.current_blueprint.data_layer.tables:
                    auth_artifacts[f"supabase/policies/{table['name']}.sql"] = agent_auth.generate_rls_sql(table['name'])
                
                task.artifacts = auth_artifacts
                task.output_artifact = auth_artifacts["frontend/src/components/Login.jsx"]
                print(f"📁 Generated Auth & Security Artifacts for {task.agent_name}")

            if task.agent_name == "AGENT_TEST" and self.current_blueprint:
                test_artifacts = {
                    "tests/e2e/basic.spec.js": agent_test.generate_e2e_tests(self.current_blueprint.project_name),
                    ".github/workflows/e2e.yml": agent_test.generate_github_workflow()
                }
                for table in self.current_blueprint.data_layer.tables:
                    test_artifacts[f"backend/tests/test_{table['name']}.py"] = agent_test.generate_unit_tests(table['name'])
                
                task.artifacts = test_artifacts
                task.output_artifact = list(test_artifacts.values())[0]
                print(f"📁 Generated Testing Artifacts for {task.agent_name}")
            
            task.status = "complete"
            await callback(task)

task_orchestrator = TaskOrchestrator()
