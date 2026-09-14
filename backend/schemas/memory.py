from pydantic import BaseModel, Field


class LongTermMemoryOutput(BaseModel):
    weak_areas: list[str] = Field(
      description="The student's areas of difficulty"
    )
