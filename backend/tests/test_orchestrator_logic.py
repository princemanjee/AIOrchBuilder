import pytest
from models import ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec, AgentTask
from orchestrator import task_orchestrator


def _blueprint():
    return ArchitectureBlueprint(
        project_name="demo",
        description="d",
        data_layer=DataLayerSpec(tables=[{"name": "tasks", "columns": []}], rls_policies=[]),
        api_layer=APILayerSpec(endpoints=[], middleware=[]),
        ui_layer=UILayerSpec(pages=[], components=[], style_guide={}),
        reasoning="r",
    )


@pytest.mark.asyncio
async def test_logic_agent_uses_llm_service_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, table_name, data_layer, api_layer, project_name, description, provider, models):
        return f"# LLM SERVICE for {table_name}\nclass Service: pass"

    monkeypatch.setattr("logic_engine.agent_logic.generate_backend_logic_llm", fake_llm.__get__(__import__("logic_engine").agent_logic))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_LOGIC", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM SERVICE for tasks" in task.artifacts["backend/services/tasks_service.py"]
    # frontend hook + docs still produced deterministically
    assert any(k.startswith("frontend/src/hooks/use") for k in task.artifacts)
    assert "README.md" in task.artifacts


@pytest.mark.asyncio
async def test_logic_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, table_name, data_layer, api_layer, project_name, description, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("logic_engine.agent_logic.generate_backend_logic_llm", boom.__get__(__import__("logic_engine").agent_logic))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_LOGIC", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert len(task.artifacts["backend/services/tasks_service.py"]) > 0
