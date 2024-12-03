from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from database.tables import User, UserTask, Task
from database.tables.game import Game


class UserRepository:

    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def create_user(self,
                          user_name: str,
                          telegram_id: int,
                          referrer_id: Optional[int] = None) -> User:
        new_user = User(id=telegram_id, name=user_name, balance=0)

        if referrer_id:
            referrer = await self.get_user_by_id(referrer_id)
            if referrer:
                new_user.referrer_id = referrer_id
                referrer.balance += 10
                new_user.balance += 5

        self._session.add(new_user)
        await self._session.commit()
        await self._session.refresh(new_user)
        return new_user

    async def get_all_users(self) -> List[User]:
        query = select(User)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_user_by_id(self, telegram_id: int) -> Optional[User]:
        query = select(User).where(User.id == telegram_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_friends(self, user_id: int) -> List[User]:
        result = await self._session.scalars(
            select(User).where(User.referrer_id == user_id))
        friends = result.all()
        return friends

    async def get_user_games(self, user_id: int) -> list:
        query = select(Game).where(Game.user_id == user_id)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_user_tasks(self, user_id: int) -> List[Task]:
        completed_task_alias = aliased(UserTask)

        # Select tasks not completed by the user
        query = (
            select(Task).outerjoin(
                completed_task_alias, (completed_task_alias.task_id == Task.id)
                & (completed_task_alias.user_id == user_id)).where(
                    completed_task_alias.user_id == None, Task.expired_at
                    > datetime.now(), Task.repeat_count
                    > 0)  # Only tasks the user hasn't completed
        )

        result = await self._session.execute(query)
        return result.scalars().all()

    async def finish_task(self, user_id: int, task_id: int) -> None:
        task = await self._session.get(Task, task_id)
        if task is None:
            raise ValueError(f"Task with ID {task_id} not found")

        if task.repeat_count <= 0:
            raise ValueError(f"Task with ID {task_id} has no more repeats")

        user = await self._session.get(User, user_id)
        if user is None:
            raise ValueError(f"User with ID {user_id} not found")

        user_task = UserTask(user_id=user_id, task_id=task_id)
        self._session.add(user_task)

        user.balance += task.reward
        task.repeat_count -= 1

        await self._session.commit()

    async def update_user_balance(self, user_id: int, reward: float) -> None:
        query = update(User).where(User.id == user_id).values(
            balance=User.balance + reward)
        await self._session.execute(query)
        await self._session.commit()
