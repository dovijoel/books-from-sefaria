"""
Integration tests for the Jobs API  (/api/v1/jobs)
TODO: implement when backend/app/routers/jobs.py is ready
"""
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# POST /api/v1/jobs  — create a job
# ---------------------------------------------------------------------------

class TestCreateJob:
    def test_create_job_returns_201_with_id(self, test_client, sample_book_config):
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-celery-id"
            response = test_client.post("/api/v1/jobs", json=sample_book_config)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    def test_create_job_response_contains_created_at(self, test_client, sample_book_config):
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-celery-id-2"
            response = test_client.post("/api/v1/jobs", json=sample_book_config)

        assert response.status_code == 201
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
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-celery-id-3"
            test_client.post("/api/v1/jobs", json=sample_book_config)

        mock_task.assert_called_once()


# ---------------------------------------------------------------------------
# GET /api/v1/jobs/{job_id}  — poll status
# ---------------------------------------------------------------------------

class TestGetJobStatus:
    def _create_job(self, test_client, sample_book_config):
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-celery-id"
            resp = test_client.post("/api/v1/jobs", json=sample_book_config)
        return resp.json()["id"]

    def test_get_job_returns_pending_status(self, test_client, sample_book_config):
        job_id = self._create_job(test_client, sample_book_config)
        response = test_client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] in ("pending", "processing", "complete", "failed")

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
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-celery-id"
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

    def test_download_complete_job_returns_pdf(self, test_client, sample_book_config, tmp_path):
        """When a job has status=complete and a PDF path, we get a file response."""
        import os

        # Create a dummy PDF file the endpoint can serve
        dummy_pdf = tmp_path / "test.pdf"
        dummy_pdf.write_bytes(b"%PDF-1.4 dummy")

        job_id = self._create_job(test_client, sample_book_config)

        # Patch the DB record to look complete with a valid path
        with patch("app.routers.jobs.get_job_by_id") as mock_get:
            mock_job = MagicMock()
            mock_job.status = "complete"
            mock_job.pdf_path = str(dummy_pdf)
            mock_get.return_value = mock_job

            response = test_client.get(f"/api/v1/jobs/{job_id}/download")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"


# ---------------------------------------------------------------------------
# GET /api/v1/jobs  — list jobs
# ---------------------------------------------------------------------------

class TestListJobs:
    def test_list_jobs_returns_array(self, test_client):
        response = test_client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_jobs_after_creation(self, test_client, sample_book_config):
        with patch("app.workers.tasks.generate_book_pdf.delay") as mock_task:
            mock_task.return_value.id = "mock-list-id"
            test_client.post("/api/v1/jobs", json=sample_book_config)

        response = test_client.get("/api/v1/jobs")
        assert response.status_code == 200
        assert len(response.json()) >= 1
