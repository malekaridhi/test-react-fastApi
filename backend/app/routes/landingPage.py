from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db
from services.llmService import LLMService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/landing-pages", tags=["landing-pages"])

llm_service = LLMService()

# ==================== CRUD OPERATIONS ====================

@router.post("/", response_model=schemas.LandingPage, status_code=status.HTTP_201_CREATED)
async def create_landing_page(
    landing_page: schemas.LandingPageCreate,
    db: Session = Depends(get_db)
):
    """Create a new landing page"""
    # Check if lead magnet exists
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=landing_page.lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {landing_page.lead_magnet_id} not found"
        )
    
    try:
        return crud.create_landing_page(db=db, landing_page=landing_page)
    except Exception as e:
        logger.error(f"Error creating landing page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create landing page: {str(e)}"
        )

@router.get("/", response_model=List[schemas.LandingPage])
async def get_landing_pages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all landing pages"""
    return crud.get_landing_pages(db=db, skip=skip, limit=limit)

@router.get("/{landing_page_id}", response_model=schemas.LandingPage)
async def get_landing_page(
    landing_page_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific landing page by ID"""
    landing_page = crud.get_landing_page(db=db, landing_page_id=landing_page_id)
    if not landing_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Landing page with id {landing_page_id} not found"
        )
    return landing_page

@router.get("/by-lead-magnet/{lead_magnet_id}", response_model=schemas.LandingPage)
async def get_landing_page_by_lead_magnet(
    lead_magnet_id: int,
    db: Session = Depends(get_db)
):
    """Get landing page for a specific lead magnet"""
    landing_page = crud.get_landing_page_by_lead_magnet(
        db=db,
        lead_magnet_id=lead_magnet_id
    )
    if not landing_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No landing page found for lead magnet {lead_magnet_id}"
        )
    return landing_page

@router.put("/{landing_page_id}", response_model=schemas.LandingPage)
async def update_landing_page(
    landing_page_id: int,
    landing_page_update: schemas.LandingPageCreate,
    db: Session = Depends(get_db)
):
    """Update a landing page"""
    landing_page = crud.update_landing_page(
        db=db,
        landing_page_id=landing_page_id,
        landing_page_update=landing_page_update
    )
    if not landing_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Landing page with id {landing_page_id} not found"
        )
    return landing_page

@router.delete("/{landing_page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_landing_page(
    landing_page_id: int,
    db: Session = Depends(get_db)
):
    """Delete a landing page"""
    success = crud.delete_landing_page(db=db, landing_page_id=landing_page_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Landing page with id {landing_page_id} not found"
        )
    return None

# ==================== GENERATE LANDING PAGE ====================

@router.post("/{lead_magnet_id}/generate", response_model=schemas.LandingPage, status_code=status.HTTP_201_CREATED)
async def generate_landing_page(
    lead_magnet_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate landing page copy for a lead magnet using AI
    """
    # Get the lead magnet
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    
    # Check if landing page already exists
    existing = crud.get_landing_page_by_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Landing page already exists for this lead magnet. Use PUT to update."
        )
    
    try:
        # Convert lead magnet to dict for LLM service
        lead_magnet_dict = {
            "title": lead_magnet.title,
            "type": lead_magnet.type.value,
            "value_promise": lead_magnet.value_promise
        }
        
        # Generate landing page copy
        landing_page_data = llm_service.generate_landing_page_copy(lead_magnet_dict)
        
        # Create landing page schema
        landing_page_create = schemas.LandingPageCreate(
            lead_magnet_id=lead_magnet_id,
            headline=landing_page_data.get("headline", ""),
            value=landing_page_data.get("subheadline", ""),
            cta=landing_page_data.get("cta", "Download Now"),
            from_field=landing_page_data.get("form_fields", ["name", "email"]),
            thank_you_page=landing_page_data.get("thank_you_page", "")
        )
        
        # Save to database
        return crud.create_landing_page(db=db, landing_page=landing_page_create)
        
    except Exception as e:
        logger.error(f"Error generating landing page: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate landing page: {str(e)}"
        )