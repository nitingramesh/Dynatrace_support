from pydantic import BaseModel, Field
from typing import List, Optional


class RetrievedSource(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None


class TroubleshootingResponse(BaseModel):
    question: str
    intent: str = Field(description="question type such as troubleshooting, setup, integration, concept, command_lookup")
    summary: str = Field(description="short direct answer")
    troubleshooting_steps: List[str] = Field(default_factory=list)
    commands: List[str] = Field(default_factory=list)
    relevant_sources: List[RetrievedSource] = Field(default_factory=list)
    confidence: Optional[str] = None