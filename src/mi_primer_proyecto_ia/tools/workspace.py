"""Sandbox de solo lectura sobre un directorio "workspace".

Es el ÚNICO punto del proyecto que toca el sistema de archivos para las tools
`list_files` y `read_file`, y por tanto el único punto de control de seguridad:
las tools solo delegan aquí. Un futuro indexador RAG debe reutilizar esta misma
clase para leer documentos, heredando exactamente las mismas garantías.

Qué garantiza (control de acceso lógico, no un sandbox de proceso):
- solo rutas relativas al workspace: sin absolutas, sin `..`, sin `\\`, sin
  caracteres de control, sin segmentos ocultos (`.env`, `.git`, `.ssh`...);
- solo extensiones de una whitelist (por defecto .txt/.md/.json/.csv);
- NINGÚN enlace simbólico: se rechaza cualquier componente de la ruta (archivo
  o directorio) que sea symlink, aunque apunte dentro del workspace. No basta
  con mirar la ruta textual: además se resuelve el objetivo real y se exige
  que quede dentro de `WORKSPACE_ROOT` (defensa en profundidad, independiente
  de la comprobación de symlinks) y que cumpla las mismas reglas;
- el archivo se abre con `O_NOFOLLOW` y se comprueba con `fstat` sobre el
  descriptor ya abierto: si entre la validación y la apertura alguien lo
  reemplaza por un symlink (TOCTOU), la apertura falla en vez de leer fuera;
- lectura acotada por bytes, solo texto UTF-8 (rechaza binarios);
- listado acotado por número de entradas, sin symlinks ni nombres con
  caracteres de control.

Riesgos residuales (documentados, no eliminados): una carrera sobre un
directorio INTERMEDIO reemplazado por symlink tras validar (requiere un
atacante con escritura concurrente en el workspace) y los hard links a
archivos externos (no son symlinks y no se detectan).

CONTENIDO NO CONFIABLE: todo lo que sale de aquí (contenido de archivos Y
nombres de archivo) es entrada no confiable. Este módulo solo lo lee y lo
devuelve como texto opaco: nunca lo parsea, evalúa ni usa para decidir qué
hacer. Las tools que lo exponen son de solo lectura, así que un texto
inyectado no tiene ninguna acción que provocar.

Los errores son `WorkspaceError` (un `ValueError`) con mensajes que nunca
incluyen rutas absolutas del sistema.
"""

from __future__ import annotations

import os
import re
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_MAX_PATH_LENGTH = 255
_WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


class WorkspaceError(ValueError):
    """Acceso rechazado o error al leer/listar dentro del workspace."""


@dataclass(frozen=True)
class FileEntry:
    path: str
    size_bytes: int
    extension: str


@dataclass(frozen=True)
class FileContent:
    path: str
    content: str
    size_bytes_returned: int
    total_size_bytes: int
    truncated: bool


class WorkspaceSandbox:
    def __init__(
        self,
        root: Path | str,
        allowed_extensions: Iterable[str],
        max_read_bytes: int,
        max_list_entries: int,
    ) -> None:
        root_path = Path(root)
        if not root_path.is_dir():
            raise WorkspaceError("El workspace no existe o no es un directorio")
        self._root = root_path.resolve()
        self._extensions = frozenset(ext.lower() for ext in allowed_extensions)
        self._max_read_bytes = max_read_bytes
        self._max_list_entries = max_list_entries

    @property
    def allowed_extensions(self) -> list[str]:
        return sorted(self._extensions)

    @property
    def max_read_bytes(self) -> int:
        return self._max_read_bytes

    # -- validación ---------------------------------------------------------

    def _parse(self, path: object) -> list[str]:
        """Valida la forma de una ruta relativa y devuelve sus segmentos."""
        if not isinstance(path, str):
            raise WorkspaceError("La ruta debe ser un texto")
        if len(path) > _MAX_PATH_LENGTH:
            raise WorkspaceError(f"La ruta supera el máximo de {_MAX_PATH_LENGTH} caracteres")
        if _CONTROL_CHARS_RE.search(path):
            raise WorkspaceError("La ruta contiene caracteres no permitidos")
        if "\\" in path:
            raise WorkspaceError("La ruta no puede contener '\\'; usa '/' como separador")
        if path.startswith("/") or _WINDOWS_DRIVE_RE.match(path):
            raise WorkspaceError("Solo se permiten rutas relativas al workspace")

        parts = [segment for segment in path.split("/") if segment]
        for segment in parts:
            if segment.startswith("."):
                raise WorkspaceError(
                    "No se permiten '..' ni archivos o carpetas ocultos (que empiezan por '.')"
                )
        return parts

    def _check_extension(self, name: str) -> None:
        extension = PurePosixPath(name).suffix.lower()
        if extension not in self._extensions:
            allowed = ", ".join(self.allowed_extensions)
            raise WorkspaceError(f"Extensión no permitida. Extensiones permitidas: {allowed}")

    def _reject_symlinks(self, parts: list[str]) -> None:
        """Rechaza si CUALQUIER componente de la ruta es un enlace simbólico.

        `is_symlink()` usa lstat (no sigue el enlace), así que detecta también
        enlaces rotos y bucles, y funciona para archivos y directorios
        intermedios, con destino dentro o fuera del workspace.
        """
        current = self._root
        for segment in parts:
            current = current / segment
            if current.is_symlink():
                raise WorkspaceError("No se permiten enlaces simbólicos")

    def _contain(self, parts: list[str]) -> Path:
        """Resuelve la ruta (siguiendo symlinks) y exige que quede dentro del root."""
        try:
            resolved = self._root.joinpath(*parts).resolve()
        except (OSError, RuntimeError) as exc:
            raise WorkspaceError("No se pudo resolver la ruta") from exc
        if not resolved.is_relative_to(self._root):
            raise WorkspaceError("La ruta queda fuera del workspace")
        # El destino real también debe cumplir las reglas (un symlink interno no
        # puede convertir un .txt en un .py ni apuntar a una carpeta oculta).
        for segment in resolved.relative_to(self._root).parts:
            if segment.startswith("."):
                raise WorkspaceError("La ruta resuelve a un archivo o carpeta oculto")
        return resolved

    def resolve_file(self, path: object) -> Path:
        parts = self._parse(path)
        if not parts:
            raise WorkspaceError("La ruta no puede estar vacía")
        self._check_extension(parts[-1])
        self._reject_symlinks(parts)
        resolved = self._contain(parts)
        self._check_extension(resolved.name)
        if not resolved.exists():
            raise WorkspaceError(f"El archivo no existe: {'/'.join(parts)}")
        if not resolved.is_file():
            raise WorkspaceError(f"No es un archivo: {'/'.join(parts)}")
        return resolved

    # -- operaciones --------------------------------------------------------

    def read_text(self, path: object) -> FileContent:
        resolved = self.resolve_file(path)
        relative = resolved.relative_to(self._root).as_posix()
        data, total_size = self._read_bytes(resolved, relative)

        truncated = len(data) > self._max_read_bytes
        data = data[: self._max_read_bytes]

        if b"\x00" in data:
            raise WorkspaceError(f"El archivo parece binario, no texto: {relative}")
        text = self._decode(data, truncated=truncated, relative=relative)
        return FileContent(
            path=relative,
            content=text,
            size_bytes_returned=len(text.encode("utf-8")),
            total_size_bytes=max(total_size, len(data)),
            truncated=truncated,
        )

    def _read_bytes(self, resolved: Path, relative: str) -> tuple[bytes, int]:
        """Abre SIN seguir enlaces y valida sobre el descriptor ya abierto.

        `O_NOFOLLOW`: si tras la validación el archivo fue reemplazado por un
        symlink, `os.open` falla (ELOOP) en vez de leer fuera del workspace.
        `O_NONBLOCK`: un FIFO colocado en su lugar no puede colgar la lectura.
        El tamaño sale de `fstat` sobre el descriptor, no de un `stat` previo.
        """
        if not hasattr(os, "O_NOFOLLOW") and resolved.is_symlink():
            raise WorkspaceError("No se permiten enlaces simbólicos")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        try:
            fd = os.open(resolved, flags)
        except OSError as exc:
            raise WorkspaceError(
                f"No se pudo abrir el archivo (enlace simbólico o archivo modificado): {relative}"
            ) from exc
        try:
            handle = os.fdopen(fd, "rb")
        except OSError as exc:
            os.close(fd)
            raise WorkspaceError(f"No se pudo leer el archivo: {relative}") from exc
        with handle:
            try:
                info = os.fstat(handle.fileno())
                if not stat.S_ISREG(info.st_mode):
                    raise WorkspaceError(f"No es un archivo regular: {relative}")
                return handle.read(self._max_read_bytes + 1), info.st_size
            except OSError as exc:
                raise WorkspaceError(f"No se pudo leer el archivo: {relative}") from exc

    @staticmethod
    def _decode(data: bytes, *, truncated: bool, relative: str) -> str:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as exc:
            # Al truncar puede quedar un carácter multibyte a medias al final:
            # se descarta solo ese fragmento; cualquier otro fallo es "no es UTF-8".
            if truncated and exc.reason == "unexpected end of data":
                try:
                    return data[: exc.start].decode("utf-8")
                except UnicodeDecodeError:
                    pass
            raise WorkspaceError(f"El archivo no es texto UTF-8 válido: {relative}") from exc

    def list_files(self, directory: object = "") -> tuple[str, list[FileEntry], bool]:
        """Devuelve (directorio_relativo, entradas, truncated)."""
        parts = self._parse(directory)
        if parts:
            self._reject_symlinks(parts)
            base = self._contain(parts)
        else:
            base = self._root
        if not base.is_dir():
            raise WorkspaceError(f"No es un directorio: {'/'.join(parts) or '.'}")

        entries: list[FileEntry] = []
        truncated = False
        for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
            # Se podan ocultos y symlinks a directorios (no depender solo de
            # followlinks=False); un nombre con caracteres de control no se lista.
            dirnames[:] = sorted(
                name
                for name in dirnames
                if not name.startswith(".")
                and not _CONTROL_CHARS_RE.search(name)
                and not (Path(dirpath) / name).is_symlink()
            )
            for name in sorted(filenames):
                if name.startswith(".") or _CONTROL_CHARS_RE.search(name):
                    continue
                extension = PurePosixPath(name).suffix.lower()
                if extension not in self._extensions:
                    continue
                file_path = Path(dirpath) / name
                if file_path.is_symlink() or not file_path.is_file():
                    continue
                if len(entries) >= self._max_list_entries:
                    truncated = True
                    break
                entries.append(
                    FileEntry(
                        path=file_path.relative_to(self._root).as_posix(),
                        size_bytes=file_path.stat().st_size,
                        extension=extension,
                    )
                )
            if truncated:
                break

        relative_dir = base.relative_to(self._root).as_posix()
        return ("" if relative_dir == "." else relative_dir), entries, truncated
