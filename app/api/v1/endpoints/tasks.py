"""
API endpoints for task management
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.tasks.task_queue import task_queue, TaskStatus
from app.services.tasks.news_tasks import schedule_source_scraping, schedule_periodic_scraping

router = APIRouter()


class TaskResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    started_at: str = None
    completed_at: str = None
    result: Any = None
    error: str = None
    retry_count: int = 0


class TaskStats(BaseModel):
    total_tasks: int
    status_counts: Dict[str, int]
    queue_size: int
    workers_running: int
    max_workers: int
    is_running: bool


@router.get("/stats", response_model=TaskStats)
def get_task_stats() -> Any:
    """Get task queue statistics"""
    stats = task_queue.get_stats()
    return TaskStats(**stats)


@router.get("/", response_model=List[TaskResponse])
def get_tasks(status: str = None) -> Any:
    """Get all tasks, optionally filtered by status"""
    if status:
        try:
            status_enum = TaskStatus(status)
            tasks = task_queue.get_tasks_by_status(status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    else:
        tasks = list(task_queue.tasks.values())
    
    return [
        TaskResponse(
            id=task.id,
            name=task.name,
            status=task.status.value,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            result=task.result,
            error=task.error,
            retry_count=task.retry_count
        )
        for task in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str) -> Any:
    """Get a specific task by ID"""
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        name=task.name,
        status=task.status.value,
        created_at=task.created_at.isoformat(),
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
        result=task.result,
        error=task.error,
        retry_count=task.retry_count
    )


@router.post("/scrape/all")
def schedule_scrape_all() -> Any:
    """Schedule scraping of all sources"""
    schedule_periodic_scraping()
    return {"message": "Periodic scraping scheduled"}


@router.post("/scrape/source/{source_id}")
def schedule_scrape_source(source_id: str, limit: int = 10) -> Any:
    """Schedule scraping of a specific source"""
    task_id = schedule_source_scraping(source_id, limit)
    return {"message": f"Scraping scheduled for source {source_id}", "task_id": task_id}


@router.delete("/{task_id}")
def cancel_task(task_id: str) -> Any:
    """Cancel a pending task"""
    success = task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
    return {"message": f"Task {task_id} cancelled"}