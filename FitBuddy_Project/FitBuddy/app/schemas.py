from typing import Literal
from pydantic import BaseModel, Field, field_validator

class UserInput(BaseModel):
    user_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=500)
    goal: str = Field(min_length=2, max_length=80)
    intensity: Literal["low", "medium", "high"]

    @field_validator("name", "goal")
    @classmethod
    def clean_text(cls, value):
        return " ".join(value.strip().split())

class FeedbackRequest(BaseModel):
    feedback: str = Field(min_length=3, max_length=2000)
