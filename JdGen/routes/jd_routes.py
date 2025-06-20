# ai_hr_jd_project/routes/jd_routes.py
from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from database.connection import get_db # Use get_db for dependency injection
from services.gemini_service import GeminiService
from services.jd_service import JDService
from schemas.jd_schemas import (
    JDGenerateRequest, JobDescriptionContent,
    JDCreateRequest, JDUpdateRequest,
    JDResponse, JDListResponseItem
)
from pydantic import ValidationError
import json # For parsing jd_content_json from DB

jd_bp = Blueprint('jd_routes', __name__, url_prefix='/api/jd')

gemini_service = GeminiService()
jd_service = JDService()

@jd_bp.route('/generate', methods=['POST'])
def generate_jd_endpoint():
    try:
        req_data = JDGenerateRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422 # Unprocessable Entity

    try:
        generated_content: JobDescriptionContent = gemini_service.generate_structured_jd(req_data)
        return jsonify(generated_content.model_dump()), 200
    except Exception as e:
        # Log the exception e
        print(f"Error in /generate endpoint: {e}")
        return jsonify({"error": "Failed to generate JD", "details": str(e)}), 500

@jd_bp.route('', methods=['POST'])
def create_jd_endpoint():
    db: Session = next(get_db())
    try:
        # Ensure jd_content is parsed into JobDescriptionContent if it's a dict
        raw_data = request.json
        if raw_data is not None and 'jd_content' in raw_data and isinstance(raw_data['jd_content'], dict):
            raw_data['jd_content'] = JobDescriptionContent(**raw_data['jd_content'])

        req_data = JDCreateRequest.model_validate(raw_data)
    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422

    try:
        created_jd_db = jd_service.create_jd(db, req_data)
        return jsonify({"job_id": created_jd_db.id, "message": "JD created successfully"}), 201
    except Exception as e:
        print(f"Error in POST /api/jd endpoint: {e}")
        db.rollback()
        return jsonify({"error": "Failed to create JD", "details": str(e)}), 500

@jd_bp.route('', methods=['GET'])
def list_jds_endpoint():
    db: Session = next(get_db())
    try:
        jds_summary_db = jd_service.get_all_jds_summary(db)
        # Manually construct the response if direct Pydantic conversion is tricky for tuples
        response_items = [{"id": item.id, "job_title": item.job_title} for item in jds_summary_db]
        return jsonify(response_items), 200
    except Exception as e:
        print(f"Error in GET /api/jd endpoint: {e}")
        return jsonify({"error": "Failed to retrieve JDs", "details": str(e)}), 500

@jd_bp.route('/<int:job_id>', methods=['GET'])
def get_jd_endpoint(job_id: int):
    db: Session = next(get_db())
    db_jd = jd_service.get_jd_by_id(db, job_id)
    if db_jd is None:
        abort(404, description="Job Description not found")
    
    # Parse the stored JSON string back into the Pydantic model for the response
    parsed_content = jd_service.parse_jd_content(getattr(db_jd, "jd_content_json"))
    
    response_data = JDResponse(
        id=getattr(db_jd, "id"),
        job_title=getattr(db_jd, "job_title"),
        jd_content=parsed_content,
        created_at=getattr(db_jd, "created_at"),
        expires_at=getattr(db_jd, "expires_at"),
        status=db_jd.status.value # Get string value from Enum
    )
    return jsonify(response_data.model_dump()), 200


@jd_bp.route('/<int:job_id>', methods=['PUT'])
def update_jd_endpoint(job_id: int):
    db: Session = next(get_db())
    try:
        raw_data = request.json
        # Handle jd_content if it's part of the update
        if raw_data is not None and 'jd_content' in raw_data and raw_data['jd_content'] and isinstance(raw_data['jd_content'], dict):
            raw_data['jd_content'] = JobDescriptionContent(**raw_data['jd_content'])
        
        req_data = JDUpdateRequest.model_validate(raw_data)

    except ValidationError as e:
        return jsonify({"detail": e.errors()}), 422

    updated_jd_db = jd_service.update_jd(db, job_id, req_data)
    if updated_jd_db is None:
        abort(404, description="Job Description not found")

    # Parse content for response
    parsed_content = jd_service.parse_jd_content(getattr(updated_jd_db, "jd_content_json"))
    response_data = JDResponse(
        id=getattr(updated_jd_db, "id"),
        job_title=getattr(updated_jd_db, "job_title"),
        jd_content=parsed_content,
        created_at=getattr(updated_jd_db, "created_at"),
        expires_at=getattr(updated_jd_db, "expires_at"),
        status=updated_jd_db.status.value
    )
    return jsonify(response_data.model_dump()), 200

@jd_bp.route('/<int:job_id>', methods=['DELETE'])
def delete_jd_endpoint(job_id: int):
    db: Session = next(get_db())
    deleted = jd_service.delete_jd(db, job_id)
    if not deleted:
        abort(404, description="Job Description not found")
    return jsonify({"message": "Job Description deleted successfully"}), 200