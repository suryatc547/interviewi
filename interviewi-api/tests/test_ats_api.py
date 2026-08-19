import io

# Minimal valid PDF with "Hello World" text embedded — manually crafted
# so extract_text_from_pdf returns non-empty text.
_SAMPLE_PDF = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
    b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
    b"4 0 obj<</Length 56>>stream\n"
    b"BT /F1 12 Tf 100 700 Td (John Doe Software Engineer) Tj ET\n"
    b"endstream\nendobj\n"
    b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000058 00000 n \n"
    b"0000000115 00000 n \n"
    b"0000000266 00000 n \n"
    b"0000000372 00000 n \n"
    b"trailer<</Size 6/Root 1 0 R>>\n"
    b"startxref\n441\n%%EOF\n"
)


def _scan_data(jd="Senior Python Engineer with 5+ years experience."):
    return {
        "resume": (io.BytesIO(_SAMPLE_PDF), "resume.pdf"),
        "job_description": jd,
    }


class TestScanResume:
    def test_success(self, app, client, stub_llm):
        stub_llm({
            "overall_score": 72,
            "keyword_score": 80,
            "skills_score": 70,
            "experience_score": 65,
            "format_score": 75,
            "matched_keywords": ["python", "flask", "docker", "aws"],
            "missing_keywords": ["kubernetes", "ci/cd", "graphql"],
            "suggestions": [
                "Add Kubernetes experience or certification",
                "Include CI/CD pipeline experience",
                "Quantify achievements with metrics",
            ],
        })
        resp = client.post(
            "/api/ats/scan",
            data=_scan_data(),
            content_type="multipart/form-data",
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["scan_id"]
        assert data["overall_score"] == 72
        assert data["keyword_score"] == 80
        assert "python" in data["matched_keywords"]
        assert "kubernetes" in data["missing_keywords"]
        assert len(data["suggestions"]) == 3

    def test_missing_resume_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={"job_description": "JD here"},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "resume" in resp.get_json()["error"].lower()

    def test_missing_jd_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={"resume": (io.BytesIO(_SAMPLE_PDF), "r.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "job_description" in resp.get_json()["error"]

    def test_empty_jd_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={
                "resume": (io.BytesIO(_SAMPLE_PDF), "r.pdf"),
                "job_description": "   ",
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400

    def test_non_pdf_extension_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={
                "resume": (io.BytesIO(b"not pdf"), "resume.txt"),
                "job_description": "JD here",
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "PDF" in resp.get_json()["error"]

    def test_wrong_extension_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={
                "resume": (io.BytesIO(b"not pdf"), "resume.docx"),
                "job_description": "JD here",
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "PDF" in resp.get_json()["error"]

    def test_jd_too_long_400(self, app, client):
        resp = client.post(
            "/api/ats/scan",
            data={
                "resume": (io.BytesIO(_SAMPLE_PDF), "r.pdf"),
                "job_description": "x" * 20001,
            },
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "exceeds maximum length" in resp.get_json()["error"]

    def test_llm_failure_502(self, app, client, stub_llm):
        stub_llm(RuntimeError("boom"))
        resp = client.post(
            "/api/ats/scan",
            data=_scan_data(),
            content_type="multipart/form-data",
        )
        assert resp.status_code == 502

    def test_scan_persisted(self, app, client, stub_llm):
        stub_llm({
            "overall_score": 65,
            "keyword_score": 70,
            "skills_score": 60,
            "experience_score": 55,
            "format_score": 75,
            "matched_keywords": ["python"],
            "missing_keywords": ["kubernetes"],
            "suggestions": ["Add more keywords"],
        })
        resp = client.post(
            "/api/ats/scan",
            data=_scan_data(),
            content_type="multipart/form-data",
        )
        assert resp.status_code == 201
        from models.models import ATSScan
        with app.app_context():
            scan = ATSScan.query.filter_by(
                id=resp.get_json()["scan_id"]
            ).first()
            assert scan is not None
            assert scan.overall_score == 65


class TestGetScan:
    def test_success(self, app, client, stub_llm):
        stub_llm({
            "overall_score": 80,
            "keyword_score": 85,
            "skills_score": 75,
            "experience_score": 70,
            "format_score": 90,
            "matched_keywords": ["python"],
            "missing_keywords": [],
            "suggestions": ["Good match"],
        })
        scan_resp = client.post(
            "/api/ats/scan",
            data=_scan_data(),
            content_type="multipart/form-data",
        )
        scan_id = scan_resp.get_json()["scan_id"]

        resp = client.get(f"/api/ats/scan/{scan_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["scan_id"] == scan_id
        assert data["overall_score"] == 80

    def test_404_unknown_scan(self, app, client):
        resp = client.get("/api/ats/scan/9999")
        assert resp.status_code == 404
