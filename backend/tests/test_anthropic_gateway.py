import httpx
import respx
import pytest
from providers.anthropic_gateway import AnthropicGatewayProvider

GATEWAY = "http://localhost:3210"


@pytest.mark.asyncio
@respx.mock
async def test_generate_sends_anthropic_shape_and_parses_text():
    route = respx.post(f"{GATEWAY}/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={"content": [{"type": "text", "text": "SELECT 1;"}]},
        )
    )
    provider = AnthropicGatewayProvider(GATEWAY, "secret-key", default_max_tokens=512)

    out = await provider.generate(
        prompt="make a schema",
        system_prompt="you are AGENT_DATA",
        model="claude-sonnet-4-5",
    )

    assert out == "SELECT 1;"
    assert route.called
    assert route.calls.last.request.headers["x-api-key"] == "secret-key"
    import json as _json
    payload = _json.loads(route.calls.last.request.content)
    assert payload["model"] == "claude-sonnet-4-5"
    assert payload["system"] == "you are AGENT_DATA"
    assert payload["messages"] == [{"role": "user", "content": "make a schema"}]
    assert payload["max_tokens"] == 512
    assert "thinking" not in payload


@pytest.mark.asyncio
@respx.mock
async def test_generate_concatenates_multiple_text_blocks():
    respx.post(f"{GATEWAY}/v1/messages").mock(
        return_value=httpx.Response(
            200,
            json={"content": [
                {"type": "text", "text": "part1 "},
                {"type": "tool_use", "id": "x", "name": "n", "input": {}},
                {"type": "text", "text": "part2"},
            ]},
        )
    )
    provider = AnthropicGatewayProvider(GATEWAY, "secret-key")
    out = await provider.generate(prompt="p", model="claude-code-cli")
    assert out == "part1 part2"


@pytest.mark.asyncio
@respx.mock
async def test_generate_raises_on_http_error():
    respx.post(f"{GATEWAY}/v1/messages").mock(return_value=httpx.Response(401, json={"error": "bad key"}))
    provider = AnthropicGatewayProvider(GATEWAY, "wrong-key")
    with pytest.raises(httpx.HTTPStatusError):
        await provider.generate(prompt="p", model="claude-code-cli")
