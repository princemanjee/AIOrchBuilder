import pytest
from models import DataLayerSpec
from data_engine import agent_data


class _StubProvider:
    async def generate(self, prompt, system_prompt="", model=None, **kwargs):
        # Echo proof that context reached the model + return plausible SQL.
        assert "tasks" in prompt  # table name from the spec made it in
        return "CREATE TABLE public.tasks (id uuid primary key);"

    def name(self):
        return "stub"


@pytest.mark.asyncio
async def test_generate_schema_llm_calls_model_with_context():
    data_layer = DataLayerSpec(
        tables=[{"name": "tasks", "columns": [{"name": "title", "type": "text"}]}],
        rls_policies=["Users see own tasks"],
    )
    sql = await agent_data.generate_schema_llm(
        data_layer, project_name="demo", provider=_StubProvider(), models=["m1"]
    )
    assert "CREATE TABLE" in sql
