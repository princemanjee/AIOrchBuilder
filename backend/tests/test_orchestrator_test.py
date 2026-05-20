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
async def test_test_agent_uses_llm_unit_tests_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, table_name, api_layer, data_layer, project_name, provider, models):
        return f"# LLM UNIT TESTS for {table_name}\nimport pytest"

    monkeypatch.setattr("test_engine.agent_test.generate_unit_tests_llm", fake_llm.__get__(__import__("test_engine").agent_test))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_TEST", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM UNIT TESTS for tasks" in task.artifacts["backend/tests/test_tasks.py"]
    # e2e + workflow still produced deterministically
    assert "tests/e2e/basic.spec.js" in task.artifacts
    assert ".github/workflows/e2e.yml" in task.artifacts


@pytest.mark.asyncio
async def test_test_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, table_name, api_layer, data_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("test_engine.agent_test.generate_unit_tests_llm", boom.__get__(__import__("test_engine").agent_test))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_TEST", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert len(task.artifacts["backend/tests/test_tasks.py"]) > 0
