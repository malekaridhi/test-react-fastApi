from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from services.llmService import LLMService
from services.emails import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-templates", tags=["email-templates"])

llm_service = LLMService()
email_service = EmailService()

# ==================== CRUD OPERATIONS ====================

@router.post("/", response_model=schemas.EmailTemplate, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    email_template: schemas.EmailTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new email template"""
    # Check if lead magnet exists
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=email_template.lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {email_template.lead_magnet_id} not found"
        )
    
    try:
        return crud.create_email_template(db=db, email_template=email_template)
    except Exception as e:
        logger.error(f"Error creating email template: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create email template: {str(e)}"
        )

@router.get("/", response_model=List[schemas.EmailTemplate])
async def get_email_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all email templates"""
    return crud.get_email_templates(db=db, skip=skip, limit=limit)

@router.get("/{email_template_id}", response_model=schemas.EmailTemplate)
async def get_email_template(
    email_template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific email template by ID"""
    email_template = crud.get_email_template(db=db, email_template_id=email_template_id)
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email template with id {email_template_id} not found"
        )
    return email_template

@router.get("/by-lead-magnet/{lead_magnet_id}", response_model=List[schemas.EmailTemplate])
async def get_email_templates_by_lead_magnet(
    lead_magnet_id: int,
    db: Session = Depends(get_db)
):
    """Get all email templates for a specific lead magnet"""
    return crud.get_email_templates_by_lead_magnet(
        db=db,
        lead_magnet_id=lead_magnet_id
    )

@router.put("/{email_template_id}", response_model=schemas.EmailTemplate)
async def update_email_template(
    email_template_id: int,
    email_template_update: schemas.EmailTemplateCreate,
    db: Session = Depends(get_db)
):
    """Update an email template"""
    email_template = crud.update_email_template(
        db=db,
        email_template_id=email_template_id,
        email_template_update=email_template_update
    )
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email template with id {email_template_id} not found"
        )
    return email_template

@router.delete("/{email_template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_template(
    email_template_id: int,
    db: Session = Depends(get_db)
):
    """Delete an email template"""
    success = crud.delete_email_template(db=db, email_template_id=email_template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email template with id {email_template_id} not found"
        )
    return None

# ==================== GENERATE EMAIL SEQUENCE ====================

@router.post("/{lead_magnet_id}/generate-sequence", response_model=List[schemas.EmailTemplate], status_code=status.HTTP_201_CREATED)
async def generate_email_sequence(
    lead_magnet_id: int,
    num_emails: int = 5,
    db: Session = Depends(get_db)
):
    """
    Generate a nurture email sequence for a lead magnet using AI
    """
    # Get the lead magnet
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    
    # Check if sequence already exists
    existing = crud.get_email_templates_by_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sequence already exists for this lead magnet. Delete existing templates first."
        )
    
    try:
        # Convert lead magnet to dict for LLM service
        lead_magnet_dict = {
            "title": lead_magnet.title,
            "type": lead_magnet.type.value,
            "value_promise": lead_magnet.value_promise
        }
        
        # Generate email sequence
        emails = llm_service.generate_nurture_emails(lead_magnet_dict, num_emails)
        
        # Save emails to database
        created_templates = []
        for email_data in emails:
            email_template_create = schemas.EmailTemplateCreate(
                lead_magnet_id=lead_magnet_id,
                sequence_number=email_data.get("sequence_number", 1),
                subject=email_data.get("subject", ""),
                body=email_data.get("body", "")
            )
            created_template = crud.create_email_template(db=db, email_template=email_template_create)
            created_templates.append(created_template)
        
        return created_templates
        
    except Exception as e:
        logger.error(f"Error generating email sequence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate email sequence: {str(e)}"
        )

# ==================== SEND EMAILS ====================

@router.post("/{email_template_id}/send-to-leads")
async def send_email_to_leads(
    email_template_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send email template to all leads associated with its lead magnet
    """
    # Get email template
    email_template = crud.get_email_template(db=db, email_template_id=email_template_id)
    if not email_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Email template with id {email_template_id} not found"
        )
    
    # Get all leads for this lead magnet
    leads = crud.get_leads_by_lead_magnet(
        db=db,
        lead_magnet_id=email_template.lead_magnet_id
    )
    
    if not leads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No leads found for this lead magnet"
        )
    
    # Convert to dicts
    email_template_dict = {
        "subject": email_template.subject,
        "body": email_template.body,
        "sequence_number": email_template.sequence_number
    }
    
    leads_dict = [
        {"id": lead.id, "name": lead.name, "email": lead.email}
        for lead in leads
    ]
    
    # Send emails in background
    background_tasks.add_task(
        email_service.send_bulk_emails,
        leads_dict,
        email_template_dict
    )
    
    return {
        "message": f"Sending emails to {len(leads)} leads in background",
        "leads_count": len(leads)
    }

@router.post("/send-sequence-to-lead/{lead_id}")
async def send_sequence_to_lead(
    lead_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Send entire email sequence to a specific lead
    """
    # Get lead
    lead = crud.get_lead(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found"
        )
    
    # Get email templates for this lead's lead magnet
    email_templates = crud.get_email_templates_by_lead_magnet(
        db=db,
        lead_magnet_id=lead.lead_magnet_id
    )
    
    if not email_templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No email templates found for this lead magnet"
        )
    
    # Convert to dicts
    lead_dict = {"id": lead.id, "name": lead.name, "email": lead.email}
    
    # Send each email in sequence (in background)
    for email_template in email_templates:
        email_dict = {
            "subject": email_template.subject,
            "body": email_template.body,
            "sequence_number": email_template.sequence_number
        }
        background_tasks.add_task(
            email_service.send_nurture_email,
            lead_dict,
            email_dict
        )
    
    return {
        "message": f"Sending {len(email_templates)} emails to {lead.email} in background",
        "emails_count": len(email_templates)
    }