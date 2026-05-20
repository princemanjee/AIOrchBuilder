from llm_router import llm_router, ModelType


def test_phase_mapping_unchanged():
    assert llm_router.get_model_type_for_phase("04_BUILD") == ModelType.CODE
    assert llm_router.get_model_type_for_phase("01_ANALYSIS") == ModelType.SMART


def test_resolve_gateway_models_returns_ordered_list_with_fallbacks():
    models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", {})
    assert isinstance(models, list) and len(models) >= 2
    # primary is a code-capable model name ClaudeMCP understands
    assert models[0] == "claude-sonnet-4-5"
    # last resort is always a free local model
    assert models[-1].startswith("ollama:")


def test_config_can_override_primary_per_agent():
    cfg = {"gateway_model_overrides": {"AGENT_DATA": "gemini-1.5-pro"}}
    models = llm_router.resolve_gateway_models("04_BUILD", "AGENT_DATA", cfg)
    assert models[0] == "gemini-1.5-pro"


def test_smart_phase_routes_to_opus_class_model():
    models = llm_router.resolve_gateway_models("01_ANALYSIS", "AGENT_LOGIC", {})
    assert models[0] == "claude-opus-4-7"
