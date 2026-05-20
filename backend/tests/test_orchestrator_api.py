import pytest
from models import ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec, AgentTask
from orchestrator import task_orchestrator


def _blueprint():
    return ArchitectureBlueprint(
        project_name="demo",
        description="d",
        data_layer=DataLayerSpec(tables=[{"name": "tasks", "columns": []}], rls_policies=[]),
        api_layer=APILayerSpec(endpoints=[{"method": "GET", "path": "/tasks"}], middleware=[]),
        ui_layer=UILayerSpec(pages=[], components=[], style_guide={}),
        reasoning="r",
    )


@pytest.mark.asyncio
async def test_api_agent_uses_llm_router_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, api_layer, data_layer, project_name, provider, models):
        return "# LLM ROUTER\nfrom fastapi import APIRouter"

    monkeypatch.setattr("api_engine.agent_api.generate_router_llm", fake_llm.__get__(__import__("api_engine").agent_api))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_API", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM ROUTER" in task.artifacts["backend/routers/main.py"]
    # boilerplate files still produced deterministically
    assert "backend/main.py" in task.artifacts
    assert "backend/models.py" in task.artifacts


@pytest.mark.asyncio
async def test_api_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, api_layer, data_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("api_engine.agent_api.generate_router_llm", boom.__get__(__import__("api_engine").agent_api))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_API", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    # deterministic router still present (non-empty)
    assert len(task.artifacts["backend/routers/main.py"]) > 0
