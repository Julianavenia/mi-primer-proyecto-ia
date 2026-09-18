import pytest

from mi_primer_proyecto_ia.tools.workspace import WorkspaceError, WorkspaceSandbox

ALLOWED = [".txt", ".md", ".json", ".csv"]


@pytest.fixture
def layout(tmp_path):
    """workspace/ con contenido válido + un archivo secreto FUERA del workspace."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "nota.md").write_text("# Hola\nmundo\n", encoding="utf-8")
    (workspace / "datos.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    (workspace / "docs").mkdir()
    (workspace / "docs" / "guia.txt").write_text("guía", encoding="utf-8")

    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    (outside_dir / "secreto.txt").write_text("TOP-SECRET", encoding="utf-8")
    return workspace, outside_dir, tmp_path


def make_sandbox(root, max_read_bytes=1000, max_list_entries=100):
    return WorkspaceSandbox(root, ALLOWED, max_read_bytes, max_list_entries)


# --- lectura válida ---------------------------------------------------------


def test_reads_allowed_file(layout):
    workspace, _, _ = layout
    result = make_sandbox(workspace).read_text("nota.md")

    assert result.path == "nota.md"
    assert result.content == "# Hola\nmundo\n"
    assert result.truncated is False
    assert result.total_size_bytes == len(b"# Hola\nmundo\n")


def test_reads_nested_file_and_uppercase_extension(layout):
    workspace, _, _ = layout
    (workspace / "docs" / "MAYUS.TXT").write_text("ok", encoding="utf-8")
    sandbox = make_sandbox(workspace)

    assert sandbox.read_text("docs/guia.txt").content == "guía"
    assert sandbox.read_text("docs/MAYUS.TXT").content == "ok"


def test_reads_empty_file(layout):
    workspace, _, _ = layout
    (workspace / "vacio.txt").write_text("", encoding="utf-8")

    result = make_sandbox(workspace).read_text("vacio.txt")

    assert result.content == ""
    assert result.truncated is False


# --- traversal y rutas fuera del workspace -----------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "../outside/secreto.txt",
        "docs/../../outside/secreto.txt",
        "a/../../outside/secreto.txt",
        "./nota.md",
        "docs/./guia.txt",
        "..\\outside\\secreto.txt",
        "docs\\guia.txt",
        "/etc/passwd",
        "/etc/hosts.txt",
        "C:/Windows/win.ini",
        "C:secreto.txt",
    ],
)
def test_rejects_traversal_and_non_relative_paths(layout, path):
    workspace, _, tmp_path = layout

    with pytest.raises(WorkspaceError) as exc_info:
        make_sandbox(workspace).read_text(path)

    assert "TOP-SECRET" not in str(exc_info.value)
    assert str(tmp_path) not in str(exc_info.value)


def test_rejects_absolute_path_pointing_to_real_file_outside(layout):
    workspace, outside_dir, _ = layout

    with pytest.raises(WorkspaceError):
        make_sandbox(workspace).read_text(str(outside_dir / "secreto.txt"))


@pytest.mark.parametrize("path", [None, 123, ["nota.md"], b"nota.md"])
def test_rejects_non_string_paths(layout, path):
    workspace, _, _ = layout
    with pytest.raises(WorkspaceError, match="texto"):
        make_sandbox(workspace).read_text(path)


@pytest.mark.parametrize("path", ["", "   ", "/", "//"])
def test_rejects_empty_paths(layout, path):
    workspace, _, _ = layout
    with pytest.raises(WorkspaceError):
        make_sandbox(workspace).read_text(path)


def test_rejects_null_byte_and_too_long_paths(layout):
    workspace, _, _ = layout
    sandbox = make_sandbox(workspace)

    with pytest.raises(WorkspaceError, match="no permitidos"):
        sandbox.read_text("nota.md\x00.txt")
    with pytest.raises(WorkspaceError, match="máximo"):
        sandbox.read_text("a" * 300 + ".txt")


# --- ocultos, claves y extensiones -------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        ".env",
        ".env.txt",
        ".secret.txt",
        ".git/config",
        ".ssh/id_rsa.txt",
        "docs/.oculto.md",
        ".venv/x.txt",
    ],
)
def test_rejects_hidden_files_and_folders(layout, path):
    workspace, _, _ = layout
    (workspace / ".git").mkdir(exist_ok=True)
    (workspace / ".env").write_text("API_KEY=sk-secret", encoding="utf-8")

    with pytest.raises(WorkspaceError, match="ocultos"):
        make_sandbox(workspace).read_text(path)


@pytest.mark.parametrize(
    "path",
    ["codigo.py", "clave.pem", "id_rsa", "foto.png", "sin_extension", "datos.txt.exe", "app.env"],
)
def test_rejects_disallowed_extensions(layout, path):
    workspace, _, _ = layout
    (workspace / path).write_bytes(b"contenido")

    with pytest.raises(WorkspaceError, match="Extensión no permitida"):
        make_sandbox(workspace).read_text(path)


def test_env_content_is_never_returned(layout):
    workspace, _, _ = layout
    (workspace / ".env").write_text("API_KEY=sk-secret", encoding="utf-8")
    sandbox = make_sandbox(workspace)

    for path in [".env", "./.env", "../workspace/.env"]:
        with pytest.raises(WorkspaceError) as exc_info:
            sandbox.read_text(path)
        assert "sk-secret" not in str(exc_info.value)


# --- symlinks ----------------------------------------------------------------


def test_rejects_symlink_file_escaping_workspace(layout):
    workspace, outside_dir, _ = layout
    (workspace / "enlace.txt").symlink_to(outside_dir / "secreto.txt")

    with pytest.raises(WorkspaceError, match="enlaces simbólicos"):
        make_sandbox(workspace).read_text("enlace.txt")


def test_rejects_symlink_directory_escaping_workspace(layout):
    workspace, outside_dir, _ = layout
    (workspace / "carpeta_enlace").symlink_to(outside_dir, target_is_directory=True)
    sandbox = make_sandbox(workspace)

    with pytest.raises(WorkspaceError, match="enlaces simbólicos"):
        sandbox.read_text("carpeta_enlace/secreto.txt")
    with pytest.raises(WorkspaceError, match="enlaces simbólicos"):
        sandbox.list_files("carpeta_enlace")


def test_rejects_internal_symlink_to_hidden_target(layout):
    workspace, _, _ = layout
    (workspace / ".privado").mkdir()
    (workspace / ".privado" / "clave.txt").write_text("oculto", encoding="utf-8")
    (workspace / "alias.txt").symlink_to(workspace / ".privado" / "clave.txt")

    with pytest.raises(WorkspaceError, match="enlaces simbólicos"):
        make_sandbox(workspace).read_text("alias.txt")


def test_rejects_internal_symlink_to_disallowed_extension(layout):
    workspace, _, _ = layout
    (workspace / "codigo.py").write_text("print(1)", encoding="utf-8")
    (workspace / "alias.txt").symlink_to(workspace / "codigo.py")

    with pytest.raises(WorkspaceError, match="enlaces simbólicos"):
        make_sandbox(workspace).read_text("alias.txt")


# --- estado del archivo -------------------------------------------------------


def test_rejects_missing_file_and_directory(layout):
    workspace, _, _ = layout
    (workspace / "carpeta.md").mkdir()
    sandbox = make_sandbox(workspace)

    with pytest.raises(WorkspaceError, match="no existe"):
        sandbox.read_text("fantasma.md")
    with pytest.raises(WorkspaceError, match="No es un archivo"):
        sandbox.read_text("carpeta.md")


def test_rejects_binary_disguised_as_text(layout):
    workspace, _, _ = layout
    (workspace / "binario.txt").write_bytes(b"abc\x00def")

    with pytest.raises(WorkspaceError, match="binario"):
        make_sandbox(workspace).read_text("binario.txt")


def test_rejects_invalid_utf8(layout):
    workspace, _, _ = layout
    (workspace / "latin1.txt").write_bytes("canción".encode("latin-1"))

    with pytest.raises(WorkspaceError, match="UTF-8"):
        make_sandbox(workspace).read_text("latin1.txt")


# --- límite de tamaño ---------------------------------------------------------


def test_truncates_large_files_and_reports_it(layout):
    workspace, _, _ = layout
    (workspace / "grande.txt").write_text("a" * 100, encoding="utf-8")

    result = make_sandbox(workspace, max_read_bytes=10).read_text("grande.txt")

    assert result.content == "a" * 10
    assert result.truncated is True
    assert result.size_bytes_returned == 10
    assert result.total_size_bytes == 100


def test_file_exactly_at_limit_is_not_truncated(layout):
    workspace, _, _ = layout
    (workspace / "justo.txt").write_text("a" * 10, encoding="utf-8")

    result = make_sandbox(workspace, max_read_bytes=10).read_text("justo.txt")

    assert result.truncated is False
    assert result.content == "a" * 10


def test_truncation_in_the_middle_of_a_multibyte_char_drops_the_partial_char(layout):
    workspace, _, _ = layout
    (workspace / "ene.txt").write_text("ñ" * 10, encoding="utf-8")  # 20 bytes

    result = make_sandbox(workspace, max_read_bytes=5).read_text("ene.txt")

    assert result.content == "ññ"
    assert result.truncated is True


# --- listado ------------------------------------------------------------------


def test_lists_only_allowed_visible_files_sorted(layout):
    workspace, _, _ = layout
    (workspace / "codigo.py").write_text("x", encoding="utf-8")
    (workspace / "foto.png").write_bytes(b"\x89PNG")
    (workspace / ".env").write_text("K=v", encoding="utf-8")
    (workspace / ".git").mkdir()
    (workspace / ".git" / "config.txt").write_text("x", encoding="utf-8")

    directory, entries, truncated = make_sandbox(workspace).list_files()

    assert directory == ""
    assert truncated is False
    assert [entry.path for entry in entries] == ["datos.csv", "nota.md", "docs/guia.txt"]
    assert entries[1].extension == ".md"
    assert entries[1].size_bytes == len(b"# Hola\nmundo\n")


def test_lists_subdirectory(layout):
    workspace, _, _ = layout

    directory, entries, _ = make_sandbox(workspace).list_files("docs")

    assert directory == "docs"
    assert [entry.path for entry in entries] == ["docs/guia.txt"]


def test_list_skips_symlinked_files_and_does_not_follow_symlinked_dirs(layout):
    workspace, outside_dir, _ = layout
    (workspace / "enlace.txt").symlink_to(outside_dir / "secreto.txt")
    (workspace / "carpeta_enlace").symlink_to(outside_dir, target_is_directory=True)

    _, entries, _ = make_sandbox(workspace).list_files()

    paths = [entry.path for entry in entries]
    assert "enlace.txt" not in paths
    assert all("secreto" not in path for path in paths)


def test_list_is_bounded_by_max_entries(layout):
    workspace, _, _ = layout
    for index in range(5):
        (workspace / f"extra{index}.txt").write_text("x", encoding="utf-8")

    _, entries, truncated = make_sandbox(workspace, max_list_entries=3).list_files()

    assert len(entries) == 3
    assert truncated is True


@pytest.mark.parametrize("directory", ["..", "../outside", "/etc", ".git", "docs/.."])
def test_list_rejects_traversal_and_hidden_directories(layout, directory):
    workspace, _, _ = layout
    with pytest.raises(WorkspaceError):
        make_sandbox(workspace).list_files(directory)


def test_list_rejects_missing_or_non_directory(layout):
    workspace, _, _ = layout
    sandbox = make_sandbox(workspace)

    with pytest.raises(WorkspaceError):
        sandbox.list_files("no_existe")
    with pytest.raises(WorkspaceError, match="No es un directorio"):
        sandbox.list_files("nota.md")


# --- construcción -------------------------------------------------------------


def test_rejects_missing_root_without_leaking_its_path(tmp_path):
    missing = tmp_path / "no_existe"

    with pytest.raises(WorkspaceError) as exc_info:
        make_sandbox(missing)

    assert str(tmp_path) not in str(exc_info.value)


def test_errors_never_include_absolute_paths(layout):
    workspace, _, tmp_path = layout
    sandbox = make_sandbox(workspace)

    for path in ["fantasma.md", "docs", "../x.txt", "nota.py"]:
        with pytest.raises(WorkspaceError) as exc_info:
            sandbox.read_text(path)
        assert str(tmp_path) not in str(exc_info.value)
