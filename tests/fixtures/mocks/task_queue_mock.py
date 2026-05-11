"""Async task queue mock for LECS host management integration tests.

Simulates an asynchronous task queue (Celery/RQ replacement) for testing
host lifecycle operations that involve async state transitions.

Instead of spawning real worker processes, this mock tracks task states
in memory and allows tests to explicitly trigger completions and state
transitions with full control over timing.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


class TaskQueueMock:
    """Mock async task queue for deterministic task execution testing.

    Tracks tasks by ID and allows tests to:
    - Submit tasks and get task IDs
    - Check task status (pending/running/completed/failed)
    - Explicitly simulate task completion or failure
    - Simulate host state transitions triggered by task completion

    This replaces Celery/RQ in integration tests, enabling precise
    control over async behavior without external dependencies.

    Attributes:
        tasks: Internal dict mapping task_id to task state dict
    """

    VALID_STATUSES = {"pending", "running", "completed", "failed"}

    def __init__(self):
        """Initialize the task queue mock."""
        self.tasks: dict[str, dict] = {}
        self.host_states: dict[str, str] = {}  # host_id → current status
        self._call_count = 0
        self._task_history: list[dict] = []

    def submit_task(self, task_type: str, host_id: str, **kwargs) -> str:
        """Submit a new async task.

        Args:
            task_type: Type of task (e.g., 'create_host', 'stop_host', 'start_host', 'delete_host')
            host_id: The host this task operates on
            **kwargs: Additional task metadata

        Returns:
            task_id: Unique task identifier
        """
        self._call_count += 1
        task_id = str(uuid.uuid4())

        task = {
            "task_id": task_id,
            "task_type": task_type,
            "host_id": host_id,
            "status": "pending",
            "result": None,
            "error": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            **kwargs,
        }
        self.tasks[task_id] = task
        self._task_history.append({
            "action": "submit",
            "task_id": task_id,
            "task_type": task_type,
            "host_id": host_id,
            "timestamp": task["created_at"],
        })

        # Set host to initial state based on task type
        if task_type == "create_host":
            self.host_states[host_id] = "creating"
        elif task_type in ("stop_host", "start_host", "delete_host"):
            transition_map = {
                "stop_host": "shutting_down",
                "start_host": "starting",
                "delete_host": "deleting",
            }
            self.host_states[host_id] = transition_map[task_type]

        return task_id

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Get the current status of a task.

        Args:
            task_id: Task identifier returned by submit_task

        Returns:
            dict with keys:
                - task_id: Task identifier
                - status: Current status ('pending', 'running', 'completed', 'failed')
                - result: Task result (if completed)
                - error: Error message (if failed)
            Returns None if task_id not found.
        """
        self._call_count += 1
        task = self.tasks.get(task_id)
        if task is None:
            return None
        return {
            "task_id": task["task_id"],
            "status": task["status"],
            "result": task["result"],
            "error": task["error"],
        }

    def simulate_completion(self, task_id: str, success: bool = True, result: Optional[dict] = None) -> Optional[dict]:
        """Mark a task as completed (success or failure).

        Simulates the async worker finishing the task and updating its state.

        Args:
            task_id: Task identifier
            success: If True, mark as 'completed'; if False, mark as 'failed'
            result: Optional result data to store with the task

        Returns:
            Updated task dict, or None if task not found
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None

        now = datetime.now(timezone.utc)
        task["status"] = "completed" if success else "failed"
        task["result"] = result
        if not success and result:
            task["error"] = result.get("error", "Task failed")
        task["updated_at"] = now

        self._task_history.append({
            "action": "complete" if success else "fail",
            "task_id": task_id,
            "host_id": task["host_id"],
            "timestamp": now,
        })

        # Update host state based on task type and result
        host_id = task["host_id"]
        task_type = task["task_type"]

        if success:
            completion_map = {
                "create_host": "normal",
                "stop_host": "stopped",
                "start_host": "normal",
                "delete_host": "deleted",
            }
            self.host_states[host_id] = completion_map.get(task_type, "normal")
        else:
            # Failed tasks: go to 'failed' state (except delete which stays deleting→failed)
            if task_type == "create_host":
                self.host_states[host_id] = "failed"
            elif task_type == "delete_host":
                self.host_states[host_id] = "failed"  # Delete failed, host remains

        return task

    def simulate_running(self, task_id: str) -> Optional[dict]:
        """Mark a task as currently running (in progress).

        Args:
            task_id: Task identifier

        Returns:
            Updated task dict, or None if not found
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None
        task["status"] = "running"
        task["updated_at"] = datetime.now(timezone.utc)
        return task

    def simulate_state_transition(self, host_id: str, new_status: str) -> Optional[str]:
        """Directly simulate an async state transition for a host.

        Useful for testing intermediate states without going through full
        task lifecycle.

        Args:
            host_id: Host identifier
            new_status: Target status (must be a valid HostStatus value)

        Returns:
            The new status, or None if host not tracked
        """
        if host_id not in self.host_states:
            self.host_states[host_id] = new_status
            return new_status
        self.host_states[host_id] = new_status
        return new_status

    def get_host_status(self, host_id: str) -> Optional[str]:
        """Get the current tracked status of a host.

        Args:
            host_id: Host identifier

        Returns:
            Current status string, or None if not tracked
        """
        return self.host_states.get(host_id)

    def get_tasks_for_host(self, host_id: str) -> list[dict]:
        """Get all tasks associated with a specific host.

        Args:
            host_id: Host identifier

        Returns:
            list of task dicts
        """
        return [t for t in self.tasks.values() if t["host_id"] == host_id]

    def get_pending_tasks(self) -> list[dict]:
        """Get all tasks in 'pending' status.

        Returns:
            list of pending task dicts
        """
        return [t for t in self.tasks.values() if t["status"] == "pending"]

    def get_task_history(self) -> list[dict]:
        """Get the ordered history of all task operations.

        Returns:
            list of history entries with action, task_id, timestamp
        """
        return list(self._task_history)

    def reset(self):
        """Clear all tasks, host states, and history."""
        self.tasks.clear()
        self.host_states.clear()
        self._call_count = 0
        self._task_history.clear()

    @property
    def call_count(self) -> int:
        """Total number of operations performed on this mock."""
        return self._call_count
