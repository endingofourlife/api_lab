from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.tables import User


class LeaderboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session: AsyncSession = session

    async def get_leaderboard_top_10(self):
        query = (select(User).
                 order_by(User.won_games.desc()).limit(10))
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_user_place(self, user_id: int):
        # Get the count of users with more won games than the target user
        query = select(func.count()).select_from(User).where(User.won_games >
                                                             (select(User.won_games).where(
                                                                 User.id == user_id).scalar_subquery()))
        result = await self._session.execute(query)
        place = result.scalar()
        return place + 1 if place is not None else None
