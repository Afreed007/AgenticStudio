"""Sandboxed workspace file manager for the target project."""

import os
import shutil
from pathlib import Path
from typing import List, Optional


class WorkspaceManager:
    """Manages files within an isolated sandbox directory, preventing traversal attacks."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_safe(self, rel_path: str) -> Path:
        """Resolve a relative path and verify it stays inside the workspace root."""
        # Normalize separators
        clean_rel = os.path.normpath(rel_path.strip().lstrip("/\\"))
        target = (self.root_dir / clean_rel).resolve()
        if not str(target).startswith(str(self.root_dir)):
            raise ValueError(
                f"Security violation: Attempted path traversal outside workspace: '{rel_path}'"
            )
        return target

    def write_file(self, rel_path: str, content: str) -> str:
        """Write content to a file inside the workspace."""
        target = self._resolve_safe(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    def read_file(self, rel_path: str) -> str:
        """Read content of a file inside the workspace."""
        target = self._resolve_safe(rel_path)
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"File not found in workspace: '{rel_path}'")
        return target.read_text(encoding="utf-8")

    def file_exists(self, rel_path: str) -> bool:
        """Check if a file exists inside the workspace."""
        try:
            target = self._resolve_safe(rel_path)
            return target.exists() and target.is_file()
        except ValueError:
            return False

    def list_files(self, extension: Optional[str] = None) -> List[str]:
        """List all relative file paths in the workspace."""
        files: List[str] = []
        for path in self.root_dir.rglob("*"):
            if path.is_file():
                if extension and not path.name.endswith(extension):
                    continue
                # Compute relative path
                rel = path.relative_to(self.root_dir).as_posix()
                files.append(rel)
        return sorted(files)

    def clean(self) -> None:
        """Empty the workspace directory."""
        if self.root_dir.exists():
            for item in self.root_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
