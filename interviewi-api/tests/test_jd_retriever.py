from services.jd_retriever import chunk_jd, retrieve_chunks, sanitize_jd


class TestSanitizeJd:
    def test_non_string_returns_empty(self):
        assert sanitize_jd(None) == ""
        assert sanitize_jd(123) == ""
        assert sanitize_jd(["x"]) == ""

    def test_strips_control_chars_keeps_newlines(self):
        assert sanitize_jd("line1\x00\x07line2\nline3") == "line1line2\nline3"

    def test_collapses_spaces_and_strips(self):
        assert sanitize_jd("  hi   there  \n ") == "hi there"

    def test_truncates_to_max(self):
        assert sanitize_jd("x" * 30000, max_chars=100) == "x" * 100


class TestChunkJd:
    def test_empty_input(self):
        assert chunk_jd("") == []
        assert chunk_jd("   \n  ") == []

    def test_splits_sentences_into_chunks(self):
        jd = "We need a Python developer. Responsibilities include Flask. Must know SQL."
        chunks = chunk_jd(jd, max_chars=30)
        assert len(chunks) >= 2
        for c in chunks:
            assert len(c) <= 30

    def test_merges_short_fragments(self):
        jd = "Role: Backend Engineer. Stack: Python. Domain: payments."
        chunks = chunk_jd(jd, max_chars=1000)
        assert len(chunks) == 1
        assert "Backend Engineer" in chunks[0]
        assert "payments" in chunks[0]

    def test_hard_wraps_overlong_sentence(self):
        long = "Word " * 200
        chunks = chunk_jd(long, max_chars=50)
        assert chunks
        assert max(len(c) for c in chunks) <= 50


class TestRetrieveChunks:
    def _chunks(self):
        return [
            "We need a Python developer with strong SQL skills",
            "The team uses React for the frontend",
            "We hire people with at least five years of React experience",
        ]

    def test_ranks_relevant_chunk_first(self):
        chunks = self._chunks()
        assert retrieve_chunks("Python developer", chunks)[0] == chunks[0]

    def test_respects_k(self):
        chunks = self._chunks()
        assert retrieve_chunks("React", chunks, k=1) == [chunks[1]]

    def test_empty_query_returns_first_k(self):
        chunks = self._chunks()
        assert retrieve_chunks("", chunks, k=2) == chunks[:2]

    def test_empty_chunks(self):
        assert retrieve_chunks("anything", []) == []

    def test_ignores_query(self):
        chunks = self._chunks()
        result = retrieve_chunks("zzzqqq", chunks, k=1)
        assert len(result) == 1
        assert result[0] == chunks[0]
