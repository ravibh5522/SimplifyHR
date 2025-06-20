# ai_hr_jd_project/services/jd_service.py
from sqlalchemy.orm import Session
from database.models import JDTable, JobStatus
from schemas.jd_schemas import JDCreateRequest, JDUpdateRequest, JobDescriptionContent
from datetime import datetime
import json

class JDService:
    def create_jd(self, db: Session, jd_data: JDCreateRequest) -> JDTable:
        # Convert Pydantic model to JSON string for storage
        jd_content_json_str = jd_data.jd_content.model_dump_json()

        db_jd = JDTable(
            job_title=jd_data.job_title, # Using the explicit job_title from request
            jd_content_json=jd_content_json_str,
            created_at=datetime.utcnow(),
            expires_at=jd_data.expires_at,
            status=JobStatus.ACTIVE # Default status
        )
        db.add(db_jd)
        db.commit()
        db.refresh(db_jd)
        return db_jd

    def get_jd_by_id(self, db: Session, job_id: int) -> JDTable | None:
        return db.query(JDTable).filter(JDTable.id == job_id).first()

    def get_all_jds_summary(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(JDTable.id, JDTable.job_title).offset(skip).limit(limit).all()

    def update_jd(self, db: Session, job_id: int, update_data: JDUpdateRequest) -> JDTable | None:
        db_jd = self.get_jd_by_id(db, job_id)
        if db_jd:
            if update_data.job_title is not None:
                setattr(db_jd, "job_title", update_data.job_title)
            if update_data.jd_content is not None:
                setattr(db_jd, "jd_content_json", update_data.jd_content.model_dump_json())
            if update_data.expires_at is not None:  # Allows setting to None too
                setattr(db_jd, "expires_at", update_data.expires_at)
            if update_data.status is not None:
                setattr(db_jd, "status", update_data.status)

            db.commit()
            db.refresh(db_jd)
        return db_jd

    def delete_jd(self, db: Session, job_id: int) -> bool:
        db_jd = self.get_jd_by_id(db, job_id)
        if db_jd:
            db.delete(db_jd)
            db.commit()
            return True
        return False

    # Helper to parse the JSON content back to Pydantic model for responses
    def parse_jd_content(self, jd_content_json: str) -> JobDescriptionContent:
        return JobDescriptionContent.model_validate_json(jd_content_json)