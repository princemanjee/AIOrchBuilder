import pytest
from models import ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec, AgentTask
from orchestrator import task_orchestrator


def _blueprint():
    return ArchitectureBlueprint(
        project_name="demo",
        description="d",
        data_layer=DataLayerSpec(tables=[{"name": "tasks", "columns": []}], rls_policies=[]),
        api_layer=APILayerSpec(endpoints=[], middleware=[]),
        ui_layer=UILayerSpec(pages=[], components=[], style_guide={"primary": "#fff"}),
        reasoning="r",
    )


@pytest.mark.asyncio
async def test_auth_agent_uses_llm_middleware_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, data_layer, project_name, provider, models):
        return "# LLM AUTH MIDDLEWARE\nfrom fastapi import Request"

    monkeypatch.setattr("auth_engine.agent_auth.generate_auth_middleware_llm", fake_llm.__get__(__import__("auth_engine").agent_auth))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_AUTH", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM AUTH MIDDLEWARE" in task.artifacts["backend/middleware/auth.py"]
    # RLS policy + login still produced deterministically
    assert "supabase/policies/tasks.sql" in task.artifacts
    assert "frontend/src/components/Login.jsx" in task.artifacts


@pytest.mark.asyncio
async def test_auth_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, data_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("auth_engine.agent_auth.generate_auth_middleware_llm", boom.__get__(__import__("auth_engine").agent_auth))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_AUTH", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert len(task.artifacts["backend/middleware/auth.py"]) > 0
