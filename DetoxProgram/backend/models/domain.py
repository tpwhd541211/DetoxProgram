from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    status: str

class DetoxScore(BaseModel):
    diversity: float
    stability: float
    proactivity: float
    openness: float
    manipulation_index: float
    persona_type: str
