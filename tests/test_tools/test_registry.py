from mi_primer_proyecto_ia.config import Settings
from mi_primer_proyecto_ia.tools import registry
from mi_primer_proyecto_ia.tools.registry import build_default_tools


def test_default_tools_include_file_tools_when_workspace_exists(tmp_path):
    tools = build_default_tools(Settings(workspace_root=str(tmp_path)))

    assert [tool.name for tool in tools] == ["calculator", "list_files", "read_file"]


def test_file_tools_are_skipped_when_workspace_is_missing(tmp_path):
    tools = build_default_tools(Settings(workspace_root=str(tmp_path / "no_existe")))

    assert [tool.name for tool in tools] == ["calculator"]


def test_workspace_settings_are_applied_to_the_sandbox(tmp_path):
    (tmp_path / "a.log").write_text("x", encoding="utf-8")
    (tmp_path / "b.md").write_text("x" * 100, encoding="utf-8")
    settings = Settings(
        workspace_root=str(tmp_path),
        workspace_allowed_extensions=[".md"],
        workspace_max_read_bytes=10,
    )
    _, list_tool, read_tool = build_default_tools(settings)

    assert '"path": "b.md"' in list_tool.run() and "a.log" not in list_tool.run()
    assert '"truncated": true' in read_tool.run(path="b.md")


def test_registered_tool_schemas_are_valid_and_unique(tmp_path):
    tools = build_default_tools(Settings(workspace_root=str(tmp_path)))

    names = [tool.name for tool in tools]
    assert len(names) == len(set(names))
    for tool in tools:
        assert tool.description
        assert tool.input_schema["type"] == "object"
        assert tool.input_schema["additionalProperties"] is False


def test_global_registry_exposes_schemas_and_lookup():
    schemas = registry.get_tool_schemas()
    names = {schema["name"] for schema in schemas}

    assert "calculator" in names
    for schema in schemas:
        assert set(schema) == {"name", "description", "input_schema"}
        assert registry.get_tool(schema["name"]).name == schema["name"]
