def _generate_body():
    return {
        "name": "Alice",
        "email": "alice@example.com",
        "stack": "Python, Flask",
        "experience": {"Python": "3", "Flask": "2"},
    }


class TestGenerate:
    def test_success(self, app, client, stub_llm):
        stub_llm({
            "questions": [
                {"text": "Q1", "topic": "Python", "difficulty": "Medium"},
                {"text": "Q2", "topic": "Flask", "difficulty": "hard"},
            ]
        })
        resp = client.post("/api/interview/generate", json=_generate_body())
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["interview_id"]
        assert data["user"]["name"] == "Alice"
        assert len(data["questions"]) == 2
        assert data["questions"][1]["difficulty"] == "Hard"

    def test_missing_fields_400(self, app, client):
        resp = client.post("/api/interview/generate", json={"name": "Alice"})
        assert resp.status_code == 400
        assert "Missing required fields" in resp.get_json()["error"]

    def test_empty_questions_502_and_rollback(self, app, client, stub_llm):
        stub_llm({"questions": []})
        resp = client.post("/api/interview/generate", json=_generate_body())
        assert resp.status_code == 502
        from models.models import Interview
        with app.app_context():
            assert Interview.query.count() == 0  # rolled back

    def test_existing_user_reused(self, app, client, stub_llm):
        stub_llm({"questions": [{"text": "Q1", "topic": "Python", "difficulty": "easy"}]})
        first = client.post("/api/interview/generate", json=_generate_body())
        assert first.status_code == 201
        second = client.post("/api/interview/generate", json=_generate_body())
        assert second.status_code == 201
        from models.models import User
        with app.app_context():
            assert User.query.filter_by(email="alice@example.com").count() == 1


class TestGetQuestions:
    def test_404_unknown_interview(self, app, client):
        resp = client.get("/api/interview/questions/9999")
        assert resp.status_code == 404

    def test_returns_questions_with_answer(self, app, client, stub_llm):
        stub_llm({"questions": [{"text": "Q1", "topic": "Python", "difficulty": "easy"}]})
        gen = client.post("/api/interview/generate", json=_generate_body())
        interview_id = gen.get_json()["interview_id"]
        question_id = gen.get_json()["questions"][0]["id"]

        client.post("/api/interview/answer", json={
            "question_id": question_id,
            "answer_text": "My answer",
        })

        resp = client.get(f"/api/interview/questions/{interview_id}")
        assert resp.status_code == 200
        question = resp.get_json()["questions"][0]
        assert question["answer"]["text"] == "My answer"


class TestSubmitAnswer:
    def _setup_question(self, client, stub_llm):
        stub_llm({"questions": [{"text": "Q1", "topic": "Python", "difficulty": "easy"}]})
        gen = client.post("/api/interview/generate", json=_generate_body())
        return gen.get_json()["questions"][0]["id"]

    def test_success(self, app, client, stub_llm):
        qid = self._setup_question(client, stub_llm)
        resp = client.post("/api/interview/answer", json={
            "question_id": qid,
            "answer_text": "A solid answer.",
        })
        assert resp.status_code == 201
        assert resp.get_json()["answer_id"]

    def test_missing_question_id_400(self, app, client):
        resp = client.post("/api/interview/answer", json={"answer_text": "x"})
        assert resp.status_code == 400

    def test_empty_answer_400(self, app, client, stub_llm):
        qid = self._setup_question(client, stub_llm)
        resp = client.post("/api/interview/answer", json={"question_id": qid, "answer_text": "   "})
        assert resp.status_code == 400

    def test_answer_too_long_400(self, app, client, stub_llm):
        qid = self._setup_question(client, stub_llm)
        resp = client.post("/api/interview/answer", json={
            "question_id": qid,
            "answer_text": "x" * 5001,
        })
        assert resp.status_code == 400

    def test_unknown_question_404(self, app, client):
        resp = client.post("/api/interview/answer", json={
            "question_id": 9999,
            "answer_text": "x",
        })
        assert resp.status_code == 404


class TestEvaluate:
    def _setup_answer(self, client, stub_llm):
        stub_llm({"questions": [{"text": "Q1", "topic": "Python", "difficulty": "easy"}]})
        gen = client.post("/api/interview/generate", json=_generate_body())
        qid = gen.get_json()["questions"][0]["id"]
        ans = client.post("/api/interview/answer", json={"question_id": qid, "answer_text": "A"})
        return ans.get_json()["answer_id"]

    def test_evaluate_updates_score(self, app, client, stub_llm):
        answer_id = self._setup_answer(client, stub_llm)
        stub_llm({
            "score": 8,
            "feedback": "Great",
            "strengths": ["Clear structure"],
            "improvements": [],
        })
        resp = client.post(f"/api/interview/evaluate/{answer_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ai_score"] == 8
        assert "Clear structure" in data["ai_feedback"]

    def test_unknown_answer_404(self, app, client):
        resp = client.post("/api/interview/evaluate/9999")
        assert resp.status_code == 404

    def test_llm_failure_keeps_default(self, app, client, stub_llm):
        answer_id = self._setup_answer(client, stub_llm)
        stub_llm(RuntimeError("boom"))
        resp = client.post(f"/api/interview/evaluate/{answer_id}")
        assert resp.status_code == 200
        assert resp.get_json()["ai_score"] == 0
