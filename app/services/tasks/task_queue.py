"""
Simple task queue system for background processing
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents a background task"""
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class TaskQueue:
    """Simple async task queue for background processing"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, Task] = {}
        self.pending_queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.worker_semaphore = asyncio.Semaphore(max_workers)
    
    def add_task(
        self, 
        task_id: str, 
        name: str, 
        func: Callable, 
        *args, 
        max_retries: int = 3,
        **kwargs
    ) -> Task:
        """Add a new task to the queue"""
        task = Task(
            id=task_id,
            name=name,
            func=func,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries
        )
        
        self.tasks[task_id] = task
        self.pending_queue.put_nowait(task)
        logger.info(f"Added task {task_id}: {name}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Get all tasks with a specific status"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            logger.info(f"Cancelled task {task_id}")
            return True
        return False
    
    async def start_workers(self):
        """Start background worker tasks"""
        if self.running:
            return
        
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]
        logger.info(f"Started {self.max_workers} workers")
    
    async def stop_workers(self):
        """Stop all background workers"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        logger.info("Stopped all workers")
    
    async def _worker(self, worker_name: str):
        """Background worker that processes tasks"""
        logger.info(f"Worker {worker_name} started")
        
        while self.running:
            try:
                async with self.worker_semaphore:
                    # Wait for a task with timeout
                    try:
                        task = await asyncio.wait_for(
                            self.pending_queue.get(), 
                            timeout=1.0
                        )
                    except asyncio.TimeoutError:
                        continue
                    
                    if task.status == TaskStatus.CANCELLED:
                        continue
                    
                    await self._execute_task(task, worker_name)
                    
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {str(e)}")
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _execute_task(self, task: Task, worker_name: str):
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        
        logger.info(f"Worker {worker_name} executing task {task.id}: {task.name}")
        
        try:
            if asyncio.iscoroutinefunction(task.func):
                result = await task.func(*task.args, **task.kwargs)
            else:
                result = task.func(*task.args, **task.kwargs)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            
            duration = (task.completed_at - task.started_at).total_seconds()
            logger.info(f"Task {task.id} completed in {duration:.2f}s")
            
        except Exception as e:
            error_msg = str(e)
            task.error = error_msg
            task.retry_count += 1
            
            logger.error(f"Task {task.id} failed: {error_msg} (attempt {task.retry_count})")
            
            if task.retry_count < task.max_retries:
                # Retry the task
                task.status = TaskStatus.PENDING
                await asyncio.sleep(2 ** task.retry_count)  # Exponential backoff
                self.pending_queue.put_nowait(task)
                logger.info(f"Retrying task {task.id} (attempt {task.retry_count + 1})")
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                logger.error(f"Task {task.id} failed permanently after {task.max_retries} attempts")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(self.get_tasks_by_status(status))
        
        return {
            "total_tasks": len(self.tasks),
            "status_counts": status_counts,
            "queue_size": self.pending_queue.qsize(),
            "workers_running": len(self.workers),
            "max_workers": self.max_workers,
            "is_running": self.running
        }
    
    async def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all pending tasks to complete"""
        start_time = datetime.utcnow()
        
        while True:
            pending_tasks = self.get_tasks_by_status(TaskStatus.PENDING)
            running_tasks = self.get_tasks_by_status(TaskStatus.RUNNING)
            
            if not pending_tasks and not running_tasks:
                logger.info("All tasks completed")
                break
            
            if timeout:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                if elapsed > timeout:
                    logger.warning(f"Timeout waiting for tasks after {timeout}s")
                    break
            
            await asyncio.sleep(0.5)


# Global task queue instance
task_queue = TaskQueue()