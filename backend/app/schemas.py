from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
class LeadMagnetBase(BaseModel):
    title: str
    type: str
    value_promise: Optional[str] = None
    conversion_score: int
    content: Optional[Any] = None
class LeadMagnetCreate(LeadMagnetBase):
    pass
class LeadMagnet(LeadMagnetBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class LeadBase(BaseModel):
    name: str
    email: str
    lead_magnet_id: int
class LeadCreate(LeadBase):
    pass
class Lead(LeadBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class LandingPageBase(BaseModel):
    lead_magnet_id: int
    headline: str
    value: Optional[str] = None
    cta: str
    from_field: Optional[Any] = None
    thank_you_page: Optional[str] = None
class LandingPageCreate(LandingPageBase):
    pass
class LandingPage(LandingPageBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class EmailTemplateBase(BaseModel):
    lead_magnet_id: int
    sequence_number: int
    subject: str
    body: str
class EmailTemplateCreate(EmailTemplateBase):
    pass
class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class UpgradeOfferBase(BaseModel):
    lead_magnet_id: int
    title: str
    description: Optional[str] = None
    link: str
class UpgradeOfferCreate(UpgradeOfferBase):
    pass
class UpgradeOffer(UpgradeOfferBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True     
