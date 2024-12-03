from typing import Optional

from sqlalchemy import INTEGER, REAL, BOOLEAN, BIGINT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base
from ..mixin import TimeStampMixin, TableNameMixin


class Game(Base, TimeStampMixin, TableNameMixin):
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    bet: Mapped[float] = mapped_column(REAL, nullable=False)
    symbol: Mapped[str] = mapped_column(String(255), nullable=False)
    result: Mapped[str] = mapped_column(String(255), nullable=True)

    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped['User'] = relationship(back_populates='games')
