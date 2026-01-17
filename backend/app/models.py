from sqlalchemy import  Integer, Text, String,ForeignKey,TIMESTAMP, JSON,Column,Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
from enum import Enum
from sqlalchemy.orm import relationship
class LeadMagnetTypeEnum(str, Enum):
    checklist = "checklist"
    template = "template"
    calculator = "calculator"
    report = "report"
    
class LeadMagnet(Base):
    __tablename__ = "lead_magnet"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(SQLEnum(LeadMagnetTypeEnum), nullable=False)
    value_promise = Column(Text, nullable=True)
    conversion_score = Column(Integer, nullable=False)
    content = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    #relationships
    LandingPages = relationship("LandingPage",  back_populates="lead_magnet")
    Leads = relationship("Lead", back_populates="lead_magnet")
    emails_templates = relationship("EmailTemplate", back_populates="lead_magnet")
    offer_upgrades = relationship("upgradeOffer", back_populates="lead_magnet")
class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    lead_magnet_id = Column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    #relationship to lead magnet
    lead_magnet = relationship("LeadMagnet", back_populates="leads")
class LandingPage(Base):
    __tablename__ = "landing_pages"
    id = Column(Integer, primary_key=True, index=True)
    lead_magnet_id = Column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    headline = Column(String, nullable=False)
    value = Column(Text, nullable=True)
    cta = Column(String, nullable=False)
    form_field = Column(JSON, nullable=True)
    thank_you_page = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    #relationship to lead magnet
    lead_magnet = relationship("LeadMagnet", back_populates="landing_pages")
class EmailTemplate(Base):
    __tablename__ = "email_templates"
    id = Column(Integer, primary_key=True, index=True)
    lead_magnet_id = Column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    # relationship to lead magnet 
    lead_magnet = relationship("LeadMagnet", back_populates="email_templates")
class upgradeOffer(Base):
    __tablename__ = "upgrade_offers"
    id = Column(Integer, primary_key=True, index=True)
    lead_magnet_id = Column(Integer, ForeignKey("lead_magnet.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    link = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
     # relationship to lead magnet 
    lead_magnet = relationship("LeadMagnet", back_populates="upgrade_offers")