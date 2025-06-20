# ai_hr_jd_project/schemas/jd_schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Gemini Structured Output Schema ---
class Section(BaseModel):
    title: str
    content: str # Can be a long string, potentially with markdown

class JobDescriptionContent(BaseModel):
    job_title_generated: str = Field(..., alias="job_title", description="The main title of the job.") # Use alias for gemini
    company_summary: Optional[str] = Field(None, description="A brief summary of the company.")
    role_summary: str = Field(description="A brief summary of the role.")
    key_responsibilities: List[str] = Field(description="List of key responsibilities.")
    required_qualifications: List[str] = Field(description="List of required skills and qualifications.")
    preferred_qualifications: Optional[List[str]] = Field(None, description="List of preferred skills and qualifications.")
    benefits: Optional[List[str]] = Field(None, description="List of benefits offered.")
    # You can add more specific sections or a generic list of sections like:
    # custom_sections: Optional[List[Section]] = None

    class Config:
        populate_by_name = True # Allows using alias in assignment

# --- API Request/Response Schemas ---
class JDGenerateRequest(BaseModel):
    job_title_input: str
    key_responsibilities_input: List[str]
    required_skills_input: List[str]
    company_description_input: Optional[str] = None
    # Add other inputs Gemini might need, e.g., tone, experience_level

class JDCreateRequest(BaseModel):
    job_title: str # For DB storage and easy query, can be same as jd_content.job_title_generated
    jd_content: JobDescriptionContent # The structured JD from Gemini or manual input
    expires_at: Optional[datetime] = None

class JDUpdateRequest(BaseModel):
    job_title: Optional[str] = None
    jd_content: Optional[JobDescriptionContent] = None
    expires_at: Optional[datetime] = None
    status: Optional[str] = None # 'active' or 'inactive'

    @validator('status')
    def status_must_be_valid(cls, value):
        if value is not None and value not in ['active', 'inactive']:
            raise ValueError("Status must be 'active' or 'inactive'")
        return value

class JDResponse(BaseModel):
    id: int
    job_title: str
    jd_content: JobDescriptionContent # Or Dict[str, Any] if you prefer to send raw JSON
    created_at: datetime
    expires_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True #  For SQLAlchemy model conversion (orm_mode in Pydantic v1)

class JDListResponseItem(BaseModel):
    id: int
    job_title: str

    class Config:
        from_attributes = True