from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.sql import func

from app.core.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    decision_id = Column(
        Integer,
        ForeignKey("decisions.id"),
        nullable=False,
        index=True
    )

    analysis = Column(Text, nullable=False)

    recommendations = Column(JSON, nullable=False, default=list)

    status = Column(String(30), nullable=False, default="completed")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )