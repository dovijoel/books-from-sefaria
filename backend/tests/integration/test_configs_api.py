"""
Integration tests for the Configs API  (/api/v1/configs)
TODO: implement when backend/app/routers/configs.py is ready
"""
import pytest


# ---------------------------------------------------------------------------
# POST /api/v1/configs
# ---------------------------------------------------------------------------

class TestCreateConfig:
    def test_create_config_returns_201(self, test_client, sample_book_config):
        response = test_client.post("/api/v1/configs", json=sample_book_config)
        assert response.status_code == 201

    def test_create_config_returns_id(self, test_client, sample_book_config):
        response = test_client.post("/api/v1/configs", json=sample_book_config)
        data = response.json()
        assert "id" in data

    def test_create_config_name_persisted(self, test_client, sample_book_config):
        response = test_client.post("/api/v1/configs", json=sample_book_config)
        data = response.json()
        assert data.get("name") == sample_book_config["name"]

    def test_create_config_missing_name_returns_422(self, test_client, sample_book_config):
        bad = {k: v for k, v in sample_book_config.items() if k != "name"}
        response = test_client.post("/api/v1/configs", json=bad)
        assert response.status_code == 422

    def test_create_config_empty_body_returns_422(self, test_client):
        response = test_client.post("/api/v1/configs", json={})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /api/v1/configs
# ---------------------------------------------------------------------------

class TestListConfigs:
    def _create(self, test_client, sample_book_config, name_suffix=""):
        config = {**sample_book_config, "name": sample_book_config["name"] + name_suffix}
        return test_client.post("/api/v1/configs", json=config).json()

    def test_list_configs_returns_array(self, test_client):
        response = test_client.get("/api/v1/configs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_configs_includes_created_config(self, test_client, sample_book_config):
        created = self._create(test_client, sample_book_config)
        response = test_client.get("/api/v1/configs")
        ids = [c["id"] for c in response.json()]
        assert created["id"] in ids

    def test_list_configs_multiple_entries(self, test_client, sample_book_config):
        self._create(test_client, sample_book_config, " A")
        self._create(test_client, sample_book_config, " B")
        response = test_client.get("/api/v1/configs")
        assert len(response.json()) >= 2


# ---------------------------------------------------------------------------
# GET /api/v1/configs/{id}
# ---------------------------------------------------------------------------

class TestGetConfigById:
    def test_get_existing_config(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        response = test_client.get(f"/api/v1/configs/{created_id}")
        assert response.status_code == 200
        assert response.json()["id"] == created_id

    def test_get_config_not_found(self, test_client):
        response = test_client.get("/api/v1/configs/nonexistent-uuid")
        assert response.status_code == 404

    def test_get_config_contains_full_data(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        data = test_client.get(f"/api/v1/configs/{created_id}").json()
        assert "texts" in data
        assert "format" in data


# ---------------------------------------------------------------------------
# PUT /api/v1/configs/{id}
# ---------------------------------------------------------------------------

class TestUpdateConfig:
    def test_update_config_returns_200(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        updated = {**sample_book_config, "name": "Updated Name"}
        response = test_client.put(f"/api/v1/configs/{created_id}", json=updated)
        assert response.status_code == 200

    def test_update_config_persists_changes(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        updated = {**sample_book_config, "name": "My New Name"}
        test_client.put(f"/api/v1/configs/{created_id}", json=updated)
        fetched = test_client.get(f"/api/v1/configs/{created_id}").json()
        assert fetched["name"] == "My New Name"

    def test_update_config_not_found(self, test_client, sample_book_config):
        response = test_client.put("/api/v1/configs/ghost-id", json=sample_book_config)
        assert response.status_code == 404

    def test_update_config_partial_invalid_returns_422(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        # texts must be a list
        response = test_client.put(f"/api/v1/configs/{created_id}", json={**sample_book_config, "texts": "bad"})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /api/v1/configs/{id}
# ---------------------------------------------------------------------------

class TestDeleteConfig:
    def test_delete_config_returns_204(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        response = test_client.delete(f"/api/v1/configs/{created_id}")
        assert response.status_code in (200, 204)

    def test_delete_config_removes_it(self, test_client, sample_book_config):
        created_id = test_client.post("/api/v1/configs", json=sample_book_config).json()["id"]
        test_client.delete(f"/api/v1/configs/{created_id}")
        response = test_client.get(f"/api/v1/configs/{created_id}")
        assert response.status_code == 404

    def test_delete_config_not_found(self, test_client):
        response = test_client.delete("/api/v1/configs/ghost-id")
        assert response.status_code == 404

    def test_delete_does_not_affect_other_configs(self, test_client, sample_book_config):
        id_a = test_client.post("/api/v1/configs", json={**sample_book_config, "name": "A"}).json()["id"]
        id_b = test_client.post("/api/v1/configs", json={**sample_book_config, "name": "B"}).json()["id"]
        test_client.delete(f"/api/v1/configs/{id_a}")
        response = test_client.get(f"/api/v1/configs/{id_b}")
        assert response.status_code == 200
