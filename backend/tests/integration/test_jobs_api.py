"""
Integration tests for the Jobs API  (/api/v1/jobs)
"""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# POST /api/v1/jobs  — create a job
# ---------------------------------------------------------------------------

class TestCreateJob:
    def test_create_job_returns_202_with_id(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async"):
            response = test_client.post("/api/v1/jobs", json=sample_book_config)

        assert response.status_code == 202
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    def test_create_job_response_contains_created_at(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async"):
            response = test_client.post("/api/v1/jobs", json=sample_book_config)

        assert response.status_code == 202
        data = response.json()
        assert "created_at" in data

    def test_create_job_missing_required_fields_returns_422(self, test_client):
        """Sending an empty body should fail validation."""
        response = test_client.post("/api/v1/jobs", json={})
        assert response.status_code == 422

    def test_create_job_missing_texts_returns_422(self, test_client, sample_book_config):
        bad_config = {k: v for k, v in sample_book_config.items() if k != "texts"}
        response = test_client.post("/api/v1/jobs", json=bad_config)
        assert response.status_code == 422

    def test_create_job_empty_texts_returns_422(self, test_client, sample_book_config):
        config = {**sample_book_config, "texts": []}
        response = test_client.post("/api/v1/jobs", json=config)
        assert response.status_code == 422

    def test_create_job_dispatches_celery_task(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async") as mock_task:
            test_client.post("/api/v1/jobs", json=sample_book_config)

        mock_task.assert_called_once()


# ---------------------------------------------------------------------------
# GET /api/v1/jobs/{job_id}  — poll status
# ---------------------------------------------------------------------------

class TestGetJobStatus:
    def _create_job(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async"):
            resp = test_client.post("/api/v1/jobs", json=sample_book_config)
        return resp.json()["id"]

    def test_get_job_returns_pending_status(self, test_client, sample_book_config):
        job_id = self._create_job(test_client, sample_book_config)
        response = test_client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] in ("pending", "running", "success", "failure")

    def test_get_job_not_found_returns_404(self, test_client):
        response = test_client.get("/api/v1/jobs/nonexistent-id-xyz")
        assert response.status_code == 404

    def test_get_job_response_shape(self, test_client, sample_book_config):
        """Response includes id, status, and created_at at minimum."""
        job_id = self._create_job(test_client, sample_book_config)
        data = test_client.get(f"/api/v1/jobs/{job_id}").json()
        for field in ("id", "status", "created_at"):
            assert field in data, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# GET /api/v1/jobs/{job_id}/download  — download PDF
# ---------------------------------------------------------------------------

class TestDownloadPdf:
    def _create_job(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async"):
            resp = test_client.post("/api/v1/jobs", json=sample_book_config)
        return resp.json()["id"]

    def test_download_pending_job_returns_409_or_404(self, test_client, sample_book_config):
        """Attempting to download a job that isn't complete should return an error."""
        job_id = self._create_job(test_client, sample_book_config)
        response = test_client.get(f"/api/v1/jobs/{job_id}/download")
        assert response.status_code in (404, 409, 425)

    def test_download_nonexistent_job_returns_404(self, test_client):
        response = test_client.get("/api/v1/jobs/ghost-id/download")
        assert response.status_code == 404

    def test_download_complete_job_returns_pdf(
        self, test_client, db_session, sample_book_config, tmp_path
    ):
        """When a job has status=success and a valid PDF path, we get a file response."""
        from app.models.job import Job, JobStatus

        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

        job_id = self._create_job(test_client, sample_book_config)

        # Update the job record directly via the shared test DB session
        job = db_session.get(Job, job_id)
        job.status = JobStatus.SUCCESS
        job.pdf_path = str(dummy_pdf)
        db_session.commit()

        response = test_client.get(f"/api/v1/jobs/{job_id}/download")
        assert response.status_code == 200
        assert "application/pdf" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# GET /api/v1/jobs  — list jobs (endpoint not implemented; tests skipped)
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason="GET /api/v1/jobs list endpoint is not implemented")
class TestListJobs:
    def test_list_jobs_returns_array(self, test_client):
        response = test_client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_jobs_after_creation(self, test_client, sample_book_config):
        with patch("app.api.v1.jobs.generate_pdf_task.apply_async"):
            test_client.post("/api/v1/jobs", json=sample_book_config)

        response = test_client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert len(response.json()) >= 1

