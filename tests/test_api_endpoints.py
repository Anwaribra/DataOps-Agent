import os
import pytest
import anyio
import httpx
from api.main import app


class ASGITestClient:
    def request(self, method, url, **kwargs):
        async def send_request():
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
                return await client.request(method, url, **kwargs)

        return anyio.run(send_request)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)


client = ASGITestClient()

def test_api_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DataOps Agent Platform API"

def test_api_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "data_quality_score" in data

def test_api_pipeline_nodes_endpoint():
    response = client.get("/api/pipeline")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 7
    node_ids = [n["id"] for n in data]
    assert "dbt_transformation" in node_ids
    assert "mcp_server" in node_ids

def test_api_incidents_list_endpoint():
    response = client.get("/api/incidents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "incident_id" in data[0]

def test_api_remediation_approval_workflow():
    # 1. Investigate incident
    inv_res = client.get("/api/incidents/inc_test_01/investigation")
    assert inv_res.status_code == 200
    inv_data = inv_res.json()
    assert inv_data["incident_id"] == "inc_test_01"

    # 2. Get remediation plan
    plan_res = client.get("/api/incidents/inc_test_01/remediation")
    assert plan_res.status_code == 200
    plan_data = plan_res.json()
    assert plan_data["status"] == "PENDING_APPROVAL"

    # 3. Approve plan via API
    appr_res = client.post("/api/incidents/inc_test_01/approve", json={"approver": "OPERATOR_ALICE"})
    assert appr_res.status_code == 200
    appr_data = appr_res.json()
    assert appr_data["status"] == "APPROVED"
    assert appr_data["approved_by"] == "OPERATOR_ALICE"

    # 4. Execute approved plan via API
    exec_res = client.post("/api/incidents/inc_test_01/execute")
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "SUCCESS"

    # 5. Verify recovery via API
    verif_res = client.post("/api/incidents/inc_test_01/verify")
    assert verif_res.status_code == 200
    verif_data = verif_res.json()
    assert verif_data["status"] == "PASSED"

def test_api_authorization_enforcement(monkeypatch):
    # Set secret key requirement
    monkeypatch.setenv("API_SECRET_KEY", "super-secret-key-123")

    # 1. Investigate incident for auth test
    inv_res = client.get("/api/incidents/inc_auth_01/investigation")
    assert inv_res.status_code == 200

    # Attempt approve without key -> Expect 401
    unauth_res = client.post("/api/incidents/inc_auth_01/approve", json={"approver": "OPERATOR_ALICE"})
    assert unauth_res.status_code == 401

    # Attempt approve with invalid key -> Expect 401
    bad_res = client.post("/api/incidents/inc_auth_01/approve", headers={"X-API-Key": "wrong"}, json={"approver": "OPERATOR_ALICE"})
    assert bad_res.status_code == 401

    # Attempt approve with valid key -> Expect 200
    good_res = client.post("/api/incidents/inc_auth_01/approve", headers={"X-API-Key": "super-secret-key-123"}, json={"approver": "OPERATOR_ALICE"})
    assert good_res.status_code == 200

def test_api_demo_inject_and_reset():
    # Inject failure
    inj_res = client.post("/api/demo/inject", json={"scenario": "null_customer_id"})
    assert inj_res.status_code == 200
    assert inj_res.json()["scenario"] == "null_customer_id"

    # Reset failure
    res_res = client.post("/api/demo/reset")
    assert res_res.status_code == 200
    assert res_res.json()["status"] == "HEALTHY"
