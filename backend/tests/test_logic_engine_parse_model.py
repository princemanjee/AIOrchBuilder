import pytest
from logic_engine import agent_logic
import providers.factory as factory_mod


class _CaptureProvider:
    def __init__(self):
        self.model = None

    def name(self):
        return "capture"

    async def generate(self, prompt, system_prompt="", model=None, **kwargs):
        self.model = model
        # Return minimal valid blueprint JSON so parse() succeeds.
        return (
            '{"project_name":"demo","description":"d",'
            '"data_layer":{"tables":[],"rls_policies":[]},'
            '"api_layer":{"endpoints":[],"middleware":[]},'
            '"ui_layer":{"pages":[],"components":[],"style_guide":{}},'
            '"reasoning":"r"}'
        )


@pytest.mark.asyncio
async def test_parse_sends_claude_model_to_gateway(monkeypatch):
    cap = _CaptureProvider()
    monkeypatch.setattr(factory_mod.provider_factory, "get_provider", lambda engine, config: cap)

    from models import RequirementRequest
    cfg = {"multi_llm_orchestration": True, "active_llm_engine": "Ollama (Local/Remote)", "active_model": "llama3"}
    bp = await agent_logic.parse(RequirementRequest(prompt="build a todo app"), cfg)

    assert bp.project_name == "demo"
    # The model sent to the gateway must be a ClaudeMCP-routable Claude name, not an Ollama name.
    assert cap.model.startswith("claude-"), f"expected claude- model, got {cap.model}"
