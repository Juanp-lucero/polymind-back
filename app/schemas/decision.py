from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

MAX_ALTERNATIVES = 8
MAX_ALTERNATIVE_LENGTH = 200


def normalize_alternatives(values: list[str] | None) -> list[str] | None:
    """Quita espacios, alternativas vacías y repetidas; limita su cantidad."""
    if values is None:
        return None

    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        alternative = " ".join(str(value).split())
        if not alternative:
            continue
        if len(alternative) > MAX_ALTERNATIVE_LENGTH:
            raise ValueError(
                f"Cada alternativa admite máximo {MAX_ALTERNATIVE_LENGTH} caracteres"
            )
        key = alternative.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(alternative)

    if len(cleaned) > MAX_ALTERNATIVES:
        raise ValueError(
            f"Se permiten máximo {MAX_ALTERNATIVES} alternativas"
        )
    return cleaned


class DecisionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)
    context: Optional[str] = None
    alternatives: list[str] = Field(default_factory=list)

    @field_validator("alternatives")
    @classmethod
    def clean_alternatives(cls, value):
        return normalize_alternatives(value)


class DecisionUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    description: Optional[str] = Field(default=None, min_length=10)
    context: Optional[str] = None
    alternatives: Optional[list[str]] = None
    status: Optional[str] = Field(
        default=None,
        pattern="^(pending|in_progress|completed|cancelled)$"
    )

    @field_validator("alternatives")
    @classmethod
    def clean_alternatives(cls, value):
        return normalize_alternatives(value)


class DecisionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    context: Optional[str]
    alternatives: list[str]
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
