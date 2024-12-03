from sqlalchemy.ext.declarative import declared_attr


class TableNameMixin:

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'
