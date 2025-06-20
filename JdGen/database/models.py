# ai_hr_jd_project/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class JDTable(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_title = Column(String(255), nullable=False, index=True)
    # Storing the structured JD as JSON text.
    # For MySQL, JSON type is better if available and using newer versions,
    # otherwise TEXT/LONGTEXT is fine.
    jd_content_json = Column(Text, nullable=False) # Store Pydantic model as JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.ACTIVE, nullable=False)

    def __repr__(self):
        return f"<JDTable(id={self.id}, job_title='{self.job_title}')>"