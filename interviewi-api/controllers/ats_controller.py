import logging

from flask import Blueprint, jsonify, request

from models.models import ATSScan, db
from services.gemini_service import get_gemini_service
from services.pdf_extractor import PDFError, extract_text_from_pdf

logger = logging.getLogger(__name__)

ats_bp = Blueprint('ats', __name__)

MAX_JD_LENGTH = 20000


@ats_bp.route('/scan', methods=['POST'])
def scan_resume():
    """Analyze a PDF resume against a job description for ATS compatibility."""
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "resume PDF file is required"}), 400

        resume_file = request.files['resume']
        if not resume_file.filename:
            return jsonify({"error": "resume PDF file is required"}), 400

        if not resume_file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are accepted"}), 400

        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            return jsonify({
                "error": "job_description is required and must be a non-empty string"
            }), 400

        if len(job_description) > MAX_JD_LENGTH:
            return jsonify({
                "error": (
                    f"Job description exceeds maximum length of "
                    f"{MAX_JD_LENGTH} characters"
                ),
                "current_length": len(job_description),
                "max_length": MAX_JD_LENGTH
            }), 400

        try:
            resume_text = extract_text_from_pdf(resume_file)
        except PDFError as exc:
            return jsonify({"error": str(exc)}), 400

        analysis = get_gemini_service().analyze_ats(resume_text, job_description)

        if analysis is None:
            return jsonify({
                "error": "Failed to analyze resume. Please try again."
            }), 502

        scan = ATSScan(
            resume_text=resume_text,
            job_description=job_description,
            overall_score=analysis['overall_score'],
            keyword_score=analysis['keyword_score'],
            skills_score=analysis['skills_score'],
            experience_score=analysis['experience_score'],
            format_score=analysis['format_score'],
            matched_keywords=analysis['matched_keywords'],
            missing_keywords=analysis['missing_keywords'],
            suggestions=analysis['suggestions'],
        )
        db.session.add(scan)
        db.session.commit()

        return jsonify({
            "scan_id": scan.id,
            "overall_score": scan.overall_score,
            "keyword_score": scan.keyword_score,
            "skills_score": scan.skills_score,
            "experience_score": scan.experience_score,
            "format_score": scan.format_score,
            "matched_keywords": scan.matched_keywords,
            "missing_keywords": scan.missing_keywords,
            "suggestions": scan.suggestions,
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error("Error scanning resume: %s", e)
        return jsonify({"error": str(e)}), 500


@ats_bp.route('/scan/<int:scan_id>', methods=['GET'])
def get_scan(scan_id):
    """Retrieve a previously saved ATS scan result."""
    try:
        scan = db.session.get(ATSScan, scan_id)
        if not scan:
            return jsonify({"error": "Scan not found"}), 404

        return jsonify({
            "scan_id": scan.id,
            "overall_score": scan.overall_score,
            "keyword_score": scan.keyword_score,
            "skills_score": scan.skills_score,
            "experience_score": scan.experience_score,
            "format_score": scan.format_score,
            "matched_keywords": scan.matched_keywords,
            "missing_keywords": scan.missing_keywords,
            "suggestions": scan.suggestions,
        }), 200

    except Exception as e:
        logger.error("Error fetching scan: %s", e)
        return jsonify({"error": str(e)}), 500
