from enum import Enum

from pydantic import BaseModel, Field 

class ContextType(str, Enum):
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"


class RouterOutput(BaseModel):
    context: ContextType = Field(
        ...,
        description=f"{ContextType.RELEVANT}: relevant to the clinical case; {ContextType.IRRELEVANT}: irrelevant to the clinical case;"
    )
