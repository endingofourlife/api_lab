from datetime import datetime

from sqlalchemy import INTEGER, String, TIMESTAMP, REAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.mixin import TimeStampMixin, TableNameMixin
from database.tables import Base


class Task(Base, TableNameMixin, TimeStampMixin):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)
    reward: Mapped[float] = mapped_column(REAL, nullable=False)
    repeat_count: Mapped[int] = mapped_column(INTEGER, default=1, nullable=False)

    users: Mapped[list["User"]] = relationship(
        back_populates="finished_tasks",
        secondary="user_tasks"
    )
