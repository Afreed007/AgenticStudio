"""RunManager: Coordinates multi-agent background runs and WebSocket broadcasts."""

import asyncio
import concurrent.futures
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from fastapi import WebSocket
from pydantic import BaseModel, Field

from agentic_studio.config import StudioConfig
from agentic_studio.orchestrator import StudioOrchestrator
from agentic_studio.protocol.models import A2AMessage

logger = logging.getLogger("RunManager")


class RunSession(BaseModel):
    run_id: str
    prompt: str
    workspace: str
    mock_mode: bool
    status: str = "PENDING"  # PENDING, RUNNING, SUCCESS, ESCALATED, FAILED
    created_at: float = Field(default_factory=time.time)
    finished_at: Optional[float] = None
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    files: List[str] = Field(default_factory=list)
    tickets_stats: Dict[str, int] = Field(default_factory=dict)
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RunManager:
    """Singleton managing active/historical agency runs and real-time WebSocket listeners."""

    def __init__(self):
        self.runs: Dict[str, RunSession] = {}
        self.orchestrators: Dict[str, StudioOrchestrator] = {}
        # run_id -> set of connected WebSockets
        self._listeners: Dict[str, Set[WebSocket]] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    def list_runs(self) -> List[RunSession]:
        return list(self.runs.values())

    def get_run(self, run_id: str) -> Optional[RunSession]:
        return self.runs.get(run_id)

    async def register_websocket(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if run_id not in self._listeners:
            self._listeners[run_id] = set()
        self._listeners[run_id].add(websocket)

        # Send existing message backlog to newly connected client
        run = self.get_run(run_id)
        if run:
            for msg in run.messages:
                await websocket.send_json({"type": "a2a_message", "data": msg})
            if run.status in ("SUCCESS", "ESCALATED", "FAILED"):
                await websocket.send_json({"type": "run_status", "data": run.model_dump()})

    def unregister_websocket(self, run_id: str, websocket: WebSocket):
        if run_id in self._listeners and websocket in self._listeners[run_id]:
            self._listeners[run_id].remove(websocket)

    def _sync_observer(self, run_id: str, msg: A2AMessage):
        """Called by the orchestrator A2A bus from the worker thread."""
        msg_dict = msg.model_dump()
        if run_id in self.runs:
            self.runs[run_id].messages.append(msg_dict)

        # Broadcast to all connected WebSockets
        listeners = list(self._listeners.get(run_id, []))
        for ws in listeners:
            try:
                # Schedule coroutine on main event loop
                asyncio.run_coroutine_threadsafe(
                    ws.send_json({"type": "a2a_message", "data": msg_dict}),
                    asyncio.get_event_loop()
                )
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {e}")

    def start_run(
        self,
        prompt: str,
        workspace: Optional[str] = None,
        mock_mode: bool = True,
    ) -> RunSession:
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        workspace_path = workspace or f"./workspaces/{run_id}"

        session = RunSession(
            run_id=run_id,
            prompt=prompt,
            workspace=workspace_path,
            mock_mode=mock_mode,
            status="RUNNING",
        )
        self.runs[run_id] = session

        # Launch in background thread
        self._executor.submit(self._execute_agency_run, run_id, prompt, workspace_path, mock_mode)
        return session

    def _execute_agency_run(self, run_id: str, prompt: str, workspace_path: str, mock_mode: bool):
        try:
            cfg = StudioConfig(
                workspace_root=Path(workspace_path),
                use_mock_llm=mock_mode,
            )

            # Wire orchestrator with observer for this run_id
            orchestrator = StudioOrchestrator(
                custom_config=cfg,
                observer=lambda msg: self._sync_observer(run_id, msg),
            )
            self.orchestrators[run_id] = orchestrator

            result = orchestrator.run(client_prompt=prompt, clean_workspace=True)

            session = self.runs[run_id]
            session.status = result.get("status", "SUCCESS")
            session.finished_at = time.time()
            session.files = orchestrator.workspace.list_files()
            session.tickets_stats = orchestrator.blackboard.get_stats()
            session.summary = result

            # Broadcast final status
            listeners = list(self._listeners.get(run_id, []))
            for ws in listeners:
                try:
                    asyncio.run_coroutine_threadsafe(
                        ws.send_json({"type": "run_status", "data": session.model_dump()}),
                        asyncio.get_event_loop()
                    )
                except Exception:
                    pass

        except Exception as e:
            logger.exception(f"Agency run error for {run_id}: {e}")
            if run_id in self.runs:
                session = self.runs[run_id]
                session.status = "FAILED"
                session.error = str(e)
                session.finished_at = time.time()


run_manager = RunManager()
