"""Service for task operations."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.tasks import TaskCreate, TaskUpdate
from app.models.task import Task, TaskPriority, TaskStatus, TaskType


class TaskService:
    """Service for managing tasks."""

    def __init__(self, db: AsyncSession, practice_id: UUID):
        self.db = db
        self.practice_id = practice_id

    # ============================================================================
    # CRUD Operations
    # ============================================================================

    async def create_task(
        self,
        task_in: TaskCreate,
        assigned_by_user_id: Optional[UUID] = None,
    ) -> Task:
        """Create a new task."""
        task = Task(
            practice_id=self.practice_id,
            task_type=task_in.task_type,
            status=TaskStatus.PENDING,
            priority=task_in.priority,
            title=task_in.title,
            description=task_in.description,
            assigned_to_user_id=task_in.assigned_to_user_id,
            assigned_to_role=task_in.assigned_to_role,
            assigned_by_user_id=assigned_by_user_id,
            patient_id=task_in.patient_id,
            appointment_id=task_in.appointment_id,
            claim_id=task_in.claim_id,
            document_id=task_in.document_id,
            due_date=task_in.due_date,
            due_time=task_in.due_time,
            scheduled_for=task_in.scheduled_for,
            workflow_id=task_in.workflow_id,
            parent_task_id=task_in.parent_task_id,
            depends_on_task_id=task_in.depends_on_task_id,
            is_automated=task_in.is_automated,
            automation_config=task_in.automation_config,
            is_recurring=task_in.is_recurring,
            recurrence_rule=task_in.recurrence_rule,
            tags=task_in.tags,
            metadata=task_in.metadata,
            reminder_sent=False,
        )

        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        """Get task by ID."""
        result = await self.db.execute(
            select(Task).where(
                and_(
                    Task.id == task_id,
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_task(
        self, task_id: UUID, task_in: TaskUpdate
    ) -> Optional[Task]:
        """Update task."""
        task = await self.get_task(task_id)
        if not task:
            return None

        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_id: UUID) -> bool:
        """Soft delete task."""
        task = await self.get_task(task_id)
        if not task:
            return False

        task.is_deleted = True
        task.updated_at = datetime.utcnow().isoformat()
        await self.db.flush()
        return True

    # ============================================================================
    # Task Assignment
    # ============================================================================

    async def assign_task(
        self,
        task_id: UUID,
        assigned_to_user_id: UUID,
        assigned_by_user_id: UUID,
        assigned_to_role: Optional[str] = None,
    ) -> Optional[Task]:
        """Assign task to a user."""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.assigned_to_user_id = assigned_to_user_id
        task.assigned_to_role = assigned_to_role
        task.assigned_by_user_id = assigned_by_user_id
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def reassign_task(
        self,
        task_id: UUID,
        new_assigned_to_user_id: UUID,
        reassigned_by_user_id: UUID,
    ) -> Optional[Task]:
        """Reassign task to a different user."""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.assigned_to_user_id = new_assigned_to_user_id
        task.assigned_by_user_id = reassigned_by_user_id
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task

    # ============================================================================
    # Task Completion
    # ============================================================================

    async def complete_task(
        self,
        task_id: UUID,
        completed_by_user_id: UUID,
        completion_notes: Optional[str] = None,
    ) -> Optional[Task]:
        """Mark task as completed."""
        task = await self.get_task(task_id)
        if not task:
            return None

        if task.status == TaskStatus.COMPLETED:
            return task

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow().isoformat()
        task.completed_by_user_id = completed_by_user_id
        task.completion_notes = completion_notes
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def cancel_task(
        self, task_id: UUID, reason: Optional[str] = None
    ) -> Optional[Task]:
        """Cancel a task."""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskStatus.CANCELLED
        if reason and task.metadata:
            task.metadata["cancellation_reason"] = reason
        elif reason:
            task.metadata = {"cancellation_reason": reason}
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def start_task(self, task_id: UUID) -> Optional[Task]:
        """Mark task as in progress."""
        task = await self.get_task(task_id)
        if not task:
            return None

        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.utcnow().isoformat()
            await self.db.flush()
            await self.db.refresh(task)

        return task

    async def put_task_on_hold(
        self, task_id: UUID, reason: Optional[str] = None
    ) -> Optional[Task]:
        """Put task on hold."""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskStatus.ON_HOLD
        if reason and task.metadata:
            task.metadata["hold_reason"] = reason
        elif reason:
            task.metadata = {"hold_reason": reason}
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task

    # ============================================================================
    # Workflow Operations
    # ============================================================================

    async def create_workflow(
        self,
        workflow_name: str,
        tasks: list[TaskCreate],
        assigned_by_user_id: UUID,
    ) -> tuple[UUID, list[Task]]:
        """Create a workflow with multiple tasks."""
        workflow_id = uuid4()
        created_tasks = []

        for task_data in tasks:
            task_data.workflow_id = workflow_id
            task = await self.create_task(task_data, assigned_by_user_id)
            created_tasks.append(task)

        await self.db.flush()
        return workflow_id, created_tasks

    async def get_workflow_tasks(
        self, workflow_id: UUID
    ) -> list[Task]:
        """Get all tasks in a workflow."""
        query = (
            select(Task)
            .where(
                and_(
                    Task.workflow_id == workflow_id,
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                )
            )
            .order_by(Task.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_subtasks(self, parent_task_id: UUID) -> list[Task]:
        """Get all subtasks of a parent task."""
        query = (
            select(Task)
            .where(
                and_(
                    Task.parent_task_id == parent_task_id,
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                )
            )
            .order_by(Task.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_dependent_tasks(self, task_id: UUID) -> list[Task]:
        """Get tasks that depend on this task."""
        query = (
            select(Task)
            .where(
                and_(
                    Task.depends_on_task_id == task_id,
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                )
            )
            .order_by(Task.created_at.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ============================================================================
    # Query Operations
    # ============================================================================

    async def list_tasks(
        self,
        task_type: Optional[TaskType] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assigned_to_user_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        overdue_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Task], int]:
        """List tasks with filters."""
        conditions = [
            Task.practice_id == self.practice_id,
            Task.is_deleted == False,
        ]

        if task_type:
            conditions.append(Task.task_type == task_type)
        if status:
            conditions.append(Task.status == status)
        if priority:
            conditions.append(Task.priority == priority)
        if assigned_to_user_id:
            conditions.append(Task.assigned_to_user_id == assigned_to_user_id)
        if patient_id:
            conditions.append(Task.patient_id == patient_id)

        # Count query
        count_query = select(func.count()).select_from(Task).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Data query
        query = (
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.priority.desc(), Task.due_date.asc(), Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        # Filter overdue if requested
        if overdue_only:
            tasks = [t for t in tasks if t.is_overdue]
            total = len(tasks)

        return list(tasks), total

    async def get_user_tasks(
        self,
        user_id: UUID,
        status: Optional[TaskStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Task], int]:
        """Get tasks assigned to a user."""
        return await self.list_tasks(
            assigned_to_user_id=user_id,
            status=status,
            skip=skip,
            limit=limit,
        )

    async def get_overdue_tasks(
        self, limit: int = 100
    ) -> list[Task]:
        """Get all overdue tasks."""
        from datetime import date

        today = date.today().isoformat()

        query = (
            select(Task)
            .where(
                and_(
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                    Task.due_date.isnot(None),
                    Task.due_date < today,
                    Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
                )
            )
            .order_by(Task.due_date.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_patient_tasks(
        self, patient_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Task], int]:
        """Get all tasks for a patient."""
        return await self.list_tasks(
            patient_id=patient_id,
            skip=skip,
            limit=limit,
        )

    async def get_appointment_tasks(
        self, appointment_id: UUID
    ) -> list[Task]:
        """Get all tasks for an appointment."""
        query = select(Task).where(
            and_(
                Task.appointment_id == appointment_id,
                Task.practice_id == self.practice_id,
                Task.is_deleted == False,
            )
        ).order_by(Task.created_at.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_pending_automated_tasks(
        self, limit: int = 100
    ) -> list[Task]:
        """Get automated tasks ready to execute."""
        now = datetime.utcnow().isoformat()

        query = (
            select(Task)
            .where(
                and_(
                    Task.practice_id == self.practice_id,
                    Task.is_deleted == False,
                    Task.is_automated == True,
                    Task.status == TaskStatus.PENDING,
                    or_(
                        Task.scheduled_for.is_(None),
                        Task.scheduled_for <= now,
                    ),
                )
            )
            .order_by(Task.priority.desc(), Task.scheduled_for.asc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ============================================================================
    # Statistics
    # ============================================================================

    async def get_task_stats(self, user_id: Optional[UUID] = None) -> dict:
        """Get task statistics."""
        conditions = [
            Task.practice_id == self.practice_id,
            Task.is_deleted == False,
        ]

        if user_id:
            conditions.append(Task.assigned_to_user_id == user_id)

        # Count by status
        status_query = (
            select(
                Task.status,
                func.count().label("count")
            )
            .where(and_(*conditions))
            .group_by(Task.status)
        )
        status_result = await self.db.execute(status_query)
        status_counts = {row.status.value: row.count for row in status_result}

        # Count by priority
        priority_query = (
            select(
                Task.priority,
                func.count().label("count")
            )
            .where(and_(*conditions))
            .group_by(Task.priority)
        )
        priority_result = await self.db.execute(priority_query)
        priority_counts = {row.priority.value: row.count for row in priority_result}

        # Count by type
        type_query = (
            select(
                Task.task_type,
                func.count().label("count")
            )
            .where(and_(*conditions))
            .group_by(Task.task_type)
        )
        type_result = await self.db.execute(type_query)
        type_counts = {row.task_type.value: row.count for row in type_result}

        # Count overdue
        overdue_tasks = await self.get_overdue_tasks(limit=10000)
        if user_id:
            overdue_tasks = [t for t in overdue_tasks if t.assigned_to_user_id == user_id]

        total_query = select(func.count()).select_from(Task).where(and_(*conditions))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar_one()

        return {
            "total_tasks": total,
            "pending_tasks": status_counts.get("pending", 0),
            "in_progress_tasks": status_counts.get("in_progress", 0),
            "completed_tasks": status_counts.get("completed", 0),
            "overdue_tasks": len(overdue_tasks),
            "by_priority": priority_counts,
            "by_type": type_counts,
        }

    # ============================================================================
    # Automation
    # ============================================================================

    async def execute_automated_task(self, task_id: UUID) -> Optional[Task]:
        """Execute an automated task."""
        task = await self.get_task(task_id)
        if not task:
            return None

        if not task.is_automated:
            raise ValueError("Task is not automated")

        # Update execution timestamps
        task.last_execution_at = datetime.utcnow().isoformat()
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.utcnow().isoformat()

        # If recurring, calculate next execution
        if task.is_recurring and task.recurrence_rule:
            # In production, parse recurrence_rule and calculate next_execution_at
            # For now, just mark it
            task.next_execution_at = None  # Would be calculated from RRULE

        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def update_automation_config(
        self, task_id: UUID, automation_config: dict
    ) -> Optional[Task]:
        """Update task automation configuration."""
        task = await self.get_task(task_id)
        if not task:
            return None

        task.automation_config = automation_config
        task.updated_at = datetime.utcnow().isoformat()

        await self.db.flush()
        await self.db.refresh(task)
        return task
