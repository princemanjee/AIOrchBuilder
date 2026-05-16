from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class Profile_viewBase(BaseModel):
    viewer_ip: Optional[str] = None
    view_date: Optional[str] = None
    page: Optional[str] = None
    created_at: Optional[datetime] = None

class Profile_viewCreate(Profile_viewBase):
    pass

class Profile_view(Profile_viewBase):
    id: UUID

    class Config:
        from_attributes = True

class Contact_messageBase(BaseModel):
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    message: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None

class Contact_messageCreate(Contact_messageBase):
    pass

class Contact_message(Contact_messageBase):
    id: UUID

    class Config:
        from_attributes = True

