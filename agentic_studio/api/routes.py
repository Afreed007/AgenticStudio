"""REST and WebSocket API route definitions."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from .manager import run_manager, RunSession

router = APIRouter()


class StartRunRequest(BaseModel):
    prompt: str
    workspace: Optional[str] = None
    mock_mode: bool = True


class FileContentResponse(BaseModel):
    path: str
    content: str


@router.post("/runs", response_model=RunSession)
def start_run(req: StartRunRequest):
    """Start an autonomous multi-agent agency run."""
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    return run_manager.start_run(
        prompt=req.prompt,
        workspace=req.workspace,
        mock_mode=req.mock_mode,
    )


@router.get("/runs", response_model=List[RunSession])
def list_runs():
    """List all active and completed runs."""
    return run_manager.list_runs()


@router.get("/runs/{run_id}", response_model=RunSession)
def get_run(run_id: str):
    """Get status and details of a specific run."""
    session = run_manager.get_run(run_id)
    if not session:
        raise HTTPException(status_code=404, detail="Run not found")
    return session


@router.get("/runs/{run_id}/files", response_model=List[str])
def list_run_files(run_id: str):
    """List all files generated in the workspace of a run."""
    session = run_manager.get_run(run_id)
    if not session:
        raise HTTPException(status_code=404, detail="Run not found")

    orchestrator = run_manager.orchestrators.get(run_id)
    if orchestrator:
        return orchestrator.workspace.list_files()
    return session.files


@router.get("/runs/{run_id}/files/content", response_model=FileContentResponse)
def get_file_content(run_id: str, path: str = Query(..., description="Relative file path")):
    """Read the source code content of a generated file."""
    session = run_manager.get_run(run_id)
    if not session:
        raise HTTPException(status_code=404, detail="Run not found")

    orchestrator = run_manager.orchestrators.get(run_id)
    if not orchestrator:
        raise HTTPException(status_code=400, detail="Workspace is not active")

    try:
        content = orchestrator.workspace.read_file(path)
        return FileContentResponse(path=path, content=content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{path}' not found in workspace")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.websocket("/ws/runs/{run_id}")
async def run_websocket(websocket: WebSocket, run_id: str):
    """WebSocket endpoint streaming live A2AMessage events for a run."""
    await run_manager.register_websocket(run_id, websocket)
    try:
        while True:
            # Keep connection alive; accept any client messages/pings
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        run_manager.unregister_websocket(run_id, websocket)
    except Exception:
        run_manager.unregister_websocket(run_id, websocket)
