from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    status: str

class DetoxScore(BaseModel):
    tds: float
    sbs: float
    ebs: float
    vos: float
    sms: float
    uas: float
    brs: float
    persona_type: str
