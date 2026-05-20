import pytest
from llm_client import agent_generate


class _StubProvider:
    def __init__(self, behavior):
        self.behavior = behavior  # dict model -> "text" | Exception
        self.calls = []

    def name(self):
        return "stub"

    async def generate(self, prompt, system_prompt="", model=None, **kwargs):
        self.calls.append(model)
        result = self.behavior[model]
        if isinstance(result, Exception):
            raise result
        return result


@pytest.mark.asyncio
async def test_uses_first_model_when_it_succeeds():
    provider = _StubProvider({"m1": "OK"})
    text = await agent_generate(
        provider, models=["m1", "m2"], system_prompt="sys",
        context={"project_name": "demo"}, instruction="go",
    )
    assert text == "OK"
    assert provider.calls == ["m1"]


@pytest.mark.asyncio
async def test_falls_back_to_next_model_on_failure():
    provider = _StubProvider({"m1": RuntimeError("down"), "m2": "OK2"})
    text = await agent_generate(
        provider, models=["m1", "m2"], system_prompt="sys",
        context={"project_name": "demo"}, instruction="go",
    )
    assert text == "OK2"
    assert provider.calls == ["m1", "m2"]


@pytest.mark.asyncio
async def test_raises_when_all_models_fail():
    provider = _StubProvider({"m1": RuntimeError("a"), "m2": RuntimeError("b")})
    with pytest.raises(RuntimeError):
        await agent_generate(
            provider, models=["m1", "m2"], system_prompt="sys",
            context={}, instruction="go",
        )


@pytest.mark.asyncio
async def test_context_is_serialized_into_the_prompt():
    captured = {}

    class _Capture(_StubProvider):
        async def generate(self, prompt, system_prompt="", model=None, **kwargs):
            captured["prompt"] = prompt
            return "OK"

    provider = _Capture({"m1": "OK"})
    await agent_generate(
        provider, models=["m1"], system_prompt="sys",
        context={"project_name": "demo", "data_layer": {"tables": []}},
        instruction="Generate the schema.",
    )
    assert "demo" in captured["prompt"]
    assert "Generate the schema." in captured["prompt"]
