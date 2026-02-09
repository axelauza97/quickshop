from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import mapped_column
from sqlalchemy import (
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID
from sqlalchemy.orm import mapped_column
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = mapped_column(PSQL_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_sub = mapped_column(String, unique=True, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
