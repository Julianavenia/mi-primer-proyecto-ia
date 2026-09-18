import json

import pytest

from mi_primer_proyecto_ia.tools.list_files import ListFilesTool
from mi_primer_proyecto_ia.tools.read_file import UNTRUSTED_NOTICE, ReadFileTool
from mi_primer_proyecto_ia.tools.workspace import WorkspaceError, WorkspaceSandbox


@pytest.fixture
def sandbox(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "docs").mkdir(parents=True)
    (workspace / "nota.md").write_text("# Hola", encoding="utf-8")
    (workspace / "docs" / "guia.txt").write_text("guía", encoding="utf-8")
    return WorkspaceSandbox(workspace, [".txt", ".md", ".json", ".csv"], 8, 100)


def test_read_file_returns_structured_json(sandbox):
    payload = json.loads(ReadFileTool(sandbox).run(path="nota.md"))

    assert payload == {
        "path": "nota.md",
        "content": "# Hola",
        "size_bytes_returned": 6,
        "total_size_bytes": 6,
        "truncated": False,
        "encoding": "utf-8",
        "untrusted": True,
        "notice": UNTRUSTED_NOTICE,
    }


def test_read_file_reports_truncation(sandbox, tmp_path):
    (tmp_path / "workspace" / "largo.txt").write_text("x" * 50, encoding="utf-8")

    payload = json.loads(ReadFileTool(sandbox).run(path="largo.txt"))

    assert payload["truncated"] is True
    assert payload["size_bytes_returned"] == 8
    assert payload["total_size_bytes"] == 50


def test_read_file_errors_are_exceptions_so_the_loop_reports_is_error(sandbox):
    with pytest.raises(WorkspaceError):
        ReadFileTool(sandbox).run(path="../etc/passwd")


def test_list_files_returns_structured_json(sandbox):
    payload = json.loads(ListFilesTool(sandbox).run())

    assert payload["directory"] == ""
    assert payload["count"] == 2
    assert payload["truncated"] is False
    assert payload["untrusted"] is True
    assert payload["files"] == [
        {"path": "nota.md", "size_bytes": 6, "extension": ".md"},
        {"path": "docs/guia.txt", "size_bytes": 5, "extension": ".txt"},
    ]


def test_list_files_accepts_subdirectory(sandbox):
    payload = json.loads(ListFilesTool(sandbox).run(directory="docs"))

    assert payload["directory"] == "docs"
    assert [entry["path"] for entry in payload["files"]] == ["docs/guia.txt"]


def test_list_files_rejects_traversal(sandbox):
    with pytest.raises(WorkspaceError):
        ListFilesTool(sandbox).run(directory="..")


def test_schemas_are_strict_and_describe_limits(sandbox):
    list_tool, read_tool = ListFilesTool(sandbox), ReadFileTool(sandbox)

    assert list_tool.name == "list_files" and read_tool.name == "read_file"
    assert list_tool.input_schema["additionalProperties"] is False
    assert read_tool.input_schema["additionalProperties"] is False
    assert read_tool.input_schema["required"] == ["path"]
    assert "required" not in list_tool.input_schema
    for tool in (list_tool, read_tool):
        assert ".md" in tool.description and ".env" not in tool.description
    assert "8 bytes" in read_tool.description
