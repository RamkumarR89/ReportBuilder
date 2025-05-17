from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.models import ChatSession, ChartConfiguration, ChatMessage, SessionWorkflow, Report, Settings, ReportMessageSQL, ChartType, ReportChartConfiguration, ReportWorkflow
from datetime import datetime
from app.schemas.report import Report as ReportSchema, ReportCreate
from pydantic import BaseModel
from app.schemas.settings import SettingsCreate, SettingsResponse
import pyodbc
import json
import os
import requests
import logging

router = APIRouter()

class ChatMessageCreate(BaseModel):
    message: str
    generated_sql: str
    role: str = "admin"

class DBMetaRequest(BaseModel):
    server: str
    user: str
    password: str
    database: str

class GenerateSQLRequest(BaseModel):
    message: str

class ReportChartConfigCreate(BaseModel):
    chart_type_id: int
    x_axis_field: str
    y_axis_field: str
    series_field: str = None
    size_field: str = None
    color_field: str = None
    options_json: str = None
    filters_json: str = None

class ReportChartConfigResponse(BaseModel):
    id: int
    report_id: int
    chart_type_id: int
    x_axis_field: str
    y_axis_field: str
    series_field: str = None
    size_field: str = None
    color_field: str = None
    options_json: str = None
    filters_json: str = None
    created_at: datetime
    updated_at: datetime = None
    class Config:
        orm_mode = True
        fields = {
            'id': 'Id',
            'report_id': 'ReportId',
            'chart_type_id': 'ChartTypeId',
            'x_axis_field': 'XAxisField',
            'y_axis_field': 'YAxisField',
            'series_field': 'SeriesField',
            'size_field': 'SizeField',
            'color_field': 'ColorField',
            'options_json': 'OptionsJson',
            'filters_json': 'FiltersJson',
            'created_at': 'CreatedAt',
            'updated_at': 'UpdatedAt',
        }

class ReportUpdate(BaseModel):
    report_name: str = None
    report_desc: str = None
    is_deleted: bool = None

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
    reports = db.query(Report).filter(Report.is_deleted == False).offset(skip).limit(limit).all()
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
    # Create ReportWorkflow row
    workflow = ReportWorkflow(ReportId=db_report.id, HasReportName=True)
    db.add(workflow)
    db.commit()
    return db_report

@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@router.post("/settings", response_model=SettingsResponse)
def save_settings(settings_in: SettingsCreate, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if settings:
        for field, value in settings_in.dict().items():
            setattr(settings, field, value)
    else:
        settings = Settings(**settings_in.dict())
        db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

@router.get("/chart-types")
def get_chart_types(db: Session = Depends(get_db)):
    chart_types = db.query(ChartType).all()
    return [
        {
            "id": ct.Id,
            "name": ct.Name,
            "description": ct.Description
        }
        for ct in chart_types
    ]

@router.get("/workflow-status")
def get_workflow_status(db: Session = Depends(get_db)):
    workflows = db.query(ReportWorkflow).all()
    return [
        {
            "report_id": w.ReportId,
            "has_report_name": w.HasReportName,
            "has_message_query": w.HasMessageQuery,
            "has_chart_configured": w.HasChartConfigured,
            "is_published": w.IsPublished
        }
        for w in workflows
    ]

@router.get("/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/{report_id}", response_model=ReportSchema)
def update_report(report_id: int, update: ReportUpdate, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if update.report_name is not None:
        # Check for unique name
        existing = db.query(Report).filter(Report.title == update.report_name, Report.id != report_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="This report name already exists.")
        report.title = update.report_name
    if update.report_desc is not None:
        report.description = update.report_desc
    if update.is_deleted is not None:
        report.is_deleted = update.is_deleted
    db.commit()
    db.refresh(report)
    return report

@router.post("/{report_id}/messages")
def add_message(report_id: int, msg: ChatMessageCreate, db: Session = Depends(get_db)):
    # Check if the report exists
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report_msg = ReportMessageSQL(
        ReportId=report_id,
        Message=msg.message,
        GeneratedSql=msg.generated_sql,
        Role=msg.role,
        CreatedAt=datetime.utcnow()
    )
    db.add(report_msg)
    # Update workflow
    workflow = db.query(ReportWorkflow).filter(ReportWorkflow.ReportId == report_id).first()
    if workflow:
        workflow.HasMessageQuery = True
    db.commit()
    db.refresh(report_msg)
    return {"message": "Saved", "id": report_msg.Id}

@router.get("/{report_id}/messages")
def get_report_messages(report_id: int, db: Session = Depends(get_db)):
    messages = db.query(ReportMessageSQL).filter(
        ReportMessageSQL.ReportId == report_id,
        ReportMessageSQL.is_deleted == False
    ).order_by(ReportMessageSQL.CreatedAt.desc()).all()
    return [
        {
            "id": m.Id,
            "message": m.Message,
            "generated_sql": m.GeneratedSql,
            "role": m.Role,
            "created_at": m.CreatedAt
        }
        for m in messages
    ]

@router.post("/db-metadata")
def get_db_metadata(req: DBMetaRequest):
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={req.server};"
        f"UID={req.user};"
        f"PWD={req.password};"
        f"DATABASE={req.database};"
        f"TrustServerCertificate=yes;"
    )
    query = '''
SELECT 
    t.name AS TableName,
    s.name AS SchemaName,
    (
        SELECT 
            c.name AS ColumnName,
            ty.name AS DataType,
            c.max_length AS MaxLength,
            c.precision AS Precision,
            c.scale AS Scale,
            c.is_nullable AS IsNullable,
            c.is_identity AS IsIdentity,
            dc.definition AS DefaultValue
        FROM sys.columns c
        INNER JOIN sys.types ty ON c.user_type_id = ty.user_type_id
        LEFT JOIN sys.default_constraints dc 
            ON dc.parent_object_id = c.object_id AND dc.parent_column_id = c.column_id
        WHERE c.object_id = t.object_id
        FOR JSON PATH
    ) AS Columns,
    (
        SELECT DISTINCT
            kc.name AS PrimaryKeyName,
            col.name AS ColumnName
        FROM sys.key_constraints kc
        INNER JOIN sys.index_columns ic 
            ON kc.parent_object_id = ic.object_id AND kc.unique_index_id = ic.index_id
        INNER JOIN sys.columns col 
            ON ic.object_id = col.object_id AND ic.column_id = col.column_id
        WHERE kc.parent_object_id = t.object_id AND kc.type = 'PK'
        FOR JSON PATH
    ) AS PrimaryKeys,
    (
        SELECT DISTINCT
            fk.name AS ForeignKeyName,
            pc.name AS ColumnName,
            rt.name AS ReferencedTable,
            rc.name AS ReferencedColumn
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc 
            ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.columns pc 
            ON fkc.parent_object_id = pc.object_id AND fkc.parent_column_id = pc.column_id
        INNER JOIN sys.columns rc 
            ON fkc.referenced_object_id = rc.object_id AND fkc.referenced_column_id = rc.column_id
        INNER JOIN sys.tables rt 
            ON rt.object_id = rc.object_id
        WHERE fk.parent_object_id = t.object_id
        FOR JSON PATH
    ) AS ForeignKeys
FROM sys.tables t
INNER JOIN sys.schemas s ON s.schema_id = t.schema_id
where s.name not in ('alerts','bops','cache','ftp','integration','reports','sellerrating','smart','admin')
ORDER BY s.name, t.name FOR JSON PATH;
'''
    schema_file_path = os.path.join(os.path.dirname(__file__), '../../schemas/schema_metadata.json')
    schema_file_path = os.path.normpath(schema_file_path)
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                row_dict = dict(zip(columns, row))
                for key in ["Columns", "PrimaryKeys", "ForeignKeys"]:
                    if row_dict.get(key):
                        row_dict[key] = json.loads(row_dict[key])
                results.append(row_dict)
            # Write to file
            with open(schema_file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")

# New endpoint to read schema metadata from file
@router.get("/db-metadata-file")
def get_db_metadata_file():
    schema_file_path = os.path.join(os.path.dirname(__file__), '../../schemas/schema_metadata.json')
    schema_file_path = os.path.normpath(schema_file_path)
    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Schema metadata file not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading schema metadata file: {str(e)}")

@router.post("/generate-sql")
def generate_sql(req: GenerateSQLRequest, db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings or not settings.gemini_api_key or not settings.gemini_model:
        raise HTTPException(status_code=400, detail="Gemini API settings not configured.")
    api_key = settings.gemini_api_key
    model = settings.gemini_model
    # Load schema from file
    schema_file_path = os.path.join(os.path.dirname(__file__), '../../schemas/schema_metadata.json')
    schema_file_path = os.path.normpath(schema_file_path)
    try:
        with open(schema_file_path, 'r', encoding='utf-8') as f:
            db_schema = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load schema metadata: {str(e)}")
    # Compose prompt
    prompt = (
        "You are an expert SQL generator. Given this database schema (in JSON) and a user request, "
        "write a valid SQL query using the schema. "
        "Always list all column names explicitly in the SELECT clause (do not use *). "
        "Only output the SQL, no explanation or markdown.\n"
        f"Schema: {db_schema}\n"
        f"User request: {req.message}\n"
        "SQL:"
    )
    # Call Gemini API (adjust endpoint as needed)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, json=payload)
    if not response.ok:
        raise HTTPException(status_code=500, detail="Gemini API error: " + response.text)
    data = response.json()
    generated_sql = data["candidates"][0]["content"]["parts"][0]["text"]
    return {"generated_sql": generated_sql}

@router.post("/{report_id}/chart-configurations", response_model=ReportChartConfigResponse)
def create_report_chart_config(report_id: int, config: ReportChartConfigCreate, db: Session = Depends(get_db)):
    chart_config = ReportChartConfiguration(
        ReportId=report_id,
        ChartTypeId=config.chart_type_id,
        XAxisField=config.x_axis_field,
        YAxisField=config.y_axis_field,
        SeriesField=config.series_field,
        SizeField=config.size_field,
        ColorField=config.color_field,
        OptionsJson=config.options_json,
        FiltersJson=config.filters_json
    )
    db.add(chart_config)
    # Update workflow
    workflow = db.query(ReportWorkflow).filter(ReportWorkflow.ReportId == report_id).first()
    if workflow:
        workflow.HasChartConfigured = True
    db.commit()
    db.refresh(chart_config)
    return chart_config

@router.get("/{report_id}/chart-configurations", response_model=ReportChartConfigResponse)
def get_report_chart_config(report_id: int, db: Session = Depends(get_db)):
    config = db.query(ReportChartConfiguration).filter(ReportChartConfiguration.ReportId == report_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Chart configuration not found")
    return config

@router.put("/{report_id}/chart-configurations/{config_id}", response_model=ReportChartConfigResponse)
def update_report_chart_config(report_id: int, config_id: int, config: ReportChartConfigCreate, db: Session = Depends(get_db)):
    chart_config = db.query(ReportChartConfiguration).filter(ReportChartConfiguration.Id == config_id, ReportChartConfiguration.ReportId == report_id).first()
    if not chart_config:
        raise HTTPException(status_code=404, detail="Chart configuration not found")
    chart_config.ChartTypeId = config.chart_type_id
    chart_config.XAxisField = config.x_axis_field
    chart_config.YAxisField = config.y_axis_field
    chart_config.SeriesField = config.series_field
    chart_config.SizeField = config.size_field
    chart_config.ColorField = config.color_field
    chart_config.OptionsJson = config.options_json
    chart_config.FiltersJson = config.filters_json
    db.commit()
    db.refresh(chart_config)
    return chart_config

@router.get("/{report_id}/has-publish-report")
def has_publish_report(report_id: int, db: Session = Depends(get_db)):
    # Check report exists and not deleted
    report = db.query(Report).filter(Report.id == report_id, Report.is_deleted == False).first()
    if not report:
        return {"can_publish": False}
    # Check at least one message
    has_message = db.query(ReportMessageSQL).filter(ReportMessageSQL.ReportId == report_id, ReportMessageSQL.is_deleted == False).first() is not None
    # Check chart config
    has_chart = db.query(ReportChartConfiguration).filter(ReportChartConfiguration.ReportId == report_id).first() is not None
    can_publish = has_message and has_chart
    return {"can_publish": can_publish}

@router.post("/{report_id}/publish")
def publish_report(report_id: int, db: Session = Depends(get_db)):
    workflow = db.query(ReportWorkflow).filter(ReportWorkflow.ReportId == report_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found for this report")
    workflow.IsPublished = True
    db.commit()
    return {"message": "Report published"} 