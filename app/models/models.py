from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.core.database import Base
from enum import Enum

class ChartTypeEnum(str, Enum):
    Line = 'Line'
    Bar = 'Bar'
    Pie = 'Pie'
    Scatter = 'Scatter'
    Area = 'Area'
    Column = 'Column'
    Bubble = 'Bubble'
    Radar = 'Radar'
    HeatMap = 'HeatMap'
    BoxPlot = 'BoxPlot'
    Funnel = 'Funnel'
    Gauge = 'Gauge'
    Waterfall = 'Waterfall'
    Candlestick = 'Candlestick'
    TreeMap = 'TreeMap'

class ChatSession(Base):
    __tablename__ = "ChatSessions"

    Id = Column(BigInteger, primary_key=True, index=True)
    UserId = Column(String(450), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    LastModifiedAt = Column(DateTime, nullable=True)
    ReportName = Column(String(255), nullable=True)
    IsActive = Column(Boolean, nullable=False, default=True)

    # Relationships
    chart_configurations = relationship("ChartConfiguration", back_populates="chat_session", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")
    session_workflow = relationship("SessionWorkflow", back_populates="chat_session", uselist=False, cascade="all, delete-orphan")
    measured_values = relationship("MeasuredValue", back_populates="chat_session", cascade="all, delete-orphan")

class ChartType(Base):
    __tablename__ = "ChartTypes"

    Id = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False)
    Description = Column(String(100), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    IsActive = Column(Boolean, nullable=False, default=True)

    # Relationships
    chart_configurations = relationship("ChartConfiguration", back_populates="chart_type")

class ChartConfiguration(Base):
    __tablename__ = "ChartConfigurations"

    Id = Column(BigInteger, primary_key=True, index=True)
    ChatSessionId = Column(BigInteger, ForeignKey("ChatSessions.Id", ondelete="CASCADE"), nullable=False)
    ChartTypeId = Column(Integer, ForeignKey("ChartTypes.Id"), nullable=False)
    XAxisField = Column(String(100), nullable=True)
    YAxisField = Column(String(100), nullable=True)
    SeriesField = Column(String(100), nullable=True)
    SizeField = Column(String(100), nullable=True)
    ColorField = Column(String(100), nullable=True)
    OptionsJson = Column(Text, nullable=True)
    FiltersJson = Column(Text, nullable=True)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="chart_configurations")
    chart_type = relationship("ChartType", back_populates="chart_configurations")

class ChatMessage(Base):
    __tablename__ = "ChatMessages"

    Id = Column(BigInteger, primary_key=True, index=True)
    ChatSessionId = Column(BigInteger, ForeignKey("ChatSessions.Id", ondelete="CASCADE"), nullable=False)
    Message = Column(Text, nullable=False)
    Role = Column(String(50), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    GeneratedSql = Column(Text, nullable=True)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="chat_messages")

class SessionWorkflow(Base):
    __tablename__ = "SessionWorkflows"

    Id = Column(BigInteger, primary_key=True, index=True)
    ChatSessionId = Column(BigInteger, ForeignKey("ChatSessions.Id"), nullable=False)
    HasReportName = Column(Boolean, nullable=False, default=False)
    HasMessageQuery = Column(Boolean, nullable=False, default=False)
    HasChartConfigured = Column(Boolean, nullable=False, default=False)
    IsPublished = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="session_workflow")

class MeasuredValue(Base):
    __tablename__ = "MeasuredValues"

    Id = Column(BigInteger, primary_key=True, index=True)
    ChatSessionId = Column(BigInteger, ForeignKey("ChatSessions.Id", ondelete="CASCADE"), nullable=False)
    Name = Column(String(200), nullable=False)
    Description = Column(String(500), nullable=True)
    Unit = Column(String(50), nullable=True)
    Query = Column(Text, nullable=False)

    # Relationships
    chat_session = relationship("ChatSession", back_populates="measured_values")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    db_server = Column(String(255), nullable=True)
    db_user = Column(String(255), nullable=True)
    db_password = Column(String(255), nullable=True)
    db_name = Column(String(255), nullable=True)
    gemini_model = Column(String(255), nullable=True)
    gemini_api_key = Column(String(255), nullable=True)

class ReportMessageSQL(Base):
    __tablename__ = "ReportMessageSQL"
    Id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    ReportId = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    Message = Column(Text, nullable=False)
    GeneratedSql = Column(Text, nullable=True)
    Role = Column(String(50), nullable=False)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False, nullable=False)

class ReportChartConfiguration(Base):
    __tablename__ = "ReportChartConfiguration"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    ReportId = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    ChartTypeId = Column(Integer, ForeignKey("ChartTypes.Id"), nullable=False)
    XAxisField = Column(String(100))
    YAxisField = Column(String(100))
    SeriesField = Column(String(100))
    SizeField = Column(String(100))
    ColorField = Column(String(100))
    OptionsJson = Column(Text)
    FiltersJson = Column(Text)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, onupdate=datetime.utcnow)

class ReportWorkflow(Base):
    __tablename__ = "ReportWorkflow"
    Id = Column(Integer, primary_key=True, autoincrement=True)
    ReportId = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, unique=True)
    HasReportName = Column(Boolean, default=False, nullable=False)
    HasMessageQuery = Column(Boolean, default=False, nullable=False)
    HasChartConfigured = Column(Boolean, default=False, nullable=False)
    IsPublished = Column(Boolean, default=False, nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, onupdate=datetime.utcnow)