"""API endpoints for task management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.v1.schemas.common import PaginatedResponse, SuccessResponse
from app.api.v1.schemas.tasks import (
    AssignTaskRequest,
    AssignTaskResponse,
    CancelTaskResponse,
    CompleteTaskRequest,
    CompleteTaskResponse,
    CreateWorkflowRequest,
    CreateWorkflowResponse,
    ReassignTaskRequest,
    Task,
    TaskCreate,
    TaskStats,
    TaskSummary,
    TaskUpdate,
    TaskWithComputedFields,
    UpdateAutomationConfigRequest,
    UserTaskSummary,
    WorkflowDetail,
    WorkflowTask,
)
from app.models.task import TaskPriority, TaskStatus, TaskType
from app.models.user import User
from app.services.task_service import TaskService

router = APIRouter()


# ============================================================================
# CRUD Endpoints
# ============================================================================


@router.get("/", response_model=PaginatedResponse[TaskSummary])
async def list_tasks(
    task_type: Optional[TaskType] = None,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assigned_to_user_id: Optional[UUID] = None,
    patient_id: Optional[UUID] = None,
    overdue_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """List tasks with filters."""
    service = TaskService(db, current_user.practice_id)
    tasks, total = await service.list_tasks(
        task_type=task_type,
        status=status,
        priority=priority,
        assigned_to_user_id=assigned_to_user_id,
        patient_id=patient_id,
        overdue_only=overdue_only,
        skip=skip,
        limit=limit,
    )

    # Convert to summary
    task_summaries = [
        TaskSummary(
            id=t.id,
            task_type=t.task_type,
            status=t.status,
            priority=t.priority,
            title=t.title,
            assigned_to_user_id=t.assigned_to_user_id,
            due_date=t.due_date,
            is_overdue=t.is_overdue,
            created_at=t.created_at,
        )
        for t in tasks
    ]

    return PaginatedResponse(
        items=task_summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/my-tasks", response_model=PaginatedResponse[TaskSummary])
async def list_my_tasks(
    status: Optional[TaskStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get tasks assigned to current user."""
    service = TaskService(db, current_user.practice_id)
    tasks, total = await service.get_user_tasks(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=limit,
    )

    task_summaries = [
        TaskSummary(
            id=t.id,
            task_type=t.task_type,
            status=t.status,
            priority=t.priority,
            title=t.title,
            assigned_to_user_id=t.assigned_to_user_id,
            due_date=t.due_date,
            is_overdue=t.is_overdue,
            created_at=t.created_at,
        )
        for t in tasks
    ]

    return PaginatedResponse(
        items=task_summaries,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new task."""
    service = TaskService(db, current_user.practice_id)
    task = await service.create_task(task_in, assigned_by_user_id=current_user.id)
    await db.commit()
    return task


@router.get("/{task_id}", response_model=TaskWithComputedFields)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get a specific task by ID."""
    service = TaskService(db, current_user.practice_id)
    task = await service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskWithComputedFields(
        **task.__dict__,
        is_overdue=task.is_overdue,
        is_completed=task.is_completed,
        can_execute=task.can_execute,
    )


@router.patch("/{task_id}", response_model=Task)
async def update_task(
    task_id: UUID,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update task."""
    service = TaskService(db, current_user.practice_id)
    task = await service.update_task(task_id, task_in)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()
    return task


@router.delete("/{task_id}", response_model=SuccessResponse)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Delete a task (soft delete)."""
    service = TaskService(db, current_user.practice_id)
    deleted = await service.delete_task(task_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()
    return SuccessResponse(message="Task deleted successfully")


# ============================================================================
# Assignment Endpoints
# ============================================================================


@router.post("/{task_id}/assign", response_model=AssignTaskResponse)
async def assign_task(
    task_id: UUID,
    assign_request: AssignTaskRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Assign task to a user."""
    service = TaskService(db, current_user.practice_id)
    task = await service.assign_task(
        task_id=task_id,
        assigned_to_user_id=assign_request.assigned_to_user_id,
        assigned_by_user_id=current_user.id,
        assigned_to_role=assign_request.assigned_to_role,
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()

    return AssignTaskResponse(
        task_id=task.id,
        assigned_to_user_id=task.assigned_to_user_id,
        assigned_by_user_id=current_user.id,
    )


@router.post("/{task_id}/reassign", response_model=AssignTaskResponse)
async def reassign_task(
    task_id: UUID,
    reassign_request: ReassignTaskRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Reassign task to a different user."""
    service = TaskService(db, current_user.practice_id)
    task = await service.reassign_task(
        task_id=task_id,
        new_assigned_to_user_id=reassign_request.assigned_to_user_id,
        reassigned_by_user_id=current_user.id,
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()

    return AssignTaskResponse(
        task_id=task.id,
        assigned_to_user_id=task.assigned_to_user_id,
        assigned_by_user_id=current_user.id,
        message="Task reassigned successfully",
    )


# ============================================================================
# Status Change Endpoints
# ============================================================================


@router.post("/{task_id}/start", response_model=Task)
async def start_task(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Start a task (mark as in progress)."""
    service = TaskService(db, current_user.practice_id)
    task = await service.start_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()
    return task


@router.post("/{task_id}/complete", response_model=CompleteTaskResponse)
async def complete_task(
    task_id: UUID,
    complete_request: CompleteTaskRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Mark task as completed."""
    service = TaskService(db, current_user.practice_id)
    task = await service.complete_task(
        task_id=task_id,
        completed_by_user_id=current_user.id,
        completion_notes=complete_request.completion_notes,
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()

    return CompleteTaskResponse(
        task_id=task.id,
        status=task.status,
        completed_at=task.completed_at,
        completed_by_user_id=task.completed_by_user_id,
    )


@router.post("/{task_id}/cancel", response_model=CancelTaskResponse)
async def cancel_task(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Cancel a task."""
    service = TaskService(db, current_user.practice_id)
    task = await service.cancel_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()

    return CancelTaskResponse(
        task_id=task.id,
        status=task.status,
    )


@router.post("/{task_id}/hold", response_model=Task)
async def put_task_on_hold(
    task_id: UUID,
    reason: Optional[str] = Query(None),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Put task on hold."""
    service = TaskService(db, current_user.practice_id)
    task = await service.put_task_on_hold(task_id, reason)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.commit()
    return task


# ============================================================================
# Workflow Endpoints
# ============================================================================


@router.post("/workflows", response_model=CreateWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow_request: CreateWorkflowRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a workflow with multiple tasks."""
    service = TaskService(db, current_user.practice_id)
    workflow_id, tasks = await service.create_workflow(
        workflow_name=workflow_request.workflow_name,
        tasks=workflow_request.tasks,
        assigned_by_user_id=current_user.id,
    )

    await db.commit()

    return CreateWorkflowResponse(
        workflow_id=workflow_id,
        created_tasks=[t.id for t in tasks],
    )


@router.get("/workflows/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow_tasks(
    workflow_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all tasks in a workflow."""
    service = TaskService(db, current_user.practice_id)
    tasks = await service.get_workflow_tasks(workflow_id)

    if not tasks:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow_tasks = [
        WorkflowTask(
            id=t.id,
            task_type=t.task_type,
            title=t.title,
            status=t.status,
            priority=t.priority,
            assigned_to_user_id=t.assigned_to_user_id,
            due_date=t.due_date,
            parent_task_id=t.parent_task_id,
            depends_on_task_id=t.depends_on_task_id,
        )
        for t in tasks
    ]

    completed_count = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    pending_count = sum(
        1 for t in tasks
        if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.ON_HOLD)
    )

    return WorkflowDetail(
        workflow_id=workflow_id,
        tasks=workflow_tasks,
        total_tasks=len(tasks),
        completed_tasks=completed_count,
        pending_tasks=pending_count,
    )


@router.get("/{task_id}/subtasks", response_model=list[Task])
async def get_subtasks(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all subtasks of a parent task."""
    service = TaskService(db, current_user.practice_id)
    subtasks = await service.get_subtasks(task_id)
    return subtasks


@router.get("/{task_id}/dependents", response_model=list[Task])
async def get_dependent_tasks(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get tasks that depend on this task."""
    service = TaskService(db, current_user.practice_id)
    dependent_tasks = await service.get_dependent_tasks(task_id)
    return dependent_tasks


# ============================================================================
# Query Endpoints
# ============================================================================


@router.get("/overdue", response_model=list[TaskSummary])
async def get_overdue_tasks(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all overdue tasks."""
    service = TaskService(db, current_user.practice_id)
    tasks = await service.get_overdue_tasks(limit)

    return [
        TaskSummary(
            id=t.id,
            task_type=t.task_type,
            status=t.status,
            priority=t.priority,
            title=t.title,
            assigned_to_user_id=t.assigned_to_user_id,
            due_date=t.due_date,
            is_overdue=True,
            created_at=t.created_at,
        )
        for t in tasks
    ]


@router.get("/patients/{patient_id}/tasks", response_model=PaginatedResponse[Task])
async def get_patient_tasks(
    patient_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all tasks for a patient."""
    service = TaskService(db, current_user.practice_id)
    tasks, total = await service.get_patient_tasks(patient_id, skip, limit)

    return PaginatedResponse(
        items=tasks,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@router.get("/appointments/{appointment_id}/tasks", response_model=list[Task])
async def get_appointment_tasks(
    appointment_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all tasks for an appointment."""
    service = TaskService(db, current_user.practice_id)
    tasks = await service.get_appointment_tasks(appointment_id)
    return tasks


@router.get("/automated/pending", response_model=list[Task])
async def get_pending_automated_tasks(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get automated tasks ready to execute."""
    service = TaskService(db, current_user.practice_id)
    tasks = await service.get_pending_automated_tasks(limit)
    return tasks


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/stats/summary", response_model=TaskStats)
async def get_task_stats(
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get task statistics."""
    service = TaskService(db, current_user.practice_id)
    stats = await service.get_task_stats(user_id)

    return TaskStats(
        total_tasks=stats["total_tasks"],
        pending_tasks=stats["pending_tasks"],
        in_progress_tasks=stats["in_progress_tasks"],
        completed_tasks=stats["completed_tasks"],
        overdue_tasks=stats["overdue_tasks"],
        by_priority=stats["by_priority"],
        by_type=stats["by_type"],
    )


@router.get("/stats/user/{user_id}", response_model=UserTaskSummary)
async def get_user_task_summary(
    user_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get task summary for a specific user."""
    service = TaskService(db, current_user.practice_id)
    stats = await service.get_task_stats(user_id)

    # Get overdue tasks for user
    overdue_tasks = await service.get_overdue_tasks(limit=10000)
    user_overdue = [t for t in overdue_tasks if t.assigned_to_user_id == user_id]

    return UserTaskSummary(
        user_id=user_id,
        assigned_tasks=stats["total_tasks"],
        completed_tasks=stats["completed_tasks"],
        pending_tasks=stats["pending_tasks"],
        overdue_tasks=len(user_overdue),
    )


# ============================================================================
# Automation Endpoints
# ============================================================================


@router.post("/{task_id}/automation", response_model=Task)
async def update_automation_config(
    task_id: UUID,
    automation_request: UpdateAutomationConfigRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Update task automation configuration."""
    service = TaskService(db, current_user.practice_id)
    task = await service.update_automation_config(
        task_id,
        automation_request.automation_config.model_dump(),
    )

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if automation_request.is_automated is not None:
        task.is_automated = automation_request.is_automated

    await db.commit()
    return task


@router.post("/{task_id}/execute", response_model=Task)
async def execute_automated_task(
    task_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Execute an automated task."""
    service = TaskService(db, current_user.practice_id)

    try:
        task = await service.execute_automated_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        await db.commit()
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
