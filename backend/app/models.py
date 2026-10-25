import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=False)
    role = Column(String(32), default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=utc_now, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    username = Column(String(64), nullable=False)
    action = Column(String(64), nullable=False, index=True) # search, report_generation, export, etc.
    target = Column(String(256), nullable=False)
    module = Column(String(64), nullable=False)
    purpose = Column(Text, nullable=False) # Mandatory investigation purpose
    ip_address = Column(String(64), default="127.0.0.1")
    details = Column(JSON, default=dict)

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(256), nullable=False)
    description = Column(Text, default="")
    investigator = Column(String(128), nullable=False)
    classification = Column(String(32), default="Confidential") # Public / Internal / Confidential
    status = Column(String(32), default="active") # active, closed, archived
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    tags = Column(JSON, default=list) # list of tags
    notes = Column(JSON, default=list) # list of {id, author, text, timestamp}

    findings = relationship("FindingRecord", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("ReportRecord", back_populates="case", cascade="all, delete-orphan")

class FindingRecord(Base):
    __tablename__ = "findings"

    id = Column(String(64), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=True, index=True)
    source = Column(String(128), nullable=False)
    exact_url = Column(Text, nullable=False)
    evidence_snippet = Column(Text, nullable=False)
    confidence = Column(Float, default=0.5)
    confidence_reasoning = Column(Text, default="")
    timestamp = Column(String(64), default=lambda: utc_now().isoformat())
    module = Column(String(64), nullable=False, index=True)
    target = Column(String(256), nullable=False, index=True)
    category = Column(String(64), default="general")
    verified = Column(Boolean, default=False)
    raw_metadata = Column(JSON, default=dict)

    case = relationship("Case", back_populates="findings")

class ReportRecord(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    template_type = Column(String(64), default="technical_report") # executive_summary, technical_report, personal_footprint, brand_fraud, custom
    version = Column(Integer, default=1)
    is_locked = Column(Boolean, default=False)
    executive_summary = Column(Text, default="")
    analyst_narrative = Column(Text, default="")
    finding_ids = Column(JSON, default=list) # List of Finding IDs included in report
    redaction_rules = Column(JSON, default=dict) # Redaction configuration
    hash_manifest = Column(JSON, default=list) # List of {filename, sha256, capture_time}
    chain_of_custody = Column(JSON, default=list) # List of {analyst, tool_version, action, timestamp}
    created_at = Column(DateTime, default=utc_now)
    purpose = Column(Text, nullable=False)
    integrity_status = Column(String(64), default="valid") # valid, rejected_uncited, redacted

    case = relationship("Case", back_populates="reports")
