"\"\"\"Declarative base for SQLAlchemy models.\""

from __future__ import annotations

import inflect
from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.core.database import metadata

_inflect = inflect.engine()


class Base(DeclarativeBase):
    metadata = metadata

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate snake_case pluralized table names automatically."""

        name = cls.__name__
        snake = []
        for idx, char in enumerate(name):
            if char.isupper() and idx != 0:
                snake.append("_")
            snake.append(char.lower())
        snake_name = "".join(snake)
        return _inflect.plural(snake_name)
