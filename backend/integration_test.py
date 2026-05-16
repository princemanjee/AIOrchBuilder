import asyncio
import sys
import os
import json
import traceback

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import RequirementRequest, ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec
from logic_engine import agent_logic
from orchestrator import task_orchestrator
from main import system_config

async def main():
    print("🚀 Starting End-to-End Orchestrator Run...")
    
    # Load resume payload
    resume_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "no9-idea.json")
    resume_data = {}
    if os.path.exists(resume_path):
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_data = json.load(f)
        print(f"📄 Loaded resume payload: {len(json.dumps(resume_data))} bytes")
    else:
        print("⚠️ Warning: no9-idea.json not found. Proceeding with empty context.")

    request = RequirementRequest(
        prompt="Build a personalized digital portfolio and resume web application based on this JSON CV. Include a dashboard for tracking profile views.",
        context=resume_data
    )
    
    blueprint = None
    try:
        print("🧠 1. Attempting live parsing via AGENT_LOGIC LLM...")
        blueprint = await agent_logic.parse(request, system_config)
    except Exception as e:
        print(f"⚠️ Live LLM parsing failed (ensure Ollama is running): {e}")
        print("🔄 Falling back to mocked portfolio Blueprint for testing downstream engines...")
        
        # Determine some data from the resume to make it personalized
        user_name = resume_data.get("basics", {}).get("name", "User")
        project_slug = user_name.lower().replace(" ", "_").replace(".", "").replace("(", "").replace(")", "") + "_portfolio"
        
        import re
        roles = []
        for work in resume_data.get("work", [])[:3]:
            # Convert "UX Strategy & Digital Transformation Consultant" -> "RoleUxStrategyDigitalTransformationConsultant"
            pos = work.get('position', 'Role')
            safe_name = re.sub(r'[^a-zA-Z0-9]', ' ', pos).title().replace(' ', '')
            roles.append(f"RoleCard{safe_name}")
            
        blueprint = ArchitectureBlueprint(
            project_name=project_slug,
            description="A digital portfolio and resume web application with view tracking dashboard.",
            data_layer=DataLayerSpec(
                tables=[
                    {"name": "profile_views", "columns": ["viewer_ip string", "view_date timestamp", "page string"]},
                    {"name": "contact_messages", "columns": ["sender_name string", "sender_email string", "message text", "status string"]}
                ],
                rls_policies=[
                    "Public can insert profile_views",
                    "Public can insert contact_messages",
                    "Only admin can read contact_messages"
                ]
            ),
            api_layer=APILayerSpec(
                endpoints=[
                    {"method": "GET", "path": "/views"},
                    {"method": "POST", "path": "/messages"}
                ],
                middleware=["auth", "rate_limiting"]
            ),
            ui_layer=UILayerSpec(
                pages=["Home", "Resume", "Contact", "Dashboard"],
                components=["Hero", "ExperienceTimeline", "ContactForm", "AnalyticsChart"] + roles,
                style_guide={"primary": "#00f3ff", "secondary": "#111111", "text": "#ffffff"}
            ),
            reasoning="Mocked schema dynamically built from resume failure fallback."
        )
        print(f"✅ Fallback Blueprint Generated for project: {blueprint.project_name}")

    if not blueprint:
        print("❌ Critical Failure: Could not generate a blueprint.")
        return

    print("\n🧩 2. Task Decomposition (ORCHESTRATOR)...")
    tasks = task_orchestrator.decompose(blueprint)
    for t in tasks:
        print(f"  - [{t.agent_name}] {t.id} -> {t.task_description[:50]}...")
    print(f"✅ Decomposed into {len(tasks)} tasks.")
    
    print("\n⚙️ 3. Build Execution Simulation (ALL AGENTS)...")
    async def callback(task):
        print(f"  > [{task.agent_name}] Status updated to: {task.status}")
        
    await task_orchestrator.run_simulation(tasks, system_config, callback)
    
    print("\n📂 4. Persisting Artifacts to Disk...")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "portfolio_output")
    os.makedirs(output_dir, exist_ok=True)
    
    total_files = 0
    for task in tasks:
        if task.artifacts:
            for filepath, content in task.artifacts.items():
                # Some files might have directories (e.g. backend/models.py)
                full_path = os.path.join(output_dir, filepath)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as out:
                    out.write(content)
                total_files += 1
                
    print(f"🎉 Success! The AIOrchBuilder generated your app. {total_files} files written to: {output_dir}")

if __name__ == "__main__":
    asyncio.run(main())
