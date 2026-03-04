def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_summary_tool(client):
    payload = {"user_token": "student_a", "text": "La fotosintesis es un proceso biologico en plantas."}
    response = client.post("/api/tools/resumir", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "response" in body
    assert "token_usage" in body


def test_document_search_flow(client):
    create_payload = {"user_token": "student_b", "title": "Apuntes de algebra", "content": "Matrices, vectores y determinantes."}
    response = client.post("/api/documents", json=create_payload)
    assert response.status_code == 200

    search_payload = {"user_token": "student_b", "query": "determinantes", "top_k": 3}
    response = client.post("/api/tools/buscar", json=search_payload)
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) >= 1


def test_cost_estimate(client):
    payload = {"daily_interactions": 12, "avg_tokens_in": 450, "avg_tokens_out": 450, "days": 30}
    response = client.post("/api/cost/estimate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["monthly_total_tokens"] == 324000
    assert body["monthly_cost"]["total_cost"] >= 0

