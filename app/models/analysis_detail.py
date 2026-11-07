
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    JSON,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AnalysisDetail(Base):

    __tablename__ = "analysis_details"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=False,
        unique=True,
        index=True
    )

    agent_results = Column(
        JSON,
        nullable=False,
        default=list
    )

    alternative_comparison = Column(
        JSON,
        nullable=False,
        default=list
    )

    weights = Column(
        JSON,
        nullable=False,
        default=dict
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
