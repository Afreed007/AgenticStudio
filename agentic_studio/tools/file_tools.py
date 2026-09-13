"""Workspace File Tools for Developer and Reviewer agents."""

from typing import Dict, List, Optional
from agentic_studio.blackboard.workspace import WorkspaceManager


class WorkspaceFileTools:
    """Tool wrapper allowing agents to read and modify files in the target project."""

    def __init__(self, workspace: WorkspaceManager):
        self.workspace = workspace

    def write_code(self, filepath: str, content: str) -> Dict[str, str]:
        """Write source code to a target file."""
        abs_path = self.workspace.write_file(filepath, content)
        return {
            "status": "success",
            "path": filepath,
            "message": f"Successfully wrote {len(content)} characters to {filepath}."
        }

    def read_code(self, filepath: str) -> Dict[str, str]:
        """Read source code from a target file."""
        try:
            content = self.workspace.read_file(filepath)
            return {"status": "success", "path": filepath, "content": content}
        except Exception as e:
            return {"status": "error", "path": filepath, "message": str(e)}

    def list_project_files(self) -> List[str]:
        """List all current files in the workspace."""
        return self.workspace.list_files()
