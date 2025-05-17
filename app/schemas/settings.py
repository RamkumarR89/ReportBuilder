from pydantic import BaseModel
from typing import Optional

class SettingsBase(BaseModel):
    db_server: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    gemini_model: Optional[str] = None
    gemini_api_key: Optional[str] = None

class SettingsCreate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    id: int
    class Config:
        orm_mode = True 