from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_all_tasks(self) -> List[Task]:
        query = select(Task)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def create_task(self, name: str, expired_at: datetime, reward: float, repeat_count: int = 1) -> Task:
        new_task = Task(name=name, expired_at=expired_at, reward=reward, repeat_count=repeat_count)
        self._session.add(new_task)
        await self._session.commit()
        await self._session.refresh(new_task)
        return new_task

    async def delete_task(self, task_id: int) -> None:
        query = delete(Task).where(Task.id == task_id)
        await self._session.execute(query)
        await self._session.commit()
