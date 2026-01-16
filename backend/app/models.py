from sqlalchemy import column, Integer, Text, String,ForeignKey,TIMESTAMP, JSON,Enum
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
class LeadMagnetTypeEnum(str, Enum):
    checklist = "checklist"
    template = "template"
    calculator = "calculator"
    report = "report"
    
class LeadMagnet(Base):
    __tablename__ = "lead_magnet"
    id = column(Integer, primary_key=True, index=True)
    title = column(String, nullable=False)
    type = column(String, nullable=False)
    value_promise = column(Text, nullable=True)
    conversation_score = column(Integer, nullable=False)
    content = column(JSON, nullable=True)
    created_at = column(TIMESTAMP(timezone=True), server_default=func.now())
    LandingPages = relationship("LandingPage", secondary="lead_magnet_landing_page", backref="lead_magnet")
    Leads = relationship("Lead", backref="lead_magnet")
    emails_templates = relationship("EmailTemplate", backref="lead_magnet")
    offer_upgrades = relationship("upgradeOffer", backref="lead_magnet")
class Lead(Base):
    __tablename__ = "leads"
    id = column(Integer, primary_key=True, index=True)
    name = column(String, nullable=False)
    email = column(String, nullable=False, unique=True)
    created_at = column(TIMESTAMP(timezone=True), server_default=func.now())
    lead_magnet_id = column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    lead_magnet = relationship("LeadMagnet", backref="leads")
class LandingPage(Base):
    __tablename__ = "landing_pages"
    id = column(Integer, primary_key=True, index=True)
    lead_magnet_id = column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    headline = column(String, nullable=False)
    value = column(Text, nullable=True)
    cta = column(String, nullable=False)
    from_feild = column(JSON, nullable=True)
    thank_you_page = column(Text, nullable=True)
    created_at = column(TIMESTAMP(timezone=True), server_default=func.now())
    lead_magnet = relationship("LeadMagnet", backref="landing_pages")
class EmailTemplate(Base):
    __tablename__ = "email_templates"
    id = column(Integer, primary_key=True, index=True)
    lead_magnet_id = column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    subject = column(String, nullable=False)
    body = column(Text, nullable=False)
    created_at = column(TIMESTAMP(timezone=True), server_default=func.now())
    lead_magnet = relationship("LeadMagnet", backref="email_templates")
class upgradeOffer(Base):
    __tablename__ = "upgrade_offers"
    id = column(Integer, primary_key=True, index=True)
    lead_magnet_id = column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    title = column(String, nullable=False)
    description = column(Text, nullable=True)
    link = column(String, nullable=False)
    created_at = column(TIMESTAMP(timezone=True), server_default=func.now())
    lead_magnet = relationship("LeadMagnet", backref="upgrade_offers")