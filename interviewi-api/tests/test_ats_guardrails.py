from services.gemini_service import GeminiService


class TestNormalizeScore100:
    def test_valid_int_unchanged(self):
        assert GeminiService._normalize_score_100(75) == 75

    def test_clamps_high(self):
        assert GeminiService._normalize_score_100(150) == 100

    def test_clamps_low(self):
        assert GeminiService._normalize_score_100(-10) == 0

    def test_rounds_numeric_string(self):
        assert GeminiService._normalize_score_100("74.6") == 75
        assert GeminiService._normalize_score_100("99.9") == 100

    def test_garbage_returns_zero(self):
        assert GeminiService._normalize_score_100("abc") == 0
        assert GeminiService._normalize_score_100(None) == 0
        assert GeminiService._normalize_score_100(True) == 0
        assert GeminiService._normalize_score_100([]) == 0


class TestCleanSuggestions:
    def test_normal_list(self):
        assert GeminiService._clean_suggestions(["Add keywords", "Fix format"]) == [
            "Add keywords",
            "Fix format",
        ]

    def test_strips_whitespace(self):
        assert GeminiService._clean_suggestions(["  hello  ", "  world  "]) == [
            "hello",
            "world",
        ]

    def test_drops_non_strings(self):
        assert GeminiService._clean_suggestions(["valid", 123, None, "also valid"]) == [
            "valid",
            "also valid",
        ]

    def test_drops_empty_strings(self):
        assert GeminiService._clean_suggestions(["", "  ", "valid"]) == ["valid"]

    def test_non_list_returns_empty(self):
        assert GeminiService._clean_suggestions("not a list") == []
        assert GeminiService._clean_suggestions(None) == []
        assert GeminiService._clean_suggestions(123) == []

    def test_caps_at_8(self):
        items = [f"suggestion {i}" for i in range(20)]
        assert len(GeminiService._clean_suggestions(items)) == 8


class TestCleanKeywords:
    def test_normal_list(self):
        result = GeminiService._clean_keywords(["Python", "Flask", "SQL"])
        assert result == ["python", "flask", "sql"]

    def test_strips_and_lowercases(self):
        result = GeminiService._clean_keywords(["  Python  ", "FLASK"])
        assert result == ["python", "flask"]

    def test_drops_non_strings(self):
        result = GeminiService._clean_keywords(["python", 123, None])
        assert result == ["python"]

    def test_drops_empty(self):
        result = GeminiService._clean_keywords(["", "  ", "python"])
        assert result == ["python"]

    def test_non_list_returns_empty(self):
        assert GeminiService._clean_keywords(None) == []
        assert GeminiService._clean_keywords("string") == []

    def test_caps_at_10(self):
        items = [f"kw{i}" for i in range(20)]
        assert len(GeminiService._clean_keywords(items)) == 10


class TestValidateAtsResult:
    def test_valid_result_passes(self):
        raw = {
            "overall_score": 75,
            "keyword_score": 80,
            "skills_score": 70,
            "experience_score": 65,
            "format_score": 75,
            "matched_keywords": ["python"],
            "missing_keywords": ["kubernetes"],
            "suggestions": ["Add keywords"],
        }
        result = GeminiService._validate_ats_result(raw)
        assert result is not None
        assert result["overall_score"] == 75
        assert result["matched_keywords"] == ["python"]

    def test_missing_key_returns_none(self):
        raw = {
            "overall_score": 75,
            "keyword_score": 80,
            "skills_score": 70,
            "experience_score": 65,
            "format_score": 75,
            "matched_keywords": ["python"],
            "missing_keywords": [],
        }
        assert GeminiService._validate_ats_result(raw) is None

    def test_non_dict_returns_none(self):
        assert GeminiService._validate_ats_result("not a dict") is None
        assert GeminiService._validate_ats_result(None) is None
        assert GeminiService._validate_ats_result([1, 2]) is None

    def test_scores_are_normalized(self):
        raw = {
            "overall_score": "85.7",
            "keyword_score": 200,
            "skills_score": -5,
            "experience_score": None,
            "format_score": "abc",
            "matched_keywords": [],
            "missing_keywords": [],
            "suggestions": [],
        }
        result = GeminiService._validate_ats_result(raw)
        assert result is not None
        assert result["overall_score"] == 86
        assert result["keyword_score"] == 100
        assert result["skills_score"] == 0
        assert result["experience_score"] == 0
        assert result["format_score"] == 0

    def test_keywords_are_cleaned(self):
        raw = {
            "overall_score": 50,
            "keyword_score": 50,
            "skills_score": 50,
            "experience_score": 50,
            "format_score": 50,
            "matched_keywords": ["  Python  ", "FLASK", ""],
            "missing_keywords": [123, None, "kubernetes"],
            "suggestions": ["Fix this"],
        }
        result = GeminiService._validate_ats_result(raw)
        assert result is not None
        assert result["matched_keywords"] == ["python", "flask"]
        assert result["missing_keywords"] == ["kubernetes"]
