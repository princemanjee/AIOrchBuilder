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
async def test_data_agent_uses_llm_output_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, data_layer, project_name, provider, models):
        return "-- LLM SQL\nCREATE TABLE tasks();"

    monkeypatch.setattr("data_engine.agent_data.generate_schema_llm", fake_llm.__get__(__import__("data_engine").agent_data))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_DATA", task_description="d")
    seen = []

    async def cb(t):
        seen.append(t.status)

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM SQL" in task.artifacts["supabase/migrations/01_init.sql"]
    assert seen == ["in_progress", "complete"]


@pytest.mark.asyncio
async def test_data_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, data_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("data_engine.agent_data.generate_schema_llm", boom.__get__(__import__("data_engine").agent_data))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_DATA", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    # Deterministic generator still produces valid SQL; build does not crash.
    assert task.status == "complete"
    assert "CREATE TABLE" in task.artifacts["supabase/migrations/01_init.sql"]
