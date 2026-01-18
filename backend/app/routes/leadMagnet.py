from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from database import get_db
from typing import List,Dict,Any
import schemas 
import crud
import logging
from services.llmService import LLMService
from pydantic import BaseModel
logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/lead-magnets",
    tags=["Lead Magnets"],
)
llm_service = LLMService()
class IdeaRequest(BaseModel):
    icp_profile: str
    pain_points: List[str]
    content_topics: List[str]
    offer_type: str
    brand_voice: str
    conversion_goal: str

class ContentRequest(BaseModel):
    pain_points: List[str]
@router.post("/generate-ideas", response_model=List[Dict[str, Any]])
async def generate_lead_magnet_ideas(
    request: IdeaRequest 
):
    """
    Generate lead magnet ideas using AI based on business context
    """
    try:
        ideas = llm_service.generate_lead_magnet_ideas(
           icp_profile=request.icp_profile,
            pain_points=request.pain_points,
            content_topics=request.content_topics,
            offer_type=request.offer_type,
            brand_voice=request.brand_voice,
            conversion_goal=request.conversion_goal
        )
        return ideas
    except Exception as e:
        logger.error(f"Error generating ideas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate ideas: {str(e)}"
        )
@router.post("/", response_model=schemas.LeadMagnet, status_code=status.HTTP_201_CREATED)
async def create_lead_magnet(
    lead_magnet: schemas.LeadMagnetCreate,
    db: Session = Depends(get_db)
):
    """Create a new lead magnet"""
    try:
        return crud.create_lead_magnet(db=db, lead_magnet=lead_magnet)
    except Exception as e:
        logger.error(f"Error creating lead magnet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create lead magnet: {str(e)}"
        )
@router.get("/", response_model=List[schemas.LeadMagnet])
async def get_lead_magnets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all lead magnets"""
    return crud.get_lead_magnets(db=db, skip=skip, limit=limit)    
@router.get("/{lead_magnet_id}", response_model=schemas.LeadMagnet)
async def get_lead_magnet(
    lead_magnet_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead magnet by ID"""
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    return lead_magnet
@router.put("/{lead_magnet_id}", response_model=schemas.LeadMagnet)
async def update_lead_magnet(
    lead_magnet_id: int,
    lead_magnet_update: schemas.LeadMagnetCreate,
    db: Session = Depends(get_db)
):
    """Update a lead magnet"""
    updates = lead_magnet_update.dict(exclude_unset=True)
    lead_magnet = crud.update_lead_magnet(
        db=db,
        lead_magnet_id=lead_magnet_id,
        updates=updates
    )
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    return lead_magnet
# @router.delete("/{lead_magnet_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_lead_magnet(
#     lead_magnet_id: int,
#     db: Session = Depends(get_db)
# ):
#     """Delete a lead magnet"""
#     success = crud.delete_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Lead magnet with id {lead_magnet_id} not found"
#         )
#     return None
@router.post("/{lead_magnet_id}/generate-content", response_model=schemas.LeadMagnet)
async def generate_lead_magnet_content(
    lead_magnet_id: int,
    request: ContentRequest,
    db: Session = Depends(get_db)
):
    """
    Generate content for a lead magnet based on its type
    """
    # Get the lead magnet
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    
    try:
        # Generate content based on type
        lead_type = lead_magnet.type.value
        
        if lead_type == "checklist":
            content = llm_service.generate_checklist(lead_magnet.title, request.pain_points)
        elif lead_type == "template":
            content = llm_service.generate_template_content(lead_magnet.title, request.pain_points)
        elif lead_type == "calculator":
            content = llm_service.generate_calculator_logic(lead_magnet.title, request.pain_points)
        elif lead_type == "report":
            content = llm_service.generate_report_content(lead_magnet.title, request.pain_points)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown lead magnet type: {lead_type}"
            )
        
        # Update lead magnet with generated content
        lead_magnet.content = content
        db.commit()
        db.refresh(lead_magnet)
        
        return lead_magnet
        
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}"
        )



@router.get("/{lead_magnet_id}/download")
async def download_lead_magnet(
    lead_magnet_id: int,
    db: Session = Depends(get_db)
):
    """
    Download the lead magnet as a file (PDF, HTML, etc.)
    """
    # Get the lead magnet
    lead_magnet = crud.get_lead_magnet(db=db, lead_magnet_id=lead_magnet_id)
    if not lead_magnet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead magnet with id {lead_magnet_id} not found"
        )
    
    if not lead_magnet.content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lead magnet has no content generated yet"
        )
    
    try:
        # Convert to dict for asset service
        lead_magnet_dict = {
            "id": lead_magnet.id,
            "title": lead_magnet.title,
            "type": lead_magnet.type.value,
            "value_promise": lead_magnet.value_promise,
            "content": lead_magnet.content
        }
        
        # Generate asset
        asset_buffer = asset_service.generate_asset(lead_magnet_dict)
        
        # Determine media type and filename
        if lead_magnet.type.value == "calculator":
            media_type = "text/html"
            filename = f"{lead_magnet.title.replace(' ', '_')}.html"
        else:
            media_type = "application/pdf"
            filename = f"{lead_magnet.title.replace(' ', '_')}.pdf"
        
        return StreamingResponse(
            asset_buffer,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating asset: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate asset: {str(e)}"
        )