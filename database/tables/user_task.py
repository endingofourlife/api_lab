from datetime import datetime

from sqlalchemy import INTEGER, ForeignKey, TIMESTAMP, BOOLEAN
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.mixin import TableNameMixin
from database.tables import Base


class UserTask(Base):
    __tablename__ = "user_tasks"
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False
    )
