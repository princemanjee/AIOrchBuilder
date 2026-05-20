from agent_specs import AGENT_SPECS, get_spec


def test_every_build_agent_has_a_spec():
    for agent in ["AGENT_DATA", "AGENT_API", "AGENT_UI", "AGENT_AUTH", "AGENT_TEST", "AGENT_LOGIC"]:
        spec = get_spec(agent)
        assert spec["phase"]
        assert "AGENT" in spec["system_prompt"]
        assert isinstance(spec["context_keys"], list)


def test_data_spec_requests_sql_and_rls():
    spec = get_spec("AGENT_DATA")
    sp = spec["system_prompt"].lower()
    assert "sql" in sp and "rls" in sp


def test_unknown_agent_raises():
    import pytest
    with pytest.raises(KeyError):
        get_spec("AGENT_NOPE")
