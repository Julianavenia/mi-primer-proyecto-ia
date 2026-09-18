"""Symlinks: ninguno se sigue, aunque apunte dentro o fuera; defensa en profundidad y TOCTOU."""

import os
from pathlib import Path

import pytest

from mi_primer_proyecto_ia.tools.workspace import WorkspaceError, WorkspaceSandbox

ALLOWED = [".txt", ".md", ".json", ".csv"]
SYMLINK_MSG = "enlaces simbólicos"


@pytest.fixture
def layout(tmp_path):
    """workspace/ válido + carpeta outside/ con un secreto (fuera del workspace)."""
    workspace = tmp_path / "workspace"
    (workspace / "docs" / "sub").mkdir(parents=True)
    (workspace / "nota.md").write_text("nota interna", encoding="utf-8")
    (workspace / "docs" / "guia.txt").write_text("guía", encoding="utf-8")
    (workspace / "docs" / "sub" / "x.txt").write_text("x", encoding="utf-8")

    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secreto.txt").write_text("TOP-SECRET", encoding="utf-8")
    (outside / "clave.pem").write_text("TOP-SECRET-KEY", encoding="utf-8")
    return workspace, outside, tmp_path


def sandbox_for(root, max_read_bytes=1000):
    return WorkspaceSandbox(root, ALLOWED, max_read_bytes, 100)


def assert_rejected(sandbox, path, match=SYMLINK_MSG, tmp_path=None):
    with pytest.raises(WorkspaceError, match=match) as exc_info:
        sandbox.read_text(path)
    message = str(exc_info.value)
    assert "TOP-SECRET" not in message
    if tmp_path is not None:
        assert str(tmp_path) not in message and str(tmp_path.resolve()) not in message


# --- acceso a archivos fuera del workspace mediante symlink -------------------


def test_relative_symlink_to_outside_file_is_rejected(layout):
    workspace, _, tmp_path = layout
    (workspace / "enlace.txt").symlink_to(Path("..") / "outside" / "secreto.txt")

    assert_rejected(sandbox_for(workspace), "enlace.txt", tmp_path=tmp_path)


def test_absolute_symlink_to_outside_file_is_rejected(layout):
    workspace, outside, tmp_path = layout
    (workspace / "enlace_abs.md").symlink_to(outside / "secreto.txt")

    assert_rejected(sandbox_for(workspace), "enlace_abs.md", tmp_path=tmp_path)


def test_symlinked_directory_to_outside_is_rejected_for_read_and_list(layout):
    workspace, outside, tmp_path = layout
    (workspace / "carpeta_enlace").symlink_to(outside, target_is_directory=True)
    sandbox = sandbox_for(workspace)

    assert_rejected(sandbox, "carpeta_enlace/secreto.txt", tmp_path=tmp_path)
    with pytest.raises(WorkspaceError, match=SYMLINK_MSG):
        sandbox.list_files("carpeta_enlace")


def test_symlink_chain_ending_outside_is_rejected(layout):
    workspace, outside, _ = layout
    (workspace / "b.txt").symlink_to(outside / "secreto.txt")
    (workspace / "a.txt").symlink_to(workspace / "b.txt")

    assert_rejected(sandbox_for(workspace), "a.txt")
    assert_rejected(sandbox_for(workspace), "b.txt")


@pytest.mark.skipif(not Path("/etc/hosts").exists(), reason="requiere /etc/hosts")
def test_symlink_to_system_file_is_rejected(layout):
    workspace, _, tmp_path = layout
    (workspace / "hosts.txt").symlink_to("/etc/hosts")

    assert_rejected(sandbox_for(workspace), "hosts.txt", tmp_path=tmp_path)


def test_symlink_to_disallowed_extension_outside_is_rejected_as_symlink(layout):
    workspace, outside, _ = layout
    (workspace / "enlace.md").symlink_to(outside / "clave.pem")

    assert_rejected(sandbox_for(workspace), "enlace.md")


# --- symlinks INTERNOS: también se rechazan -----------------------------------


def test_internal_symlink_to_valid_workspace_file_is_rejected(layout):
    workspace, _, _ = layout
    (workspace / "alias.md").symlink_to(workspace / "nota.md")

    assert_rejected(sandbox_for(workspace), "alias.md")


def test_internal_directory_symlink_is_rejected_for_read_and_list(layout):
    workspace, _, _ = layout
    (workspace / "docs_enlace").symlink_to(workspace / "docs", target_is_directory=True)
    sandbox = sandbox_for(workspace)

    assert_rejected(sandbox, "docs_enlace/guia.txt")
    with pytest.raises(WorkspaceError, match=SYMLINK_MSG):
        sandbox.list_files("docs_enlace")


def test_symlink_in_the_middle_of_a_deep_path_is_rejected(layout):
    workspace, _, _ = layout
    (workspace / "docs" / "sub_enlace").symlink_to(
        workspace / "docs" / "sub", target_is_directory=True
    )

    assert_rejected(sandbox_for(workspace), "docs/sub_enlace/x.txt")


def test_dangling_symlink_and_symlink_loop_are_rejected_cleanly(layout):
    workspace, _, _ = layout
    (workspace / "roto.txt").symlink_to(workspace / "no_existe.txt")
    (workspace / "bucle.txt").symlink_to(workspace / "bucle.txt")
    sandbox = sandbox_for(workspace)

    assert_rejected(sandbox, "roto.txt")
    assert_rejected(sandbox, "bucle.txt")


# --- listado -------------------------------------------------------------------


def test_listing_never_shows_symlinks_nor_follows_symlinked_directories(layout):
    workspace, outside, _ = layout
    (workspace / "enlace_ext.txt").symlink_to(outside / "secreto.txt")
    (workspace / "alias.md").symlink_to(workspace / "nota.md")
    (workspace / "carpeta_ext").symlink_to(outside, target_is_directory=True)
    (workspace / "docs_enlace").symlink_to(workspace / "docs", target_is_directory=True)

    _, entries, _ = sandbox_for(workspace).list_files()

    paths = [entry.path for entry in entries]
    assert paths == ["nota.md", "docs/guia.txt", "docs/sub/x.txt"]  # solo reales, sin duplicados


# --- defensa en profundidad: la capa de contención es independiente -----------


@pytest.fixture
def symlink_check_disabled(monkeypatch):
    monkeypatch.setattr(WorkspaceSandbox, "_reject_symlinks", lambda self, parts: None)


def test_containment_layer_still_blocks_outside_symlinks_without_symlink_check(
    layout, symlink_check_disabled
):
    workspace, outside, _ = layout
    (workspace / "enlace.txt").symlink_to(outside / "secreto.txt")
    (workspace / "carpeta_enlace").symlink_to(outside, target_is_directory=True)
    sandbox = sandbox_for(workspace)

    assert_rejected(sandbox, "enlace.txt", match="fuera del workspace")
    assert_rejected(sandbox, "carpeta_enlace/secreto.txt", match="fuera del workspace")
    with pytest.raises(WorkspaceError, match="fuera del workspace"):
        sandbox.list_files("carpeta_enlace")


def test_target_revalidation_still_blocks_hidden_and_disallowed_targets(
    layout, symlink_check_disabled
):
    workspace, _, _ = layout
    (workspace / ".privado").mkdir()
    (workspace / ".privado" / "clave.txt").write_text("oculto", encoding="utf-8")
    (workspace / "codigo.py").write_text("print(1)", encoding="utf-8")
    (workspace / "a_oculto.txt").symlink_to(workspace / ".privado" / "clave.txt")
    (workspace / "a_codigo.txt").symlink_to(workspace / "codigo.py")
    sandbox = sandbox_for(workspace)

    assert_rejected(sandbox, "a_oculto.txt", match="oculto")
    assert_rejected(sandbox, "a_codigo.txt", match="Extensión no permitida")


# --- TOCTOU: el archivo se reemplaza DESPUÉS de validar ------------------------


@pytest.mark.skipif(not hasattr(os, "O_NOFOLLOW"), reason="requiere O_NOFOLLOW (POSIX)")
def test_o_nofollow_blocks_file_swapped_for_symlink_after_validation(layout, monkeypatch):
    workspace, outside, _ = layout
    sandbox = sandbox_for(workspace)
    real_resolve = sandbox.resolve_file

    def resolve_then_swap(path):
        resolved = real_resolve(path)  # la validación pasa con el archivo legítimo...
        resolved.unlink()
        resolved.symlink_to(outside / "secreto.txt")  # ...y se sustituye antes de abrir
        return resolved

    monkeypatch.setattr(sandbox, "resolve_file", resolve_then_swap)

    with pytest.raises(WorkspaceError) as exc_info:
        sandbox.read_text("nota.md")

    assert "TOP-SECRET" not in str(exc_info.value)


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="requiere mkfifo (POSIX)")
def test_file_swapped_for_fifo_after_validation_fails_fast_instead_of_hanging(layout, monkeypatch):
    workspace, _, _ = layout
    sandbox = sandbox_for(workspace)
    real_resolve = sandbox.resolve_file

    def resolve_then_swap(path):
        resolved = real_resolve(path)
        resolved.unlink()
        os.mkfifo(resolved)
        return resolved

    monkeypatch.setattr(sandbox, "resolve_file", resolve_then_swap)

    with pytest.raises(WorkspaceError, match="archivo regular"):
        sandbox.read_text("nota.md")


# --- el root configurado -------------------------------------------------------


def test_root_configured_as_symlink_is_resolved_once_but_inner_symlinks_stay_rejected(layout):
    workspace, outside, tmp_path = layout
    root_link = tmp_path / "root_enlace"
    root_link.symlink_to(workspace, target_is_directory=True)
    (workspace / "enlace.txt").symlink_to(outside / "secreto.txt")
    sandbox = sandbox_for(root_link)

    assert sandbox.read_text("nota.md").content == "nota interna"
    assert_rejected(sandbox, "enlace.txt")


# --- ningún mensaje filtra rutas del sistema -----------------------------------


def test_symlink_errors_never_include_absolute_paths_or_secret_content(layout):
    workspace, outside, tmp_path = layout
    (workspace / "enlace.txt").symlink_to(outside / "secreto.txt")
    (workspace / "carpeta_enlace").symlink_to(outside, target_is_directory=True)
    sandbox = sandbox_for(workspace)

    for path in ["enlace.txt", "carpeta_enlace/secreto.txt", "carpeta_enlace/otro.txt"]:
        assert_rejected(sandbox, path, tmp_path=tmp_path)
