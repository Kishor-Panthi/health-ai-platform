"""Pydantic schemas for tasks."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus, TaskType


# ============================================================================
# Base Schemas
# ============================================================================


class TaskBase(BaseModel):
    """Base task schema."""

    task_type: TaskType
    priority: TaskPriority = TaskPriority.NORMAL
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    assigned_to_user_id: Optional[UUID] = None
    assigned_to_role: Optional[str] = Field(None, max_length=50)
    patient_id: Optional[UUID] = None
    appointment_id: Optional[UUID] = None
    claim_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    due_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    due_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")
    scheduled_for: Optional[str] = None
    workflow_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    depends_on_task_id: Optional[UUID] = None
    is_automated: bool = False
    automation_config: Optional[dict] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = Field(None, max_length=255)
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None


class TaskCreate(TaskBase):
    """Schema for creating a task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    assigned_to_user_id: Optional[UUID] = None
    assigned_to_role: Optional[str] = Field(None, max_length=50)
    due_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    due_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}:\d{2}$")
    tags: Optional[list[str]] = None
    metadata: Optional[dict] = None


# ============================================================================
# Response Schemas
# ============================================================================


class Task(TaskBase):
    """Complete task schema."""

    id: UUID
    practice_id: UUID
    status: TaskStatus
    assigned_by_user_id: Optional[UUID]
    completed_at: Optional[str] = None
    completed_by_user_id: Optional[UUID] = None
    completion_notes: Optional[str] = None
    last_execution_at: Optional[str] = None
    next_execution_at: Optional[str] = None
    reminder_sent: bool
    reminder_sent_at: Optional[str] = None
    created_at: str
    updated_at: str
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class TaskWithComputedFields(Task):
    """Task with computed properties."""

    is_overdue: bool
    is_completed: bool
    can_execute: bool

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Assignment Schemas
# ============================================================================


class AssignTaskRequest(BaseModel):
    """Request to assign task to user."""

    assigned_to_user_id: UUID
    assigned_to_role: Optional[str] = None


class AssignTaskResponse(BaseModel):
    """Response after assigning task."""

    task_id: UUID
    assigned_to_user_id: UUID
    assigned_by_user_id: UUID
    message: str = "Task assigned successfully"


class ReassignTaskRequest(BaseModel):
    """Request to reassign task."""

    assigned_to_user_id: UUID
    reason: Optional[str] = None


# ============================================================================
# Completion Schemas
# ============================================================================


class CompleteTaskRequest(BaseModel):
    """Request to complete a task."""

    completion_notes: Optional[str] = None


class CompleteTaskResponse(BaseModel):
    """Response after completing task."""

    task_id: UUID
    status: TaskStatus
    completed_at: Optional[str]
    completed_by_user_id: Optional[UUID]
    message: str = "Task completed successfully"


class CancelTaskRequest(BaseModel):
    """Request to cancel a task."""

    reason: Optional[str] = None


class CancelTaskResponse(BaseModel):
    """Response after canceling task."""

    task_id: UUID
    status: TaskStatus
    message: str = "Task cancelled"


# ============================================================================
# Workflow Schemas
# ============================================================================


class WorkflowTask(BaseModel):
    """Task in a workflow."""

    id: UUID
    task_type: TaskType
    title: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to_user_id: Optional[UUID]
    due_date: Optional[str]
    parent_task_id: Optional[UUID]
    depends_on_task_id: Optional[UUID]


class WorkflowDetail(BaseModel):
    """Detailed workflow information."""

    workflow_id: UUID
    tasks: list[WorkflowTask]
    total_tasks: int
    completed_tasks: int
    pending_tasks: int


class CreateWorkflowRequest(BaseModel):
    """Request to create a workflow."""

    workflow_name: str = Field(..., max_length=255)
    tasks: list[TaskCreate]


class CreateWorkflowResponse(BaseModel):
    """Response after creating workflow."""

    workflow_id: UUID
    created_tasks: list[UUID]
    message: str = "Workflow created successfully"


# ============================================================================
# Automation Schemas
# ============================================================================


class AutomationConfig(BaseModel):
    """Task automation configuration."""

    trigger_type: str  # e.g., "time", "event", "condition"
    trigger_config: dict
    action_type: str
    action_config: dict


class CreateAutomatedTaskRequest(BaseModel):
    """Request to create automated task."""

    task_create: TaskCreate
    automation_config: AutomationConfig
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None


class UpdateAutomationConfigRequest(BaseModel):
    """Request to update automation config."""

    automation_config: AutomationConfig
    is_automated: Optional[bool] = None


# ============================================================================
# Query Schemas
# ============================================================================


class TaskSummary(BaseModel):
    """Summary of task for listings."""

    id: UUID
    task_type: TaskType
    status: TaskStatus
    priority: TaskPriority
    title: str
    assigned_to_user_id: Optional[UUID]
    due_date: Optional[str]
    is_overdue: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)


class TaskStats(BaseModel):
    """Task statistics."""

    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    by_priority: dict[str, int]
    by_type: dict[str, int]


class UserTaskSummary(BaseModel):
    """Task summary for a user."""

    user_id: UUID
    assigned_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int


class OverdueTaskAlert(BaseModel):
    """Alert for overdue tasks."""

    task_id: UUID
    title: str
    due_date: str
    assigned_to_user_id: Optional[UUID]
    days_overdue: int
