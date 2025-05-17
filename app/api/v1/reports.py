from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import ChatSession, ChartConfiguration, ChatMessage, SessionWorkflow, Report
from datetime import datetime
from app.schemas.report import Report as ReportSchema, ReportCreate

router = APIRouter()

@router.post("/sessions/")
async def create_session(
    user_id: str,
    report_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new report session"""
    session = ChatSession(
        UserId=user_id,
        ReportName=report_name,
        CreatedAt=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Create associated workflow
    workflow = SessionWorkflow(
        ChatSessionId=session.Id,
        HasReportName=bool(report_name)
    )
    db.add(workflow)
    db.commit()
    
    return session

@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report session with all its related data"""
    session = db.query(ChatSession).filter(ChatSession.Id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/sessions/")
async def list_sessions(
    user_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all report sessions with optional filtering"""
    query = db.query(ChatSession)
    if user_id:
        query = query.filter(ChatSession.UserId == user_id)
    
    total = query.count()
    sessions = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "sessions": sessions
    }

@router.put("/sessions/{session_id}")
async def update_session(
    session_id: int,
    report_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update a report session"""
    session = db.query(ChatSession).filter(ChatSession.Id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if report_name is not None:
        session.ReportName = report_name
        # Update workflow status
        if session.session_workflow:
            session.session_workflow.HasReportName = True
    
    if is_active is not None:
        session.IsActive = is_active
    
    session.LastModifiedAt = datetime.utcnow()
    db.commit()
    db.refresh(session)
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Delete a report session and all its related data"""
    session = db.query(ChatSession).filter(ChatSession.Id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session deleted successfully"}

@router.get("/", response_model=List[ReportSchema])
def get_reports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reports = db.query(Report).offset(skip).limit(limit).all()
    return reports

@router.post("/", response_model=ReportSchema)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    # Check if report name already exists
    existing = db.query(Report).filter(Report.title == report.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="This report already exists.")
    db_report = Report(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

@router.get("/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report 