from pydantic import BaseModel


class ScenarioRequest(BaseModel):
    scenario: str
