from providers.factory import provider_factory
from providers.anthropic_gateway import AnthropicGatewayProvider


def test_factory_returns_gateway_provider_for_any_engine():
    provider_factory._providers.clear()
    cfg = {"gateway_url": "http://localhost:3210", "gateway_api_key": "k", "gateway_default_max_tokens": 2048}
    p = provider_factory.get_provider("AGENT_DATA", cfg)
    assert isinstance(p, AnthropicGatewayProvider)
    assert p.base_url == "http://localhost:3210"
    assert p.api_key == "k"
    assert p.default_max_tokens == 2048


def test_factory_caches_single_instance():
    provider_factory._providers.clear()
    cfg = {"gateway_url": "http://localhost:3210", "gateway_api_key": "k"}
    a = provider_factory.get_provider("AGENT_DATA", cfg)
    b = provider_factory.get_provider("AGENT_UI", cfg)
    assert a is b  # one transport for everything


def test_factory_defaults_url_and_key_when_missing():
    provider_factory._providers.clear()
    p = provider_factory.get_provider("anything", {})
    assert p.base_url == "http://localhost:3210"
    assert p.api_key == ""
