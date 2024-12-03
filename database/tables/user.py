from typing import Optional

from sqlalchemy import INTEGER, String, REAL, BIGINT, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..mixin import TimeStampMixin, TableNameMixin


class User(Base, TimeStampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    balance: Mapped[float] = mapped_column(REAL, nullable=False)

    referrer_id: Mapped[Optional[int]] = mapped_column(INTEGER, ForeignKey('users.id'))
    referrer: Mapped[Optional['User']] = relationship(
        'User',
        back_populates='referrals',
        remote_side=[id]
    )
    referrals: Mapped[list['User']] = relationship(
        'User',
        back_populates='referrer'
    )
    won_games: Mapped[Optional[int]] = mapped_column(INTEGER, nullable=False, default=0)
    games: Mapped[Optional[list['Game']]] = relationship(
        back_populates='user'
    )
    finished_tasks: Mapped[list["Task"]] = relationship(
        back_populates="users",
        secondary="user_tasks"
    )
