from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    api_key: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class Finding(BaseModel):
    id: str
    source: str
    exact_url: str
    evidence_snippet: str
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_reasoning: Optional[str] = ""
    timestamp: str
    module: str
    target: str
    category: Optional[str] = "general"
    verified: Optional[bool] = False
    raw_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class FindingCreate(BaseModel):
    source: str
    exact_url: str
    evidence_snippet: str
    confidence: float
    confidence_reasoning: Optional[str] = ""
    timestamp: Optional[str] = None
    module: str
    target: str
    category: Optional[str] = "general"
    verified: Optional[bool] = False
    raw_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class AuditLogEntry(BaseModel):
    id: str
    timestamp: datetime
    user_id: str
    username: str
    action: str
    target: str
    module: str
    purpose: str
    ip_address: str
    details: Dict[str, Any]

    class Config:
        from_attributes = True

# Search Requests
class SearchBaseRequest(BaseModel):
    purpose: str = Field(..., min_length=5, description="Mandatory stated purpose of the investigation")
    lawful_confirmation: bool = Field(..., description="Confirmation of lawful purpose & privacy awareness")
    target_type: Optional[str] = "public" # public, self, organization

class UsernameSearchRequest(SearchBaseRequest):
    username: str = Field(..., min_length=2, max_length=128)
    generate_variants: bool = True
    check_web_mentions: bool = True
    max_sites: Optional[int] = 500

class EmailDomainSearchRequest(SearchBaseRequest):
    query: str = Field(..., min_length=3, max_length=256)
    check_breaches: bool = True
    check_subdomains: bool = True
    check_ct_logs: bool = True

class PhoneSearchRequest(SearchBaseRequest):
    phone_number: str = Field(..., min_length=5, max_length=32)
    default_region: Optional[str] = "US"

class ImageSearchRequest(SearchBaseRequest):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    filename: Optional[str] = "investigation_target.jpg"

class DarkWebSafetyGate(BaseModel):
    amnesic_os_or_isolated_vm: bool
    hardware_devices_disabled: bool
    tor_connection_active: bool
    no_personal_accounts_logged: bool
    no_file_downloads_agreed: bool
    lawful_purpose_accepted: bool

class DarkWebSearchRequest(SearchBaseRequest):
    query: str = Field(..., min_length=2, max_length=256)
    safety_gate: DarkWebSafetyGate

# Case & Report
class Note(BaseModel):
    id: str
    author: str
    text: str
    timestamp: str

class CaseCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    investigator: str
    classification: Optional[str] = "Confidential" # Public, Internal, Confidential
    tags: Optional[List[str]] = Field(default_factory=list)

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    classification: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[List[Dict[str, Any]]] = None

class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    investigator: str
    classification: str
    status: str
    created_at: datetime
    updated_at: datetime
    tags: List[str]
    notes: List[Dict[str, Any]]
    findings: Optional[List[Finding]] = []

    class Config:
        from_attributes = True

class RedactionRules(BaseModel):
    mask_emails: bool = False
    mask_phones: bool = False
    mask_usernames: bool = False
    mask_urls: bool = False
    mask_gps: bool = False
    custom_terms: List[str] = Field(default_factory=list)

class ReportCreate(BaseModel):
    case_id: str
    title: str
    template_type: str = "technical_report"
    purpose: str
    executive_summary: Optional[str] = ""
    analyst_narrative: Optional[str] = ""
    finding_ids: List[str] = Field(default_factory=list)
    redaction_rules: Optional[RedactionRules] = None
    lock_report: bool = False

class ReportUpdate(BaseModel):
    title: Optional[str] = None
    executive_summary: Optional[str] = None
    analyst_narrative: Optional[str] = None
    finding_ids: Optional[List[str]] = None
    redaction_rules: Optional[RedactionRules] = None
    lock_report: Optional[bool] = None

class ReportResponse(BaseModel):
    id: str
    case_id: str
    title: str
    template_type: str
    version: int
    is_locked: bool
    executive_summary: str
    analyst_narrative: str
    finding_ids: List[str]
    redaction_rules: Dict[str, Any]
    hash_manifest: List[Dict[str, Any]]
    chain_of_custody: List[Dict[str, Any]]
    created_at: datetime
    purpose: str
    integrity_status: str

    class Config:
        from_attributes = True
