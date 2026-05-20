import pytest
from models import ArchitectureBlueprint, DataLayerSpec, APILayerSpec, UILayerSpec, AgentTask
from orchestrator import task_orchestrator


def _blueprint():
    return ArchitectureBlueprint(
        project_name="demo",
        description="d",
        data_layer=DataLayerSpec(tables=[{"name": "tasks", "columns": []}], rls_policies=[]),
        api_layer=APILayerSpec(endpoints=[], middleware=[]),
        ui_layer=UILayerSpec(pages=["home"], components=["TaskCard"], style_guide={"primary": "#fff"}),
        reasoning="r",
    )


@pytest.mark.asyncio
async def test_ui_agent_uses_llm_component_when_generation_succeeds(monkeypatch):
    async def fake_llm(self, component_name, ui_layer, project_name, provider, models):
        return f"// LLM COMPONENT {component_name}\nexport default function C() {{}}"

    monkeypatch.setattr("ui_engine.agent_ui.generate_component_llm", fake_llm.__get__(__import__("ui_engine").agent_ui))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_UI", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert "LLM COMPONENT TaskCard" in task.artifacts["frontend/src/components/TaskCard.jsx"]
    # boilerplate + a page still produced deterministically
    assert "frontend/package.json" in task.artifacts
    assert "frontend/src/app/home/page.jsx" in task.artifacts


@pytest.mark.asyncio
async def test_ui_agent_falls_back_to_deterministic_on_llm_failure(monkeypatch):
    async def boom(self, component_name, ui_layer, project_name, provider, models):
        raise RuntimeError("gateway down")

    monkeypatch.setattr("ui_engine.agent_ui.generate_component_llm", boom.__get__(__import__("ui_engine").agent_ui))

    task_orchestrator.current_blueprint = _blueprint()
    task = AgentTask(id="t1", agent_name="AGENT_UI", task_description="d")

    async def cb(t):
        pass

    await task_orchestrator.run_simulation([task], {"gateway_url": "http://x", "gateway_api_key": "k"}, cb)

    assert task.status == "complete"
    assert len(task.artifacts["frontend/src/components/TaskCard.jsx"]) > 0
