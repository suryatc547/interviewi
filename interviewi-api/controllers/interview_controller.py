import logging

from flask import Blueprint, jsonify, request

from models.models import Answer, Interview, Question, User, db
from services.gemini_service import get_gemini_service

logger = logging.getLogger(__name__)

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/generate', methods=['POST'])
def generate_interview():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        role = data.get('role')
        industry = data.get('industry')
        experience = data.get('experience') # Dictionary of {skill: years}
        job_description = data.get('job_description')

        if not all([name, email, role, industry, experience]):
            return jsonify({"error": "Missing required fields"}), 400

        if not isinstance(role, str) or not role.strip():
            return jsonify({"error": "role must be a non-empty string"}), 400
        if not isinstance(industry, str) or not industry.strip():
            return jsonify({"error": "industry must be a non-empty string"}), 400
        if not isinstance(experience, dict):
            return jsonify({"error": "experience must be an object of {skill: years}"}), 400
        role = role.strip()
        industry = industry.strip()
        if len(role) > 100:
            return jsonify({"error": "role exceeds maximum length of 100 characters"}), 400
        if len(industry) > 100:
            return jsonify({"error": "industry exceeds maximum length of 100 characters"}), 400

        if job_description is not None and not isinstance(job_description, str):
            return jsonify({"error": "job_description must be a string"}), 400
        if job_description is not None:
            job_description = job_description.strip()
            MAX_JD_LENGTH = 20000
            if len(job_description) > MAX_JD_LENGTH:
                return jsonify({
                    "error": (
                        "Job description exceeds maximum length of "
                        f"{MAX_JD_LENGTH} characters"
                    ),
                    "current_length": len(job_description),
                    "max_length": MAX_JD_LENGTH
                }), 400

        # Find or create user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email)
            db.session.add(user)
            db.session.commit()

        # Create Interview. Commit BEFORE generating: generation writes session
        # history on a second sqlite connection (see resolve_database_url), and
        # an uncommitted flush would hold a write lock -> "database is locked".
        # On generation failure the interview is deleted so nothing is persisted.
        interview = Interview(
            user_id=user.id,
            role=role,
            industry=industry,
            experience_levels=experience,
            job_description=job_description or None
        )
        db.session.add(interview)
        db.session.commit()

        # Generate Questions
        questions_data = get_gemini_service().generate_questions(
            role, industry, experience, interview.id, job_description
        )

        if not questions_data:
            db.session.delete(interview)
            db.session.commit()
            return jsonify({
                "error": "Failed to generate interview questions. Please try again."
            }), 502

        # Save Questions
        questions_to_save = []
        for q in questions_data:
            question = Question(
                interview_id=interview.id,
                text=q.get('text'),
                topic=q.get('topic'),
                difficulty=q.get('difficulty'),
                score=0
            )
            db.session.add(question)
            questions_to_save.append(question)

        db.session.commit()

        # Build response with question IDs (now available after commit)
        saved_questions = []
        for question in questions_to_save:
            saved_questions.append({
                "id": question.id,
                "text": question.text,
                "topic": question.topic,
                "difficulty": question.difficulty,
                "score": question.score
            })

        return jsonify({
            "interview_id": interview.id,
            "user": {"name": user.name, "email": user.email},
            "questions": saved_questions
        }), 201

    except Exception as e:
        logger.error(f"Error generating interview: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/questions/<int:interview_id>', methods=['GET'])
def get_questions(interview_id):
    """Get all questions for a specific interview"""
    try:
        interview = db.session.get(Interview, interview_id)
        if not interview:
            return jsonify({"error": "Interview not found"}), 404

        questions = Question.query.filter_by(interview_id=interview_id).all()

        questions_data = []
        for q in questions:
            # Get the latest answer if exists
            latest_answer = (
                Answer.query.filter_by(question_id=q.id)
                .order_by(Answer.created_at.desc())
                .first()
            )

            questions_data.append({
                "id": q.id,
                "text": q.text,
                "topic": q.topic,
                "difficulty": q.difficulty,
                "score": q.score,
                "answer": {
                    "id": latest_answer.id if latest_answer else None,
                    "text": latest_answer.answer_text if latest_answer else "",
                    "ai_score": latest_answer.ai_score if latest_answer else 0,
                    "ai_feedback": latest_answer.ai_feedback if latest_answer else ""
                } if latest_answer else None
            })

        return jsonify({
            "interview_id": interview.id,
            "questions": questions_data
        }), 200

    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/answer', methods=['POST'])
def submit_answer():
    """Submit an answer to a question with validation"""
    try:

        data = request.get_json()
        question_id = data.get('question_id')
        answer_text = data.get('answer_text', '').strip()

        if not question_id:
            return jsonify({"error": "question_id is required"}), 400

        if not answer_text:
            return jsonify({"error": "answer_text cannot be empty"}), 400

        # Validate answer length (max 5000 characters)
        MAX_ANSWER_LENGTH = 5000
        if len(answer_text) > MAX_ANSWER_LENGTH:
            return jsonify({
                "error": f"Answer exceeds maximum length of {MAX_ANSWER_LENGTH} characters",
                "current_length": len(answer_text),
                "max_length": MAX_ANSWER_LENGTH
            }), 400

        # Check if question exists
        question = db.session.get(Question, question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        # Create or update answer
        existing_answer = Answer.query.filter_by(question_id=question_id).first()

        if existing_answer:
            existing_answer.answer_text = answer_text
            existing_answer.ai_score = 0  # Reset score when answer is updated
            existing_answer.ai_feedback = None
            answer = existing_answer
        else:
            answer = Answer(
                question_id=question_id,
                answer_text=answer_text
            )
            db.session.add(answer)

        db.session.commit()

        return jsonify({
            "answer_id": answer.id,
            "question_id": question_id,
            "answer_text": answer.answer_text,
            "message": "Answer saved successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error submitting answer: {e}")
        return jsonify({"error": str(e)}), 500

@interview_bp.route('/evaluate/<int:answer_id>', methods=['POST'])
def evaluate_answer(answer_id):
    """Evaluate an answer using AI and update the score"""
    try:

        answer = db.session.get(Answer, answer_id)
        if not answer:
            return jsonify({"error": "Answer not found"}), 404

        question = db.session.get(Question, answer.question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        interview = db.session.get(Interview, question.interview_id)

        # Evaluate using LangChain — passes interview_id for DB-backed session memory
        evaluation = get_gemini_service().evaluate_answer(
            question_text=question.text,
            question_topic=question.topic,
            question_difficulty=question.difficulty,
            answer_text=answer.answer_text,
            interview_id=question.interview_id,
            job_description=interview.job_description if interview else None,
        )

        # Update answer with AI evaluation
        answer.ai_score = evaluation['score']

        # Format feedback with strengths and improvements
        feedback_parts = [evaluation['feedback']]

        if evaluation.get('strengths'):
            feedback_parts.append("\n\n**Strengths:**")
            for strength in evaluation['strengths']:
                feedback_parts.append(f"- {strength}")

        if evaluation.get('improvements'):
            feedback_parts.append("\n\n**Areas for Improvement:**")
            for improvement in evaluation['improvements']:
                feedback_parts.append(f"- {improvement}")

        answer.ai_feedback = '\n'.join(feedback_parts)

        # Update question score (you might want to average all answers or use latest)
        question.score = answer.ai_score

        db.session.commit()

        return jsonify({
            "answer_id": answer.id,
            "question_id": question.id,
            "ai_score": answer.ai_score,
            "ai_feedback": answer.ai_feedback,
            "evaluation": evaluation
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error evaluating answer: {e}")
        return jsonify({"error": str(e)}), 500

