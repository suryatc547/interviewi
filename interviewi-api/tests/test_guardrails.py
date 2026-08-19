from services.gemini_service import GeminiService


class TestNormalizeScore:
    def test_valid_int_unchanged(self):
        assert GeminiService._normalize_score(7) == 7

    def test_clamps_high(self):
        assert GeminiService._normalize_score(42) == 10

    def test_clamps_low(self):
        assert GeminiService._normalize_score(-5) == 0

    def test_rounds_numeric_string(self):
        assert GeminiService._normalize_score("7.4") == 7
        assert GeminiService._normalize_score("9.6") == 10

    def test_garbage_returns_zero(self):
        assert GeminiService._normalize_score("abc") == 0
        assert GeminiService._normalize_score(None) == 0
        assert GeminiService._normalize_score(True) == 0
        assert GeminiService._normalize_score([]) == 0


class TestCleanQuestions:
    def test_normalizes_difficulty_and_topic(self):
        raw = [
            {"text": "  Valid question  ", "topic": "Python", "difficulty": "easy"},
            {"text": "Hard one", "topic": "Flask", "difficulty": "HARD"},
            {"text": "Tricky", "topic": 123, "difficulty": "bogus"},
        ]
        cleaned = GeminiService._clean_questions(raw)
        assert cleaned == [
            {"text": "Valid question", "topic": "Python", "difficulty": "Easy"},
            {"text": "Hard one", "topic": "Flask", "difficulty": "Hard"},
            {"text": "Tricky", "topic": "123", "difficulty": "Medium"},
        ]

    def test_drops_garbage(self):
        raw = [
            {"text": "", "topic": "x"},
            {"text": "   ", "topic": "y"},
            "not-a-dict",
            None,
            {"difficulty": "Easy"},
        ]
        assert GeminiService._clean_questions(raw) == []


class TestClip:
    def test_short_untouched(self):
        assert GeminiService._clip("hello", 10) == "hello"

    def test_truncates_with_marker(self):
        assert GeminiService._clip("a" * 50, 10) == "a" * 10 + "...[truncated]"

    def test_none_becomes_empty(self):
        assert GeminiService._clip(None, 10) == ""
