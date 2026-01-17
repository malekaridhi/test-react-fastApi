from sqlalchemy.orm import Session
from models import LeadMagnet, Lead, LandingPage, EmailTemplate, upgradeOffer
import schemas


# Create a new lead magnet
def create_lead_magnet(db: Session, lead_magnet: schemas.LeadMagnetCreate):
    db_lead_magnet = LeadMagnet(
        title=lead_magnet.title,
        type=lead_magnet.type,
        value_promise=lead_magnet.value_promise,
        conversion_score=lead_magnet.conversion_score,
        content=lead_magnet.content,
    )
    db.add(db_lead_magnet)
    db.commit()
    db.refresh(db_lead_magnet)
    return db_lead_magnet

# Get a lead magnet by ID
def get_lead_magnet(db: Session, lead_magnet_id: int):
    return db.query(LeadMagnet).filter(LeadMagnet.id == lead_magnet_id).first()
# Create a new lead
def create_lead(db: Session, lead: schemas.LeadCreate):
    db_lead = Lead(
        name=lead.name,
        email=lead.email,
        lead_magnet_id=lead.lead_magnet_id,
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead
# Create a new landing page
def create_landing_page(db: Session, landing_page: schemas.LandingPageCreate):
    db_landing_page = LandingPage(
        lead_magnet_id=landing_page.lead_magnet_id,
        headline=landing_page.headline,
        value=landing_page.value,
        cta=landing_page.cta,
        form_field=landing_page.form_field,
        thank_you_page=landing_page.thank_you_page,
    )
    db.add(db_landing_page)
    db.commit()
    db.refresh(db_landing_page)
    return db_landing_page
# Create a new email template
def create_email_template(db: Session, email_template: schemas.EmailTemplateCreate):
    db_email_template = EmailTemplate(
        lead_magnet_id=email_template.lead_magnet_id,
        sequence_number=email_template.sequence_number,
        subject=email_template.subject,
        body=email_template.body,
    )
    db.add(db_email_template)
    db.commit()
    db.refresh(db_email_template)
    return db_email_template
# Create a new upgrade offer
def create_upgrade_offer(db: Session, upgrade_offer: schemas.UpgradeOfferCreate):
    db_upgrade_offer = upgradeOffer(
        lead_magnet_id=upgrade_offer.lead_magnet_id,
        title=upgrade_offer.title,
        description=upgrade_offer.description,
        link=upgrade_offer.link,
    )
    db.add(db_upgrade_offer)
    db.commit()
    db.refresh(db_upgrade_offer)
    return db_upgrade_offer 
