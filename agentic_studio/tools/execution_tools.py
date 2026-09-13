"""Sandboxed code execution and test runner tools for QA agents."""

import subprocess
import sys
from typing import Dict, List, Optional
from agentic_studio.blackboard.workspace import WorkspaceManager


class SandboxedExecutionTools:
    """Safely executes commands and test suites against the target project."""

    def __init__(self, workspace: WorkspaceManager, timeout_seconds: int = 30):
        self.workspace = workspace
        self.timeout_seconds = timeout_seconds

    def run_pytest(self, test_path: Optional[str] = None) -> Dict[str, any]:
        """Run pytest inside the target project workspace."""
        cmd = [sys.executable, "-m", "pytest"]
        if test_path:
            cmd.append(test_path)
        # Suppress verbose tracebacks slightly for clean output, but keep failure details
        cmd.extend(["-v", "--tb=short"])

        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.workspace.root_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            return {
                "passed": res.returncode == 0,
                "exit_code": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr,
                "command": " ".join(cmd),
            }
        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout_seconds} seconds.",
                "command": " ".join(cmd),
            }
        except Exception as e:
            return {
                "passed": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(cmd),
            }

    def check_python_syntax(self, filepath: str) -> Dict[str, any]:
        """Check for compilation / syntax errors in a python file."""
        cmd = [sys.executable, "-m", "py_compile", filepath]
        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.workspace.root_dir),
                capture_output=True,
                text=True,
                timeout=10,
            )
            return {
                "valid": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr,
            }
        except Exception as e:
            return {"valid": False, "stdout": "", "stderr": str(e)}
