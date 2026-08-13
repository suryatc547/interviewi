from services.gemini_service import get_gemini_service


def test_generate_questions_returns_cleaned_list(app, stub_llm):
    stub_llm({
        "questions": [
            {"text": "What is Python?", "topic": "Python", "difficulty": "easy"},
            {"text": "Explain GIL", "topic": "Python", "difficulty": "Hard"},
        ]
    })
    questions = get_gemini_service().generate_questions("Python", "3 years", 1)
    assert questions == [
        {"text": "What is Python?", "topic": "Python", "difficulty": "Easy"},
        {"text": "Explain GIL", "topic": "Python", "difficulty": "Hard"},
    ]


def test_generate_questions_falls_back_on_garbage(app, stub_llm):
    stub_llm({"unexpected": "shape"})
    assert get_gemini_service().generate_questions("Python", "3 years", 1) == []


def test_generate_questions_falls_back_on_llm_error(app, stub_llm):
    stub_llm(RuntimeError("boom"))
    assert get_gemini_service().generate_questions("Python", "3 years", 1) == []


def test_generate_questions_clips_inputs(app, stub_llm):
    stub_llm({"questions": []})
    get_gemini_service().generate_questions("P" * 1000, "E" * 2000, 1)
    assert get_gemini_service().generate_questions("P" * 1000, "E" * 2000, 1) == []


def test_evaluate_answer_normalizes_and_type_checks(app, stub_llm):
    stub_llm({
        "score": "9.6",
        "feedback": "Solid answer.",
        "strengths": "nope",  # string -> not a list -> dropped
        "improvements": ["Go deeper on edge cases"],
    })
    result = get_gemini_service().evaluate_answer(
        "Q", "Python", "Easy", "An answer", 1
    )
    assert result["score"] == 10
    assert result["feedback"] == "Solid answer."
    assert result["strengths"] == []
    assert result["improvements"] == ["Go deeper on edge cases"]


def test_history_persists_turns(app, stub_llm):
    stub_llm({"questions": [{"text": "Q?", "topic": "t", "difficulty": "easy"}]})
    service = get_gemini_service()
    service.generate_questions("Python", "2 years", 99)
    history = service._get_session_history(99)
    assert len(history.messages) == 2  # user turn + AI reply
    assert "Python" in history.messages[0].content


def test_lazy_singleton_shared(app):
    assert get_gemini_service() is get_gemini_service()
