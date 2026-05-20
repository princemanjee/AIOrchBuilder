from models import DataLayerSpec
from data_engine import agent_data


def test_generate_schema_handles_dict_columns():
    spec = DataLayerSpec(
        tables=[{"name": "tasks", "columns": [{"name": "title", "type": "text"}, {"name": "status", "type": "text"}]}],
        rls_policies=[],
    )
    sql = agent_data.generate_schema(spec)
    assert "CREATE TABLE IF NOT EXISTS public.tasks" in sql
    assert "title TEXT" in sql
    assert "status TEXT DEFAULT 'pending'" in sql


def test_generate_schema_still_handles_string_columns():
    spec = DataLayerSpec(
        tables=[{"name": "notes", "columns": ["title text", "body text"]}],
        rls_policies=[],
    )
    sql = agent_data.generate_schema(spec)
    assert "CREATE TABLE IF NOT EXISTS public.notes" in sql
    assert "title TEXT" in sql
