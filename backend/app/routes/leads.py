from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from services.assetsSevice import AssetService
from services.emails import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/leads", tags=["leads"])

asset_service = AssetService()
email_service = EmailService()

# ==================== CRUD OPERATIONS ====================

@router.post("/", response_model=schemas.Lead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead: schemas.LeadCreate,
    background_tasks: BackgroundTasks,
    send_welcome: bool = True,
    db: Session = Depends(get_db)
):
    """
    Create a new lead (from landing page form submission)
    Optionally sends welcome email with lead magnet
    """
    # Check if lead magnet exists
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead.lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead.lead_magnet_id} not found"
        )
    
    # Check if email already exists
    existing_lead = crud.get_lead_by_email(db=db, email=lead.email)
    if existing_lead:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create the lead
        new_lead = crud.create_lead(db=db, lead=lead)
        
        # Send welcome email in background if requested
        if send_welcome and lead_magnet.content:
            background_tasks.add_task(
                send_welcome_email_task,
                new_lead,
                lead_magnet,
                db
            )
        
        return new_lead
        
    except Exception as e:
        logger.error(f"Error creating lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lead: {str(e)}"
        )

@router.get("/", response_model=List[schemas.Lead])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all leads"""
    return crud.get_leads(db=db, skip=skip, limit=limit)

@router.get("/{lead_id}", response_model=schemas.Lead)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead by ID"""
    lead = crud.get_lead(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found"
        )
    return lead

@router.get("/by-lead-magnet/{lead_magnet_id}", response_model=List[schemas.Lead])
async def get_leads_by_lead_magnet(
    lead_magnet_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all leads for a specific lead magnet"""
    return crud.get_leads_by_lead_magnet(
        db=db,
        lead_magnet_id=lead_magnet_id,
        skip=skip,
        limit=limit
    )

@router.put("/{lead_id}", response_model=schemas.Lead)
async def update_lead(
    lead_id: int,
    lead_update: schemas.LeadCreate,
    db: Session = Depends(get_db)
):
    """Update a lead"""
    lead = crud.update_lead(db=db, lead_id=lead_id, lead_update=lead_update)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found"
        )
    return lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Delete a lead"""
    success = crud.delete_lead(db=db, lead_id=lead_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found"
        )
    return None

# ==================== EMAIL OPERATIONS ====================

@router.post("/{lead_id}/send-welcome-email")
async def send_welcome_email(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Manually send welcome email to a lead"""
    # Get the lead
    lead = crud.get_lead(db=db, lead_id=lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with id {lead_id} not found"
        )
    
    # Get the lead magnet
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead.lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead magnet not found"
        )
    
    if not lead_magnet.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead magnet has no content generated"
        )
    
    try:
        # Generate asset
        lead_magnet_dict = {
            "id": lead_magnet.id,
            "title": lead_magnet.title,
            "type": lead_magnet.type.value,
            "value_promise": lead_magnet.value_promise,
            "content": lead_magnet.content
        }
        asset_buffer = asset_service.generate_asset(lead_magnet_dict)
        
        # Send email
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email
        }
        
        success = email_service.send_welcome_email(
            lead=lead_dict,
            lead_magnet=lead_magnet_dict,
            asset_bytes=asset_buffer.read()
        )
        
        if success:
            return {"message": "Welcome email sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
            
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

# ==================== BACKGROUND TASKS ====================

def send_welcome_email_task(lead, lead_magnet, db: Session):
    """Background task to send welcome email"""
    try:
        # Generate asset
        lead_magnet_dict = {
            "id": lead_magnet.id,
            "title": lead_magnet.title,
            "type": lead_magnet.type.value,
            "value_promise": lead_magnet.value_promise,
            "content": lead_magnet.content
        }
        asset_buffer = asset_service.generate_asset(lead_magnet_dict)
        
        # Send email
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email
        }
        
        email_service.send_welcome_email(
            lead=lead_dict,
            lead_magnet=lead_magnet_dict,
            asset_bytes=asset_buffer.read()
        )
        
        logger.info(f"Welcome email sent to {lead.email}")
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")